# Technical Context: Menu OCR + Product Matcher

## Technology Stack

### Frontend
- **React 18**: Modern React with hooks and functional components
- **TailwindCSS**: Utility-first CSS framework for rapid UI development
- **Axios**: HTTP client for API communication
- **React Router**: Client-side routing (if needed for multiple pages)

### Backend
- **FastAPI**: Modern Python web framework with automatic OpenAPI docs
- **Python 3.11+**: Latest Python for performance and features
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for FastAPI

### Database & Storage
- **MongoDB**: NoSQL document database for flexible schemas
- **PyMongo**: Python MongoDB driver
- **MinIO**: S3-compatible object storage
- **Docker**: Containerization for all services

### External APIs
- **OpenAI GPT-4o Vision**: OCR and text extraction
- **Pexels API**: Primary image search service
- **Unsplash API**: Fallback image search service

## Development Environment

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Local Development Setup
```bash
# Clone repository
git clone <repo-url>
cd menu-visualizer

# Start services
docker-compose up -d

# Frontend development
cd frontend
npm install
npm run dev

# Backend development
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Configuration Management

### Environment Variables
```env
# OpenAI
OPENAI_API_KEY=sk-...

# Image APIs
PEXELS_API_KEY=...
UNSPLASH_ACCESS_KEY=...

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=menu_matcher

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password
MINIO_BUCKET=menu-images

# Application
CORS_ORIGINS=http://localhost:3000
MAX_FILE_SIZE=5242880  # 5MB
```

## Technical Constraints

### Performance
- Image upload limit: 5MB
- OCR processing timeout: 30 seconds
- Maximum concurrent requests: 10
- Image search results: 1 per product

### Security
- CORS configured for frontend origin
- File type validation (images only)
- API key protection via environment variables
- No authentication required for MVP

### Scalability Considerations
- Stateless backend for horizontal scaling
- MongoDB for flexible schema evolution
- MinIO for distributed file storage
- External API rate limiting handled

## Dependencies

### Backend Requirements
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pymongo==4.6.0
minio==7.2.0
openai==1.3.0
requests==2.31.0
python-dotenv==1.0.0
Pillow==10.1.0
fuzzywuzzy==0.18.0
python-levenshtein==0.23.0
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.3",
    "vite": "^4.4.5"
  }
}
```

## Deployment Strategy

### Docker Compose Services
- **web**: React frontend (port 3000)
- **api**: FastAPI backend (port 8000)
- **mongo**: MongoDB database (port 27017)
- **minio**: Object storage (ports 9000, 9001)

### Production Considerations
- Use production-grade MongoDB cluster
- Configure MinIO with proper access policies
- Set up reverse proxy (nginx) for SSL termination
- Implement proper logging and monitoring
- Configure backup strategies for data persistence 