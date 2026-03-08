# DevPost Submission — FormPilot

## Project Name
FormPilot — Smart Form Navigator

## Category
Best UI Navigator

## Tagline
Screenshot any form, describe your situation, get field-by-field fill instructions with auto-fill suggestions

## Description

### Inspiration
Everyone fills out complex forms — government applications, insurance claims, tax documents, HR onboarding. Small business owners spend 45+ minutes per form: reading fine print, googling terms, calling helplines. One wrong field can delay processing by weeks. We wanted to build an AI that could look at any form screenshot, understand every field, and tell you exactly what to enter.

### What it does
Upload a screenshot of any form and describe your situation in plain English. FormPilot:

- **Detects every visible field** — text inputs, checkboxes, dropdowns, radio buttons
- **Generates fill instructions** — what each field means and how to fill it correctly
- **Suggests specific values** based on your context ("sole trader, earned $75K, single")
- **Warns about common mistakes** — required fields, format requirements, legal implications
- **Shows field positions** as numbered markers overlaid on the original form image
- **Provides a step-by-step checklist** to track completion

### How we built it
**Backend**: Python FastAPI on Cloud Run. The form analyzer sends the uploaded screenshot + user context to Gemini Vision (`gemini-2.5-flash`), which returns structured JSON with field names, types, suggested values, instructions, warnings, and approximate positions.

The prompt engineering is critical — we instruct Gemini to:
1. Identify every visible form field (including partially visible ones)
2. Infer field types from visual cues (text box vs. checkbox vs. dropdown)
3. Generate contextually appropriate fill values based on the user's description
4. Flag fields that commonly cause errors
5. Return approximate x,y positions for overlay markers

**Frontend**: Next.js with drag-and-drop upload, annotated form image with numbered position markers, expandable field cards with instructions/warnings, and a step-by-step checklist mode with completion tracking.

### Challenges we ran into
- Getting Gemini to return consistent position coordinates for field overlay markers
- Handling diverse form layouts (government forms, insurance documents, web forms, PDF screenshots)
- Balancing between detailed instructions and concise, actionable guidance

### Accomplishments that we're proud of
- The field detection accuracy is impressive — Gemini correctly identifies fields even in complex multi-column government forms
- The numbered position markers overlaid on the form image make it immediately clear which instruction corresponds to which field
- The checklist mode turns a confusing form into a step-by-step guided process

### What we learned
- Gemini Vision's form understanding is remarkably good — it can read handwritten labels, understand form layouts, and infer field purposes from context
- Structured JSON output from Gemini is reliable when the prompt specifies the exact schema
- Position coordinates (x%, y%) work well enough for approximate field markers even though they're AI-estimated

### What's next for FormPilot
- Browser extension for in-page form detection (no screenshot needed)
- Auto-fill integration with form input fields
- Multi-page form support with cross-page field validation
- Form template library for common government forms

## Built With
- Google Gemini 2.5 Flash Vision API (gemini-2.5-flash)
- Google GenAI SDK
- FastAPI + Uvicorn
- Next.js 14 + React 18 + TypeScript
- Tailwind CSS
- Google Cloud Run
- Google Cloud Build
- Google Secret Manager
- SQLite + aiosqlite
- Python 3.12

## Try it out
- GitHub: https://github.com/astraedus/formpilot
- Live Demo: https://formpilot-api-93135657352.us-central1.run.app

#GeminiLiveAgentChallenge
