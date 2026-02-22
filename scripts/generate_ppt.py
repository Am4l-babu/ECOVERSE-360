"""
ECOVERSE 360 — Competition Pitch Presentation Generator
NAVA Eco Ideathon — "Eco-preneurship for a Sustainable Future"
Adi Shankara Institute of Engineering and Technology

Generates a 14-slide pitch deck focused on WHAT we're building,
WHY it matters, and HOW we'll scale.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# ── Color Palette ─────────────────────────────────────────────────────
ECO_DARK   = RGBColor(0x08, 0x4C, 0x2E)   # Dark green
ECO_GREEN  = RGBColor(0x16, 0xB3, 0x64)   # Primary green
ECO_LIGHT  = RGBColor(0xD3, 0xF8, 0xDF)   # Light green bg
ECO_BG     = RGBColor(0xED, 0xFC, 0xF2)   # Very light green
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
BLACK      = RGBColor(0x1A, 0x1A, 0x2E)
GRAY       = RGBColor(0x6B, 0x72, 0x80)
LIGHT_GRAY = RGBColor(0xF3, 0xF4, 0xF6)
CARBON     = RGBColor(0x9B, 0x70, 0xF1)   # Purple accent
AMBER      = RGBColor(0xF5, 0x9E, 0x0B)
BLUE       = RGBColor(0x3B, 0x82, 0xF6)
RED_ACCENT = RGBColor(0xEF, 0x44, 0x44)
DARK_BG    = RGBColor(0x0F, 0x17, 0x2A)
SLIDE_BG   = RGBColor(0xFF, 0xFF, 0xFF)
TEAL       = RGBColor(0x14, 0xB8, 0xA6)
ORANGE     = RGBColor(0xF9, 0x73, 0x16)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

W = prs.slide_width
H = prs.slide_height

TOTAL_SLIDES = 14


# ═══════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def add_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_color, border_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def add_rounded_rect(slide, left, top, width, height, fill_color, border_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def add_text_box(slide, left, top, width, height, text, font_size=18,
                 color=BLACK, bold=False, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_multi_text(slide, left, top, width, height, lines, font_size=14,
                   color=BLACK, spacing=Pt(6), line_bold=None):
    """Add multiple paragraphs with optional per-line bold control."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = "Calibri"
        p.space_after = spacing
        if line_bold and i < len(line_bold):
            p.font.bold = line_bold[i]
    return txBox


def add_bullet_frame(slide, left, top, width, height, items, font_size=14,
                     color=BLACK, spacing=Pt(6)):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = "Calibri"
        p.space_after = spacing
    return txBox


def add_slide_number(slide, num):
    add_text_box(slide, Inches(12.2), Inches(7.05), Inches(1), Inches(0.4),
                 f"{num}/{TOTAL_SLIDES}", font_size=10, color=GRAY,
                 alignment=PP_ALIGN.RIGHT)


def add_top_bar(slide, title_text, subtitle_text=None):
    """Green top bar with title and optional subtitle."""
    add_rect(slide, Inches(0), Inches(0), W, Inches(1.0), ECO_DARK)
    add_text_box(slide, Inches(0.6), Inches(0.12), Inches(10), Inches(0.7),
                 title_text, font_size=28, color=WHITE, bold=True)
    if subtitle_text:
        add_text_box(slide, Inches(0.6), Inches(0.55), Inches(10), Inches(0.4),
                     subtitle_text, font_size=13, color=ECO_LIGHT)
    # Accent dot
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(12.4), Inches(0.25),
                                  Inches(0.5), Inches(0.5))
    dot.fill.solid()
    dot.fill.fore_color.rgb = ECO_GREEN
    dot.line.fill.background()


def card(slide, left, top, width, height, title, body_lines, icon_text="",
         title_color=ECO_DARK, accent_color=ECO_GREEN):
    """Card with accent bar, optional icon, title, and bullet body."""
    add_rounded_rect(slide, left, top, width, height, WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, left, top, width, Inches(0.06), accent_color)

    if icon_text:
        c = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                   left + Inches(0.2), top + Inches(0.15),
                                   Inches(0.45), Inches(0.45))
        c.fill.solid()
        c.fill.fore_color.rgb = ECO_BG
        c.line.fill.background()
        add_text_box(slide, left + Inches(0.2), top + Inches(0.15),
                     Inches(0.45), Inches(0.45), icon_text,
                     font_size=16, color=ECO_GREEN, alignment=PP_ALIGN.CENTER)

    title_left = left + (Inches(0.8) if icon_text else Inches(0.25))
    add_text_box(slide, title_left, top + Inches(0.12),
                 width - Inches(0.5), Inches(0.4),
                 title, font_size=15, color=title_color, bold=True)

    body_top = top + Inches(0.55)
    add_bullet_frame(slide, left + Inches(0.25), body_top,
                     width - Inches(0.5), height - Inches(0.65),
                     body_lines, font_size=11, color=GRAY, spacing=Pt(4))


def stat_block(slide, left, top, number, label, accent=ECO_GREEN):
    """Big number + label stat block."""
    add_rounded_rect(slide, left, top, Inches(2.2), Inches(1.6), WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, left, top, Inches(2.2), Inches(0.06), accent)
    add_text_box(slide, left, top + Inches(0.2), Inches(2.2), Inches(0.8),
                 number, font_size=36, color=accent, bold=True,
                 alignment=PP_ALIGN.CENTER)
    add_text_box(slide, left, top + Inches(0.95), Inches(2.2), Inches(0.5),
                 label, font_size=12, color=GRAY, alignment=PP_ALIGN.CENTER)


