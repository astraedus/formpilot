#!/usr/bin/env python3
"""Generate proper mockup screenshots for FormPilot v2 demo video.

Replaces the broken screenshots (YouTube Studio, DevPost login) with
realistic mockups of FormPilot actually working on a form.
"""

from PIL import Image, ImageDraw, ImageFont
import os

DIR = "/home/astraedus/projects/formpilot/demo/v2"
W, H = 1920, 1080

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (245, 245, 245)
MED_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
TEXT_BLACK = (30, 30, 30)
CHROME_BG = (222, 225, 230)
CHROME_TAB = (255, 255, 255)
CHROME_BAR = (241, 243, 244)
URL_TEXT = (60, 60, 60)
BLUE = (59, 130, 246)
BLUE_DARK = (37, 99, 235)
BLUE_LIGHT = (219, 234, 254)
GREEN = (34, 197, 94)
GREEN_LIGHT = (220, 252, 231)
GREEN_DARK = (22, 101, 52)
ORANGE = (245, 158, 11)
ORANGE_LIGHT = (254, 243, 199)
RED = (239, 68, 68)
RED_LIGHT = (254, 226, 226)
PURPLE = (139, 92, 246)
FORM_BG = (249, 250, 251)
FIELD_BORDER = (209, 213, 219)
FIELD_BG = WHITE
TOOLTIP_BG = (30, 58, 138)
TOOLTIP_TEXT = WHITE


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


def draw_browser_chrome(draw, url="https://services.gov.au/visa-application", active_tab="Visa Application"):
    """Draw realistic Chrome browser chrome at top."""
    # Tab bar
    draw.rectangle([(0, 0), (W, 40)], fill=CHROME_BG)
    # Active tab
    draw.rounded_rectangle([(8, 8), (280, 40)], radius=8, fill=CHROME_TAB)
    tab_font = get_font(13, bold=False)
    draw.text((20, 16), active_tab, font=tab_font, fill=TEXT_BLACK)

    # URL bar
    draw.rectangle([(0, 40), (W, 80)], fill=CHROME_TAB)
    draw.rounded_rectangle([(200, 48), (1400, 72)], radius=12, fill=CHROME_BAR)
    url_font = get_font(13, bold=False)
    draw.text((220, 52), url, font=url_font, fill=URL_TEXT)

    # Lock icon (small circle)
    draw.ellipse([(206, 54), (216, 64)], fill=(34, 197, 94))

    # FormPilot extension icon in toolbar (blue circle with F)
    ext_x = 1720
    draw.ellipse([(ext_x, 48), (ext_x + 24, 72)], fill=BLUE)
    ext_font = get_font(14)
    draw.text((ext_x + 7, 51), "F", font=ext_font, fill=WHITE)

    return 85  # y offset where page content starts


def draw_form_field(draw, x, y, label, value="", width=500, filled=False):
    """Draw a form field with label."""
    label_font = get_font(14, bold=False)
    value_font = get_font(14, bold=False)

    draw.text((x, y), label, font=label_font, fill=DARK_GRAY)
    field_y = y + 22
    draw.rounded_rectangle([(x, field_y), (x + width, field_y + 36)], radius=6,
                           fill=FIELD_BG, outline=FIELD_BORDER, width=1)
    if value:
        color = TEXT_BLACK if filled else (180, 180, 180)
        draw.text((x + 10, field_y + 8), value, font=value_font, fill=color)
    return field_y + 44


