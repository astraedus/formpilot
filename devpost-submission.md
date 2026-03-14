# DevPost Submission — FormPilot

## Project Name
FormPilot — AI Form Assistant

## Category
Best UI Navigator

## Tagline
Chrome extension that guides you through any form with AI-powered tooltips and one-click autofill

## Description

### Inspiration
Everyone fills out complex forms -- government applications, insurance claims, tax documents, HR onboarding. Small business owners spend 45+ minutes per form: reading fine print, googling terms, calling helplines. One wrong field can delay processing by weeks. We wanted to build an AI that meets users where they already are -- right on the form page -- and tells them exactly what to enter.

### What it does
Install the FormPilot Chrome extension, navigate to any form, click the icon, and describe your situation in plain English. FormPilot:

- **Analyzes the live page** -- captures a screenshot and extracts DOM structure of the form you're looking at
- **Generates field-by-field guidance** -- numbered tooltip circles appear directly on each form field
- **Suggests specific values** based on your context ("sole trader, earned $75K, single")
- **Warns about common mistakes** -- required fields, format requirements, legal implications
- **One-click autofill** -- fills every field with the AI-suggested values instantly
- **Works on any form** -- government, insurance, tax, HR, medical, any web form

### How we built it
**Chrome Extension (MV3)**: TypeScript popup UI for entering context. Content script captures a screenshot of the active tab and extracts the DOM structure of all form fields (inputs, selects, textareas, checkboxes, radio buttons). After receiving guidance from the API, the content script renders numbered tooltip circles on each field using Shadow DOM (isolated from the page's styles) and handles one-click autofill by programmatically setting field values and dispatching input events.

**Backend**: Python FastAPI on Google Cloud Run. Receives the screenshot + DOM structure + user context. Sends them to Gemini Vision (`gemini-2.5-flash`) with structured output prompting. Gemini returns JSON with field names, types, suggested values, instructions, warnings, and CSS selectors for targeting.

**Architecture**: Chrome Extension (popup + content script) -> Cloud Run API (FastAPI) -> Gemini 2.5 Flash Vision (structured JSON) -> Extension renders tooltips + autofill on the live page.

### Challenges we ran into
- Isolating tooltip UI from page styles using Shadow DOM so tooltips render consistently across all websites
- Matching Gemini's field analysis back to actual DOM elements for accurate autofill targeting
- Handling diverse form layouts (government forms, multi-step wizards, dynamic forms with conditional fields)

### Accomplishments that we're proud of
- The extension meets users where they already are -- no uploading screenshots, no switching tabs. Click the icon and get guidance right on the form
- Shadow DOM isolation means tooltips look perfect regardless of the page's CSS
- One-click autofill actually works -- it dispatches proper input events so React/Angular/Vue forms recognize the changes

### What we learned
- Gemini Vision's form understanding is remarkably good -- it can identify fields even in complex multi-column government forms from a single screenshot
- Shadow DOM is essential for Chrome extensions that inject UI -- without it, page styles bleed into your components
- Combining screenshot analysis (visual layout) with DOM extraction (semantic structure) gives much better results than either alone

### What's next for FormPilot
- Multi-page form support with cross-page field validation and progress tracking
- Voice input for describing your situation hands-free
- Chrome Web Store publication for public availability
- Form template library for common government forms with pre-filled guidance

## Built With
- Google Gemini 2.5 Flash Vision API (gemini-2.5-flash)
- Google GenAI SDK
- Chrome Extensions API (Manifest V3)
- TypeScript
- Shadow DOM
- FastAPI + Uvicorn
- Google Cloud Run
- Google Cloud Build
- Google Secret Manager
- Python 3.12

## Try it out
- GitHub: https://github.com/astraedus/formpilot (install instructions in README)
- Cloud Run API: https://formpilot-api-93135657352.us-central1.run.app

#GeminiLiveAgentChallenge
