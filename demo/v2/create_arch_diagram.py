#!/usr/bin/env python3
"""Create a clean architecture diagram for FormPilot demo + DevPost."""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = "/home/astraedus/projects/formpilot/demo/v2"
DOCS_DIR = "/home/astraedus/projects/formpilot/docs"
W, H = 1920, 1080

# Colors
BG = (255, 255, 255)
TITLE_COLOR = (30, 30, 30)
ARROW_COLOR = (120, 120, 120)

# Box colors (fill, border, text)
BOXES = [
    {
        "label": "Chrome Extension",
        "sub": ["Popup UI", "Content Script", "DOM Extraction"],
        "fill": (219, 234, 254),   # blue-100
        "border": (59, 130, 246),  # blue-500
        "text": (30, 64, 175),     # blue-800
    },
    {
        "label": "Cloud Run API",
        "sub": ["FastAPI", "Screenshot + DOM", "Context Processing"],
        "fill": (220, 252, 231),   # green-100
        "border": (34, 197, 94),   # green-500
        "text": (22, 101, 52),     # green-800
    },
    {
        "label": "Gemini Vision",
        "sub": ["gemini-2.5-flash", "Form Analysis", "Structured JSON"],
        "fill": (254, 243, 199),   # amber-100
        "border": (245, 158, 11),  # amber-500
        "text": (146, 64, 14),     # amber-800
    },
    {
        "label": "Response",
        "sub": ["Numbered Tooltips", "Fill Suggestions", "One-Click Autofill"],
        "fill": (243, 232, 255),   # purple-100
        "border": (168, 85, 247),  # purple-500
        "text": (88, 28, 135),     # purple-800
    },
]


def get_font(size, bold=True):
    if bold:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_arrow(draw, x1, y1, x2, y2):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    draw.line([(x1, y1), (x2, y2)], fill=ARROW_COLOR, width=3)
    # Arrowhead
    arrow_len = 12
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    ax1 = x2 - arrow_len * math.cos(angle - 0.4)
    ay1 = y2 - arrow_len * math.sin(angle - 0.4)
    ax2 = x2 - arrow_len * math.cos(angle + 0.4)
    ay2 = y2 - arrow_len * math.sin(angle + 0.4)
    draw.polygon([(x2, y2), (int(ax1), int(ay1)), (int(ax2), int(ay2))], fill=ARROW_COLOR)


def create_diagram():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Title
    title_font = get_font(48)
    title = "FormPilot Architecture"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 50), title, font=title_font, fill=TITLE_COLOR)

    # Subtitle
    sub_font = get_font(24, bold=False)
    subtitle = "Chrome Extension + Cloud Run + Gemini Vision"
    bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
    sw = bbox[2] - bbox[0]
    draw.text(((W - sw) // 2, 110), subtitle, font=sub_font, fill=(100, 100, 100))

    # Box dimensions
    num_boxes = len(BOXES)
    box_w = 340
    box_h = 260
    total_w = num_boxes * box_w + (num_boxes - 1) * 60
    start_x = (W - total_w) // 2
    box_y = (H - box_h) // 2 + 30

    label_font = get_font(26)
    sub_label_font = get_font(18, bold=False)

    box_centers = []

    for i, box in enumerate(BOXES):
        x = start_x + i * (box_w + 60)

        # Rounded rect (approximate with regular rect + corner circles)
        r = 16
        draw.rounded_rectangle(
            [(x, box_y), (x + box_w, box_y + box_h)],
            radius=r,
            fill=box["fill"],
            outline=box["border"],
            width=3,
        )

        # Label centered at top of box
        bbox = draw.textbbox((0, 0), box["label"], font=label_font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        draw.text((x + (box_w - lw) // 2, box_y + 25), box["label"], font=label_font, fill=box["text"])

        # Divider line
        div_y = box_y + 25 + lh + 15
        draw.line([(x + 20, div_y), (x + box_w - 20, div_y)], fill=box["border"], width=1)

        # Sub-labels
        sub_y = div_y + 15
        for sub_text in box["sub"]:
            bbox = draw.textbbox((0, 0), sub_text, font=sub_label_font)
            stw = bbox[2] - bbox[0]
            sth = bbox[3] - bbox[1]
            # Bullet point
            bullet_x = x + 30
            draw.ellipse([(bullet_x, sub_y + sth // 2 - 3), (bullet_x + 6, sub_y + sth // 2 + 3)], fill=box["border"])
            draw.text((bullet_x + 14, sub_y), sub_text, font=sub_label_font, fill=box["text"])
            sub_y += sth + 12

        box_centers.append((x + box_w, box_y + box_h // 2))

    # Draw arrows between boxes
    for i in range(num_boxes - 1):
        x1 = box_centers[i][0] + 4
        y1 = box_centers[i][1]
        x2 = start_x + (i + 1) * (box_w + 60) - 4
        y2 = y1
        draw_arrow(draw, x1, y1, x2, y2)

    # Footer
    footer_font = get_font(18, bold=False)
    footer = "Gemini Live Agent Challenge 2026"
    bbox = draw.textbbox((0, 0), footer, font=footer_font)
    fw = bbox[2] - bbox[0]
    draw.text(((W - fw) // 2, H - 60), footer, font=footer_font, fill=(150, 150, 150))

    # Save to both locations
    demo_path = os.path.join(OUTPUT_DIR, "prepared_arch.png")
    docs_path = os.path.join(DOCS_DIR, "architecture-clean.png")

    img.save(demo_path)
    print(f"Saved: {demo_path}")

    img.save(docs_path)
    print(f"Saved: {docs_path}")


if __name__ == "__main__":
    create_diagram()
