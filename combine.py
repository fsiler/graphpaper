#!/usr/bin/env python
import sys
from datetime import datetime
from PyPDF2 import PdfMerger

if len(sys.argv) < 2:
    print("Usage: python combine_pdfs.py file1.pdf file2.pdf ...")
    sys.exit(1)

# Get the list of PDF files from command-line arguments
pdf_files = sys.argv[1:]

# Generate output filename with current date
date_str = datetime.now().strftime('%Y%m%d')
output_filename = f"output_{date_str}.pdf"

# Merge PDFs
merger = PdfMerger()
for pdf in pdf_files:
    merger.append(pdf)

with open(output_filename, 'wb') as fout:
    merger.write(fout)

print(f"Combined PDF saved as {output_filename}")

