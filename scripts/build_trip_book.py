#!/usr/bin/env python3
"""Build the Cliffs to Clouds detailed Kerala trip book PDF."""

from __future__ import annotations

import math
import os
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"
OUTPUT = ROOT / "output" / "pdf" / "Cliffs-to-Clouds-Detailed-Trip-Book.pdf"
WEB_COPY = ASSETS / "Cliffs-to-Clouds-Detailed-Trip-Book.pdf"

W, H = A4
M = 42

INK = HexColor("#061715")
INK_2 = HexColor("#0A211D")
FOREST = HexColor("#0D3B31")
SEA = HexColor("#287A7A")
MINT = HexColor("#9BD9C8")
CORAL = HexColor("#F17E58")
GOLD = HexColor("#F4BA78")
PAPER = HexColor("#EAF0E9")
WARM = HexColor("#F0EEE6")
WHITE = HexColor("#F9FBF8")
MUTED = HexColor("#6E807A")
PALE = HexColor("#C9D8D1")
RED = HexColor("#B84D3A")


def register_fonts() -> None:
    base = Path("/usr/share/fonts/truetype/dejavu")
    fonts = {
        "TripSans": "DejaVuSans.ttf",
        "TripSansBold": "DejaVuSans-Bold.ttf",
        "TripSansOblique": "DejaVuSans.ttf",
        "TripSerif": "DejaVuSerif.ttf",
        "TripSerifBold": "DejaVuSerif-Bold.ttf",
        "TripSerifItalic": "DejaVuSerif.ttf",
    }
    for name, filename in fonts.items():
        pdfmetrics.registerFont(TTFont(name, str(base / filename)))


