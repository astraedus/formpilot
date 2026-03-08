# FormPilot

Smart form navigator powered by Gemini Vision. Upload a screenshot of any form and get field-by-field fill instructions with auto-fill suggestions.

## Architecture

```
formpilot/
  backend/    Python FastAPI + Gemini Vision + SQLite
  frontend/   Next.js 14 (App Router) + Tailwind CSS
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set GEMINI_API_KEY

uvicorn main:app --reload --port 8000
```

API available at http://localhost:8000
Swagger docs at http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install

cp .env.local.example .env.local
# Edit NEXT_PUBLIC_API_URL if backend is not on port 8000

npm run dev
```

App available at http://localhost:3000

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analyze` | Upload form screenshot + context, returns analysis |
| GET | `/api/analyses` | List all past analyses |
| GET | `/api/analyses/{id}` | Get a specific analysis |
| GET | `/uploads/{filename}` | Serve uploaded images |
| GET | `/health` | Health check |

### POST /api/analyze

Form data fields:
- `file` (required): image file (PNG, JPG, GIF, WebP, max 10MB)
- `user_context` (optional): description of who you are and what form you're filling

Response:
```json
{
  "id": 1,
  "image_path": "/uploads/abc123.png",
  "user_context": "...",
  "fields": [
    {
      "field_name": "Full Name",
      "field_type": "text",
      "suggested_value": "Jane Doe",
      "instructions": "Enter your full legal name.",
      "warning": null,
      "position": {"x": 30, "y": 15}
    }
  ],
  "summary": "Gemini analyzed 5 field(s) in the form.",
  "created_at": "2026-01-01T00:00:00",
  "is_mock": false
}
```

## Environment Variables

### Backend (.env)
| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | (required) | Google Gemini API key |
| `DATABASE_URL` | `./formpilot.db` | SQLite database path |
| `UPLOAD_DIR` | `./uploads` | Directory for uploaded images |

### Frontend (.env.local)
| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

## Without a Gemini API Key

The backend gracefully falls back to realistic mock analysis data when `GEMINI_API_KEY` is not set. Analyses are labeled "Sample data (no API key)" in the UI. This is useful for frontend development without an API key.

Get a free Gemini API key at https://aistudio.google.com/apikey

## Features

- Drag-and-drop or click-to-upload form screenshots
- Gemini Vision analyzes every visible field
- Field-level instructions and auto-fill suggestions
- Position overlays on the form image (numbered markers)
- Step-by-step checklist mode with completion tracking
- Analysis history with thumbnails
- SQLite persistence (no external DB required)
- Mock fallback for development without an API key
