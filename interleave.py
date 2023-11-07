#!/usr/bin/env python
import sys
import PyPDF2
from reportlab.lib.pagesizes import letter, mm
from reportlab.pdfgen import canvas

spacing = mm * 7.5
shade = 0.45

# Function to create a single page with a gray dot grid
def create_dot_grid_page(output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)

    for x in range(0, int(letter[0]), int(spacing)):
        for y in range(0, int(letter[1]), int(spacing)):
            c.setFillColorRGB(shade, shade, shade)  # Gray color
            c.circle(x + spacing / 2, y + spacing / 2, 0.6, stroke=0, fill=1)

## add text
#    c.setFillColorRGB(0.7, 0.7, 0.7)  # Light gray color
#    text_object = c.beginText(spacing, spacing / 1.5)
#    text_object.textLine("“You should never start your day until it's finished on paper.” — Jim Rohn")
#    c.drawText(text_object)

    c.save()

# Function to create the specified number of pages with dot grids
def interleave_dot_grid_pdf(output_pdf, existing_pdfs=[]):
    temp_pdf = "temp.pdf"
    create_dot_grid_page(temp_pdf)
    dot_paper_page = PyPDF2.PdfReader(open(temp_pdf, 'rb')).pages[0]

    pdf_writer = PyPDF2.PdfWriter()

    for existing_pdf in existing_pdfs:
        with open(existing_pdf, 'rb') as existing_file:
            existing_pdf_reader = PyPDF2.PdfReader(existing_file)

            # Copy pages from the existing PDF
            for page in existing_pdf_reader.pages:
                pdf_writer.add_page(page)
                pdf_writer.add_page(dot_paper_page)

    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)

if __name__ == "__main__":
    existing_pdfs = sys.argv[1:]

    output_pdf = "interleaved.pdf"

    interleave_dot_grid_pdf(output_pdf, existing_pdfs)
