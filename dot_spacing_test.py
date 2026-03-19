#!/usr/bin/env python
"""Generate a dot-spacing test sheet with progressively larger grid spacings."""

import math
from reportlab.lib.pagesizes import letter, mm
from reportlab.pdfgen import canvas


# ── drawing primitives ──────────────────────────────────────────────────

def draw_dot_rows(c, x_start, x_end, y_top, spacing, num_rows,
                  dot_radius=0.6, shade=0.45, exclude=None):
    """Draw num_rows of dots. Returns y of last drawn row.

    exclude: optional (x_min, y_min, x_max, y_max) rect — dots inside are skipped.
    """
    c.setFillColorRGB(shade, shade, shade)
    cols = []
    x = x_start
    while x <= x_end:
        cols.append(x)
        x += spacing

    y = y_top
    for row in range(num_rows):
        for x in cols:
            if exclude and (exclude[0] <= x <= exclude[2]
                            and exclude[1] <= y <= exclude[3]):
                continue
            c.circle(x, y, dot_radius, stroke=0, fill=1)
        if row < num_rows - 1:
            y -= spacing
    return y


def draw_section_marker(c, y_top, y_bottom, y_mid, x, label,
                        font_size=5.5, color=0.72):
    """Draw a label at the middle row with a vertical bracket spanning the section."""
    grey = color
    c.setStrokeColorRGB(grey, grey, grey)
    c.setFillColorRGB(grey, grey, grey)
    c.setLineWidth(0.4)

    bar_x = x
    tick = 1.2 * mm  # horizontal tick length

    # vertical bar from top row to bottom row
    c.line(bar_x, y_top, bar_x, y_bottom)
    # top tick
    c.line(bar_x, y_top, bar_x - tick, y_top)
    # bottom tick
    c.line(bar_x, y_bottom, bar_x - tick, y_bottom)

    # label centered on middle row, to the right of the bar
    c.setFont("Helvetica", font_size)
    c.drawString(bar_x + 1.5 * mm, y_mid - font_size / 3, label)


# ── layout helpers ──────────────────────────────────────────────────────

def compute_section_height(spacing, rows_per_spacing):
    """Height from first dot row to last dot row in a section."""
    return spacing * (rows_per_spacing - 1)


def compute_layout(spacings, rows_per_spacing, page_h, gap=4 * mm):
    """Compute y positions for each section, centered vertically.

    Returns list of (spacing, y_top) tuples.
    """
    heights = [compute_section_height(sp, rows_per_spacing) for sp in spacings]
    total = sum(heights) + gap * (len(spacings) - 1)

    block_top = page_h / 2 + total / 2

    sections = []
    y = block_top
    for i, (sp, h) in enumerate(zip(spacings, heights)):
        sections.append((sp, y))
        y -= h
        if i < len(spacings) - 1:
            y -= gap

    return sections


# ── page composition ────────────────────────────────────────────────────

def build_spacing_test_page(c, spacings, rows_per_spacing=3,
                            edge_pad=2 * mm):
    """Lay out dot-spacing sections centered vertically, with top/bottom
    sections extended to fill the page edges."""
    page_w, page_h = letter
    x_start = edge_pad + 2 * mm
    x_end = page_w - edge_pad

    # title
    c.setFillColorRGB(0.75, 0.75, 0.75)
    c.setFont("Times-Roman", 20)
    c.drawString(x_start, page_h - 10 * mm, "Ali's Handwriting Exam")

    sections = compute_layout(spacings, rows_per_spacing, page_h)

    for idx, (sp, y_top) in enumerate(sections):
        label = f"{sp / mm:.1f}"

        # extend first section upward to page edge
        if idx == 0:
            extra_above = int(math.floor((page_h - edge_pad - y_top) / sp))
            actual_top = y_top + extra_above * sp
            total_rows = rows_per_spacing + extra_above
        # extend last section downward to page edge
        elif idx == len(sections) - 1:
            actual_top = y_top
            section_bottom = y_top - (rows_per_spacing - 1) * sp
            extra_below = int(math.floor((section_bottom - edge_pad) / sp))
            total_rows = rows_per_spacing + extra_below
        else:
            actual_top = y_top
            total_rows = rows_per_spacing

        # bracket + label on the core rows, right side
        core_top = y_top
        core_bottom = y_top - (rows_per_spacing - 1) * sp
        core_mid = y_top - ((rows_per_spacing - 1) / 2) * sp
        marker_x = x_end - 7 * mm

        # exclusion zone: clear the right margin for the full page height
        exclude = (marker_x - 1.5 * mm - 1.5 * mm,
                   0,
                   page_w,
                   page_h)

        draw_dot_rows(c, x_start, x_end, actual_top, sp, total_rows,
                      exclude=exclude)

        draw_section_marker(c, core_top, core_bottom, core_mid,
                            marker_x, label)


def create_spacing_test_pdf(output_pdf,
                            start_mm=3.0, end_mm=10.0, step_mm=0.5,
                            rows_per_spacing=3, num_pages=2):
    """Create a multi-page PDF with dot rows at each spacing."""
    spacings = []
    s = start_mm
    while s <= end_mm + 0.001:
        spacings.append(s * mm)
        s += step_mm

    c = canvas.Canvas(output_pdf, pagesize=letter)
    for page in range(num_pages):
        build_spacing_test_page(c, spacings, rows_per_spacing=rows_per_spacing)
        c.showPage()
    c.save()


# ── CLI ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out = "dot_spacing_test.pdf"
    create_spacing_test_pdf(out)
    print(f"Spacing test sheet created → {out}")
