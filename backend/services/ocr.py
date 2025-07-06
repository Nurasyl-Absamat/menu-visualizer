import os
import base64
import json
from typing import List, Dict, Any
from fastapi import UploadFile
import openai
import logging
import re

logger = logging.getLogger(__name__)

class OCRService:
    """OpenAI GPT-4o Vision OCR service with structured output"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def _get_image_mime_type(self, image_content: bytes) -> str:
        """Detect image MIME type from content"""
        # Check magic bytes to determine image format
        if image_content.startswith(b'\xff\xd8\xff'):
            return "image/jpeg"
        elif image_content.startswith(b'\x89PNG\r\n\x1a\n'):
            return "image/png"
        elif image_content.startswith(b'GIF87a') or image_content.startswith(b'GIF89a'):
            return "image/gif"
        elif image_content.startswith(b'RIFF') and b'WEBP' in image_content[:12]:
            return "image/webp"
        else:
            # Default to JPEG if we can't detect
            return "image/jpeg"
    
    async def extract_structured_data(self, image_file: UploadFile) -> Dict[str, Any]:
        """Extract structured menu data from image using GPT-4o Vision"""
        try:
            # Reset file pointer to beginning
            await image_file.seek(0)
            
            # Read image content
            image_content = await image_file.read()
            
            # Validate image content
            if not image_content:
                logger.error("Empty image content")
                return {
                    "products": [],
                    "error": "Empty image content - please upload a valid image"
                }
            
            # Detect image format
            mime_type = self._get_image_mime_type(image_content)
            logger.info(f"Detected image format: {mime_type}")
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # Validate base64 encoding
            if not image_base64:
                logger.error("Failed to encode image to base64")
                return {
                    "products": [],
                    "error": "Failed to process image - encoding error"
                }
            
            logger.info(f"Base64 encoded image length: {len(image_base64)}")
            
            # Create the structured prompt for menu OCR
            prompt = """
            Analyze this menu image and extract all food items with their details. 
            Return the data in the following JSON format:
            
            {
                "products": [
                    {
                        "name": "Food item name as it appears on the menu (original language)",
                        "nameEnglish": "English translation of the food item name (for image search)",
                        "price": "Price if visible (e.g., '$12.99', '€15.50', or empty string if not visible)",
                        "description": "Brief description if available (or empty string)",
                        "parsingError": "Any issue parsing this specific item (or empty string if no issues)"
                    }
                ],
                "error": ""
            }
            
            Instructions:
            - Extract ALL food items: main dishes, appetizers, soups, salads, beverages, desserts
            - Keep original names in 'name' field exactly as they appear on the menu
            - Provide English translation in 'nameEnglish' field for better image search
            - If the original name is already in English, use the same name for both fields
            - Clean item names: remove numbering, prices, and extra formatting
            - Include prices only if clearly visible and associated with items
            - Add descriptions only if they exist in the menu
            - Use parsingError field for items that are hard to read or unclear
            - Use the main error field only for overall parsing problems
            - If you can't read the menu at all, set the main error field
            - Return valid JSON format
            - Focus on common, searchable English food names for nameEnglish (e.g., "Pizza", "Burger", "Salad")
            """
            
            # Make API call to GPT-4o Vision
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse the structured response
            response_content = response.choices[0].message.content
            logger.info(f"OCR response length: {len(response_content)}")
            
            try:
                structured_data = json.loads(response_content)
                
                # Validate the structure
                if not isinstance(structured_data, dict):
                    raise ValueError("Response is not a valid JSON object")
                
                if "products" not in structured_data:
                    structured_data["products"] = []
                
                if "error" not in structured_data:
                    structured_data["error"] = ""
                
                # Validate products array
                if not isinstance(structured_data["products"], list):
                    structured_data["products"] = []
                
                # Clean and validate each product
                cleaned_products = []
                for product in structured_data["products"]:
                    if isinstance(product, dict):
                        cleaned_product = {
                            "name": str(product.get("name", "")).strip(),
                            "nameEnglish": str(product.get("nameEnglish", "")).strip(),
                            "price": str(product.get("price", "")).strip(),
                            "description": str(product.get("description", "")).strip(),
                            "parsingError": str(product.get("parsingError", "")).strip()
                        }
                        
                        # Only add products with valid names
                        if cleaned_product["name"] and len(cleaned_product["name"]) > 1:
                            cleaned_products.append(cleaned_product)
                
                structured_data["products"] = cleaned_products
                
                logger.info(f"Successfully parsed {len(cleaned_products)} products")
                return structured_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response_content}")
                return {
                    "products": [],
                    "error": f"Failed to parse menu data - invalid response format"
                }
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "products": [],
                "error": f"AI service error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "products": [],
                "error": f"Menu processing failed: {str(e)}"
            }
    
    async def extract_text(self, image_file: UploadFile) -> str:
        """Legacy method for backward compatibility - extracts text only"""
        try:
            structured_data = await self.extract_structured_data(image_file)
            
            if structured_data.get("error"):
                logger.warning(f"OCR error: {structured_data['error']}")
                return ""
            
            # Convert structured data back to text format for compatibility
            products = structured_data.get("products", [])
            text_lines = []
            
            for product in products:
                name = product.get("name", "")
                if name:
                    text_lines.append(name)
            
            return "\n".join(text_lines)
            
        except Exception as e:
            logger.error(f"Legacy text extraction failed: {e}")
            return ""
    
    async def parse_product_names(self, ocr_text: str) -> List[str]:
        """Legacy method for backward compatibility - parses product names from text"""
        try:
            if not ocr_text.strip():
                return []
            
            # Split by lines and clean up
            lines = ocr_text.strip().split('\n')
            product_names = []
            
            for line in lines:
                # Clean up the line
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Remove common menu artifacts
                line = re.sub(r'^\d+[\.\)]\s*', '', line)  # Remove numbering
                line = re.sub(r'\$[\d\.,]+', '', line)    # Remove prices
                line = re.sub(r'\d+\.\d+', '', line)      # Remove decimal numbers
                line = re.sub(r'\s+', ' ', line)          # Normalize spaces
                line = line.strip()
                
                # Skip if too short or looks like noise
                if len(line) < 3:
                    continue
                
                # Skip lines that are mostly numbers or symbols
                if re.match(r'^[\d\s\$\.\,\-]+$', line):
                    continue
                
                # Add to results
                product_names.append(line)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_names = []
            for name in product_names:
                if name.lower() not in seen:
                    seen.add(name.lower())
                    unique_names.append(name)
            
            logger.info(f"Parsed {len(unique_names)} product names from OCR text")
            return unique_names[:20]  # Limit to 20 items for MVP
            
        except Exception as e:
            logger.error(f"Product name parsing failed: {e}")
            return [] 