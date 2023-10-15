#!/usr/bin/env python
import PyPDF2
from reportlab.lib.pagesizes import letter, inch, mm
from reportlab.pdfgen import canvas
from sys import argv

spacing = inch / 3
# Function to create a single page with a gray dot grid
def create_dot_grid_page(output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)

    # Draw gray dots at 1/2" (0.5 inch) intervals
    for x in range(0, int(letter[0]), int(spacing)):
        for y in range(0, int(letter[1]), int(spacing)):
            c.setFillColorRGB(0.2, 0.2, 0.2)  # Gray color
            c.circle(x + spacing/2, y + spacing/2, 0.5, stroke=0, fill=1)

    c.save()

# Function to create the specified number of pages with dot grids
def create_dot_grid_pdf(output_pdf, num_pages):
    with open(output_pdf, 'wb') as f:
        pdf_writer = PyPDF2.PdfWriter()
        for _ in range(num_pages):
            temp_pdf = "temp.pdf"
            create_dot_grid_page(temp_pdf)
            reader = PyPDF2.PdfReader(temp_pdf)
            pdf_writer.add_page(reader.pages[0])

        pdf_writer.write(f)

if __name__ == "__main__":
    num_pages = int(argv[1])
    output_pdf = "dot_grid.pdf"

    create_dot_grid_pdf(output_pdf, num_pages)

    print(f"{num_pages} pages of dot grid PDF created in {output_pdf}")

