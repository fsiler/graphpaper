import sys
import getpass
from PyPDF2 import PdfReader, PdfWriter

def remove_password(input_file, password):
    try:
        # Open the PDF file
        reader = PdfReader(input_file)

        # Check if the PDF is encrypted
        if reader.is_encrypted:
            # Try to decrypt with the provided password
            reader.decrypt(password)

        # Create a PDF writer object
        writer = PdfWriter()

        # Add all pages to the writer
        for page in reader.pages:
            writer.add_page(page)

        # Generate the output filename
        output_file = input_file.rsplit('.', 1)[0] + '_nopassword.pdf'

        # Write the new PDF to a file
        with open(output_file, 'wb') as f:
            writer.write(f)

        print(f"Password removed. New file created: {output_file}")

    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")

def main():
    # Check if filenames are provided as command line arguments
    if len(sys.argv) < 2:
        print("Usage: python script.py <pdf_file1> <pdf_file2> ...")
        sys.exit(1)

    # Process each PDF file
    for pdf_file in sys.argv[1:]:
        password = getpass.getpass(f"Enter password for {pdf_file} (press Enter if no password): ")
        remove_password(pdf_file, password)

if __name__ == "__main__":
    main()

