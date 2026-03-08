# Building FormPilot: AI-Powered Form Navigation with Gemini Vision

**TL;DR**: I built FormPilot, a tool that analyzes any form screenshot and provides field-by-field fill instructions with suggested values — powered by Gemini Vision on Cloud Run.

## The Problem

Everyone fills out forms. Government applications, insurance claims, tax documents, HR onboarding — these forms are often confusing, with unclear labels, hidden requirements, and fine print. Small business owners spend 45+ minutes per form, googling terms and calling helplines. One wrong field can delay processing by weeks.

## What FormPilot Does

Upload a screenshot of any form, describe your situation in plain English, and FormPilot:

- **Detects every field** in the form (text inputs, checkboxes, dropdowns, radio buttons)
- **Generates fill instructions** for each field based on your context
- **Suggests values** you should enter
- **Warns about common mistakes** (required fields, format requirements, legal implications)
- **Shows field positions** as numbered markers overlaid on your form image

## How It Works

The pipeline is straightforward:

1. User uploads a form screenshot (PNG, JPG, WebP, up to 10MB)
2. User optionally describes their situation ("I'm a sole trader, earned $75K, single, no dependents")
3. Gemini Vision analyzes the screenshot + context
4. Returns structured field-by-field analysis

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_image(image_data),
        types.Part.from_text(analysis_prompt),
    ],
)
```

The prompt instructs Gemini to return structured JSON with:

```json
{
  "fields": [
    {
      "field_name": "ABN (Australian Business Number)",
      "field_type": "text",
      "suggested_value": "12 345 678 901",
      "instructions": "Enter your 11-digit ABN. Find it at abr.business.gov.au",
      "warning": "Must match your registered business name exactly",
      "position": {"x": 30, "y": 15}
    }
  ],
  "summary": "This is a BAS (Business Activity Statement) form..."
}
```

## Architecture

```
Browser (Next.js)                    Google Cloud
  │                                  ┌──────────────────┐
  ├─ Upload screenshot               │  Cloud Run       │
  │   + context text                 │  (FastAPI)       │
  │   → POST /api/analyze ─────►    │       │          │
  │                                  │  Gemini 2.5 Flash│
  │                                  │  Vision API      │
  │                                  │       │          │
  │   ◄── field analysis ◄──────    │  Field detection │
  │                                  │  + suggestions   │
  ├─ View annotated form             │  + warnings      │
  │   (numbered markers)             │       │          │
  ├─ Step-by-step checklist          │  SQLite DB       │
  └─ Analysis history                │  Uploads dir     │
                                     └──────────────────┘
```

## Frontend Features

- **Drag-and-drop upload** with image preview
- **Position overlays** — numbered markers on the form image showing where each field is
- **Step-by-step checklist** — check off fields as you fill them, with completion tracking
- **Analysis history** — browse previous analyses with thumbnails
- **Warning highlights** — fields with potential issues are flagged

## Google Cloud Services

| Service | Purpose |
|---------|---------|
| **Cloud Run** | Backend hosting (auto-scaling, serverless) |
| **Cloud Build** | Container image building |
| **Secret Manager** | API key storage |
| **Generative Language API** | Gemini Vision form analysis |

## Infrastructure as Code

One script deploys everything:

```bash
export GOOGLE_API_KEY="your-key"
export GOOGLE_CLOUD_PROJECT="your-project-id"
./deploy.sh
```

Automates: GCP API enablement, Secret Manager secret creation, container build, Cloud Run deploy, and optional Vercel frontend deployment.

## Mock Mode

Without a Gemini API key, FormPilot returns realistic mock analysis data — the full UI works for development. The UI labels mock results as "Sample data (no API key)."

Get a free Gemini API key at https://aistudio.google.com/apikey to unlock real analysis.

## Try It

- **GitHub**: https://github.com/astraedus/formpilot
- **Live Demo**: https://formpilot-api-93135657352.us-central1.run.app

Built for the Gemini Live Agent Challenge. #GeminiLiveAgentChallenge

---

*Built with Gemini 2.5 Flash Vision API, FastAPI, Next.js, and Cloud Run.*