def draw_tooltip_circle(draw, x, y, number, active=False):
    """Draw a numbered tooltip circle."""
    r = 16
    bg = TOOLTIP_BG if not active else BLUE
    draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=bg)
    num_font = get_font(14)
    bbox = draw.textbbox((0, 0), str(number), font=num_font)
    nw = bbox[2] - bbox[0]
    draw.text((x - nw // 2, y - 8), str(number), font=num_font, fill=WHITE)


def draw_visa_form(draw, top_y, fields_state="empty"):
    """Draw a realistic visa application form.
    fields_state: 'empty', 'placeholder', 'filled'
    """
    # Form header
    header_font = get_font(28)
    sub_font = get_font(16, bold=False)

    # Government header bar
    draw.rectangle([(0, top_y), (W, top_y + 60)], fill=(0, 51, 102))
    draw.text((60, top_y + 14), "Australian Government  |  Department of Home Affairs",
              font=get_font(18), fill=WHITE)
    draw.text((W - 300, top_y + 18), "Visa Application Form", font=get_font(16), fill=(200, 220, 255))

    form_top = top_y + 80
    # Form container
    draw.rounded_rectangle([(100, form_top), (W - 100, H - 30)], radius=12, fill=WHITE, outline=MED_GRAY, width=1)

    draw.text((140, form_top + 20), "Subclass 482 - Temporary Skill Shortage Visa",
              font=header_font, fill=TEXT_BLACK)
    draw.text((140, form_top + 55), "Please complete all required fields marked with *",
              font=sub_font, fill=DARK_GRAY)

    # Section header
    draw.rectangle([(140, form_top + 85), (W - 140, form_top + 115)], fill=BLUE_LIGHT)
    draw.text((155, form_top + 90), "Section 1: Personal Details", font=get_font(16), fill=BLUE_DARK)

    # Form fields - two columns
    col1_x = 160
    col2_x = 960
    field_w = 700

    values_empty = {
        "Given name(s) *": "",
        "Family name *": "",
        "Date of birth * (DD/MM/YYYY)": "",
        "Passport number *": "",
        "Country of passport *": "",
        "Current visa subclass (if any)": "",
    }
    values_placeholder = {
        "Given name(s) *": "e.g. John Michael",
        "Family name *": "e.g. Smith",
        "Date of birth * (DD/MM/YYYY)": "e.g. 15/03/1995",
        "Passport number *": "e.g. PA1234567",
        "Country of passport *": "e.g. United Kingdom",
        "Current visa subclass (if any)": "e.g. 417 (Working Holiday)",
    }
    values_filled = {
        "Given name(s) *": "Diven",
        "Family name *": "Rastdus",
        "Date of birth * (DD/MM/YYYY)": "01/01/2000",
        "Passport number *": "N1234567",
        "Country of passport *": "Australia",
        "Current visa subclass (if any)": "N/A - Citizen",
    }

    if fields_state == "filled":
        vals = values_filled
        filled = True
    elif fields_state == "placeholder":
        vals = values_placeholder
        filled = False
    else:
        vals = values_empty
        filled = False

    field_keys = list(vals.keys())
    y = form_top + 130
    field_positions = []  # Store (x, y) of each field for tooltip placement

    for i, key in enumerate(field_keys):
        col_x = col1_x if i < 3 else col2_x
        fy = y + (i % 3) * 70
        next_y = draw_form_field(draw, col_x, fy, key, vals[key], width=380, filled=filled)
        field_positions.append((col_x + 390, fy + 30))

    # Section 2
    sec2_y = y + 230
    draw.rectangle([(140, sec2_y), (W - 140, sec2_y + 30)], fill=BLUE_LIGHT)
    draw.text((155, sec2_y + 5), "Section 2: Nominated Occupation", font=get_font(16), fill=BLUE_DARK)

    more_fields = [
        ("ANZSCO occupation code *", "e.g. 261313" if fields_state == "placeholder" else ("261313 - Software Engineer" if fields_state == "filled" else ""), 160, sec2_y + 45),
        ("Nominated position title *", "e.g. Senior Software Engineer" if fields_state == "placeholder" else ("Senior Software Engineer" if fields_state == "filled" else ""), 160, sec2_y + 115),
        ("Sponsoring employer TFN *", "e.g. 123 456 789" if fields_state == "placeholder" else ("987 654 321" if fields_state == "filled" else ""), 600, sec2_y + 45),
        ("Employment start date *", "e.g. 01/04/2026" if fields_state == "placeholder" else ("01/04/2026" if fields_state == "filled" else ""), 600, sec2_y + 115),
    ]
    for label, val, fx, fy in more_fields:
        draw_form_field(draw, fx, fy, label, val, width=380, filled=(fields_state == "filled"))
        field_positions.append((fx + 390, fy + 30))

    return field_positions


# ============================================================
# seg_03: Form page with FormPilot icon highlighted in toolbar
# Narration: "Here's how it works. You're on a form page. Click the FormPilot icon in your toolbar."
# ============================================================
def create_seg_03():
    img = Image.new("RGB", (W, H), LIGHT_GRAY)
    draw = ImageDraw.Draw(img)
    top_y = draw_browser_chrome(draw, "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/temporary-skill-shortage-482", "Visa Application - Home Affairs")
    draw_visa_form(draw, top_y, "empty")

    # Highlight the extension icon with a glowing ring + arrow
    ext_x = 1720
    # Glow
    for r in range(20, 0, -2):
        alpha = 100 - r * 4
        c = (59, 130, 246)
        draw.ellipse([(ext_x - r + 12, 60 - r), (ext_x + r + 12, 60 + r)], outline=c, width=2)
    # Arrow pointing to extension
    arrow_font = get_font(16)
    draw.text((ext_x - 120, 82), "Click here!", font=arrow_font, fill=BLUE)
    # Arrow line
    draw.line([(ext_x - 20, 88), (ext_x + 5, 75)], fill=BLUE, width=2)

    img.save(os.path.join(DIR, "prepared_seg_03.png"))
    print("Saved: prepared_seg_03.png")


# ============================================================
# seg_06: Processing screen - "Sending to Gemini Vision..."
# Narration: "It sends this to Gemini Vision, which analyzes the form and returns guidance for each field."
# ============================================================
def create_seg_06():
    img = Image.new("RGB", (W, H), LIGHT_GRAY)
    draw = ImageDraw.Draw(img)
    top_y = draw_browser_chrome(draw, "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/temporary-skill-shortage-482", "Visa Application - Home Affairs")
    draw_visa_form(draw, top_y, "empty")

    # Overlay: semi-transparent processing indicator
    # Draw a centered card overlay
    overlay_w, overlay_h = 500, 200
    ox = (W - overlay_w) // 2
    oy = (H - overlay_h) // 2
    # Shadow
    draw.rounded_rectangle([(ox + 4, oy + 4), (ox + overlay_w + 4, oy + overlay_h + 4)],
                           radius=16, fill=(0, 0, 0, 30))
    draw.rounded_rectangle([(ox, oy), (ox + overlay_w, oy + overlay_h)],
                           radius=16, fill=WHITE, outline=BLUE, width=2)

    # Gemini icon (orange diamond)
    gx, gy = ox + overlay_w // 2, oy + 55
    draw.regular_polygon((gx, gy, 20), 4, rotation=45, fill=ORANGE)
    draw.text((gx - 5, gy - 8), "G", font=get_font(16), fill=WHITE)

    # Text
    proc_font = get_font(22)
    sub_font = get_font(14, bold=False)
    text1 = "Analyzing with Gemini Vision..."
    bbox1 = draw.textbbox((0, 0), text1, font=proc_font)
    draw.text((ox + (overlay_w - (bbox1[2] - bbox1[0])) // 2, oy + 90), text1, font=proc_font, fill=TEXT_BLACK)

    text2 = "Extracting fields, generating suggestions, checking for errors"
    bbox2 = draw.textbbox((0, 0), text2, font=sub_font)
    draw.text((ox + (overlay_w - (bbox2[2] - bbox2[0])) // 2, oy + 125), text2, font=sub_font, fill=DARK_GRAY)

    # Progress bar
    bar_y = oy + 155
    bar_w = 350
    bar_x = ox + (overlay_w - bar_w) // 2
    draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + 8)], radius=4, fill=MED_GRAY)
    draw.rounded_rectangle([(bar_x, bar_y), (bar_x + int(bar_w * 0.65), bar_y + 8)], radius=4, fill=BLUE)

    img.save(os.path.join(DIR, "prepared_seg_06.png"))
    print("Saved: prepared_seg_06.png")


# ============================================================
# seg_07: Numbered tooltip circles on form fields
# Narration: "Numbered circles appear next to each field. Click any circle to see instructions, suggested values, and warnings."
# ============================================================
def create_seg_07():
    img = Image.new("RGB", (W, H), LIGHT_GRAY)
    draw = ImageDraw.Draw(img)
    top_y = draw_browser_chrome(draw, "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/temporary-skill-shortage-482", "Visa Application - Home Affairs")
    field_positions = draw_visa_form(draw, top_y, "placeholder")

    # Draw tooltip circles next to each field
    for i, (fx, fy) in enumerate(field_positions):
        draw_tooltip_circle(draw, fx + 15, fy, i + 1, active=(i == 2))

    # Show expanded tooltip for field 3 (Date of birth)
    if len(field_positions) >= 3:
        tx, ty = field_positions[2]
        # Tooltip card
        tw, th = 320, 140
        ttx = tx + 35
        tty = ty - 50
        draw.rounded_rectangle([(ttx, tty), (ttx + tw, tty + th)], radius=10,
                               fill=TOOLTIP_BG, outline=BLUE, width=2)

        tip_font = get_font(13)
        tip_font_r = get_font(12, bold=False)

        draw.text((ttx + 12, tty + 10), "Field 3: Date of birth", font=tip_font, fill=WHITE)
        draw.line([(ttx + 12, tty + 30), (ttx + tw - 12, tty + 30)], fill=(60, 90, 180), width=1)
        draw.text((ttx + 12, tty + 38), "Format: DD/MM/YYYY", font=tip_font_r, fill=(180, 200, 255))
        draw.text((ttx + 12, tty + 58), "Suggested: 01/01/2000", font=tip_font_r, fill=GREEN_LIGHT)

        # Warning
        draw.text((ttx + 12, tty + 82), "! Must be 18+ at application date", font=tip_font_r, fill=(255, 200, 200))
        draw.text((ttx + 12, tty + 102), "! Must match passport exactly", font=tip_font_r, fill=(255, 200, 200))

    img.save(os.path.join(DIR, "prepared_seg_07.png"))
    print("Saved: prepared_seg_07.png")


# ============================================================
# seg_08: Autofill completed - all fields filled, success banner
# Narration: "When you're ready, click Autofill All. Every field is filled with AI-suggested values in one click."
# ============================================================
def create_seg_08():
    img = Image.new("RGB", (W, H), LIGHT_GRAY)
    draw = ImageDraw.Draw(img)
    top_y = draw_browser_chrome(draw, "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/temporary-skill-shortage-482", "Visa Application - Home Affairs")
    field_positions = draw_visa_form(draw, top_y, "filled")

    # Green checkmarks next to filled fields
    check_font = get_font(18)
    for i, (fx, fy) in enumerate(field_positions):
        draw.ellipse([(fx + 5, fy - 10), (fx + 25, fy + 10)], fill=GREEN)
        draw.text((fx + 9, fy - 8), "V", font=get_font(12), fill=WHITE)

    # Success banner at top of form
    banner_y = top_y + 62
    draw.rounded_rectangle([(120, banner_y), (W - 120, banner_y + 45)], radius=8, fill=GREEN_LIGHT, outline=GREEN, width=2)
    banner_font = get_font(16)
    draw.text((155, banner_y + 12), "All 10 fields filled successfully! Review and submit.",
              font=banner_font, fill=GREEN_DARK)
    # Autofill button
    btn_x = W - 340
    draw.rounded_rectangle([(btn_x, banner_y + 6), (btn_x + 180, banner_y + 38)], radius=8, fill=GREEN)
    draw.text((btn_x + 20, banner_y + 12), "Autofill Complete", font=get_font(13), fill=WHITE)

    img.save(os.path.join(DIR, "prepared_seg_08.png"))
    print("Saved: prepared_seg_08.png")


# ============================================================
# seg_09: "Works on any form" - collage of form types
# Narration: "FormPilot works on any form. Visa applications, tax returns, insurance claims."
# ============================================================
def create_seg_09():
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # Title
    title_font = get_font(36)
    title = "Works on any form"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 40), title, font=title_font, fill=TEXT_BLACK)

    sub_font = get_font(18, bold=False)
    sub = "Powered by Gemini Vision + Chrome Extensions API"
    bbox2 = draw.textbbox((0, 0), sub, font=sub_font)
    sw = bbox2[2] - bbox2[0]
    draw.text(((W - sw) // 2, 85), sub, font=sub_font, fill=DARK_GRAY)

    # 3 form type cards
    cards = [
        ("Visa Applications", "Government forms with\ncomplex requirements", BLUE, BLUE_LIGHT, (59, 130, 246)),
        ("Tax Returns", "Financial documents with\nlegal implications", GREEN, GREEN_LIGHT, (34, 197, 94)),
        ("Insurance Claims", "Medical & property forms\nwith specific terminology", PURPLE, (243, 232, 255), (139, 92, 246)),
    ]

    card_w = 480
    card_h = 350
    gap = 50
    total = len(cards) * card_w + (len(cards) - 1) * gap
    start_x = (W - total) // 2
    card_y = 140

    card_font = get_font(24)
    desc_font = get_font(16, bold=False)

    for i, (title, desc, accent, bg, border) in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        # Card
        draw.rounded_rectangle([(cx, card_y), (cx + card_w, card_y + card_h)],
                               radius=16, fill=bg, outline=border, width=2)
        # Accent bar at top
        draw.rounded_rectangle([(cx, card_y), (cx + card_w, card_y + 60)],
                               radius=16, fill=accent)
        draw.rectangle([(cx, card_y + 40), (cx + card_w, card_y + 60)], fill=accent)

        # Title on accent bar
        bbox = draw.textbbox((0, 0), title, font=card_font)
        cw = bbox[2] - bbox[0]
        draw.text((cx + (card_w - cw) // 2, card_y + 16), title, font=card_font, fill=WHITE)

        # Mini form mockup inside card
        form_y = card_y + 80
        mini_fields = [
            "Full Name",
            "Reference Number",
            "Date",
            "Description",
        ]
        for j, field in enumerate(mini_fields):
            fy = form_y + j * 55
            draw.text((cx + 30, fy), field, font=get_font(12, bold=False), fill=DARK_GRAY)
            draw.rounded_rectangle([(cx + 30, fy + 18), (cx + card_w - 30, fy + 42)],
                                   radius=4, fill=WHITE, outline=FIELD_BORDER, width=1)
            # Filled value
            draw.text((cx + 40, fy + 22), "AI-suggested value", font=get_font(11, bold=False), fill=(150, 150, 150))
            # Tooltip circle
            draw_tooltip_circle(draw, cx + card_w - 18, fy + 30, j + 1)

        # Description
        lines = desc.split("\n")
        for k, line in enumerate(lines):
            draw.text((cx + 30, card_y + card_h - 55 + k * 20), line, font=desc_font, fill=DARK_GRAY)

    # Bottom tagline
    bottom_font = get_font(20)
    bottom = "Built with Gemini 2.5 Flash Vision  |  Chrome Extension MV3  |  Cloud Run"
    bbox = draw.textbbox((0, 0), bottom, font=bottom_font)
    bw = bbox[2] - bbox[0]
    draw.text(((W - bw) // 2, H - 70), bottom, font=bottom_font, fill=BLUE)

    img.save(os.path.join(DIR, "prepared_seg_09.png"))
    print("Saved: prepared_seg_09.png")


# ============================================================
# Also fix seg_02: Replace W3Schools with a proper gov form
# ============================================================
def create_seg_02():
    img = Image.new("RGB", (W, H), LIGHT_GRAY)
    draw = ImageDraw.Draw(img)
    top_y = draw_browser_chrome(draw, "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/temporary-skill-shortage-482", "Visa Application - Home Affairs")
    draw_visa_form(draw, top_y, "empty")

    # Overlay text showing confusion
    # Draw thought bubbles / question marks near fields
    q_font = get_font(28)
    positions = [(580, 340), (580, 410), (980, 340), (980, 410)]
    for px, py in positions:
        draw.text((px, py), "?", font=q_font, fill=RED)

    img.save(os.path.join(DIR, "prepared_seg_02.png"))
    print("Saved: prepared_seg_02.png")


if __name__ == "__main__":
    create_seg_02()
    create_seg_03()
    create_seg_06()
    create_seg_07()
    create_seg_08()
    create_seg_09()
    print("\nAll mockup screenshots generated!")
