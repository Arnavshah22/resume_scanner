import os
from pdfminer.high_level import extract_text as extract_pdf
from docx import Document

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_pdf(file_path)
    elif ext == '.docx':
        doc = Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])
    return None
