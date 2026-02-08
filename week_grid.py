#!/usr/bin/env python
import PyPDF2
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime, timedelta

def get_week_start(date):
    """Get the Sunday of the week containing the given date."""
    # weekday() returns 0 for Monday, 6 for Sunday
    # So we need to adjust: if it's Sunday (6), offset is 0, otherwise offset is weekday + 1
    days_since_sunday = (date.weekday() + 1) % 7
    return date - timedelta(days=days_since_sunday)

def create_8week_grid_page(output_pdf, start_date=None):
    """Create a single page with an 8-week grid."""
    if start_date is None:
        start_date = datetime.now().date()

    # Get the Sunday of the current week
    week_start = get_week_start(start_date)

    # Use landscape orientation for space efficiency
    page_width, page_height = landscape(letter)
    c = canvas.Canvas(output_pdf, pagesize=landscape(letter))

    # Grid settings
    margin = 0.3 * inch
    grid_width = page_width - (2 * margin)
    grid_height = page_height - (2 * margin)

    # 7 columns (days) and 8 rows (weeks)
    col_width = grid_width / 7
    row_height = grid_height / 8

    # Starting positions
    x_start = margin
    y_start = page_height - margin

    # Draw grid and fill with dates
    c.setLineWidth(0.5)

    # Single letter day codes: U M T W R F S (Sunday through Saturday)
    day_codes = ['U', 'M', 'T', 'W', 'R', 'F', 'S']
    c.setFont("Helvetica", 8)

    for week in range(8):
        for day_idx in range(7):
            current_date = week_start + timedelta(weeks=week, days=day_idx)

            x = x_start + (day_idx * col_width)
            y = y_start - ((week + 1) * row_height)

            # Draw cell border
            c.rect(x, y, col_width, row_height)

            # Format: "Feb8 U"
            date_text = f"{current_date.strftime('%b%d')} {day_codes[day_idx]}"
            c.drawString(x + 4, y + row_height - 12, date_text)

    # Add title at the top
    c.setFont("Helvetica-Bold", 12)
    title = f"8-Week Planner: {week_start.strftime('%B %d, %Y')} - {(week_start + timedelta(weeks=7, days=6)).strftime('%B %d, %Y')}"
    title_width = c.stringWidth(title, "Helvetica-Bold", 12)
    c.drawString((page_width - title_width) / 2, page_height - margin / 2, title)

    c.save()

def create_8week_grid_pdf(output_pdf, start_date=None):
    """Create a PDF with an 8-week grid."""
    with open(output_pdf, 'wb') as f:
        pdf_writer = PyPDF2.PdfWriter()
        temp_pdf = "temp_week_grid.pdf"
        create_8week_grid_page(temp_pdf, start_date)
        reader = PyPDF2.PdfReader(temp_pdf)
        pdf_writer.add_page(reader.pages[0])
        pdf_writer.write(f)

if __name__ == "__main__":
    output_pdf = "8week_grid.pdf"

    # By default, starts with the current week
    create_8week_grid_pdf(output_pdf)

    print(f"8-week grid PDF created in {output_pdf}")
    print(f"Starting from Sunday, {get_week_start(datetime.now().date()).strftime('%B %d, %Y')}")
