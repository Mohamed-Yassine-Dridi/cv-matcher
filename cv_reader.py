import io
from PyPDF2 import PdfReader


def extract_text(pdf_bytes):
    """
    Takes the raw bytes of an uploaded PDF and extracts text.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        full_text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + " "

        return full_text.strip()

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""