def phase_block(slide, left, top, phase_num, title, desc, color, status_text):
    """Phase card for implementation roadmap."""
    add_rounded_rect(slide, left, top, Inches(2.8), Inches(3.8), WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, left, top, Inches(2.8), Inches(0.08), color)
    # Phase badge
    badge = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                   left + Inches(1.0), top + Inches(0.25),
                                   Inches(0.7), Inches(0.7))
    badge.fill.solid()
    badge.fill.fore_color.rgb = color
    badge.line.fill.background()
    add_text_box(slide, left + Inches(1.0), top + Inches(0.3),
                 Inches(0.7), Inches(0.6), str(phase_num),
                 font_size=24, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
    # Title
    add_text_box(slide, left + Inches(0.15), top + Inches(1.1),
                 Inches(2.5), Inches(0.5), title,
                 font_size=14, color=BLACK, bold=True, alignment=PP_ALIGN.CENTER)
    # Description
    add_text_box(slide, left + Inches(0.15), top + Inches(1.6),
                 Inches(2.5), Inches(1.5), desc,
                 font_size=11, color=GRAY, alignment=PP_ALIGN.CENTER)
    # Status pill
    status_shape = add_rounded_rect(slide, left + Inches(0.6), top + Inches(3.3),
                                     Inches(1.6), Inches(0.3), color)
    add_text_box(slide, left + Inches(0.6), top + Inches(3.3),
                 Inches(1.6), Inches(0.3), status_text,
                 font_size=10, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 1 — TITLE / COVER
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, DARK_BG)

# Accent bar left edge
add_rect(slide, Inches(0), Inches(0), Inches(0.15), H, ECO_GREEN)

# Decorative circles
s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.5), Inches(-1.5),
                            Inches(6), Inches(6))
s.fill.solid()
s.fill.fore_color.rgb = RGBColor(0x0A, 0x91, 0x50)
s.line.fill.background()

s2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.5), Inches(4.5),
                             Inches(4.5), Inches(4.5))
s2.fill.solid()
s2.fill.fore_color.rgb = RGBColor(0x08, 0x73, 0x42)
s2.line.fill.background()

# Competition badge
add_rounded_rect(slide, Inches(0.8), Inches(0.6), Inches(4.5), Inches(0.5),
                 RGBColor(0x0A, 0x91, 0x50))
add_text_box(slide, Inches(0.8), Inches(0.62), Inches(4.5), Inches(0.45),
             "NAVA ECO IDEATHON 2025", font_size=14,
             color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

# Subtitle
add_text_box(slide, Inches(0.8), Inches(1.3), Inches(6), Inches(0.5),
             "Eco-preneurship for a Sustainable Future",
             font_size=15, color=ECO_GREEN, bold=False)

# Main title
add_text_box(slide, Inches(0.8), Inches(2.2), Inches(9), Inches(1.5),
             "ECOVERSE 360", font_size=64, color=WHITE, bold=True)

# Tagline
add_text_box(slide, Inches(0.8), Inches(3.7), Inches(9), Inches(1.0),
             "The Sustainability Operating System That\n"
             "Transforms Every Space Into an Eco-Intelligent Ecosystem",
             font_size=22, color=RGBColor(0xA0, 0xF0, 0xC4))

# Tech pillars
add_text_box(slide, Inches(0.8), Inches(5.2), Inches(9), Inches(0.6),
             "IoT Sensing  ·  Digital Twin  ·  Machine Learning  ·  Carbon Credits  ·  Gamification",
             font_size=15, color=GRAY)

# Bottom bar
add_rect(slide, Inches(0), Inches(6.5), W, Inches(1.0), RGBColor(0x0A, 0x12, 0x20))
add_text_box(slide, Inches(0.8), Inches(6.7), Inches(5), Inches(0.5),
             "Team Ecoverse  |  Adi Shankara Institute of Engineering & Technology",
             font_size=12, color=GRAY)
add_text_box(slide, Inches(7), Inches(6.7), Inches(6), Inches(0.5),
             "Center for AI-IoT Innovation & IEDC",
             font_size=12, color=ECO_GREEN, alignment=PP_ALIGN.RIGHT)

add_slide_number(slide, 1)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 2 — THE CRISIS (Problem Statement)
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "THE CRISIS", "Why the world needs intelligent sustainability — NOW")

# Big stat callouts across center
stats = [
    ("36.8B", "Tonnes CO\u2082\nemitted/year globally", RED_ACCENT),
    ("40%", "Building energy\nwasted on empty rooms", AMBER),
    ("2B+", "Tonnes of waste\nmismanaged annually", ORANGE),
    ("68%", "People want to help\nbut don't know how", BLUE),
]

for i, (num, label, color) in enumerate(stats):
    x = Inches(0.4) + i * Inches(3.2)
    y = Inches(1.4)
    stat_block(slide, x, y, num, label, accent=color)
    # Widen stat blocks
    # Already using stat_block helper

# Problem description
problems = [
    "Buildings, campuses, and factories generate massive carbon footprints — invisible and untracked",
    "Air and water quality issues go undetected for hours in urban environments",
    "40% of recyclable waste is misclassified — smart bins overflow before collection",
    "AC and exhaust systems dump recoverable thermal energy into the atmosphere",
    "Individual eco-friendly actions (recycling, carpooling, planting) earn zero recognition",
    "No platform connects sensing, prediction, simulation, and rewards in one system",
]

add_text_box(slide, Inches(0.6), Inches(3.4), Inches(12), Inches(0.5),
             "The Problems We're Solving:", font_size=18, color=ECO_DARK, bold=True)

for i, problem in enumerate(problems):
    y = Inches(4.0) + i * Inches(0.52)
    # Red dot indicator
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.6), y + Inches(0.05),
                                  Inches(0.18), Inches(0.18))
    dot.fill.solid()
    dot.fill.fore_color.rgb = RED_ACCENT
    dot.line.fill.background()
    add_text_box(slide, Inches(1.0), y, Inches(11.5), Inches(0.45),
                 problem, font_size=13, color=BLACK)

add_slide_number(slide, 2)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 3 — WHAT WE'RE BUILDING (Solution Overview)
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "WHAT WE'RE BUILDING",
            "A complete sustainability operating system — from sensors to carbon credits")

# Central value proposition
add_rounded_rect(slide, Inches(0.4), Inches(1.3), Inches(12.5), Inches(1.3),
                 ECO_BG, border_color=ECO_GREEN)
add_text_box(slide, Inches(0.7), Inches(1.4), Inches(12), Inches(1.1),
             "Ecoverse 360 connects IoT sensors across air, water, waste, agriculture, and energy "
             "domains — feeding real-time data into a Digital Twin that models your environment "
             "as a living simulation. ML models predict issues before they happen. Every sustainable "
             "action earns carbon credits through gamified engagement.",
             font_size=15, color=ECO_DARK)

