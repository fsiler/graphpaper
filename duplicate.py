#!/usr/bin/env python
import sys
import PyPDF2
from reportlab.lib.pagesizes import letter, mm
from reportlab.pdfgen import canvas
from datetime import datetime

# Function to create the specified number of pages with dot grids
def interleave_dot_grid_pdf(output_pdf, existing_pdfs=[]):
    pdf_writer = PyPDF2.PdfWriter()

    for existing_pdf in existing_pdfs:
        with open(existing_pdf, 'rb') as existing_file:
            existing_pdf_reader = PyPDF2.PdfReader(existing_file)

            # Copy pages from the existing PDF
            for page in existing_pdf_reader.pages:
                pdf_writer.add_page(page)
                pdf_writer.add_page(page)

    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)

if __name__ == "__main__":
    existing_pdfs = sys.argv[1:]

    # Generate ISO timestamp
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")

    # Create output file name with timestamp
    output_pdf = f"duplicated_{timestamp}.pdf"

    interleave_dot_grid_pdf(output_pdf, existing_pdfs)

