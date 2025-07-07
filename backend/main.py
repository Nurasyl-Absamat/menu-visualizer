from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, Any

from services.database import DatabaseService
from services.ocr import OCRService
from services.matching import MatchingService
from services.image_search import ImageSearchService
from services.storage import StorageService
from models.schemas import ProcessImageResponse, ProductResponse, SessionResponse, ImageResult

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
db_service = None
ocr_service = None
matching_service = None
image_search_service = None
storage_service = None

# Background task status tracking
background_tasks_status: Dict[str, Dict[str, Any]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global db_service, ocr_service, matching_service, image_search_service, storage_service
    
    try:
        # Initialize services
        db_service = DatabaseService()
        await db_service.connect()
        
        ocr_service = OCRService()
        matching_service = MatchingService(db_service)
        image_search_service = ImageSearchService()
        storage_service = StorageService()
        
        logger.info("All services initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        if db_service:
            await db_service.disconnect()
        logger.info("Services cleaned up")

# Create FastAPI app
app = FastAPI(
    title="Menu Visualizer API",
    description="AI-Powered Menu OCR + Product Matcher",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_images_background(session_id: str, enhanced_matches: list):
    """Background task to process images for all products"""
    try:
        logger.info(f"Starting background image processing for session {session_id}")
        
        # Update status
        background_tasks_status[session_id] = {
            "status": "processing_images",
            "progress": 0,
            "total": len(enhanced_matches),
            "completed": 0,
            "error": None
        }
        
        # Process images in parallel for better performance
        async def process_single_product(match_index: int, match: dict):
            try:
                # Use English name for image search if available, otherwise use original name
                search_name = match["nameEnglish"] if match["nameEnglish"] else match["name"]
                logger.info(f"Searching for images for product: '{match['name']}' using search term: '{search_name}'")
                
                # Get multiple images (3 by default)
                images = await image_search_service.search_product_images(search_name, count=3)
                match["images"] = images
                
                # Keep backward compatibility with single image_url
                if images and len(images) > 0:
                    match["image_url"] = images[0]["url"]
                else:
                    match["image_url"] = None
                
                # Update progress
                background_tasks_status[session_id]["completed"] += 1
                background_tasks_status[session_id]["progress"] = (
                    background_tasks_status[session_id]["completed"] / 
                    background_tasks_status[session_id]["total"] * 100
                )
                
                logger.info(f"✅ Processed images for '{match['name']}' ({background_tasks_status[session_id]['completed']}/{background_tasks_status[session_id]['total']})")
                
            except Exception as e:
                logger.error(f"Error processing images for product '{match['name']}': {e}")
                # Set placeholder images on error
                match["images"] = [{
                    "url": f"https://via.placeholder.com/400x300/e5e7eb/6b7280?text={match['name'].replace(' ', '+')}",
                    "source": "placeholder",
                    "photographer": "System Generated",
                    "photographer_url": None
                }] * 3
                match["image_url"] = match["images"][0]["url"]
        
        # Process all products in parallel
        tasks = []
        for i, match in enumerate(enhanced_matches):
            task = asyncio.create_task(process_single_product(i, match))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update session in database with processed images
        session_data = await db_service.get_session(session_id)
        if session_data:
            session_data["matches"] = enhanced_matches
            # Update the session document
            await db_service.update_session(session_id, {"matches": enhanced_matches})
        
        # Mark as completed
        background_tasks_status[session_id]["status"] = "completed"
        background_tasks_status[session_id]["progress"] = 100
        
        logger.info(f"✅ Background image processing completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Background image processing failed for session {session_id}: {e}")
        background_tasks_status[session_id]["status"] = "error"
        background_tasks_status[session_id]["error"] = str(e)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Menu Visualizer API is running"}

# Main image processing endpoint - now returns immediate OCR results
@app.post("/parse-image", response_model=ProcessImageResponse)
async def parse_image(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Process uploaded menu image:
    1. Extract structured data using OCR (immediate response)
    2. Start background task for image processing
    3. Return OCR results immediately
    """
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file size (5MB limit)
        max_size = int(os.getenv("MAX_FILE_SIZE", 5242880))  # 5MB
        content = await file.read()
        file_size = len(content)
        
        if file_size > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
        
        # Reset file pointer for subsequent operations
        await file.seek(0)
        
        # Store uploaded image (this will reset file pointer internally)
        image_path = await storage_service.store_image(file)
        
        # Reset file pointer again before OCR
        await file.seek(0)
        
        # Extract structured data using OCR
        logger.info("Starting OCR processing...")
        structured_ocr = await ocr_service.extract_structured_data(file)
        
        # Check for OCR errors
        ocr_error = structured_ocr.get("error", "")
        if ocr_error:
            logger.warning(f"OCR processing error: {ocr_error}")
        
        # Get products from structured OCR
        ocr_products = structured_ocr.get("products", [])
        logger.info(f"OCR extracted {len(ocr_products)} products")
        
        # Convert OCR products to product names for matching
        product_names = []
        for product in ocr_products:
            name = product.get("name", "").strip()
            name_english = product.get("nameEnglish", "").strip()
            if name:
                product_names.append(name)
                logger.info(f"OCR Product: '{name}' -> English: '{name_english}'")
        
        logger.info(f"Product names for matching: {product_names}")
        
        # Match products against catalog
        matches = await matching_service.match_products(product_names)
        
        # Enhance matches with OCR details (without images initially)
        enhanced_matches = []
        for i, match in enumerate(matches):
            # Find corresponding OCR product
            ocr_product = None
            if i < len(ocr_products):
                ocr_product = ocr_products[i]
            
            # Create enhanced match without images initially
            enhanced_match = {
                "name": match["name"],
                "nameEnglish": ocr_product.get("nameEnglish", "") if ocr_product else "",
                "matched": match["matched"],
                "confidence": match.get("confidence"),
                "product_id": match.get("product_id"),
                "image_url": None,  # Will be populated by background task
                "images": [],  # Will be populated by background task
                "price": ocr_product.get("price", "") if ocr_product else "",
                "description": ocr_product.get("description", "") if ocr_product else "",
                "parsingError": ocr_product.get("parsingError", "") if ocr_product else ""
            }
            
            enhanced_matches.append(enhanced_match)
        
        # Store initial session results without images
        session_data = {
            "image_path": image_path,
            "raw_ocr_text": "",  # Legacy field - keep for compatibility
            "parsed_items": product_names,
            "matches": enhanced_matches,
            "structured_ocr": structured_ocr,
            "images_processed": False
        }
        
        session_id = await db_service.store_session(session_data)
        
        # Start background image processing
        logger.info(f"Starting background image processing for session {session_id}")
        background_tasks.add_task(process_images_background, session_id, enhanced_matches)
        
        # Return immediate response with OCR results
        return ProcessImageResponse(
            session_id=session_id,
            items=enhanced_matches,
            total_items=len(enhanced_matches),
            matched_items=len([m for m in enhanced_matches if m["matched"]]),
            ocr_error=ocr_error if ocr_error else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# New endpoint to check session status and get updated results
@app.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get session processing status and updated results"""
    try:
        # Get session from database
        session_data = await db_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get background task status
        task_status = background_tasks_status.get(session_id, {
            "status": "completed" if session_data.get("images_processed", False) else "not_started",
            "progress": 100 if session_data.get("images_processed", False) else 0,
            "total": len(session_data.get("matches", [])),
            "completed": len(session_data.get("matches", [])) if session_data.get("images_processed", False) else 0,
            "error": None
        })
        
        return {
            "session_id": session_id,
            "processing_status": task_status,
            "items": session_data.get("matches", []),
            "total_items": len(session_data.get("matches", [])),
            "matched_items": len([m for m in session_data.get("matches", []) if m.get("matched", False)]),
            "ocr_error": session_data.get("structured_ocr", {}).get("error")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get products from catalog
@app.get("/products", response_model=list[ProductResponse])
async def get_products(limit: int = 50, offset: int = 0):
    """Get products from catalog"""
    try:
        products = await db_service.get_products(limit=limit, offset=offset)
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get specific product
@app.get("/product/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get specific product by ID"""
    try:
        product = await db_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get session results
@app.get("/results/{session_id}", response_model=SessionResponse)
async def get_session_results(session_id: str):
    """Get OCR session results"""
    try:
        session = await db_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 