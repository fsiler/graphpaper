#!/usr/bin/env python
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import messagebox
import PyPDF2
import os
from datetime import datetime

class PDFCombinerApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF Combiner")
        master.geometry("400x300")

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

        output_file = self.combine_pdfs(pdf_files)
        messagebox.showinfo("Success", f"PDFs combined into {output_file}")

    def combine_pdfs(self, input_files):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_names = "_".join([os.path.splitext(os.path.basename(f))[0] for f in input_files])
        truncated_names = base_names[:50]  # Limit to 50 characters to avoid excessively long filenames
        output_file = f"{timestamp}_{truncated_names}_combined.pdf"

        pdf_writer = PyPDF2.PdfWriter()

        for file in input_files:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

        with open(output_file, 'wb') as out:
            pdf_writer.write(out)

        return output_file

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFCombinerApp(root)
    root.mainloop()

