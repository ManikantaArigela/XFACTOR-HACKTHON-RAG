# Arudhra Mobile Stores — RAG AI Shopping Assistant Backend

Official RAG / Retrieval / Grounding Layer for **Arudhra Mobile Stores** (Pithapuram, Andhra Pradesh, India).

Built for the **X-Factor LevelX Phase 2 Hackathon**.

---

## Technical Stack
- **Language**: Python 3.10+
- **API Framework**: Flask
- **Database**: PostgreSQL with `pgvector` extension & SQLAlchemy ORM
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions)
- **LLM Engine**: Multi-provider (Google Gemini / OpenAI / Zero-hallucination fallback)
- **Guardrails**: Cosine similarity thresholding & SQL query strict constraint checking

---

## Directory Layout
```
BACKEND/
├── config/             # Settings loader (pydantic-settings & dotenv)
├── db/                 # Database engine & SQLAlchemy models (pgvector)
├── data/
│   ├── raw/            # Raw Instagram post JSON data
│   └── processed/
├── ingestion/          # Loader, cleaner, spec extractor, RAG document builder
├── embeddings/         # SentenceTransformers 384d vector embedder
├── retrieval/          # pgvector vector search, SQL structured search, hybrid merger
├── guardrails/         # Grounding evaluation & "I don't know" refusal guardrails
├── generation/         # Query analyzer, prompt templates, LLM generator
├── api/                # Flask Blueprint (POST /api/chat)
├── evaluation/         # Benchmark suite (questions.json & evaluate.py)
├── scripts/            # Database init & ingestion execution scripts
├── uploads/            # Local image storage
├── main.py             # Flask entry point
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variable template
```

---

## Quickstart Setup Guide

### 1. Install Dependencies
```bash
cd BACKEND
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your PostgreSQL server credentials and optional `GEMINI_API_KEY` are configured in `.env`.

### 3. Initialize PostgreSQL + pgvector Schema
```bash
python -m scripts.init_db
```
*Creates `vector` extension, `uuid-ossp` extension, database tables, and the HNSW vector index.*

### 4. Run Data Ingestion Pipeline
```bash
python -m scripts.run_ingestion
```
*Parses raw Instagram posts (`data/raw/instagram_posts.json`), extracts structured product specifications into PostgreSQL `products`, generates 384-dim embeddings, and updates `knowledge_documents` in pgvector.*

### 5. Run RAG Benchmark & Evaluation Suite
```bash
python -m evaluation.evaluate
```
*Runs automated evaluation tests across known queries, unknown product questions, and prompt injection attacks.*

### 6. Start the Flask API Server
```bash
python main.py
```
The server will start at `http://localhost:5000`.

---

## API Documentation

### `POST /api/chat`

#### Request:
```json
{
  "message": "Show me Samsung phones under 30000"
}
```

#### Grounded Response (Success):
```json
{
  "answer": "Here are the details from Arudhra Mobile Stores, Pithapuram:\n\n• Samsung Galaxy S23 5G...\n• Samsung Galaxy M14 5G (6GB RAM | 128GB Storage)\n  Price: ₹13,999.00",
  "products": [
    {
      "id": "c7a...",
      "name": "Samsung Galaxy M14 5G",
      "brand": "Samsung",
      "price": 13999.0,
      "ram": "6GB",
      "storage": "128GB",
      "image_path": "uploads/instagram/samsung_m14.jpg"
    }
  ],
  "sources": [
    {
      "source_type": "instagram",
      "source_url": "https://www.instagram.com/p/post_samsung_m14_07/"
    }
  ],
  "grounded": true,
  "confidence": 0.7852
}
```

#### Grounded Refusal Response (Unknown Data Query):
```json
{
  "answer": "I don't have enough information to answer that from the available Arudhra store data.",
  "products": [],
  "sources": [],
  "grounded": false,
  "confidence": 0.0
}
```
