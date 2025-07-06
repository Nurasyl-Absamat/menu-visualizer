# System Patterns: Menu OCR + Product Matcher

## Architecture Overview
```
Frontend (React) ↔ Backend (FastAPI) ↔ [MongoDB, MinIO, External APIs]
```

## Core Components

### 1. Frontend Layer (React + TailwindCSS)
- **Single Page Application**: Simple upload → results flow
- **Component Structure**:
  - `ImageUploader`: Drag/drop file upload
  - `ResultsDisplay`: Grid of matched products with images
  - `ProductCard`: Individual product match display
  - `LoadingSpinner`: Processing feedback

### 2. Backend Layer (FastAPI)
- **API-First Design**: RESTful endpoints for all operations
- **Service Architecture**:
  - `OCRService`: GPT-4o Vision integration
  - `MatchingService`: Product catalog matching logic
  - `ImageService`: Pexels/Unsplash image fetching
  - `StorageService`: MongoDB/MinIO operations

### 3. Data Layer
- **MongoDB**: Document-based storage for flexible schemas
  - `products` collection: Product catalog
  - `ocr_sessions` collection: Processing results
- **MinIO**: S3-compatible object storage for images

### 4. External Integrations
- **OpenAI GPT-4o Vision**: OCR text extraction
- **Pexels API**: Primary image source
- **Unsplash API**: Fallback image source

## Key Design Patterns

### 1. Pipeline Processing
```
Image Upload → OCR → Text Parsing → Matching → Image Fetching → Storage
```

### 2. Fallback Strategy
- Image sources: Pexels → Unsplash → Default placeholder
- Error handling: Graceful degradation at each step

### 3. Session-Based Processing
- Each upload creates a session for tracking
- Results tied to sessions for retrieval

### 4. Async Processing
- Non-blocking API calls
- Background image fetching
- Progress feedback to frontend

## Data Flow Patterns

### Upload Flow
1. Frontend uploads image to backend
2. Backend stores in MinIO, creates session
3. Image sent to GPT-4o for OCR
4. Text parsed into product names
5. Names matched against catalog
6. Images fetched for matches
7. Results stored in MongoDB
8. Response sent to frontend

### Matching Algorithm
1. **Exact Match**: Direct name comparison
2. **Fuzzy Match**: Levenshtein distance
3. **Semantic Match**: Future enhancement with embeddings

## Error Handling Patterns
- **Graceful Degradation**: Continue processing even if some steps fail
- **Retry Logic**: Automatic retries for external API calls
- **Fallback Responses**: Default images and messages
- **Logging**: Comprehensive error tracking

## Performance Patterns
- **Caching**: Image URLs and matching results
- **Batch Processing**: Multiple image searches in parallel
- **Lazy Loading**: Frontend loads images as needed
- **Connection Pooling**: Database and external API connections 