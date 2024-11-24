import json
import logging
from typing import Optional, List
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import HttpUrl
import random
import os
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw

from presentation_builder import PresentationBuilder
from slide_renderer import SlideRenderer
from models import PresentationResponse
from deepfake_service import generate_deepfake_videos
from llm_service import generate_presentation_content
from stable_diffusion_service import generate_images
from tts_service import generate_audio_scripts
from utils import *

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def read_root():
    logger.info("Root endpoint accessed.")
    return {"Hello": "World"}


@router.post("/generate-presentation")
async def generate_presentation(
        request: Request,
        file: Optional[UploadFile] = File(None, description="File containing content."),
        text: Optional[str] = Form(None, description="Text content."),
        duration: int = Form(..., description="Duration in minutes."),
        detail_level: str = Form(..., description="Detail level."),
        character: str = Form(..., description="Character for deepfake."),
):
    logger.info("Generate presentation called.")
    host_url = str(request.base_url).rstrip('/')

    if not file and not text:
        raise HTTPException(status_code=400, detail="Either file or text must be provided.")

    try:
        # Handle file or text input
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

        # Generate content
        presentation_content = await generate_presentation_content(text_content, duration, detail_level, character)
        presentation_content = json.loads(presentation_content)

        # Generate assets
        tittles = extract_tittles_from_presentation_content(presentation_content)
        image_file_paths = await generate_images(tittles)
        scripts = extract_scripts_from_presentation_content(presentation_content)
        audio_file_paths = await generate_audio_scripts(scripts)
        deepfake_file_paths = await generate_deepfake_videos(character, audio_file_paths)
        slide_file_paths = generate_slides(presentation_content, image_file_paths, "output")
        final_video_path = build_final_presentation(slide_file_paths, deepfake_file_paths, "output")

        if not os.path.exists(final_video_path):
            raise HTTPException(status_code=500, detail="Failed to generate presentation video")

        # Return final video
        return FileResponse(
            path=final_video_path,
            filename="presentation.mp4",
            media_type="video/mp4",
        )

    except Exception as e:
        logger.exception("Error during presentation generation.")
        raise HTTPException(status_code=500, detail=str(e))