# Solution pillars — 5 cards
pillars = [
    ("Monitor", "200+ IoT sensors track\nair, water, waste, soil,\nand energy in real-time",
     ECO_GREEN),
    ("Model", "Digital Twin mirrors your\nenvironment — run what-if\nscenarios instantly",
     BLUE),
    ("Predict", "4 ML models forecast\nwaste overflow, AQI,\nenergy & crop yield",
     CARBON),
    ("Reward", "EcoPoints gamification\nturns daily green habits\ninto carbon credits",
     AMBER),
    ("Scale", "Campuses → Homes →\nGovernment → Factories\nacross 4 rollout phases",
     TEAL),
]

for i, (title, desc, color) in enumerate(pillars):
    x = Inches(0.3) + i * Inches(2.55)
    y = Inches(3.0)

    add_rounded_rect(slide, x, y, Inches(2.4), Inches(2.8), WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, x, y, Inches(2.4), Inches(0.07), color)

    # Circle badge
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.85),
                                     y + Inches(0.25), Inches(0.7), Inches(0.7))
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    add_text_box(slide, x + Inches(0.85), y + Inches(0.3), Inches(0.7), Inches(0.6),
                 str(i + 1), font_size=22, color=WHITE, bold=True,
                 alignment=PP_ALIGN.CENTER)

    add_text_box(slide, x, y + Inches(1.1), Inches(2.4), Inches(0.4),
                 title, font_size=16, color=BLACK, bold=True,
                 alignment=PP_ALIGN.CENTER)
    add_text_box(slide, x + Inches(0.1), y + Inches(1.55), Inches(2.2), Inches(1.1),
                 desc, font_size=11, color=GRAY, alignment=PP_ALIGN.CENTER)

# Flow arrow hint at bottom
add_text_box(slide, Inches(0.4), Inches(6.1), Inches(12.5), Inches(0.5),
             "Sensor Data  →  MQTT Pipeline  →  Digital Twin  →  ML Predictions  →  "
             "Dashboard  →  EcoPoints  →  Carbon Credits",
             font_size=12, color=GRAY, alignment=PP_ALIGN.CENTER)

add_slide_number(slide, 3)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 4 — ARCHITECTURE (How It Works)
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "HOW IT WORKS", "6-layer architecture — from physical sensors to carbon economy")

# 6 architecture layers as horizontal bands
layers = [
    ("LAYER 1 — PHYSICAL / IoT", "Smart Bins · Air Monitors · Water Probes · "
     "Vertical Farm · Energy Tiles · Precision Farm Edge (ESP32-S3)",
     ECO_GREEN, WHITE),
    ("LAYER 2 — DATA INGESTION", "Mosquitto MQTT Broker · Fog Gateway "
     "(validation + emergency control) · Offline Buffer · Cloud Sync",
     RGBColor(0x0D, 0x9A, 0x5B), WHITE),
    ("LAYER 3 — STORAGE", "PostgreSQL 16 (18+ tables, JSONB, triggers) · "
     "Redis 7 (cache, pub/sub) · SQLite (fog buffer)",
     BLUE, WHITE),
    ("LAYER 4 — INTELLIGENCE", "Digital Twin (state + simulator + physics model) · "
     "4 ML Models · Carbon Calculator · Occupancy Optimizer",
     CARBON, WHITE),
    ("LAYER 5 — APPLICATION", "Next.js Dashboard · FastAPI Backend (25+ endpoints) · "
     "WebSocket · JWT Auth · Swagger UI",
     TEAL, WHITE),
    ("LAYER 6 — INCENTIVE ECONOMY", "EcoPoints Engine (17 activities, 9 levels) · "
     "Carbon Credit Aggregation · Leaderboard · Challenges",
     AMBER, WHITE),
]

for i, (title, desc, bg_color, text_color) in enumerate(layers):
    y = Inches(1.2) + i * Inches(0.95)
    # Layer band
    add_rounded_rect(slide, Inches(0.4), y, Inches(12.5), Inches(0.85),
                     bg_color)
    # Layer title
    add_text_box(slide, Inches(0.7), y + Inches(0.05), Inches(4), Inches(0.35),
                 title, font_size=13, color=text_color, bold=True)
    # Layer description
    add_text_box(slide, Inches(0.7), y + Inches(0.4), Inches(12), Inches(0.4),
                 desc, font_size=11, color=RGBColor(0xF0, 0xF0, 0xF0))

# Bottom note
add_text_box(slide, Inches(0.4), Inches(7.0), Inches(12.5), Inches(0.4),
             "Each layer is independently deployable via Docker · "
             "Fog layer ensures offline resilience · "
             "Entire stack runs on-premise or cloud",
             font_size=11, color=GRAY, alignment=PP_ALIGN.CENTER)

add_slide_number(slide, 4)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 5 — IoT SENSING NETWORK
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "IoT SENSING NETWORK",
            "6 custom-built sensor nodes covering 5 environmental domains")

sensors = [
    ("Air Quality", "ESP32", "MQ135 · PMS5003 · DHT22",
     "AQI calculation · CO\u2082 estimation\nPM2.5/PM10 tracking\nThreshold alerts (>150 warning)",
     ECO_GREEN),
    ("Water Quality", "ESP32", "TDS · pH · DS18B20",
     "Total dissolved solids\npH monitoring (6.5–8.5 safe)\nDrinking water grading",
     BLUE),
    ("Smart Waste", "ESP8266", "HC-SR04 · HX711",
     "Ultrasonic fill level (0–100%)\nWeight measurement\nML overflow prediction",
     AMBER),
    ("Vertical Farm", "ESP32", "Soil · BH1750 · pH",
     "Auto-irrigation (moisture <30%)\nLight intensity tracking\nCrop health scoring",
     RGBColor(0x22, 0xC5, 0x5E)),
    ("Energy Tiles", "ESP8266", "Piezo disc",
     "Footstep energy harvesting\nTraffic density classification\nCumulative Wh tracking",
     CARBON),
    ("Precision Farm", "ESP32-S3", "DHT22 · LDR · Soil",
     "3-layer Edge→Fog→Cloud\nPhysics-based Digital Twin\nEmergency auto-control",
     TEAL),
]

