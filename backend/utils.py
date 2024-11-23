from io import BytesIO
from PyPDF2 import PdfReader

def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def extract_tittles_from_presentation_content(content):
    titles = []
    for slide in content['slides']:
        if slide['type'] == "main":
            titles.append(slide['content'])

    return titles

def extract_scripts_from_presentation_content(content):
    scripts = []
    for slide in content['slides']:
        if slide['type'] == "main":
            scripts.append(slide['content'])

    return scripts