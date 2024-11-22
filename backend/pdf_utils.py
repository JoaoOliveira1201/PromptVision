from io import BytesIO
from PyPDF2 import PdfReader

def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
