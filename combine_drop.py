import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import messagebox
import PyPDF2
import os

class PDFCombinerApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF Combiner")
        master.geometry("300x200")

        self.label = tk.Label(master, text="Drop PDF files here", font=("Arial", 14))
        self.label.pack(expand=True, fill='both')

        # Enable drag and drop for the label
        self.label.drop_target_register(DND_FILES)
        self.label.dnd_bind('<<Drop>>', self.drop)

    def drop(self, event):
        files = event.data
        if isinstance(files, str):
            files = self.master.tk.splitlist(files)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]

        if not pdf_files:
            messagebox.showwarning("No PDFs", "No PDF files were dropped.")
            return

        output_file = "combined_output.pdf"
        self.combine_pdfs(pdf_files, output_file)
        messagebox.showinfo("Success", f"PDFs combined into {output_file}")

    def combine_pdfs(self, input_files, output_file):
        pdf_writer = PyPDF2.PdfWriter()

        for file in input_files:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

        with open(output_file, 'wb') as out:
            pdf_writer.write(out)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFCombinerApp(root)
    root.mainloop()

