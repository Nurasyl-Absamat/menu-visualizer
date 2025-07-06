# Menu Visualizer - AI-Powered OCR + Product Matcher

A web application that uses AI to extract product names from restaurant menu images and matches them against a product catalog with visual results.

## 🚀 Features

- **Image Upload**: Drag and drop menu images with preview
- **AI OCR**: Extract text using GPT-4o Vision API
- **Product Matching**: Match extracted items against catalog
- **Visual Results**: Display matches with product images from Pexels/Unsplash
- **Data Storage**: MongoDB for structured data, MinIO for images
- **Responsive UI**: Modern React interface with TailwindCSS
- **Containerized**: Full Docker Compose deployment

## 🛠️ Technology Stack

- **Frontend**: React 18 + TailwindCSS + Vite
- **Backend**: FastAPI + Python 3.11
- **Database**: MongoDB
- **Storage**: MinIO (S3-compatible)
- **AI**: OpenAI GPT-4o Vision
- **Images**: Pexels API + Unsplash API
- **Deployment**: Docker Compose

## 📋 Prerequisites

- Docker & Docker Compose
- API Keys for:
  - OpenAI GPT-4o Vision
  - Pexels API
  - Unsplash API

## 🚀 Quick Start

### Production Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd menu-visualizer
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

### Development Setup (Hot Reload)
1. **Using Makefile (Recommended)**
   ```bash
   # See all available commands
   make help
   
   # Full development environment with hot reload
   make dev
   
   # Just infrastructure for local development
   make infra
   ```

2. **Local development (fastest)**
   ```bash
   # Start infrastructure only
   make infra
   
   # In separate terminals:
   make start-frontend  # Frontend with hot reload
   make start-backend   # Backend with hot reload
   ```

3. **Quick commands**
   ```bash
   make stop           # Stop everything
   make logs           # View logs
   make health         # Check service health
   make test           # Test API endpoints
   ```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (admin/password123)

## 🔧 Configuration

### Required Environment Variables

```env
# OpenAI API
OPENAI_API_KEY=sk-your-key-here

# Image Search APIs
PEXELS_API_KEY=your-pexels-key
UNSPLASH_ACCESS_KEY=your-unsplash-key
```

### Optional Configuration

```env
# Application limits
MAX_FILE_SIZE=5242880  # 5MB
CORS_ORIGINS=http://localhost:3000

# Database
MONGODB_DATABASE=menu_matcher

# MinIO
MINIO_BUCKET=menu-images
```

## 🏗️ Architecture

```
Frontend (React) ↔ Backend (FastAPI) ↔ [MongoDB, MinIO, External APIs]
```

### Core Components

1. **Frontend Layer**
   - ImageUploader: Drag/drop file upload
   - ResultsDisplay: Grid of matched products
   - ProductCard: Individual product display
   - LoadingSpinner: Processing feedback

2. **Backend Layer**
   - OCRService: GPT-4o Vision integration
   - MatchingService: Product catalog matching
   - ImageService: Pexels/Unsplash integration
   - StorageService: MongoDB/MinIO operations

3. **Data Layer**
   - MongoDB: Products catalog + OCR sessions
   - MinIO: Uploaded images storage

## 📁 Project Structure

```
menu-visualizer/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── Dockerfile
│   └── package.json
├── backend/                  # FastAPI application
│   ├── services/           # Business logic services
│   ├── models/             # Data models
│   ├── main.py             # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── memory-bank/             # Project documentation
├── docker-compose.yml       # Service orchestration
└── README.md
```

## 🔄 User Flow

1. **Upload**: User uploads menu image
2. **OCR**: GPT-4o extracts text from image
3. **Parse**: Text is parsed into product names
4. **Match**: Names matched against catalog
5. **Images**: Product images fetched from APIs
6. **Results**: Display matched products with images

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/parse-image` | Process menu image |
| GET | `/products` | Get product catalog |
| GET | `/product/{id}` | Get specific product |
| GET | `/results/{session_id}` | Get session results |
| GET | `/health` | Health check |

## 🔧 Development

### Local Development (without Docker)

1. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Services**
   - Start MongoDB: `docker run -p 27017:27017 mongo:6`
   - Start MinIO: `docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"`

### Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📊 Sample Data

The application comes with pre-seeded product catalog:
- Caesar Salad
- Minestrone Soup
- Margherita Pizza
- Grilled Chicken
- Fish and Chips
- Chocolate Cake
- Pasta Carbonara
- Beef Burger

## 🚨 Troubleshooting

### Common Issues

1. **API Keys**: Ensure all API keys are properly set in `.env`
2. **Docker**: Make sure Docker has enough memory allocated
3. **Ports**: Check that ports 3000, 8000, 9000, 9001, 27017 are available
4. **File Size**: Images must be under 5MB

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs web
```

## 🔮 Future Enhancements

- [ ] User authentication
- [ ] Admin panel for catalog management
- [ ] Multilingual menu support
- [ ] Advanced product details
- [ ] Feedback system for improving matches
- [ ] AI-generated product images
- [ ] Performance analytics

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `/docs` 