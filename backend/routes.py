from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from pydantic import HttpUrl

from models import PresentationResponse
from deepfake import generate_deepfake_video
from llm import generate_presentation_text
from stable_diffusion import generate_images
from tts import convert_text_to_speech
from pdf_utils import extract_text_from_pdf

router = APIRouter()


@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.post("/generate-presentation", response_model=PresentationResponse)
async def generate_presentation(
        request: Request,
        file: Optional[UploadFile] = File(None, description="Text or PDF file containing the presentation content."),
        text: Optional[str] = Form(None, description="Text content for the presentation."),
        duration: int = Form(..., description="Duration of the presentation in minutes."),
        detail_level: str = Form(..., description="Level of detail for the presentation (e.g., high, medium, low)."),
        character: str = Form(..., description="Character selection for the deepfake."),
        language: str = Form(..., description="Language for the presentation.")
):
    host_url = str(request.base_url).rstrip('/')

    if not file and not text:
        raise HTTPException(status_code=400, detail="Either a file or text must be provided.")

    try:
        # Step 1: Read and process the input file or text
        if file:
            content = await file.read()
            if file.content_type == "application/pdf":
                text_content = extract_text_from_pdf(content)
            elif file.content_type.startswith("text/"):
                text_content = content.decode('utf-8')
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type.")
        else:
            text_content = text.strip()
            if not text_content:
                raise HTTPException(status_code=400, detail="Text content cannot be empty.")

        # Step 2: Generate presentation text using LLM
        #presentation_text = await generate_presentation_text(text_content, duration, detail_level)

        # Step 3: Generate images using Stable Diffusion
        #images = await generate_images(presentation_text['titles'])

        # Step 4: Convert script to speech
        #script_audio = await convert_text_to_speech(presentation_text['script'])

        # Step 5: Generate deepfake video
        #final_video = await generate_deepfake_video(images, script_audio, host_url)

        return PresentationResponse(video_url=HttpUrl("https://voidsoftware.com"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