for i, (name, mcu, hw_sensors, features, color) in enumerate(sensors):
    col = i % 3
    row = i // 3
    x = Inches(0.3) + col * Inches(4.3)
    y = Inches(1.3) + row * Inches(3.0)

    add_rounded_rect(slide, x, y, Inches(4.1), Inches(2.8), WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, x, y, Inches(4.1), Inches(0.07), color)

    # MCU badge
    badge = add_rounded_rect(slide, x + Inches(3.0), y + Inches(0.15),
                              Inches(0.9), Inches(0.3), color)
    add_text_box(slide, x + Inches(3.0), y + Inches(0.15),
                 Inches(0.9), Inches(0.3), mcu,
                 font_size=9, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    # Name
    add_text_box(slide, x + Inches(0.2), y + Inches(0.15),
                 Inches(2.8), Inches(0.35), name,
                 font_size=15, color=BLACK, bold=True)

    # Sensors used
    add_text_box(slide, x + Inches(0.2), y + Inches(0.5),
                 Inches(3.7), Inches(0.3), f"Sensors: {hw_sensors}",
                 font_size=10, color=color, bold=False)

    # Features
    add_text_box(slide, x + Inches(0.2), y + Inches(0.9),
                 Inches(3.7), Inches(1.7), features,
                 font_size=11, color=GRAY)

add_slide_number(slide, 5)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 6 — DIGITAL TWIN ENGINE
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "DIGITAL TWIN ENGINE",
            "A living digital replica of your environment — simulate before you act")

# Left panel — Campus Digital Twin
add_rounded_rect(slide, Inches(0.4), Inches(1.3), Inches(6.2), Inches(5.7),
                 WHITE, border_color=RGBColor(0xE5, 0xE7, 0xEB))
add_rect(slide, Inches(0.4), Inches(1.3), Inches(6.2), Inches(0.07), BLUE)

add_text_box(slide, Inches(0.7), Inches(1.5), Inches(5.8), Inches(0.4),
             "Campus Digital Twin", font_size=18, color=ECO_DARK, bold=True)

campus_features = [
    "Real-time state aggregation from all IoT sensors",
    "Zone health scoring (AQI 30%, water 20%, waste 25%, noise 15%, energy 10%)",
    "What-if simulation: \"What if we add 50 solar panels?\"",
    "  → Projects daily/yearly CO\u2082 reduction",
    "  → Estimates cost savings and energy generation",
    "  → Generates actionable recommendations",
    "Intervention types: solar panels, carpoolers, trees, bins, farms",
    "Auto-generated alerts for threshold breaches",
    "Carbon reduction projections per intervention",
]

add_bullet_frame(slide, Inches(0.7), Inches(2.0), Inches(5.6), Inches(4.8),
                 campus_features, font_size=12, color=GRAY, spacing=Pt(8))

# Right panel — Plant Digital Twin (Physics-based)
add_rounded_rect(slide, Inches(6.8), Inches(1.3), Inches(6.2), Inches(5.7),
                 WHITE, border_color=RGBColor(0xE5, 0xE7, 0xEB))
add_rect(slide, Inches(6.8), Inches(1.3), Inches(6.2), Inches(0.07), TEAL)

add_text_box(slide, Inches(7.1), Inches(1.5), Inches(5.8), Inches(0.4),
             "Plant Digital Twin (Already Built!)", font_size=18,
             color=ECO_DARK, bold=True)

# "LIVE" badge
live_badge = add_rounded_rect(slide, Inches(11.5), Inches(1.55),
                               Inches(1.2), Inches(0.3), ECO_GREEN)
add_text_box(slide, Inches(11.5), Inches(1.55), Inches(1.2), Inches(0.3),
             "LIVE", font_size=11, color=WHITE, bold=True,
             alignment=PP_ALIGN.CENTER)

plant_features = [
    "Physics-based water balance model:",
    "  \u0394S = P + I - ET - D - R",
    "  (Penman-Monteith evapotranspiration equation)",
    "",
    "Emergency auto-control rules:",
    "  • Auto-irrigation when soil moisture < 30%",
    "  • Fan activation when temperature > 35\u00b0C",
    "  • Critical moisture alert at soil < 20%",
    "",
    "Fog-layer offline resilience:",
    "  • Redis hot buffer for instant access",
    "  • SQLite cold buffer for persistence",
    "  • Background cloud sync when connectivity returns",
    "",
    "N-day future predictions via Twin extrapolation",
]

add_bullet_frame(slide, Inches(7.1), Inches(2.0), Inches(5.6), Inches(4.8),
                 plant_features, font_size=11, color=GRAY, spacing=Pt(5))

add_slide_number(slide, 6)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 7 — AI & ML PREDICTIONS
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "AI-POWERED PREDICTIONS",
            "Machine Learning models that predict problems before they happen")

models = [
    ("Waste Overflow", "Gradient Boosting",
     "Inputs: fill rate, weight, hour, day\nOutput: Hours until bin is full\n"
     "Impact: Optimized collection routes,\nzero overflow incidents",
     AMBER),
    ("Air Quality Forecast", "Random Forest",
     "Inputs: PM2.5, PM10, CO\u2082, temp\nOutput: Next-hour AQI prediction\n"
     "Impact: Early warnings for\nvulnerable populations",
     RED_ACCENT),
    ("Energy Demand", "Gradient Boosting",
     "Inputs: time, occupancy, temperature\nOutput: kWh prediction\n"
     "Impact: Pre-allocate renewable\nsources, reduce grid dependency",
     BLUE),
    ("Crop Yield", "Random Forest",
     "Inputs: moisture, light, pH, NPK\nOutput: Estimated kg yield\n"
     "Impact: Optimize irrigation\nand fertilization timing",
     ECO_GREEN),
]

