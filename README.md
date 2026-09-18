# Arudhra Mobile Stores

Arudhra Mobile Stores is a responsive HTML storefront with a modular Flask RAG assistant backend.

## Repository layout

- `FRONTEND/`: HTML storefront pages (`index-tailwind.html`, `shop-tailwind.html`, `product-tailwind.html`, `cart-tailwind.html`, `checkout-tailwind.html`), JavaScript logic, and prototype documentation.
- `BACKEND/`: Flask, PostgreSQL, pgvector, and RAG service API.
- `LEGACY_BACKEND/`: Monolithic legacy backend implementation kept for reference and compatibility.

## Run the frontend

Navigate to the `FRONTEND` directory and start a local static server:

```powershell
cd FRONTEND
python -m http.server 8000
```

Open <http://localhost:8000/index-tailwind.html>.

## Git workflow

Run Git commands from this repository root directory, not its parent folder:

```powershell
git status
git pull --ff-only origin main
git add -A
git commit -m "Describe the change"
git push origin main
```

The configured remote is `https://github.com/ManikantaArigela/XFACTOR-HACKTHON-RAG`.
Do not paste the output of `git remote -v` back into PowerShell. The `(fetch)` and `(push)` lines are informational output, not commands.

## Run the RAG backend

The backend requires PostgreSQL with the `pgvector` extension. Configure `BACKEND/.env` from `BACKEND/.env.example` before starting it.

1. Create a virtual environment and install dependencies:

```powershell
cd BACKEND
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Initialize the database:

```powershell
python -m scripts.init_db
```

3. Start the API:

```powershell
python main.py
```

The API runs at `http://localhost:5000`. The first embedding request downloads the configured Sentence Transformers model.

## Endpoints

- `POST /api/chat` with `{ "message": "..." }`
- `GET /health`

The backend is optional; the frontend pages run without PostgreSQL, API keys, or a server-side application.

