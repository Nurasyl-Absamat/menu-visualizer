# Project Brief: AI-Powered Menu OCR + Product Matcher MVP

## Project Overview
Build a web application that uses AI to extract product names from restaurant menu images and matches them against a product catalog with visual results.

## Core Requirements
1. **Image Upload**: Users can upload restaurant menu images
2. **OCR Processing**: Extract text using GPT-4o Vision API
3. **Product Matching**: Match extracted names against product catalog
4. **Visual Results**: Display matches with product images from Pexels/Unsplash
5. **Data Storage**: Store structured data in MongoDB, images in MinIO
6. **Containerized**: Full Docker Compose deployment

## Technology Stack
- **Frontend**: React + TailwindCSS
- **Backend**: FastAPI (Python)
- **OCR**: OpenAI GPT-4o Vision API
- **Image Search**: Pexels API → Unsplash fallback
- **Database**: MongoDB
- **Storage**: MinIO
- **Deployment**: Docker Compose

## Success Criteria
- User can upload menu image and get matched products with images
- System handles OCR extraction and fuzzy matching
- Results are stored and retrievable
- Application runs via Docker Compose
- Clean, responsive UI with good UX

## Out of Scope (MVP)
- User authentication
- Admin panel for catalog management
- Multilingual support
- Advanced product details
- Feedback mechanisms 