for i, (name, algo, details, color) in enumerate(models):
    x = Inches(0.3) + i * Inches(3.2)
    y = Inches(1.3)

    add_rounded_rect(slide, x, y, Inches(3.0), Inches(3.5), WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, x, y, Inches(3.0), Inches(0.07), color)

    # Model icon circle
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(1.05),
                                     y + Inches(0.2), Inches(0.9), Inches(0.9))
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    add_text_box(slide, x + Inches(1.05), y + Inches(0.35),
                 Inches(0.9), Inches(0.6), "ML",
                 font_size=16, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    add_text_box(slide, x, y + Inches(1.2), Inches(3.0), Inches(0.4),
                 name, font_size=14, color=BLACK, bold=True,
                 alignment=PP_ALIGN.CENTER)

    # Algorithm badge
    algo_badge = add_rounded_rect(slide, x + Inches(0.5), y + Inches(1.6),
                                   Inches(2.0), Inches(0.28), ECO_BG)
    add_text_box(slide, x + Inches(0.5), y + Inches(1.6),
                 Inches(2.0), Inches(0.28), algo,
                 font_size=9, color=ECO_DARK, bold=True, alignment=PP_ALIGN.CENTER)

    add_text_box(slide, x + Inches(0.2), y + Inches(2.0),
                 Inches(2.6), Inches(1.3), details,
                 font_size=10, color=GRAY)

# Carbon calculator section
add_rounded_rect(slide, Inches(0.3), Inches(5.1), Inches(12.7), Inches(2.0),
                 ECO_BG, border_color=ECO_GREEN)
add_text_box(slide, Inches(0.6), Inches(5.2), Inches(4), Inches(0.4),
             "Carbon Footprint Calculator", font_size=16, color=ECO_DARK, bold=True)
add_text_box(slide, Inches(0.6), Inches(5.65), Inches(12), Inches(1.3),
             "Rule-based engine that converts daily activities into kg CO\u2082 equivalents:\n"
             "Transport (mode × distance × emission factor) + Electricity (kWh × grid factor) + "
             "Food (diet type × daily factor)\n"
             "Generates personalized reduction recommendations based on individual patterns. "
             "Each activity links to measurable carbon savings tracked in the EcoPoints system.",
             font_size=12, color=GRAY)

add_slide_number(slide, 7)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 8 — ECOPOINTS & CARBON CREDITS
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "ECOPOINTS & CARBON CREDITS",
            "Gamified engagement that turns everyday green habits into real carbon value")

# Left — EcoPoints system
add_rounded_rect(slide, Inches(0.4), Inches(1.3), Inches(6.2), Inches(3.0),
                 WHITE, border_color=RGBColor(0xE5, 0xE7, 0xEB))
add_rect(slide, Inches(0.4), Inches(1.3), Inches(6.2), Inches(0.07), AMBER)
add_text_box(slide, Inches(0.7), Inches(1.45), Inches(5.5), Inches(0.4),
             "EcoPoints Gamification Engine", font_size=16, color=ECO_DARK, bold=True)

ecopoints_lines = [
    "17 trackable activities: recycle, carpool, plant_tree, compost, bike_ride...",
    "Each activity = base points + CO\u2082 saved (e.g., plant_tree = 30 pts, 22 kg CO\u2082/yr)",
    "Streak multipliers: 7-day (1.2\u00d7), 30-day (1.5\u00d7), 100-day (2.0\u00d7)",
    "Time-bound community challenges with bonus rewards",
    "Leaderboard with real-time rankings and level badges",
]

add_bullet_frame(slide, Inches(0.7), Inches(1.95), Inches(5.8), Inches(2.2),
                 ecopoints_lines, font_size=12, color=GRAY, spacing=Pt(6))

# Right — Level progression
add_rounded_rect(slide, Inches(6.8), Inches(1.3), Inches(6.2), Inches(3.0),
                 WHITE, border_color=RGBColor(0xE5, 0xE7, 0xEB))
add_rect(slide, Inches(6.8), Inches(1.3), Inches(6.2), Inches(0.07), ECO_GREEN)
add_text_box(slide, Inches(7.1), Inches(1.45), Inches(5.5), Inches(0.4),
             "9-Level Progression System", font_size=16, color=ECO_DARK, bold=True)

levels = [
    "Level 1:  Seedling  ·················  0 points",
    "Level 2:  Sapling  ··················  100 points",
    "Level 3:  Green Warrior  ···········  500 points",
    "Level 4:  Eco Guardian  ············  1,500 points",
    "Level 5:  Nature Keeper  ···········  5,000 points",
    "Level 6:  Sustainability Hero  ····  10,000 points",
    "Level 7:  Climate Champion  ·······  25,000 points",
    "Level 8:  Ecosystem Architect  ···  50,000 points",
    "Level 9:  Planetary Guardian  ····  100,000 points",
]

add_bullet_frame(slide, Inches(7.1), Inches(1.95), Inches(5.8), Inches(2.2),
                 levels, font_size=10, color=GRAY, spacing=Pt(3))

# Bottom — Carbon Credit Economy (blended idea)
add_rounded_rect(slide, Inches(0.4), Inches(4.5), Inches(12.5), Inches(2.5),
                 RGBColor(0xFE, 0xF3, 0xC7), border_color=AMBER)
add_text_box(slide, Inches(0.7), Inches(4.6), Inches(6), Inches(0.4),
             "Carbon Credit Aggregation — The Next Step", font_size=16,
             color=RGBColor(0x92, 0x40, 0x0E), bold=True)

carbon_lines = [
    "Every EcoPoints activity maps to measurable kg CO\u2082 saved",
    "Individual micro-actions are aggregated into verified carbon credits",
    "Credits can be traded on carbon offset marketplaces",
    "Institutions earn revenue from collective sustainability efforts",
    "Bridges the gap between personal habits and institutional ESG goals",
    "Creates a genuine eco-economy where sustainability pays — literally",
]

add_bullet_frame(slide, Inches(0.7), Inches(5.1), Inches(12), Inches(1.8),
                 carbon_lines, font_size=12, color=RGBColor(0x78, 0x35, 0x0F),
                 spacing=Pt(5))

add_slide_number(slide, 8)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 9 — BLENDED INNOVATIONS
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "INNOVATION HIGHLIGHTS",
            "Advanced capabilities that set Ecoverse 360 apart")