def clean(text: str) -> str:
    return (
        text.replace("–", "-")
        .replace("—", "-")
        .replace("‑", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )


def wrap_lines(text: str, font: str, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in clean(text).split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if pdfmetrics.stringWidth(candidate, font, size) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    *,
    font: str = "TripSans",
    size: float = 9,
    color=INK,
    leading: float | None = None,
    max_lines: int | None = None,
) -> float:
    leading = leading or size * 1.42
    lines = wrap_lines(text, font, size, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    c.setFont(font, size)
    c.setFillColor(color)
    cursor = y
    for line in lines:
        c.drawString(x, cursor, line)
        cursor -= leading
    return cursor


def draw_image_cover(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> None:
    with Image.open(path) as img:
        iw, ih = img.size
    scale = max(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(str(path), x - (dw - w) / 2, y - (dh - h) / 2, dw, dh, mask="auto")


def rounded_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill, radius: float = 14, stroke=None) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)


def pill(c: canvas.Canvas, text: str, x: float, y: float, fill, color, w: float | None = None) -> float:
    text = clean(text).upper()
    size = 6.8
    auto_w = pdfmetrics.stringWidth(text, "TripSansBold", size) + 18
    width = w or auto_w
    c.setFillColor(fill)
    c.roundRect(x, y, width, 19, 9.5, fill=1, stroke=0)
    c.setFillColor(color)
    c.setFont("TripSansBold", size)
    c.drawCentredString(x + width / 2, y + 6.2, text)
    return width


def label(c: canvas.Canvas, text: str, x: float, y: float, color=CORAL) -> None:
    c.setFillColor(color)
    c.setFont("TripSansBold", 7.2)
    c.drawString(x, y, clean(text).upper())


def page_header(c: canvas.Canvas, page_no: int, section: str, title: str, subtitle: str, accent=CORAL) -> float:
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(accent)
    c.circle(M, H - 46, 4, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("TripSansBold", 7.2)
    c.drawString(M + 12, H - 49, clean(section).upper())
    c.drawRightString(W - M, H - 49, f"PAGE {page_no:02d} / 11")
    c.setFillColor(INK)
    c.setFont("TripSerifBold", 25)
    c.drawString(M, H - 88, clean(title))
    draw_text(c, subtitle, M, H - 108, W - 2 * M, size=8.4, color=MUTED, leading=12)
    c.setStrokeColor(Color(0.02, 0.09, 0.08, 0.14))
    c.line(M, H - 132, W - M, H - 132)
    return H - 154


def footer(c: canvas.Canvas, note: str = "CLiffs to Clouds | 05-09 Sep 2026") -> None:
    c.setFillColor(MUTED)
    c.setFont("TripSans", 6.3)
    c.drawString(M, 24, clean(note).upper())
    c.drawRightString(W - M, 24, "TIRUPATI - SOUTH KERALA - TIRUPATI")


def metric(c: canvas.Canvas, x: float, y: float, w: float, value: str, title: str, color=INK) -> None:
    rounded_panel(c, x, y, w, 58, WHITE)
    c.setFillColor(color)
    c.setFont("TripSerifBold", 18)
    c.drawString(x + 14, y + 29, clean(value))
    c.setFillColor(MUTED)
    c.setFont("TripSansBold", 6.5)
    c.drawString(x + 14, y + 13, clean(title).upper())


def draw_timeline_event(
    c: canvas.Canvas,
    y: float,
    time: str,
    title: str,
    body: str,
    accent=CORAL,
    last=False,
    right_edge: float | None = None,
) -> float:
    x_time = M
    x_dot = M + 74
    x_text = M + 96
    body_w = (right_edge or (W - M)) - x_text
    body_lines = wrap_lines(body, "TripSans", 8.2, body_w)
    h = max(58, 40 + len(body_lines) * 11)

    c.setFillColor(accent)
    c.circle(x_dot, y - 7, 5, fill=1, stroke=0)
    if not last:
        c.setStrokeColor(Color(accent.red, accent.green, accent.blue, 0.28))
        c.setLineWidth(1.5)
        c.line(x_dot, y - 13, x_dot, y - h + 4)

    c.setFillColor(MUTED)
    c.setFont("TripSansBold", 7.8)
    c.drawRightString(x_dot - 16, y - 10, clean(time))

    c.setFillColor(INK)
    c.setFont("TripSansBold", 10.6)
    c.drawString(x_text, y - 10, clean(title))
    draw_text(c, body, x_text, y - 29, body_w, size=8.2, color=MUTED, leading=11)
    return y - h


def info_box(c: canvas.Canvas, x: float, y: float, w: float, title: str, items: list[str], fill=WHITE, accent=SEA) -> float:
    line_sets = [wrap_lines(item, "TripSans", 7.7, w - 34) for item in items]
    h = 40 + sum(max(1, len(lines)) * 10.5 + 8 for lines in line_sets)
    rounded_panel(c, x, y - h, w, h, fill)
    c.setFillColor(accent)
    c.setFont("TripSansBold", 7)
    c.drawString(x + 14, y - 21, clean(title).upper())
    cursor = y - 42
    for lines in line_sets:
        c.setFillColor(accent)
        c.circle(x + 17, cursor + 2.5, 2.1, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("TripSans", 7.7)
        for line in lines:
            c.drawString(x + 27, cursor, line)
            cursor -= 10.5
        cursor -= 8
    return y - h


def draw_cover(c: canvas.Canvas) -> None:
    draw_image_cover(c, ASSETS / "varkala-cliff.webp", 0, 0, W, H)
    c.saveState()
    c.setFillAlpha(0.76)
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.restoreState()
    c.saveState()
    c.setFillAlpha(0.22)
    c.setFillColor(CORAL)
    c.circle(W - 30, H - 40, 180, fill=1, stroke=0)
    c.restoreState()

    label(c, "The complete five-day road book", M, H - 64, GOLD)
    c.setFillColor(WHITE)
    c.setFont("TripSerifBold", 42)
    c.drawString(M, H - 132, "Cliffs")
    c.setFont("TripSerifItalic", 42)
    c.drawString(M + 76, H - 180, "to Clouds")
    c.setFillColor(CORAL)
    c.circle(M + 296, H - 167, 5, fill=1, stroke=0)

    draw_text(
        c,
        "Tirupati to Varkala, Ponmudi, Munroe Island and Palaruvi - planned for seven people in a diesel Innova Crysta with driver.",
        M,
        H - 232,
        374,
        font="TripSans",
        size=11,
        color=PALE,
        leading=16,
    )

    rounded_panel(c, M, 106, W - 2 * M, 146, Color(0.02, 0.09, 0.08, 0.76), stroke=Color(1, 1, 1, 0.13))
    pill(c, "05-09 Sep 2026", M + 18, 210, CORAL, INK)
    pill(c, "7 people", M + 136, 210, GOLD, INK)
    pill(c, "₹40k-₹45k", M + 225, 210, MINT, INK)
    c.setFillColor(WHITE)
    c.setFont("TripSansBold", 10.5)
    c.drawString(M + 18, 181, "THE ROUTE")
    draw_text(c, "Tirupati  >  Varkala  >  Ponmudi  >  Munroe Island  >  Palaruvi  >  Tirupati", M + 18, 158, W - 2 * M - 36, size=8.5, color=PALE)
    c.setFillColor(GOLD)
    c.setFont("TripSansBold", 8)
    c.drawString(M + 18, 128, "TRIP RATING  9.5 / 10")
    c.setFillColor(PALE)
    c.setFont("TripSans", 7.3)
    c.drawRightString(W - M - 18, 128, "Forecast and access checked 03 Sep 2026")

    c.setFillColor(PALE)
    c.setFont("TripSans", 6.4)
    c.drawString(M, 32, "DETAILED TRIP BOOK  |  VERSION 02")
    c.showPage()


def draw_overview(c: canvas.Canvas) -> None:
    y = page_header(
        c,
        2,
        "01 / Trip compass",
        "The entire trip on one page",
        "A Varkala base keeps the plan coherent. Ponmudi supplies the mountains, Munroe supplies the backwaters, and Palaruvi is a weather-led return stop.",
        GOLD,
    )

    gap = 8
    mw = (W - 2 * M - gap * 3) / 4
    metric(c, M, y - 58, mw, "5", "calendar days", CORAL)
    metric(c, M + (mw + gap), y - 58, mw, "~1,900", "road km", SEA)
    metric(c, M + 2 * (mw + gap), y - 58, mw, "4", "booked nights", FOREST)
    metric(c, M + 3 * (mw + gap), y - 58, mw, "₹45k", "hard ceiling", RED)

    y -= 92
    label(c, "Route rhythm", M, y)
    y -= 30
    stops = [
        ("01", "Tirupati", "10 AM departure", CORAL),
        ("02", "Varkala", "coast base", GOLD),
        ("03", "Ponmudi", "hill day", MINT),
        ("04", "Munroe", "sunrise canoe", SEA),
        ("05", "Palaruvi", "conditional stop", FOREST),
    ]
    x0 = M + 8
    usable = W - 2 * M - 16
    step = usable / (len(stops) - 1)
    c.setStrokeColor(Color(0.05, 0.23, 0.19, 0.25))
    c.setLineWidth(2)
    c.line(x0, y, x0 + usable, y)
    for idx, (num, name, note, color) in enumerate(stops):
        x = x0 + idx * step
        c.setFillColor(PAPER)
        c.setStrokeColor(color)
        c.setLineWidth(3)
        c.circle(x, y, 8, fill=1, stroke=1)
        c.setFillColor(color)
        c.circle(x, y, 3, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("TripSansBold", 7.4)
        anchor = "start" if idx == 0 else "end" if idx == len(stops) - 1 else "middle"
        if anchor == "start":
            c.drawString(x, y - 22, name)
            c.setFont("TripSans", 6.2)
            c.setFillColor(MUTED)
            c.drawString(x, y - 34, note)
        elif anchor == "end":
            c.drawRightString(x, y - 22, name)
            c.setFont("TripSans", 6.2)
            c.setFillColor(MUTED)
            c.drawRightString(x, y - 34, note)
        else:
            c.drawCentredString(x, y - 22, name)
            c.setFont("TripSans", 6.2)
            c.setFillColor(MUTED)
            c.drawCentredString(x, y - 34, note)

    y -= 72
    left_w = 294
    right_x = M + left_w + 12
    right_w = W - M - right_x
    info_box(
        c,
        M,
        y,
        left_w,
        "The five-day shape",
        [
            "Sep 5: Overnight southbound drive. No sightseeing pressure.",
            "Sep 6: Recovery day with Papanasam, temple, cliff sunset and cafe.",
            "Sep 7: Ponmudi at opening time, with Kallar only if safe and open.",
            "Sep 8: Sunrise canoe at Munroe, followed by Kappil and quiet beaches.",
            "Sep 9: Sivagiri, optional Palaruvi, then the overnight return.",
        ],
        WHITE,
        CORAL,
    )
    y2 = info_box(
        c,
        right_x,
        y,
        right_w,
        "Three bookings first",
        [
            "Varkala stay for nights Sep 5, 6, 7 and 8, with 4-6 AM arrival confirmed in writing.",
            "Munroe sunrise country canoe for seven travelers, with rain cancellation terms.",
            "Crysta: unlimited km, driver allowance/night charges and driver stay/meals clarified.",
        ],
        WARM,
        SEA,
    )
    info_box(
        c,
        right_x,
        y2 - 10,
        right_w,
        "Critical assumption",
        [
            "If seven travelers are travelling plus the driver, confirm an 8-seat Crysta and use only soft backpacks.",
            "₹45,000 works only when vehicle and driver total is capped at ₹10,000 and the four-night stay remains near ₹7,000.",
        ],
        Color(0.95, 0.83, 0.72),
        RED,
    )
    footer(c)
    c.showPage()


def draw_day_page(
    c: canvas.Canvas,
    page_no: int,
    day_label: str,
    title: str,
    subtitle: str,
    accent,
    events: list[tuple[str, str, str]],
    facts: list[tuple[str, str]],
    strategy: list[str],
    switch_title: str,
    switch_items: list[str],
) -> None:
    y = page_header(c, page_no, day_label, title, subtitle, accent)

    panel_h = 64
    rounded_panel(c, M, y - panel_h, W - 2 * M, panel_h, INK)
    fx = M + 16
    fw = (W - 2 * M - 32) / len(facts)
    for i, (value, name) in enumerate(facts):
        if i:
            c.setStrokeColor(Color(1, 1, 1, 0.13))
            c.line(fx + i * fw, y - panel_h + 12, fx + i * fw, y - 12)
        c.setFillColor(GOLD if i == 0 else MINT)
        c.setFont("TripSerifBold", 13)
        c.drawString(fx + i * fw + (8 if i else 0), y - 27, clean(value))
        c.setFillColor(PALE)
        c.setFont("TripSansBold", 6)
        c.drawString(fx + i * fw + (8 if i else 0), y - 43, clean(name).upper())
    y -= panel_h + 22

    side_w = 176
    side_x = W - M - side_w
    side_y = H - 310

    label(c, "Live schedule", M, y, accent)
    y -= 24
    for i, (time, event_title, body) in enumerate(events):
        y = draw_timeline_event(
            c,
            y,
            time,
            event_title,
            body,
            accent,
            i == len(events) - 1,
            side_x - 14,
        )

    info_box(c, side_x, side_y, side_w, "How to make the day work", strategy, WARM, accent)
    info_box(c, side_x, side_y - 178, side_w, switch_title, switch_items, Color(0.91, 0.95, 0.92), SEA)
    footer(c)
    c.showPage()


def draw_days(c: canvas.Canvas) -> None:
    draw_day_page(
        c,
        3,
        "02 / Day 01 - Sat 05 Sep",
        "The long road south",
        "Tirupati to Varkala | depart around 10:00 AM | overnight transit",
        CORAL,
        [
            ("09:30", "Meet, inspect and load", "Check tyres, spare wheel, FASTag, vehicle papers, AC and seat layout. Keep one rain bag and one snack bag accessible."),
            ("10:00", "Leave Tirupati", "Let the driver choose the fastest live route. Treat the road estimate as 760-810 km because the exact corridor and diversions can change."),
            ("13:00", "Lunch and first stretch", "Use a clean highway stop. Keep it to 40 minutes, hydrate, and avoid a heavy meal before the long night run."),
            ("17:30", "Tea, fuel and status check", "Refuel before the tank is low. Message the Varkala stay with the revised arrival estimate."),
            ("21:30", "Dinner break", "Choose a reliable restaurant on the main corridor. The driver gets a proper meal and at least 30 minutes away from the wheel."),
            ("01:30", "Night safety stop", "Tea, washroom and a short walk. No sightseeing detours and no pressure on the driver to recover lost time."),
            ("03:30-05:30", "Expected Varkala arrival", "Use the pre-agreed early check-in. Unload quietly, lock valuables and sleep immediately."),
        ],
        [("760-810 km", "route range"), ("16-18 h", "with breaks"), ("4 stops", "minimum"), ("₹3.0k", "food + fuel buffer")],
        [
            "Share the booking address and phone number with the driver before departure.",
            "Keep driver calls, tolls and navigation with the front passenger.",
            "Do not count Sep 5 as a sightseeing day.",
        ],
        "If the drive slips",
        [
            "Arrival after 6 AM: sleep until noon and keep only the Sep 6 sunset/cafe block.",
            "Severe weather: stop safely, inform the hotel, and protect driver rest over the itinerary.",
        ],
    )

    draw_day_page(
        c,
        4,
        "03 / Day 02 - Sun 06 Sep",
        "Varkala at recovery speed",
        "Papanasam + Janardhana Swamy Temple + North Cliff sunset and cafe",
        GOLD,
        [
            ("04:00-11:00", "Check in and recover", "The priority is sleep. Blackout curtains, phones on silent and no morning attraction list."),
            ("11:30", "Brunch near the stay", "Choose a Kerala meal or breakfast plate. Confirm temple evening access before leaving the hotel."),
            ("13:00", "Papanasam and South Cliff", "Walk the beach edge and cliff approaches. Avoid deep water, rock edges and closed stairways during rough sea conditions."),
            ("15:00", "Return, dry off and refresh", "Use this buffer for rain, parking, showers and a short rest. Carry temple-appropriate clothing."),
            ("16:30", "Janardhana Swamy Temple", "Visit only during the confirmed evening window. Follow local entry, dress and photography rules."),
            ("17:35", "North Cliff for sunset", "Reach before the best light. Walk slowly, stop at viewpoints and stay behind barriers near eroded edges."),
            ("19:00-21:00", "The cliff cafe evening", "Pick one cafe with a sea view, share starters and set a group spend cap of ₹1,500 before ordering."),
        ],
        [("Slow day", "recovery first"), ("~15 km", "local driving"), ("1 cafe", "planned splurge"), ("₹3.0k", "group target")],
        [
            "Park inland and walk; cliff lanes can be narrow and crowded.",
            "Keep one umbrella per two people and a waterproof phone pouch.",
            "Temple timing is the adjustable part, not the sunset block.",
        ],
        "Rain switch",
        [
            "Heavy afternoon rain: move the temple visit to its confirmed opening and use a covered cafe for the coast experience.",
            "Rough sea: enjoy the cliff viewpoint only. Do not enter the water because others are doing so.",
        ],
    )

    draw_day_page(
        c,
        5,
        "04 / Day 03 - Mon 07 Sep",
        "Morning above the clouds",
        "Varkala to Ponmudi and back | Kallar only when officially open and safe",
        MINT,
        [
            ("05:00", "Leave Varkala", "Carry rain layers, water and a light snack. Expect roughly 75-80 km and 2-2.5 hours each way in wet-road conditions."),
            ("07:15", "Breakfast near Vithura", "Keep the stop short and call or recheck the forest status before committing to the final climb."),
            ("08:00", "Enter at the opening window", "Use the official check-post process. Private vehicle access, tariff and opening are controlled by forest staff that day."),
            ("08:30-12:00", "Ponmudi viewpoints and walks", "Take the hilltop slowly: mist, ridge views, short permitted walks and group photographs. Stay on open paths."),
            ("12:30", "Descend for lunch", "Eat around Vithura or Kallar rather than waiting for a hilltop option. The descent needs low gears and patience."),
            ("14:00", "Optional Kallar or Golden Valley", "Add this only if the access road and riverside zone are officially open and the weather remains calm."),
            ("15:30-18:30", "Return to Varkala", "Leave before the late-afternoon thunderstorm window. Dinner should be close to the stay and the evening stays quiet."),
        ],
        [("150-165 km", "round trip"), ("8 AM", "target entry"), ("22 bends", "hill climb"), ("₹1.8k", "day target")],
        [
            "The Sep 3 forecast favored morning conditions and showed later storm risk.",
            "Entry closes at 4 PM on the official listing; plan to descend much earlier.",
            "Carry cash and accept the gate tariff shown that day.",
        ],
        "If Ponmudi closes",
        [
            "Do not wait at the check-post. Return toward Varkala and make Kappil plus Edava the scenic day.",
            "Keep Munroe on Sep 8. Do not replace Ponmudi with an expensive attraction that breaks the budget.",
        ],
    )

    draw_day_page(
        c,
        6,
        "05 / Day 04 - Tue 08 Sep",
        "Still water, then the sea",
        "Munroe Island sunrise canoe + Kappil + Edava, Odayam or Black Sand Beach",
        SEA,
        [
            ("04:30", "Leave Varkala", "The road distance is about 45-50 km. Carry a dry bag, water and the operator's pinned meeting location."),
            ("05:45", "Meet the canoe operator", "Confirm life jackets and weather before boarding. Pay only the pre-agreed group amount."),
            ("06:00-08:30", "Country canoe through Munroe", "Explore narrow canals, coconut groves, village life and the Ashtamudi-Kallada backwater landscape at the quietest time."),
            ("09:00", "Local breakfast", "Eat near Munroe or Kollam. Keep the meal easy and leave room for weather delays."),
            ("10:15-11:30", "Drive toward Kappil", "Return via the coast when practical. Kappil is roughly 6-7 km north of Varkala and combines lake, bridge and sea views."),
            ("11:30-13:00", "Kappil lake-meets-sea stop", "Use the bridge and shore viewpoints. Skip paid boating unless the whole group agrees and conditions are calm."),
            ("14:00-16:00", "Lunch and hotel reset", "Dry clothes, charge phones and rest before the evening beach loop."),
            ("16:30-18:30", "Quiet coast finale", "Choose Edava, Odayam or Black Sand Beach based on tide, access and crowd level. One good stop is better than three rushed ones."),
        ],
        [("100-120 km", "day loop"), ("6 AM", "canoe start"), ("2.5 h", "water time"), ("₹3.2k", "day target")],
        [
            "Book a simple country canoe, not a premium houseboat package.",
            "Ask whether all seven fit one canoe safely or require two boats.",
            "Use only the operator-provided boarding point, not a guessed map pin.",
        ],
        "Rain switch",
        [
            "Operator cancels: accept the refund and visit Kollam/Ashtamudi viewpoints before returning to Kappil.",
            "Thunder after breakfast: take the hotel rest early, then use the clearest late-afternoon beach window.",
        ],
    )

    draw_day_page(
        c,
        7,
        "06 / Day 05 - Wed 09 Sep",
        "One last cascade, then home",
        "Sivagiri + conditional Palaruvi + return to Tirupati overnight",
        FOREST,
        [
            ("05:45", "Pack and make the car ready", "Every bag should be downstairs before the local visit. Settle hotel bills and check the room once."),
            ("06:15-07:15", "Sivagiri Mutt", "Visit quietly and respectfully. If the opening arrangement differs, use the exterior grounds only and keep the departure clock."),
            ("07:30", "Breakfast and checkout", "Take water and simple snacks for the return. The driver needs a clear rest/meal plan."),
            ("08:15", "Leave Varkala", "Reconfirm Palaruvi before choosing the Aryankavu road. The waterfall is a bonus, not a reason to lose several hours."),
            ("10:15-11:45", "Palaruvi if officially open", "Allow time for entry transport and a short visit. Stay outside restricted water zones and leave immediately if rain intensifies."),
            ("12:00", "Begin the main return", "Have lunch on the chosen corridor, then use structured tea and dinner stops every 3-4 hours."),
            ("02:00-05:00 Thu", "Expected Tirupati arrival", "This is an overnight return, not a Sep 9 evening arrival. Share live location with families and finish without rushing."),
        ],
        [("800+ km", "return leg"), ("Palaruvi", "conditional"), ("3 breaks", "minimum"), ("Thu AM", "home arrival")],
        [
            "Official Palaruvi material lists a morning access window; same-day status controls.",
            "Start the return by noon if the waterfall is included.",
            "Fuel before entering a long night corridor and preserve driver rest.",
        ],
        "Best fallback",
        [
            "Palaruvi closed or stormy: skip it immediately, have an early lunch and gain a safer home-arrival window.",
            "If the group must reach Tirupati on Sep 9, Palaruvi must be removed and Varkala checkout moved much earlier.",
        ],
    )


def draw_budget(c: canvas.Canvas) -> None:
    y = page_header(
        c,
        8,
        "07 / Budget control",
        "The ₹45,000 ceiling plan",
        "The plan is viable, but only when the vehicle deal, four-night stay and simple-food target are protected before departure.",
        CORAL,
    )
    rows = [
        ("Vehicle + driver", "₹10,000", "Hard cap; unlimited km and night allowance included"),
        ("Diesel", "₹13,500", "Approx. 1,900 km at a conservative group-trip mileage"),
        ("Tolls + parking", "₹2,500", "FASTag plus local parking reserve"),
        ("Stay - four nights", "₹7,000", "Two simple rooms / group rooms, parking, early arrival"),
        ("Local food + water", "₹7,000", "Kerala meals and highway basics"),
        ("Cliff cafe", "₹1,500", "One controlled group splurge"),
        ("Munroe canoe", "₹1,500", "Pre-negotiated country-canoe target"),
        ("Entries", "₹700", "Ponmudi, Palaruvi and small parking/entry items"),
        ("Contingency", "₹1,300", "Fuel variance or one small surprise"),
    ]
    rounded_panel(c, M, y - 425, W - 2 * M, 425, WHITE)
    c.setFillColor(INK)
    c.setFont("TripSansBold", 8)
    c.drawString(M + 16, y - 25, "CATEGORY")
    c.drawString(M + 205, y - 25, "TARGET")
    c.drawString(M + 286, y - 25, "CONTROL RULE")
    cursor = y - 48
    for idx, (name, amount, note) in enumerate(rows):
        if idx % 2:
            c.setFillColor(Color(0.92, 0.95, 0.93, 0.72))
            c.rect(M + 8, cursor - 19, W - 2 * M - 16, 41, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("TripSansBold", 8.2)
        c.drawString(M + 16, cursor, clean(name))
        c.setFillColor(CORAL if amount == "₹10,000" else FOREST)
        c.setFont("TripSansBold", 8.4)
        c.drawString(M + 205, cursor, amount)
        draw_text(c, note, M + 286, cursor + 1, W - M - (M + 286) - 12, size=6.8, color=MUTED, leading=9)
        cursor -= 42

    c.setFillColor(INK)
    c.roundRect(M, y - 500, W - 2 * M, 58, 14, fill=1, stroke=0)
    c.setFillColor(PALE)
    c.setFont("TripSansBold", 7)
    c.drawString(M + 18, y - 471, "GROUP TOTAL")
    c.setFillColor(GOLD)
    c.setFont("TripSerifBold", 20)
    c.drawRightString(W - M - 18, y - 480, "₹45,000")
    c.setFillColor(PALE)
    c.setFont("TripSans", 7)
    c.drawString(M + 18, y - 487, "₹6,429 each for seven paying travelers | ₹7,500 each if six travelers split the full bill")

    info_box(
        c,
        M,
        y - 525,
        W - 2 * M,
        "Before paying the vehicle advance",
        [
            "Get written confirmation that ₹10,000 covers unlimited kilometres, driver allowance and night driving. Clarify driver meals and lodging.",
            "If driver stay/meals are extra or the hotel exceeds ₹7,000, cut Palaruvi and cafe extras first - never the fuel or safety buffer.",
            "Refundable security deposits are cash-flow needs, not trip spend, but the group must still have the money available.",
        ],
        WARM,
        RED,
    )
    footer(c)
    c.showPage()


def draw_booking_packing(c: canvas.Canvas) -> None:
    y = page_header(
        c,
        9,
        "08 / Ready room",
        "Bookings, bags and roles",
        "Give every important job an owner. The trip becomes easier when one person is not trying to navigate, pay, call and photograph at the same time.",
        SEA,
    )
    col_gap = 12
    col_w = (W - 2 * M - col_gap) / 2
    left = M
    right = M + col_w + col_gap

    info_box(
        c,
        left,
        y,
        col_w,
        "Book now",
        [
            "Varkala: four nights from Sep 5, checkout Sep 9; 4-6 AM arrival accepted in writing.",
            "Munroe: Sep 8 sunrise slot, total price, boat count, life jackets and cancellation terms.",
            "Crysta: passenger count, seat layout, luggage plan, unlimited km and driver terms.",
        ],
        WHITE,
        CORAL,
    )
    info_box(
        c,
        right,
        y,
        col_w,
        "Verify 24 hours before",
        [
            "Ponmudi official access and weather for Sep 7.",
            "Palaruvi official access for Sep 9.",
            "Munroe operator meeting pin and rain decision.",
            "Hotel parking and exact early-arrival contact.",
        ],
        WARM,
        MINT,
    )

    y2 = y - 210
    label(c, "Pack light - one soft bag each", M, y2, FOREST)
    y2 -= 20
    packs = [
        ("RAIN", ["Light rain jacket", "Umbrella for each pair", "Dry pouch for phones", "Two plastic laundry bags"]),
        ("ROAD", ["Power bank + cable", "ORS and water", "Basic medicines", "Small pillow / eye mask"]),
        ("PLACES", ["Grip footwear", "Temple-ready clothing", "Quick-dry layer", "Small towel"]),
    ]
    card_gap = 9
    card_w = (W - 2 * M - 2 * card_gap) / 3
    for i, (title, items) in enumerate(packs):
        x = M + i * (card_w + card_gap)
        rounded_panel(c, x, y2 - 154, card_w, 154, WHITE)
        c.setFillColor([CORAL, SEA, FOREST][i])
        c.setFont("TripSansBold", 7)
        c.drawString(x + 14, y2 - 22, title)
        cur = y2 - 48
        for item in items:
            c.setFillColor([CORAL, SEA, FOREST][i])
            c.circle(x + 16, cur + 2, 2, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont("TripSans", 7.5)
            c.drawString(x + 25, cur, item)
            cur -= 24

    y3 = y2 - 184
    label(c, "Assign these roles in the group chat", M, y3, CORAL)
    y3 -= 24
    roles = [
        ("Road captain", "Navigation, fuel and hotel ETA"),
        ("Money lead", "Shared expense log and cash"),
        ("Booking lead", "Stay, canoe and access calls"),
        ("Safety lead", "Headcount, weather and medicines"),
    ]
    for idx, (role, desc) in enumerate(roles):
        x = M + (idx % 2) * (col_w + col_gap)
        yy = y3 - (idx // 2) * 55
        rounded_panel(c, x, yy - 42, col_w, 42, Color(0.91, 0.95, 0.92))
        c.setFillColor(INK)
        c.setFont("TripSansBold", 8)
        c.drawString(x + 13, yy - 17, role)
        c.setFillColor(MUTED)
        c.setFont("TripSans", 6.7)
        c.drawString(x + 13, yy - 31, desc)
    footer(c)
    c.showPage()


def draw_weather_safety(c: canvas.Canvas) -> None:
    y = page_header(
        c,
        10,
        "09 / Monsoon playbook",
        "Decide early, never at the edge",
        "This route works in September because every exposed activity has a clear decision point and a no-cost backup.",
        MINT,
    )
    rows = [
        ("Varkala sea", "Red flag, rough surf or closed steps", "Stay on the cliff and viewpoints; no swimming"),
        ("Ponmudi", "Forest closure, dense fog or heavy rain", "Turn back; use Kappil/Edava as the scenic day"),
        ("Kallar", "High water or restricted access", "Skip immediately; lunch and return early"),
        ("Munroe canoe", "Operator cancels for thunder/wind", "Kollam/Ashtamudi land views, then Kappil"),
        ("Palaruvi", "Closed gate, storm or time slip", "Start the Tirupati return without the detour"),
    ]
    rounded_panel(c, M, y - 262, W - 2 * M, 262, WHITE)
    headers = [M + 14, M + 133, M + 322]
    for x, text_value in zip(headers, ["PLACE", "STOP SIGNAL", "SWITCH TO"]):
        c.setFillColor(MUTED)
        c.setFont("TripSansBold", 6.5)
        c.drawString(x, y - 24, text_value)
    cursor = y - 51
    for idx, (place, signal, switch) in enumerate(rows):
        if idx:
            c.setStrokeColor(Color(0.02, 0.09, 0.08, 0.10))
            c.line(M + 12, cursor + 13, W - M - 12, cursor + 13)
        c.setFillColor([CORAL, MINT, SEA, GOLD, FOREST][idx])
        c.setFont("TripSansBold", 8)
        c.drawString(headers[0], cursor, place)
        draw_text(c, signal, headers[1], cursor, 174, size=7.2, color=INK, leading=10)
        draw_text(c, switch, headers[2], cursor, W - M - headers[2] - 12, size=7.2, color=INK, leading=10)
        cursor -= 43

    y2 = y - 290
    col_gap = 12
    col_w = (W - 2 * M - col_gap) / 2
    info_box(
        c,
        M,
        y2,
        col_w,
        "Forecast snapshot - checked Sep 3",
        [
            "Varkala: warm, cloudy and shower-prone across Sep 5-9.",
            "Ponmudi on Sep 7: cooler morning, with storm risk rising later in the day.",
            "Munroe and Palaruvi: morning remains the preferred operating window, but thunder is possible.",
            "Recheck every morning; a forecast is not an opening confirmation.",
        ],
        WARM,
        SEA,
    )
    info_box(
        c,
        M + col_w + col_gap,
        y2,
        col_w,
        "Road and water rules",
        [
            "Seat belts for every occupied seat; no luggage blocking the rear window.",
            "No schedule pressure on the driver. Use proper meal and rest stops.",
            "Low gears on hill descents; no overtaking on blind bends.",
            "Life jackets in the canoe; no sea entry against flags or lifeguard advice.",
        ],
        Color(0.91, 0.95, 0.92),
        RED,
    )
    footer(c)
    c.showPage()


def draw_sources(c: canvas.Canvas) -> None:
    y = page_header(
        c,
        11,
        "10 / Final handoff",
        "Screenshot this page",
        "The trip is ready when the six items below are green. Official links are included for same-day access checks.",
        GOLD,
    )
    checks = [
        "Crysta seat count, unlimited km and driver terms confirmed",
        "Four Varkala nights plus early arrival confirmed",
        "Munroe sunrise canoe booked with meeting pin",
        "Ponmudi status checked on Sep 6 and again Sep 7 morning",
        "Palaruvi status checked before leaving Varkala on Sep 9",
        "Budget owner holds the shared cash and contingency",
    ]
    rounded_panel(c, M, y - 202, W - 2 * M, 202, INK)
    cur = y - 32
    for idx, item in enumerate(checks, 1):
        c.setStrokeColor(Color(1, 1, 1, 0.32))
        c.setLineWidth(1.2)
        c.circle(M + 20, cur + 2, 6, fill=0, stroke=1)
        c.setFillColor(GOLD)
        c.setFont("TripSansBold", 6)
        c.drawCentredString(M + 20, cur, str(idx))
        c.setFillColor(WHITE)
        c.setFont("TripSans", 8.2)
        c.drawString(M + 38, cur, clean(item))
        cur -= 28

    y2 = y - 232
    label(c, "Official reference pages", M, y2, CORAL)
    y2 -= 26
    sources = [
        ("Ponmudi Eco-Tourism Centre", "https://ecotourism.forest.kerala.gov.in/propertydetail/4"),
        ("Palaruvi Eco-Tourism Centre", "https://ecotourism.forest.kerala.gov.in/propertydetail/15"),
        ("Varkala Beach - Kerala Tourism", "https://www.keralatourism.org/destination/varkala-beach/328/"),
        ("Munroe Island - Kerala Tourism", "https://www.keralatourism.org/destination/munroe-island-kollam/250/"),
        ("Kappil Beach and Backwaters", "https://www.keralatourism.org/destination/kappil-beach-backwaters-varkala/427/"),
        ("Sivagiri pilgrimage context", "https://www.keralatourism.org/sreenarayanaguru/sivagiri-pilgrimage/concept"),
    ]
    for title, url in sources:
        rounded_panel(c, M, y2 - 39, W - 2 * M, 39, WHITE)
        c.setFillColor(INK)
        c.setFont("TripSansBold", 7.7)
        c.drawString(M + 13, y2 - 16, clean(title))
        c.setFillColor(SEA)
        c.setFont("TripSans", 5.8)
        c.drawString(M + 13, y2 - 29, url)
        c.linkURL(url, (M, y2 - 39, W - M, y2), relative=0)
        y2 -= 46

    rounded_panel(c, M, 64, W - 2 * M, 76, WARM)
    c.setFillColor(INK)
    c.setFont("TripSerifBold", 14)
    c.drawString(M + 16, 111, "The one-line version")
    draw_text(
        c,
        "Drive south, recover on the cliff, take Ponmudi early, paddle Munroe at sunrise, and let weather - not FOMO - decide Palaruvi.",
        M + 16,
        91,
        W - 2 * M - 32,
        size=8.2,
        color=MUTED,
        leading=11,
    )
    footer(c, "Cliffs to Clouds | operational details checked 03 Sep 2026")
    c.showPage()


def build() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    WEB_COPY.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("Cliffs to Clouds - Detailed Kerala Trip Book")
    c.setAuthor("Cliffs to Clouds")
    c.setSubject("Tirupati to Varkala, Ponmudi, Munroe Island and Palaruvi, 05-09 September 2026")
    draw_cover(c)
    draw_overview(c)
    draw_days(c)
    draw_budget(c)
    draw_booking_packing(c)
    draw_weather_safety(c)
    draw_sources(c)
    c.save()
    WEB_COPY.write_bytes(OUTPUT.read_bytes())
    print(OUTPUT)
    print(WEB_COPY)


if __name__ == "__main__":
    build()
