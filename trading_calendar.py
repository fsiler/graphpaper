#!/usr/bin/env python
"""Generate a trading calendar PDF on 11x17 portrait paper.

Weeks run Monday–Sunday in rows, with weekend columns narrower than weekdays.
NYSE non-trading days (holidays) are shaded and labeled.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from datetime import date, timedelta

# 11x17 portrait in points
PAGE_W = 11 * inch
PAGE_H = 17 * inch

MARGIN_X = 0.5 * inch
MARGIN_Y = 0.5 * inch

# NYSE holidays that fall on weekdays in this date range (Mar 16 – Aug 9, 2026)
NYSE_HOLIDAYS = {
    date(2026, 4, 3):  "Good Friday",
    date(2026, 5, 25): "Memorial Day",
    date(2026, 6, 19): "Juneteenth",
    date(2026, 7, 3):  "Independence Day\n(observed)",
}

DAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Colors
CLR_WEEKEND_BG   = HexColor("#e8e8e8")
CLR_HOLIDAY_BG   = HexColor("#ffd6d6")
CLR_HOLIDAY_TEXT  = HexColor("#aa0000")
CLR_GRID          = HexColor("#999999")
CLR_HEADER_BG     = HexColor("#333333")
CLR_HEADER_TEXT   = HexColor("#ffffff")
CLR_MONTH_TEXT    = HexColor("#336699")
CLR_DATE_TEXT     = HexColor("#000000")


def build_weeks(start: date, end: date):
    """Yield (monday, [date, ...7]) for each Mon–Sun week in range."""
    # Find the Monday on or before start
    monday = start - timedelta(days=start.weekday())
    while monday <= end:
        week = [monday + timedelta(days=i) for i in range(7)]
        yield week
        monday += timedelta(days=7)


def create_trading_calendar(output_pdf: str):
    start = date(2026, 3, 16)
    end = date(2026, 8, 9)  # first full week of August (Aug 3–9)

    weeks = list(build_weeks(start, end))
    num_weeks = len(weeks)

    usable_w = PAGE_W - 2 * MARGIN_X
    usable_h = PAGE_H - 2 * MARGIN_Y

    # Column widths: weekdays full, weekends 1/3
    # 5w + 2(w/3) = usable_w  =>  w = usable_w * 3/17
    wd_width = usable_w * 3 / 17
    we_width = wd_width / 3

    def col_width(i):
        return we_width if i >= 5 else wd_width

    def col_x(i):
        return MARGIN_X + sum(col_width(j) for j in range(i))

    # Row heights: header + data rows
    header_h = 24
    row_h = (usable_h - header_h) / num_weeks

    c = canvas.Canvas(output_pdf, pagesize=(PAGE_W, PAGE_H))

    # ── Header row ──
    y_top = PAGE_H - MARGIN_Y
    for i, label in enumerate(DAY_HEADERS):
        x = col_x(i)
        w = col_width(i)
        c.setFillColor(CLR_HEADER_BG)
        c.rect(x, y_top - header_h, w, header_h, stroke=0, fill=1)
        c.setFillColor(CLR_HEADER_TEXT)
        c.setFont("Helvetica-Bold", 10)
        tw = c.stringWidth(label, "Helvetica-Bold", 10)
        c.drawString(x + (w - tw) / 2, y_top - header_h + 8, label)

    # ── Week rows ──
    for week_idx, week in enumerate(weeks):
        y = y_top - header_h - (week_idx + 1) * row_h

        # Check if this row starts a new month (use the Monday's month)
        show_month = (week_idx == 0 or week[0].month != weeks[week_idx - 1][0].month)

        for day_idx, d in enumerate(week):
            x = col_x(day_idx)
            w = col_width(day_idx)
            is_weekend = day_idx >= 5
            is_holiday = d in NYSE_HOLIDAYS

            # Background
            if is_holiday:
                c.setFillColor(CLR_HOLIDAY_BG)
                c.rect(x, y, w, row_h, stroke=0, fill=1)
            elif is_weekend:
                c.setFillColor(CLR_WEEKEND_BG)
                c.rect(x, y, w, row_h, stroke=0, fill=1)

            # Border
            c.setStrokeColor(CLR_GRID)
            c.setLineWidth(0.5)
            c.rect(x, y, w, row_h, stroke=1, fill=0)

            # Date number
            date_str = str(d.day)
            if is_weekend:
                c.setFont("Helvetica", 7)
                c.setFillColor(CLR_GRID)
                tw = c.stringWidth(date_str, "Helvetica", 7)
                c.drawString(x + (w - tw) / 2, y + row_h - 11, date_str)
            else:
                c.setFont("Helvetica-Bold", 11)
                c.setFillColor(CLR_DATE_TEXT)
                c.drawString(x + 4, y + row_h - 14, date_str)

            # Holiday label
            if is_holiday:
                c.setFont("Helvetica", 6.5)
                c.setFillColor(CLR_HOLIDAY_TEXT)
                label_lines = NYSE_HOLIDAYS[d].split("\n")
                for li, line in enumerate(label_lines):
                    c.drawString(x + 4, y + row_h - 24 - li * 8, line)

        # Month label on left edge of first weekday cell when month changes
        if show_month:
            month_label = week[0].strftime("%B %Y")
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(CLR_MONTH_TEXT)
            c.drawString(col_x(0) + 4, y + 4, month_label)

    # ── Title ──
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(CLR_DATE_TEXT)
    title = "Trading Calendar: March–August 2026"
    tw = c.stringWidth(title, "Helvetica-Bold", 14)
    c.drawString((PAGE_W - tw) / 2, PAGE_H - MARGIN_Y + 10, title)

    # ── Legend ──
    legend_y = MARGIN_Y - 18
    c.setFont("Helvetica", 7)
    c.setFillColor(CLR_HOLIDAY_BG)
    c.rect(MARGIN_X, legend_y, 10, 10, stroke=1, fill=1)
    c.setFillColor(CLR_DATE_TEXT)
    c.drawString(MARGIN_X + 14, legend_y + 2, "NYSE Holiday (market closed)")

    c.setFillColor(CLR_WEEKEND_BG)
    c.rect(MARGIN_X + 170, legend_y, 10, 10, stroke=1, fill=1)
    c.setFillColor(CLR_DATE_TEXT)
    c.drawString(MARGIN_X + 184, legend_y + 2, "Weekend")

    c.save()


if __name__ == "__main__":
    out = "trading_calendar_2026.pdf"
    create_trading_calendar(out)
    print(f"Created {out}")