innovations = [
    ("Aerial Environmental\nSurveying", [
        "Drone-mounted sensor arrays",
        "Cover large campus/city areas rapidly",
        "Map pollution hotspots from above",
        "On-demand deployment for events/incidents",
        "Complements fixed IoT network coverage",
    ], BLUE),
    ("Thermal Energy\nRecovery", [
        "Capture waste heat from AC & exhaust",
        "Redirect for water pre-heating / warm air",
        "Thermoelectric generators for small power",
        "Monitor thermal waste via IoT sensors",
        "Can reduce HVAC costs by 15-25%",
    ], RED_ACCENT),
    ("Smart Building\nManagement", [
        "Occupancy-aware HVAC/lighting control",
        "PIR + CO\u2082 occupancy estimation",
        "Auto-dim empty zones, pre-cool busy ones",
        "Schedule optimization with weather data",
        "40% energy savings in under-utilized areas",
    ], AMBER),
    ("Micro-Zone\nEnvironmental Sculpting", [
        "AI-directed block/street level interventions",
        "Localized air quality improvement plans",
        "Targeted vegetation & shade placement",
        "Real-time zone health monitoring",
        "Urban heat island mitigation at micro scale",
    ], TEAL),
]

for i, (title, features, color) in enumerate(innovations):
    x = Inches(0.3) + i * Inches(3.2)
    y = Inches(1.3)

    add_rounded_rect(slide, x, y, Inches(3.0), Inches(5.5), WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, x, y, Inches(3.0), Inches(0.07), color)

    # Icon area
    icon_shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(1.05),
                                         y + Inches(0.25), Inches(0.9),
                                         Inches(0.9))
    icon_shape.fill.solid()
    icon_shape.fill.fore_color.rgb = color
    icon_shape.line.fill.background()

    icons = ["D", "T", "B", "M"]
    add_text_box(slide, x + Inches(1.05), y + Inches(0.35),
                 Inches(0.9), Inches(0.7), icons[i],
                 font_size=20, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    add_text_box(slide, x, y + Inches(1.3), Inches(3.0), Inches(0.7),
                 title, font_size=13, color=BLACK, bold=True,
                 alignment=PP_ALIGN.CENTER)

    add_bullet_frame(slide, x + Inches(0.2), y + Inches(2.1),
                     Inches(2.6), Inches(3.2),
                     [f"• {f}" for f in features],
                     font_size=10, color=GRAY, spacing=Pt(6))

add_slide_number(slide, 9)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 10 — PROOF OF CONCEPT (Plant DT)
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "PROOF OF CONCEPT — ALREADY BUILT",
            "A Resource-aware Digital Twin Framework for Precision Micro-farming")

# "LIVE" banner
add_rounded_rect(slide, Inches(5.0), Inches(1.2), Inches(3.5), Inches(0.45),
                 ECO_GREEN)
add_text_box(slide, Inches(5.0), Inches(1.22), Inches(3.5), Inches(0.4),
             "github.com/Am4l-babu/S6-MINI-PROJECT",
             font_size=11, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

# 3-layer architecture visualization
layers_poc = [
    ("EDGE LAYER", "ESP32-S3 with DHT22 (temp/humidity), LDR (light),\n"
     "Capacitive Soil Moisture — publishes every 10 seconds via MQTT",
     ECO_GREEN, Inches(1.8)),
    ("FOG LAYER", "Mosquitto MQTT Broker + Data Validation + Emergency Auto-Control\n"
     "Redis hot buffer + SQLite cold buffer — works offline!\n"
     "Auto-irrigation (soil<30%) · Heat protection (temp>35°C) · Cloud Sync",
     BLUE, Inches(3.4)),
    ("CLOUD LAYER", "FastAPI REST API + SQLite + Digital Twin Engine\n"
     "Physics: Water Balance (ΔS = P+I-ET-D-R) + Penman-Monteith ET\n"
     "Next.js Dashboard with real-time WebSocket + Historical Charts",
     CARBON, Inches(5.2)),
]

for title, desc, color, y_pos in layers_poc:
    add_rounded_rect(slide, Inches(0.4), y_pos, Inches(8.0), Inches(1.4),
                     WHITE, border_color=color)
    add_rect(slide, Inches(0.4), y_pos, Inches(0.12), Inches(1.4), color)

    add_text_box(slide, Inches(0.7), y_pos + Inches(0.08), Inches(3), Inches(0.3),
                 title, font_size=13, color=color, bold=True)
    add_text_box(slide, Inches(0.7), y_pos + Inches(0.4), Inches(7.5), Inches(0.9),
                 desc, font_size=11, color=GRAY)

# Right side — Key numbers
right_x = Inches(8.8)

poc_stats = [
    ("10s", "Sensor Polling\nInterval", ECO_GREEN),
    ("5+", "Docker\nServices", BLUE),
    ("10+", "API\nEndpoints", CARBON),
    ("100%", "Offline\nCapable", TEAL),
]

for i, (num, label, color) in enumerate(poc_stats):
    y = Inches(1.8) + i * Inches(1.35)
    add_rounded_rect(slide, right_x, y, Inches(4.1), Inches(1.15), WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, right_x, y, Inches(4.1), Inches(0.06), color)
    add_text_box(slide, right_x + Inches(0.2), y + Inches(0.15),
                 Inches(1.4), Inches(0.8), num,
                 font_size=28, color=color, bold=True)
    add_text_box(slide, right_x + Inches(1.6), y + Inches(0.2),
                 Inches(2.3), Inches(0.8), label,
                 font_size=11, color=GRAY)

add_slide_number(slide, 10)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 11 — TECH STACK
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "TECHNOLOGY STACK",
            "Built with production-grade tools — ready to scale")

