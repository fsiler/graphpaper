#!/usr/bin/env python
import sys
import PyPDF2
from reportlab.lib.pagesizes import letter, mm
from reportlab.pdfgen import canvas

spacing = mm * 7.5

# Function to create a single page with a gray dot grid
def create_dot_grid_page(output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)

    # Draw gray dots at 1/2" (0.5 inch) intervals
    for x in range(0, int(letter[0]), int(spacing)):
        for y in range(0, int(letter[1]), int(spacing)):
            c.setFillColorRGB(0.4, 0.4, 0.4)  # Gray color
            c.circle(x + spacing / 2, y + spacing / 2, 0.7, stroke=0, fill=1)

    c.setFillColorRGB(0.7, 0.7, 0.7)  # Light gray color
    text_object = c.beginText(spacing, spacing / 1.5)
#    text_object.textLine("“You should never start your day until it's finished on paper.” — Jim Rohn")
    c.drawText(text_object)

    c.save()

# Function to create the specified number of pages with dot grids
def create_dot_grid_pdf(output_pdf, num_pages, existing_pdf=None):
    if existing_pdf:
        with open(existing_pdf, 'rb') as existing_file:
            existing_pdf_reader = PyPDF2.PdfReader(existing_file)
            pdf_writer = PyPDF2.PdfWriter()

            # Copy pages from the existing PDF
            for page in existing_pdf_reader.pages:
                pdf_writer.add_page(page)

            # Add a page of dot paper
            temp_pdf = "temp.pdf"
            create_dot_grid_page(temp_pdf)
            dot_paper_page = PyPDF2.PdfReader(open(temp_pdf, 'rb')).pages[0]
            pdf_writer.add_page(dot_paper_page)

            # Save the new PDF with the added page
            with open(output_pdf, 'wb') as f:
                pdf_writer.write(f)
    else:
        with open(output_pdf, 'wb') as f:
            pdf_writer = PyPDF2.PdfWriter()
            for _ in range(num_pages):
                temp_pdf = "temp.pdf"
                create_dot_grid_page(temp_pdf)
                reader = PyPDF2.PdfReader(temp_pdf)
                pdf_writer.add_page(reader.pages[0])

            pdf_writer.write(f)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        existing_pdf = sys.argv[1]
    else:
        existing_pdf = None

    num_pages = 1
    output_pdf = "combined.pdf"

    create_dot_grid_pdf(output_pdf, num_pages, existing_pdf)

    print(f"{num_pages} pages of dot grid PDF created in {output_pdf}")
