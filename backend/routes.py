import logging
from typing import Optional, List
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from pydantic import HttpUrl
import random
import os

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


@router.post("/generate-presentation", response_model=PresentationResponse)
async def generate_presentation(
        request: Request,
        file: Optional[UploadFile] = File(None, description="Text or PDF file containing the presentation content."),
        text: Optional[str] = Form(None, description="Text content for the presentation."),
        duration: int = Form(..., description="Duration of the presentation in minutes."),
        detail_level: str = Form(..., description="Level of detail for the presentation (e.g., high, medium, low)."),
        character: str = Form(..., description="Character selection for the deepfake.")
):
    logger.info("Generate presentation endpoint called.")
    host_url = str(request.base_url).rstrip('/')

    if not file and not text:
        logger.error("No input provided. Either file or text must be provided.")
        raise HTTPException(status_code=400, detail="Either a file or text must be provided.")

    try:
        logger.info("Processing input...")
        if file:
            logger.info(f"File provided: {file.filename}")
            content = await file.read()
            if file.content_type == "application/pdf":
                text_content = extract_text_from_pdf(content)
                logger.info("Extracted text from PDF.")
            elif file.content_type.startswith("text/"):
                text_content = content.decode('utf-8')
                logger.info("Extracted text from plain text file.")
            else:
                logger.error("Unsupported file type provided.")
                raise HTTPException(status_code=400, detail="Unsupported file type.")
        else:
            logger.info("Text input provided.")
            text_content = text.strip()
            if not text_content:
                logger.error("Text content is empty.")
                raise HTTPException(status_code=400, detail="Text content cannot be empty.")

        logger.info("Generating presentation content using LLM...")
        presentation_content = await generate_presentation_content(text_content, duration, detail_level, character)

        logger.info("Generating images using Stable Diffusion...")
        tittles = extract_tittles_from_presentation_content(presentation_content)
        image_file_paths = await generate_images(tittles)

        logger.info("Generating audio scripts for slides...")
        scripts = extract_scripts_from_presentation_content(presentation_content)
        audio_file_paths = await generate_audio_scripts(scripts)

        logger.info("Generating deepfake videos...")
        deepfake_file_paths = await generate_deepfake_videos(character, audio_file_paths)

        logger.info("Generating slides...")
        slide_file_paths = generate_slides(presentation_content, image_file_paths, "output")

        logger.info("Building final presentation...")
        final_video_path = build_final_presentation(slide_file_paths, deepfake_file_paths, "output")

        logger.info("Presentation generation completed successfully.")
        return PresentationResponse(video_url=HttpUrl("https://voidsoftware.com"))

    except Exception as e:
        logger.exception("Error occurred during presentation generation.")
        raise HTTPException(status_code=500, detail=str(e))


def generate_slides(presentation_content, image_file_paths, output_dir) -> List[str]:
    logger.info("Generating individual slides...")
    slide_renderer = SlideRenderer()
    main_slide_template_options = ["slide_1.html", "slide_2.html"]
    slide_file_paths = []
    count = 0

    for slide in presentation_content["slides"]:
        count += 1
        try:
            if slide["type"] == "introduction":
                logger.info(f"Generating introduction slide: {slide['title']}")
                slide_renderer.generate_intro_slide(slide["title"], slide["subtitle"])
                filename = f"{output_dir}/intro_slide.png"
                slide_renderer.render_slide(filename)
                slide_file_paths.append(filename)
            elif slide["type"] == "main":
                logger.info(f"Generating main slide {count}: {slide['title']}")
                slide_renderer.generate_main_slide(slide["title"], slide["bullet_points"],
                                                   image_file_paths.pop(0), random.choice(main_slide_template_options))
                filename = f"{output_dir}/main_slide_{count}.png"
                slide_renderer.render_slide(filename)
                slide_file_paths.append(filename)
            elif slide["type"] == "conclusion":
                logger.info(f"Generating conclusion slide: {slide['title']}")
                slide_renderer.generate_conclusion_slide(slide["title"], slide["subtitle"])
                filename = f"{output_dir}/conclusion_slide.png"
                slide_renderer.render_slide(filename)
                slide_file_paths.append(filename)
        except Exception as slide_error:
            logger.error(f"Error generating slide {count}: {slide_error}")

    logger.info(f"All slides generated. Total slides: {len(slide_file_paths)}")
    return slide_file_paths


def build_final_presentation(slides, deepfake_videos, output_dir) -> str:
    logger.info("Assembling final presentation video...")
    presentation_builder = PresentationBuilder(
        video_position=("right", "bottom"),
        video_size=(400, None)
    )

    for slide, video in zip(slides, deepfake_videos):
        logger.info(f"Adding slide {slide} with video {video} to presentation.")
        presentation_builder.add_slide(slide, video)

    final_video_path = os.path.join(output_dir, "final_presentation.mp4")
    presentation_builder.produce_presentation(final_video_path)
    logger.info(f"Final presentation saved at {final_video_path}")

    return final_video_path