categories = [
    ("Backend", [
        ("Python 3.12", "Async, ML, IoT ecosystem"),
        ("FastAPI", "Fastest Python web framework"),
        ("SQLAlchemy 2.0", "Async ORM, relationships"),
        ("Pydantic v2", "Rust-powered validation"),
    ], BLUE),
    ("ML / AI", [
        ("scikit-learn", "RandomForest, GradientBoosting"),
        ("pandas", "Data manipulation, time-series"),
        ("numpy", "Numerical computing"),
        ("Physics Engine", "Custom water balance models"),
    ], CARBON),
    ("Database", [
        ("PostgreSQL 16", "ACID, JSONB, triggers"),
        ("Redis 7", "Sub-ms cache, pub/sub"),
        ("SQLite", "Fog offline buffer layer"),
        ("Materialized Views", "Pre-computed analytics"),
    ], AMBER),
    ("Frontend", [
        ("Next.js 14", "React SSR + App Router"),
        ("Tailwind CSS 3.4", "Utility-first responsive"),
        ("Recharts", "Data visualization"),
        ("Zustand 5", "Minimal state management"),
    ], ECO_GREEN),
    ("IoT / Edge", [
        ("ESP32 / ESP32-S3", "WiFi+BLE, 12-bit ADC"),
        ("ESP8266", "Low-cost WiFi MCU"),
        ("PlatformIO", "Embedded IDE+libraries"),
        ("MQTT Protocol", "Lightweight IoT pub/sub"),
    ], TEAL),
    ("DevOps", [
        ("Docker Compose", "Multi-service orchestration"),
        ("Mosquitto", "MQTT broker + WebSocket"),
        ("GitHub", "Version control + CI/CD"),
        ("Swagger UI", "Auto API documentation"),
    ], RGBColor(0x64, 0x74, 0x8B)),
]

for i, (cat_name, items, color) in enumerate(categories):
    col = i % 3
    row = i // 3
    x = Inches(0.3) + col * Inches(4.3)
    y = Inches(1.3) + row * Inches(3.0)

    add_rounded_rect(slide, x, y, Inches(4.1), Inches(2.8), WHITE,
                     border_color=RGBColor(0xE5, 0xE7, 0xEB))
    add_rect(slide, x, y, Inches(4.1), Inches(0.07), color)

    add_text_box(slide, x + Inches(0.2), y + Inches(0.15),
                 Inches(3.7), Inches(0.35), cat_name,
                 font_size=15, color=BLACK, bold=True)

    for j, (tech, desc) in enumerate(items):
        ty = y + Inches(0.6) + j * Inches(0.5)
        # Tech name
        add_text_box(slide, x + Inches(0.3), ty, Inches(1.8), Inches(0.3),
                     tech, font_size=11, color=color, bold=True)
        # Description
        add_text_box(slide, x + Inches(2.1), ty, Inches(1.8), Inches(0.3),
                     desc, font_size=10, color=GRAY)

add_slide_number(slide, 11)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 12 — IMPLEMENTATION ROADMAP (4 Phases)
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "IMPLEMENTATION ROADMAP",
            "Scaling from campuses to cities — a 4-phase rollout strategy")

# Phase 1 — Educational
phase_block(slide, Inches(0.3), Inches(1.3), 1,
            "Educational\nInstitutions",
            "Colleges · Schools · Universities\n\n"
            "• Campus IoT sensor network\n"
            "• Student EcoPoints engagement\n"
            "• Digital Twin for campus ops\n"
            "• Precision farming lab\n"
            "• Research API for students",
            ECO_GREEN, "ACTIVE NOW")

# Phase 2 — Residential
phase_block(slide, Inches(3.3), Inches(1.3), 2,
            "Residential\nCommunities",
            "Homes · Apartments · Communities\n\n"
            "• Plug-and-play sensor kits\n"
            "• Household carbon calculator\n"
            "• Rooftop farm integration\n"
            "• Waste heat recovery from AC\n"
            "• Community leaderboards",
            BLUE, "Q3 2026")

# Arrow connectors between phases
for arrow_x in [Inches(3.15), Inches(6.15), Inches(9.15)]:
    arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                                    arrow_x, Inches(3.0),
                                    Inches(0.25), Inches(0.4))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = GRAY
    arrow.line.fill.background()

# Phase 3 — Government
phase_block(slide, Inches(6.3), Inches(1.3), 3,
            "Government &\nPublic Sector",
            "Buildings · Parks · Transit Hubs\n\n"
            "• Building energy monitoring\n"
            "• Smart park irrigation\n"
            "• Energy tiles at transit hubs\n"
            "• Citizen EcoPoints app\n"
            "• ESG compliance reports",
            AMBER, "Q1 2027")

# Phase 4 — Private
phase_block(slide, Inches(9.3), Inches(1.3), 4,
            "Private Sector\n& Enterprise",
            "Offices · Factories · Industry\n\n"
            "• Smart building automation\n"
            "• Factory emissions monitoring\n"
            "• Waste heat-to-energy systems\n"
            "• Multi-facility federation\n"
            "• Carbon credit trading",
            CARBON, "2027+")

# Scaling note at bottom
add_rounded_rect(slide, Inches(0.3), Inches(5.5), Inches(12.7), Inches(1.5),
                 ECO_BG, border_color=ECO_GREEN)
add_text_box(slide, Inches(0.6), Inches(5.65), Inches(6), Inches(0.4),
             "Why This Sequence Works:", font_size=15, color=ECO_DARK, bold=True)
scaling_reasons = [
    "1. Students are most receptive — campuses are ideal controlled environments for piloting",
    "2. Proven campus tech scales naturally to homes with simplified sensor kits",
    "3. Government adoption enabled by proven impact data from Phase 1 & 2",
    "4. Enterprise sector values verified carbon credits and ESG compliance infrastructure",
]
add_bullet_frame(slide, Inches(0.6), Inches(6.05), Inches(12), Inches(0.9),
                 scaling_reasons, font_size=11, color=GRAY, spacing=Pt(3))

add_slide_number(slide, 12)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 13 — IMPACT & METRICS
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SLIDE_BG)
add_top_bar(slide, "IMPACT & METRICS",
            "Measurable sustainability outcomes — not just ideas, but results")

# Top row — big impact numbers
impact_stats = [
    ("35+", "API Endpoints\nAcross 2 Repos", BLUE),
    ("117+", "Files Built\n14,400+ Lines", ECO_GREEN),
    ("6", "IoT Device\nTypes", TEAL),
    ("20+", "Database\nTables", AMBER),
    ("5", "ML Models +\nPhysics Engine", CARBON),
]

for i, (num, label, color) in enumerate(impact_stats):
    x = Inches(0.3) + i * Inches(2.55)
    stat_block(slide, x, Inches(1.3), num, label, color)

# Middle — Environmental impact projections
add_rounded_rect(slide, Inches(0.4), Inches(3.2), Inches(6.2), Inches(3.8),
                 WHITE, border_color=RGBColor(0xE5, 0xE7, 0xEB))
