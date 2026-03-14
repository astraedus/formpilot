#!/usr/bin/env python3
"""Create title and closing slides for FormPilot v2 demo."""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = "/home/astraedus/projects/formpilot/demo/v2"
W, H = 1920, 1080
BG_COLOR = "#2563eb"
WHITE = "#ffffff"
LIGHT_BLUE = "#93c5fd"


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient_slide(output_path, lines, font_sizes, colors=None, subtitle=None):
    """Create a slide with centered text on blue gradient background."""
    img = Image.new("RGB", (W, H), hex_to_rgb(BG_COLOR))
    draw = ImageDraw.Draw(img)

    # Draw a subtle gradient by drawing rects of slightly different shades
    for y in range(H):
        ratio = y / H
        r = int(37 + (20 * ratio))
        g = int(99 + (30 * ratio))
        b = int(235 - (30 * ratio))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Try to load a nice font, fall back to default
    def get_font(size):
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                return ImageFont.truetype(fp, size)
        return ImageFont.load_default()

    def get_regular_font(size):
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                return ImageFont.truetype(fp, size)
        return ImageFont.load_default()

    # Calculate total height of all text
    text_items = list(zip(lines, font_sizes))
    line_spacing = max(40, int(font_sizes[0] * 0.4)) if font_sizes else 40
    total_height = 0
    rendered = []
    for text, size in text_items:
        font = get_font(size) if size >= 60 else get_regular_font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        rendered.append((text, font, tw, th))
        total_height += th + line_spacing

    total_height -= line_spacing  # remove last spacing

    # Draw a decorative horizontal bar
    bar_y = H // 2 + total_height // 2 + 50
    draw.rectangle([(W//2 - 200, bar_y), (W//2 + 200, bar_y + 4)], fill=hex_to_rgb(LIGHT_BLUE))

    # Start drawing text vertically centered
    current_y = (H - total_height) // 2

    color_list = colors or [WHITE] * len(lines)
    for i, (text, font, tw, th) in enumerate(rendered):
        color = hex_to_rgb(color_list[i]) if isinstance(color_list[i], str) else color_list[i]
        x = (W - tw) // 2
        # Draw subtle shadow
        draw.text((x + 2, current_y + 2), text, font=font, fill=(0, 0, 80))
        draw.text((x, current_y), text, font=font, fill=color)
        current_y += th + line_spacing

    img.save(output_path)
    print(f"Saved: {output_path}")


# Title slide
create_gradient_slide(
    os.path.join(OUTPUT_DIR, "slide_title.png"),
    lines=["FormPilot", "AI-Powered Form Assistant", "Chrome Extension"],
    font_sizes=[120, 56, 44],
    colors=["#ffffff", "#93c5fd", "#bfdbfe"],
)

# Closing slide
create_gradient_slide(
    os.path.join(OUTPUT_DIR, "slide_closing.png"),
    lines=["FormPilot", "github.com/astraedus/formpilot", "Gemini Live Agent Challenge 2026"],
    font_sizes=[120, 44, 36],
    colors=["#ffffff", "#93c5fd", "#bfdbfe"],
)

print("Slides created successfully.")
