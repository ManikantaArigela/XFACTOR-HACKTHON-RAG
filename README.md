# Arudhra Mobile Services Backend

Flask REST backend using PostgreSQL, pgvector, local image storage, and a semantic RAG workflow. No frontend or Cloudinary integration is included.

## Setup

1. Install PostgreSQL with the `pgvector` extension.
2. Create a database, then copy `.env.example` to `.env` and set `DATABASE_URL` and `SECRET_KEY`.
3. Create a virtual environment and install dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Initialize the database:

```powershell
psql "$env:DATABASE_URL" -f database/schema.sql
```

5. Start the API:

```powershell
flask --app app run --debug
```

The first embedding request downloads the configured Sentence Transformers model. Set `OPENAI_API_KEY` to enable generated RAG answers; without it, `/api/chat` returns the retrieved context as a deterministic fallback.

## Endpoints

- `POST /api/upload` multipart field `image`
- `POST /api/users` and `GET /api/users/<id>`
- `POST /api/content`
- `GET /api/content/` and `GET /api/content/<id>`
- `GET /api/search?q=...&limit=10`
- `POST /api/chat` with `{ "query": "...", "limit": 5 }`
- `GET /health`

All API responses use `{ "success": boolean, "message": string, "data": object|null }`. A content request may include `X-User-Id` and an `image_path` returned by the upload endpoint.