add_rect(slide, Inches(0.4), Inches(3.2), Inches(6.2), Inches(0.07), ECO_GREEN)
add_text_box(slide, Inches(0.7), Inches(3.35), Inches(5.5), Inches(0.4),
             "Projected Environmental Impact (Per Campus/Year)",
             font_size=15, color=ECO_DARK, bold=True)

env_impacts = [
    "30-40% reduction in waste overflow incidents",
    "Early air quality warnings → fewer health incidents",
    "15-25% energy savings from occupancy-aware optimization",
    "20%+ water savings from precision irrigation intelligence",
    "Measurable CO\u2082 reduction per participant via EcoPoints",
    "Tonnes of verified carbon credits from collective actions",
    "Data-driven allocation of sustainability budgets",
    "Student engagement rates 5\u00d7 higher with gamification",
]

add_bullet_frame(slide, Inches(0.7), Inches(3.85), Inches(5.8), Inches(3.0),
                 [f"→ {item}" for item in env_impacts],
                 font_size=11, color=GRAY, spacing=Pt(5))

# Right — What sets us apart
add_rounded_rect(slide, Inches(6.8), Inches(3.2), Inches(6.2), Inches(3.8),
                 WHITE, border_color=RGBColor(0xE5, 0xE7, 0xEB))
add_rect(slide, Inches(6.8), Inches(3.2), Inches(6.2), Inches(0.07), CARBON)
add_text_box(slide, Inches(7.1), Inches(3.35), Inches(5.5), Inches(0.4),
             "What Sets Ecoverse 360 Apart",
             font_size=15, color=ECO_DARK, bold=True)

differentiators = [
    "Not just monitoring — we PREDICT, SIMULATE, and REWARD",
    "Only platform combining IoT + Digital Twin + ML + Gamification",
    "Physics-based Digital Twin (not just data aggregation)",
    "Fog-layer offline resilience — works without internet",
    "Carbon credits from individual habits → institutional value",
    "Proven proof-of-concept already operational (Plant DT)",
    "Open architecture — modular, Docker-ready, API-first",
    "4-phase rollout: campus → home → city → enterprise",
]

add_bullet_frame(slide, Inches(7.1), Inches(3.85), Inches(5.8), Inches(3.0),
                 [f"✦ {item}" for item in differentiators],
                 font_size=11, color=GRAY, spacing=Pt(5))

add_slide_number(slide, 13)


# ═══════════════════════════════════════════════════════════════════════
#  SLIDE 14 — THANK YOU / Q&A
# ═══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, DARK_BG)

# Accent bar
add_rect(slide, Inches(0), Inches(0), Inches(0.15), H, ECO_GREEN)

# Decorative
s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.5), Inches(-1.5),
                            Inches(6), Inches(6))
s.fill.solid()
s.fill.fore_color.rgb = RGBColor(0x0A, 0x91, 0x50)
s.line.fill.background()

s2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.5), Inches(4.5),
                             Inches(4.5), Inches(4.5))
s2.fill.solid()
s2.fill.fore_color.rgb = RGBColor(0x08, 0x73, 0x42)
s2.line.fill.background()

# Thank you text
add_text_box(slide, Inches(0.8), Inches(1.5), Inches(9), Inches(1.5),
             "THANK YOU", font_size=60, color=WHITE, bold=True)

add_text_box(slide, Inches(0.8), Inches(3.2), Inches(9), Inches(0.8),
             "Because Every Space Can Be a\nSustainable Ecosystem",
             font_size=24, color=RGBColor(0xA0, 0xF0, 0xC4))

# Repo links
add_text_box(slide, Inches(0.8), Inches(4.5), Inches(9), Inches(0.6),
             "Main Platform:   github.com/Am4l-babu/ECOVERSE-360",
             font_size=14, color=ECO_GREEN)
add_text_box(slide, Inches(0.8), Inches(5.0), Inches(9), Inches(0.6),
             "Plant Digital Twin:   github.com/Am4l-babu/S6-MINI-PROJECT",
             font_size=14, color=ECO_GREEN)

# Bottom bar
add_rect(slide, Inches(0), Inches(6.5), W, Inches(1.0), RGBColor(0x0A, 0x12, 0x20))
add_text_box(slide, Inches(0.8), Inches(6.7), Inches(5), Inches(0.5),
             "Team Ecoverse  |  NAVA Eco Ideathon 2025",
             font_size=12, color=GRAY)
add_text_box(slide, Inches(7), Inches(6.7), Inches(6), Inches(0.5),
             "Adi Shankara Institute of Engineering & Technology",
             font_size=12, color=ECO_GREEN, alignment=PP_ALIGN.RIGHT)

add_text_box(slide, Inches(0.8), Inches(5.7), Inches(9), Inches(0.5),
             "Questions & Discussion",
             font_size=18, color=GRAY)

add_slide_number(slide, 14)


# ═══════════════════════════════════════════════════════════════════════
#  SAVE
# ═══════════════════════════════════════════════════════════════════════
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "Ecoverse_360_Presentation.pptx")
prs.save(output_path)
print(f"\n{'='*60}")
print(f"  ECOVERSE 360 — Competition Pitch Deck Generated!")
print(f"  Slides: {TOTAL_SLIDES}")
print(f"  Format: 16:9 Widescreen")
print(f"  Theme:  NAVA Eco Ideathon 2025")
print(f"  Output: {output_path}")
print(f"{'='*60}\n")
print("Slide Index:")
print("  1.  Title / Cover (NAVA Eco Ideathon)")
print("  2.  The Crisis — Problem Statement")
print("  3.  What We're Building — Solution Overview")
print("  4.  How It Works — 6-Layer Architecture")
print("  5.  IoT Sensing Network — 6 Device Types")
print("  6.  Digital Twin Engine — Campus + Plant")
print("  7.  AI-Powered Predictions — 4 ML Models")
print("  8.  EcoPoints & Carbon Credits")
print("  9.  Innovation Highlights — Blended Ideas")
print(" 10.  Proof of Concept — Plant DT (LIVE)")
print(" 11.  Technology Stack")
print(" 12.  Implementation Roadmap — 4 Phases")
print(" 13.  Impact & Metrics")
print(" 14.  Thank You & Q&A")
