# FormPilot

**Chrome extension that guides you through confusing forms with AI.** Click the icon, tell it about yourself, and get field-by-field tooltips + one-click autofill. Powered by Gemini Vision.

## The Problem

Government forms, visa applications, tax returns, insurance claims -- they're confusing, jargon-heavy, and high-stakes. One wrong field on a DS-160 means months of delay. 44M immigrants in the US and 55M Americans over 65 face this daily.

## The Solution

FormPilot is a Chrome extension. You're already on the form. One click. AI reads the page, guides every field, autofills with one button.

**Before**: 20 blank fields, confusing labels, no idea what to enter.
**After**: Numbered tooltips on every field, suggested values, warnings about gotchas, one-click autofill.

## Live Demo & Links

| | |
|---|---|
| **Backend API** | [formpilot-api-93135657352.us-central1.run.app](https://formpilot-api-93135657352.us-central1.run.app/health) |
| **Demo Video** | [youtu.be/t9K7kGAvduU](https://youtu.be/t9K7kGAvduU) |
| **Blog Post** | [Building FormPilot](https://dev.to/diven_rastdus_c5af27d68f3/building-formpilot-ai-powered-form-navigation-with-gemini-vision-1gbb) |
| **DevPost** | [devpost.com/software/formpilot](https://devpost.com/software/formpilot) |
| **Hackathon** | Gemini Live Agent Challenge 2026 -- UI Navigator track |

## How It Works

```
You're on a confusing form (visa app, tax return, etc.)
  -> Click FormPilot icon
  -> Enter context: "I'm a 26yo Australian applying for H-1B"
  -> Extension captures screenshot + extracts all form fields from DOM
  -> Sends to Cloud Run backend
  -> Gemini Vision analyzes screenshot + field metadata
  -> Returns field-by-field guidance
  -> Numbered tooltip circles appear on each field
  -> Click any circle for instructions, suggested value, warnings
  -> "Autofill All" fills every field with AI suggestions
```

## Install the Extension

### From Source (Developer Mode)

```bash
# Build
cd extension
npm install
npm run build

# Load in Chrome
# 1. Go to chrome://extensions
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the extension/dist/ folder
```

Or load the pre-built `extension/dist/` directory directly.

## Architecture

```
Chrome Extension (MV3)
  |-- popup/        Context input + Analyze button
  |-- content/      DOM extraction, Shadow DOM overlays, autofill
  |-- background/   Service worker
  |-- lib/          Field matcher (Gemini labels -> DOM elements)
  |
  |--> POST /api/analyze (screenshot + DOM fields + context)
  |
Cloud Run Backend (Python FastAPI)
  |-- Gemini Vision (gemini-2.5-flash)
  |-- SQLite persistence
  |-- Mock fallback (no API key)
```

**Key technical decisions:**
- **Shadow DOM** for overlay isolation (no CSS conflicts with host page)
- **DOM field metadata** sent alongside screenshot so Gemini uses exact field names (near-trivial matching)
- **Native value setter** trick (`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set`) for React/Angular/Vue compatibility
- **TypeScript + tsc** build (no bundler complexity)

## Backend Quick Start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Set GOOGLE_API_KEY
uvicorn main:app --reload --port 8000
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analyze` | Screenshot + context -> field analysis |
| GET | `/api/analyses` | List past analyses |
| GET | `/api/analyses/{id}` | Get specific analysis |
| GET | `/health` | Health check |

### POST /api/analyze

```
Content-Type: multipart/form-data
  file: <screenshot PNG>
  user_context: "User context + DOM field metadata"

Response: {
  id, fields: [{field_name, field_type, suggested_value, instructions, warning, position}],
  summary, is_mock
}
```

## Cloud Deployment

```bash
export GOOGLE_API_KEY="your-key"
./deploy.sh your-gcp-project-id
```

Automates: GCP APIs, Secret Manager, Cloud Build, Cloud Run deploy.

## Google Cloud Services

| Service | Purpose |
|---------|---------|
| Cloud Run | Backend hosting (serverless, auto-scaling) |
| Cloud Build | Container image building |
| Secret Manager | API key storage |
| Generative Language API | Gemini Vision form analysis |

## Without a Gemini API Key

Backend falls back to mock analysis data. Get a free key at https://aistudio.google.com/apikey

## Features

- **Zero friction**: Works on the page you're already on
- **DOM-aware**: Extracts real field names, labels, types from the page
- **Smart matching**: Gemini uses exact DOM labels for near-perfect field matching
- **Shadow DOM isolation**: Overlays never break the host page's styling
- **Framework-compatible autofill**: Works with React, Angular, Vue, vanilla HTML
- **Persistent context**: Remembers your info across sessions
- **Graceful fallback**: Mock data when no API key is set
