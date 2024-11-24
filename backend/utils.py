from io import BytesIO
from PyPDF2 import PdfReader

def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def extract_tittles_from_presentation_content(content):
    import json

    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("Content provided is not valid JSON.")

    if not isinstance(content, dict) or 'slides' not in content:
        raise ValueError("Content does not have the expected structure.")

    titles = []
    for slide in content['slides']:
        if slide.get('type') == "main" and 'title' in slide:
            titles.append(slide['title'])

    return titles

def extract_scripts_from_presentation_content(content):
    import json

    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("Content provided is not valid JSON.")

    if not isinstance(content, dict) or 'slides' not in content:
        raise ValueError("Content does not have the expected structure.")

    scripts = []
    for slide in content['slides']:
        if slide.get('type') == "main" and 'script' in slide:
            scripts.append(slide['script'])

    return scripts
