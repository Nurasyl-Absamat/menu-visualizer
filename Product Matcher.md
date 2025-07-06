
# 🧾 Product Requirements Document (PRD)  
### 📌 Project: AI-Powered Menu OCR + Product Matcher MVP  
### 🧑‍💻 Author: You  
### 📅 Date: July 2025  

---

## 1. 🎯 Objective

Build a simple and cool web app where a user can:
1. Upload an image of a restaurant menu or similar product list.
2. Extract product names using **GPT-4o (Vision OCR)**.
3. Match those names against a known **product catalog**.
4. Display matching results along with **product images** pulled via **Pexels**, or fallback to **Unsplash**.
5. Store structured data in **MongoDB** and images in **MinIO**.

---

## 2. 👤 User Flow

```
[User uploads image]
        ↓
[Backend processes image using GPT-4o OCR]
        ↓
[Extracted text is parsed into product names]
        ↓
[Each name is matched against the product catalog]
        ↓
[Image of the product fetched from Pexels or Unsplash]
        ↓
[Results shown: product name, match status, image]
```

---

## 3. 🖼️ UI Pages (Frontend)

| Page | Description |
|------|-------------|
| `/` (Home) | Image uploader (drag/drop or file select), submit button |
| `/results` | List of detected items with match status and images |
| `/products` | Optional: browse current product catalog |
| (future) `/admin` | Upload catalog, manage matches (not in MVP) |

---

## 4. ⚙️ Technologies

| Part | Stack |
|------|-------|
| Frontend | React + TailwindCSS |
| Backend | FastAPI (Python) |
| OCR | OpenAI GPT-4o Vision API |
| Image Search | Pexels API → fallback to Unsplash API |
| Data Storage | MongoDB |
| Image Storage | MinIO (via Docker Compose) |
| Deployment | Dockerfile + docker-compose.yml |

---

## 5. 🧠 Core Features

### ✅ MVP Features

| Feature | Description |
|--------|-------------|
| Image upload | User can upload an image |
| OCR processing | Backend sends image to GPT-4o Vision |
| Text parsing | Extracts potential product names |
| Catalog matching | Uses fuzzy or semantic matching |
| Product images | Fetched from Pexels API; fallback to Unsplash |
| Result display | Show extracted items, match status, and image |
| MongoDB | Stores catalog, OCR logs, matched results |
| MinIO | Stores uploaded images for reuse/debugging |
| Dockerized | Fully runnable via Docker Compose |

---

## 6. 🗃️ MongoDB Schema (MVP)

```json
// products
{
  "_id": "uuid",
  "name": "Minestrone Soup",
  "aliases": ["minestrone", "vegetable soup"],
  "image_url": "https://images.pexels.com/...",
  "tags": ["soup", "italian"]
}

// ocr_sessions
{
  "_id": "uuid",
  "upload_time": "2025-07-07T12:00Z",
  "image_path": "minio://uploads/menu_123.png",
  "raw_ocr_text": "...",
  "parsed_items": ["Minestrone", "Caesar Salad"],
  "matches": [
    {"name": "Minestrone", "matched": true, "product_id": "..."},
    {"name": "Caesar Salad", "matched": false}
  ]
}
```

---

## 7. 🧪 API Endpoints (MVP)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/parse-image` | Accept image, send to GPT-4o, return parsed & matched items |
| `GET`  | `/products` | Get list of catalog products |
| `GET`  | `/product/:id` | Get product details |
| `GET`  | `/results/:session_id` | View OCR result session |
| (internal) | `GET /image-search?query=...` | Used to fetch product image from Pexels/Unsplash |

---

## 8. 🔐 Security & Config

- `.env` for API keys (OpenAI, Pexels, Unsplash)
- Limit image size (e.g., 5MB)
- Optional rate limiting
- CORS enabled for frontend

---

## 9. 📦 Docker Compose Services

```yaml
services:
  web:
    build: ./frontend
    ports:
      - "3000:3000"

  api:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - mongo
      - minio

  mongo:
    image: mongo:6
    ports:
      - "27017:27017"

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - ./minio_data:/data
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: password
    command: server /data --console-address ":9001"
```

---

## 10. 🚀 Future Stretch Goals

- Product detail modal (nutrition, description)
- Multilingual menu support (e.g. Russian, Kazakh)
- Auto-tagging by GPT
- Feedback loop: user marks “wrong match”
- Catalog management panel
- AI-generated product images (DALL·E or Stable Diffusion fallback)
- OAuth login
