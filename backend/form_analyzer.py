import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MOCK_ANALYSIS = [
    {
        "field_name": "Full Name",
        "field_type": "text",
        "suggested_value": "John Doe",
        "instructions": "Enter your full legal name as it appears on government-issued ID.",
        "warning": None,
        "position": {"x": 30, "y": 15},
    },
    {
        "field_name": "Email Address",
        "field_type": "email",
        "suggested_value": "john.doe@example.com",
        "instructions": "Enter a valid email address. This will be used for account notifications.",
        "warning": None,
        "position": {"x": 30, "y": 30},
    },
    {
        "field_name": "Date of Birth",
        "field_type": "date",
        "suggested_value": "1990-01-15",
        "instructions": "Enter your date of birth in MM/DD/YYYY format.",
        "warning": "Ensure accuracy — incorrect DOB may require manual verification later.",
        "position": {"x": 30, "y": 45},
    },
    {
        "field_name": "Phone Number",
        "field_type": "tel",
        "suggested_value": "+1 (555) 123-4567",
        "instructions": "Enter a 10-digit US phone number including area code.",
        "warning": None,
        "position": {"x": 30, "y": 60},
    },
    {
        "field_name": "Address",
        "field_type": "textarea",
        "suggested_value": "123 Main St, Springfield, IL 62701",
        "instructions": "Enter your current mailing address. PO boxes may not be accepted for this form.",
        "warning": "PO boxes may be rejected — use a physical street address.",
        "position": {"x": 30, "y": 75},
    },
]


def _parse_gemini_response(raw_text: str) -> list[dict]:
    """Parse and validate the JSON response from Gemini."""
    try:
        data = json.loads(raw_text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "fields" in data:
            return data["fields"]
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        logger.debug(f"Raw response: {raw_text[:500]}")
        return []


def _normalize_field(field: dict) -> dict:
    """Ensure all required keys exist with sensible defaults."""
    return {
        "field_name": field.get("field_name", "Unknown Field"),
        "field_type": field.get("field_type", "text"),
        "suggested_value": field.get("suggested_value"),
        "instructions": field.get("instructions", "Fill in this field."),
        "warning": field.get("warning"),
        "position": field.get("position"),
    }


async def analyze_form(image_path: str, user_context: str) -> tuple[list[dict], str, bool]:
    """
    Analyze a form image using Gemini Vision.

    Returns:
        (fields, summary, is_mock) tuple.
        is_mock=True when falling back to sample data.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning("No GEMINI_API_KEY set — returning mock analysis")
        summary = (
            "Mock analysis: 5 fields detected in this sample form. "
            "Set GEMINI_API_KEY to enable real Gemini Vision analysis."
        )
        return MOCK_ANALYSIS, summary, True

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        image_bytes = Path(image_path).read_bytes()

        # Determine mime type from extension
        ext = Path(image_path).suffix.lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/png")

        prompt = f"""Analyze this form screenshot. The user's context: {user_context}

For each visible field in the form:
1. Identify the field name/label
2. Determine what type of input it expects (text, email, date, select, checkbox, textarea, etc.)
3. Suggest the correct value based on the user's context
4. Write clear, concise fill instructions
5. Flag any fields that need special attention, have gotchas, or might trip users up

Return ONLY a valid JSON array of objects with these exact keys:
- field_name (string): the label or name of the field
- field_type (string): input type (text, email, date, select, checkbox, textarea, tel, number, etc.)
- suggested_value (string or null): what to fill in based on user context
- instructions (string): step-by-step guidance for this field
- warning (string or null): any gotcha, edge case, or important note (null if none)
- position (object or null): approximate position as {{x: number, y: number}} where values are percentages (0-100) of image width/height

Return only the JSON array, no markdown, no explanation."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        raw = response.text or ""
        fields_raw = _parse_gemini_response(raw)

        if not fields_raw:
            logger.warning("Gemini returned empty/unparseable fields — falling back to mock")
            return MOCK_ANALYSIS, "Could not parse Gemini response. Showing sample data.", True

        fields = [_normalize_field(f) for f in fields_raw]
        summary = f"Gemini analyzed {len(fields)} field(s) in the form."
        return fields, summary, False

    except Exception as e:
        logger.exception(f"Gemini Vision call failed: {e}")
        return (
            MOCK_ANALYSIS,
            f"Gemini analysis failed ({type(e).__name__}). Showing sample data.",
            True,
        )
