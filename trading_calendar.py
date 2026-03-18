#!/usr/bin/env python
"""Generate a two-page trading calendar PDF on 11x17 portrait paper.

Page 1: Week of March 16 – December 31, 2026
Page 2: January 1 – December 31, 2027

Weeks run Monday–Sunday in rows, with weekend columns narrower than weekdays.
ISO week numbers shown on the left edge.
NYSE non-trading days (holidays + early closures) are shaded and labeled.

Optionally imports events from .ics files passed as extra arguments.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from datetime import date, timedelta
import sys
import os

# 11x17 portrait in points
PAGE_W = 11 * inch
PAGE_H = 17 * inch

MARGIN_X = 0.25 * inch
MARGIN_Y = 0.25 * inch

# Width reserved for ISO week number column
WEEK_NUM_W = 16

# NYSE full-day closures (weekday dates only)
NYSE_HOLIDAYS = {
    # 2026
    date(2026, 1, 1):   "New Year's Day",
    date(2026, 1, 19):  "MLK Day",
    date(2026, 2, 16):  "Presidents' Day",
    date(2026, 4, 3):   "Good Friday",
    date(2026, 5, 25):  "Memorial Day",
    date(2026, 6, 19):  "Juneteenth",
    date(2026, 7, 3):   "Independence Day\n(observed)",
    date(2026, 9, 7):   "Labor Day",
    date(2026, 11, 26): "Thanksgiving",
    date(2026, 12, 25): "Christmas",
    # 2027
    date(2027, 1, 1):   "New Year's Day",
    date(2027, 1, 18):  "MLK Day",
    date(2027, 2, 15):  "Presidents' Day",
    date(2027, 3, 26):  "Good Friday",
    date(2027, 5, 31):  "Memorial Day",
    date(2027, 6, 18):  "Juneteenth\n(observed)",
    date(2027, 7, 5):   "Independence Day\n(observed)",
    date(2027, 9, 6):   "Labor Day",
    date(2027, 11, 25): "Thanksgiving",
    date(2027, 12, 24): "Christmas\n(observed)",
}

# NYSE early closures (1:00 PM ET)
NYSE_EARLY_CLOSE = {
    date(2026, 11, 27): "Early Close\n(1 PM)",
    date(2026, 12, 24): "Early Close\n(1 PM)",
    date(2027, 11, 26): "Early Close\n(1 PM)",
}

DAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Colors
CLR_WEEKEND_BG    = HexColor("#f6f6f6")
CLR_HOLIDAY_BG    = HexColor("#ffd6d6")
CLR_HOLIDAY_TEXT   = HexColor("#aa0000")
CLR_EARLY_BG      = HexColor("#fff3cd")
CLR_EARLY_TEXT     = HexColor("#856404")
CLR_GRID           = HexColor("#999999")
CLR_HEADER_BG      = HexColor("#333333")
CLR_HEADER_TEXT    = HexColor("#ffffff")
CLR_MONTH_TEXT     = HexColor("#336699")
CLR_DATE_TEXT      = HexColor("#000000")
CLR_EVENT_TEXT     = HexColor("#1a237e")
CLR_WEEKNUM        = HexColor("#888888")


def load_ics_events(ics_paths):
    """Load events from .ics files. Returns {date: [summary, ...]}."""
    from icalendar import Calendar
    events = {}
    for path in ics_paths:
        with open(path, "rb") as f:
            cal = Calendar.from_ical(f.read())
        for component in cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get("dtstart")
                summary = str(component.get("summary", ""))
                if dtstart:
                    dt = dtstart.dt
                    if hasattr(dt, "date"):
                        dt = dt.date()
                    events.setdefault(dt, []).append(summary)
    return events


def build_weeks(start: date, end: date):
    """Yield [date, ...7] for each Mon–Sun week overlapping the range."""
    monday = start - timedelta(days=start.weekday())
    while monday <= end:
        week = [monday + timedelta(days=i) for i in range(7)]
        yield week
        monday += timedelta(days=7)


def is_trading_day(d: date) -> bool:
    """Return True if d is a regular NYSE trading day."""
    if d.weekday() >= 5:
        return False
    if d in NYSE_HOLIDAYS:
        return False
    return True


def draw_page(c, start: date, end: date, ics_events: dict):
    weeks = list(build_weeks(start, end))
    num_weeks = len(weeks)

    usable_w = PAGE_W - 2 * MARGIN_X
    usable_h = PAGE_H - 2 * MARGIN_Y

    # Column widths: weekdays full, weekends 1/3
    wd_width = usable_w * 3 / 17
    we_width = wd_width / 3

    def col_width(i):
        return we_width if i >= 5 else wd_width

    def col_x(i):
        return MARGIN_X + sum(col_width(j) for j in range(i))

    # Row heights
    header_h = 18
    row_h = (usable_h - header_h) / num_weeks

    # ── Header row ──
    y_top = PAGE_H - MARGIN_Y

    for i, label in enumerate(DAY_HEADERS):
        x = col_x(i)
        w = col_width(i)
        c.setFillColor(CLR_HEADER_BG)
        c.rect(x, y_top - header_h, w, header_h, stroke=0, fill=1)
        c.setFillColor(CLR_HEADER_TEXT)
        c.setFont("Helvetica-Bold", 9)
        tw = c.stringWidth(label, "Helvetica-Bold", 9)
        c.drawString(x + (w - tw) / 2, y_top - header_h + 5, label)

    # ── Week rows ──
    for week_idx, week in enumerate(weeks):
        y = y_top - header_h - (week_idx + 1) * row_h

        # Month label when Monday starts a new month
        show_month = (week_idx == 0 or week[0].month != weeks[week_idx - 1][0].month)

        for day_idx, d in enumerate(week):
            x = col_x(day_idx)
            w = col_width(day_idx)
            is_weekend = day_idx >= 5
            is_holiday = d in NYSE_HOLIDAYS
            is_early = d in NYSE_EARLY_CLOSE

            # Background
            if is_holiday:
                c.setFillColor(CLR_HOLIDAY_BG)
                c.rect(x, y, w, row_h, stroke=0, fill=1)
            elif is_early:
                c.setFillColor(CLR_EARLY_BG)
                c.rect(x, y, w, row_h, stroke=0, fill=1)
            elif is_weekend:
                c.setFillColor(CLR_WEEKEND_BG)
                c.rect(x, y, w, row_h, stroke=0, fill=1)

            # Border
            c.setStrokeColor(CLR_GRID)
            c.setLineWidth(0.4)
            c.rect(x, y, w, row_h, stroke=1, fill=0)

            # Date number (small, top-right corner to maximize writing space)
            date_str = str(d.day)
            if is_weekend:
                c.setFont("Helvetica", 5)
                c.setFillColor(CLR_GRID)
                tw = c.stringWidth(date_str, "Helvetica", 5)
                c.drawString(x + w - tw - 1, y + row_h - 8, date_str)
            else:
                c.setFont("Helvetica", 7)
                c.setFillColor(CLR_DATE_TEXT)
                tw = c.stringWidth(date_str, "Helvetica", 7)
                c.drawString(x + w - tw - 2, y + row_h - 9, date_str)

            # ISO week number, upper-left of Monday cell
            if day_idx == 0:
                iso_year, iso_week, _ = d.isocalendar()
                wn_label = f"W{iso_week}"
                # Show year if it differs from the Monday's calendar year
                if iso_year != d.year:
                    wn_label = f"W{iso_week} {iso_year}"
                c.setFont("Helvetica", 5)
                c.setFillColor(HexColor("#cccccc"))
                c.drawString(x + 2, y + row_h - 7, wn_label)

            # Holiday label (bottom-aligned)
            if is_holiday:
                c.setFont("Helvetica", 5.5)
                c.setFillColor(CLR_HOLIDAY_TEXT)
                label_lines = NYSE_HOLIDAYS[d].split("\n")
                for li, line in enumerate(reversed(label_lines)):
                    c.drawString(x + 3, y + 2 + li * 7, line)

            # Early close label (bottom-aligned)
            if is_early:
                c.setFont("Helvetica", 5.5)
                c.setFillColor(CLR_EARLY_TEXT)
                label_lines = NYSE_EARLY_CLOSE[d].split("\n")
                for li, line in enumerate(reversed(label_lines)):
                    c.drawString(x + 3, y + 2 + li * 7, line)

            # iCal events
            if d in ics_events and not is_weekend:
                c.setFont("Helvetica", 4.5)
                c.setFillColor(CLR_EVENT_TEXT)
                for ei, ev in enumerate(ics_events[d][:2]):  # max 2 events
                    display = ev[:18] + "…" if len(ev) > 19 else ev
                    ev_y = y + 3 + ei * 6
                    c.drawString(x + 3, ev_y, display)

        # Month label
        if show_month:
            month_label = week[0].strftime("%b %Y")
            c.setFont("Helvetica-Bold", 6.5)
            c.setFillColor(CLR_MONTH_TEXT)
            c.drawString(col_x(0) + 3, y + 2, month_label)

    # ── Legend ──
    legend_y = MARGIN_Y - 14
    c.setFont("Helvetica", 6)

    lx = MARGIN_X
    c.setFillColor(CLR_HOLIDAY_BG)
    c.rect(lx, legend_y, 8, 8, stroke=1, fill=1)
    c.setFillColor(CLR_DATE_TEXT)
    c.drawString(lx + 12, legend_y + 2, "NYSE Holiday")

    lx += 80
    c.setFillColor(CLR_EARLY_BG)
    c.rect(lx, legend_y, 8, 8, stroke=1, fill=1)
    c.setFillColor(CLR_DATE_TEXT)
    c.drawString(lx + 12, legend_y + 2, "Early Close (1 PM)")

    lx += 100
    c.setFillColor(CLR_WEEKEND_BG)
    c.rect(lx, legend_y, 8, 8, stroke=1, fill=1)
    c.setFillColor(CLR_DATE_TEXT)
    c.drawString(lx + 12, legend_y + 2, "Weekend")


def create_trading_calendar(output_pdf: str, ics_paths: list[str] | None = None):
    ics_events = {}
    if ics_paths:
        ics_events = load_ics_events(ics_paths)

    c = canvas.Canvas(output_pdf, pagesize=(PAGE_W, PAGE_H))

    # Page 1: Full week containing March 16 – December 31, 2026
    draw_page(c, date(2026, 3, 16), date(2026, 12, 31), ics_events)
    c.showPage()

    # Page 2: All of 2027 (include full weeks)
    draw_page(c, date(2027, 1, 1), date(2027, 12, 31), ics_events)

    c.save()


if __name__ == "__main__":
    out = "trading_calendar_2026_2027.pdf"
    ics_files = [a for a in sys.argv[1:] if a.endswith(".ics")]
    if ics_files:
        print(f"Loading events from: {', '.join(ics_files)}")
    create_trading_calendar(out, ics_files)
    print(f"Created {out}")
