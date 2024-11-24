import json
import logging
from typing import Optional, List
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from pydantic import HttpUrl
import random
import os
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
        presentation_content = json.loads(presentation_content)
        logger.info("Parsed presentation content: %s", presentation_content)

        logger.info("Generating images using Stable Diffusion...")
        tittles = extract_tittles_from_presentation_content(presentation_content)
        image_file_paths = await generate_images(tittles)

        logger.info("Generating audio scripts for slides...")
        scripts = extract_scripts_from_presentation_content(presentation_content)
        logger.info(f"scripts: {scripts}")
        audio_file_paths = await generate_audio_scripts(scripts)
        logger.info(f"audio_file_paths: {audio_file_paths}")

        logger.info("Generating deepfake videos...")
        deepfake_file_paths = await generate_deepfake_videos(character, audio_file_paths)
        logger.info(f"deepfake_file_paths: {deepfake_file_paths}")

        logger.info("Generating slides...")
        slide_file_paths = generate_slides(presentation_content, image_file_paths, "output")
        logger.info(f"Slide file paths: {slide_file_paths}")

        logger.info("Building final presentation...")
        final_video_path = build_final_presentation(slide_file_paths, deepfake_file_paths, "output")

        logger.info("Presentation generation completed successfully.")
        return PresentationResponse(video_url=HttpUrl("https://voidsoftware.com"))

    except Exception as e:
        logger.exception("Error occurred during presentation generation.")
        raise HTTPException(status_code=500, detail=str(e))


def create_placeholder_slide(filename):
    """Generate a placeholder slide when an error occurs."""
    image = Image.new('RGB', (1920, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((100, 100), "Error generating slide", fill=(0, 0, 0))
    image.save(filename)

def generate_slides(presentation_content, image_file_paths, output_dir) -> List[str]:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    logger.info("Generating individual slides...")
    slide_renderer = SlideRenderer()
    main_slide_template_options = ["slide_1.html", "slide_2.html"]
    slide_file_paths = []
    count = 0

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Parse presentation_content if it's a string
    if isinstance(presentation_content, str):
        try:
            presentation_content = json.loads(presentation_content)
        except json.JSONDecodeError:
            logger.error("Presentation content is not valid JSON.")
            raise ValueError("Presentation content must be a valid JSON object or dictionary.")

    # Ensure presentation_content has the correct structure
    if not isinstance(presentation_content, dict) or "slides" not in presentation_content:
        logger.error("Presentation content does not have the required 'slides' key.")
        raise ValueError("Presentation content must contain a 'slides' key with slide data.")

    # Parse presentation_content if it's a string
    if isinstance(presentation_content, str):
        try:
            presentation_content = json.loads(presentation_content)
        except json.JSONDecodeError:
            logger.error("Presentation content is not valid JSON.")
            raise ValueError("Presentation content must be a valid JSON object or dictionary.")

    # Ensure presentation_content has the correct structure
    if not isinstance(presentation_content, dict) or "slides" not in presentation_content:
        logger.error("Presentation content does not have the required 'slides' key.")
        raise ValueError("Presentation content must contain a 'slides' key with slide data.")

    # Process each slide
    for slide in presentation_content["slides"]:
        count += 1
        try:
            if slide.get("type") == "introduction":
                logger.info(f"Generating introduction slide: {slide.get('title', 'No Title')}")
                slide_renderer.generate_intro_slide(slide.get("title", ""), slide.get("subtitle", ""))
                filename = f"{output_dir}/intro_slide.png"
                slide_renderer.render_slide(filename)
                if os.path.exists(filename):
                    logger.info(f"File successfully created: {filename}")
                else:
                    logger.error(f"File creation failed: {filename}")
                    raise FileNotFoundError(f"Failed to create slide file: {filename}")
                slide_file_paths.append(filename)
            elif slide.get("type") == "main":
                logger.info(f"Generating main slide {count}: {slide.get('title', 'No Title')}")
                image_path = image_file_paths.pop(0) if image_file_paths else "default_image.png"
                if not os.path.exists(image_path):
                    logger.warning(f"Image file {image_path} not found. Using placeholder image.")
                    create_placeholder_slide(image_path)
                slide_renderer.generate_main_slide(
                    slide.get("title", ""),
                    slide.get("bullet_points", []),
                    image_path,
                    random.choice(main_slide_template_options)
                )
                filename = f"{output_dir}/main_slide_{count}.png"
                slide_renderer.render_slide(filename)
                if os.path.exists(filename):
                    logger.info(f"File successfully created: {filename}")
                else:
                    logger.error(f"File creation failed: {filename}")
                    raise FileNotFoundError(f"Failed to create slide file: {filename}")
                slide_file_paths.append(filename)
            elif slide.get("type") == "conclusion":
                logger.info(f"Generating conclusion slide: {slide.get('title', 'No Title')}")
                slide_renderer.generate_conclusion_slide(slide.get("title", ""), slide.get("subtitle", ""))
                filename = f"{output_dir}/conclusion_slide.png"
                slide_renderer.render_slide(filename)
                if os.path.exists(filename):
                    logger.info(f"File successfully created: {filename}")
                else:
                    logger.error(f"File creation failed: {filename}")
                    raise FileNotFoundError(f"Failed to create slide file: {filename}")
                slide_file_paths.append(filename)
            else:
                logger.warning(f"Unknown slide type: {slide.get('type')}. Skipping...")
        except Exception as slide_error:
            logger.error(f"Error generating slide {count}: {slide_error}")
            placeholder_path = f"{output_dir}/error_slide_{count}.png"
            create_placeholder_slide(placeholder_path)
            slide_file_paths.append(placeholder_path)

    logger.info(f"All slides generated. Total slides: {len(slide_file_paths)}")
    return slide_file_paths



def build_final_presentation(slides, deepfake_videos, output_dir) -> str:
    logger.info("Assembling final presentation video...")
    logger.info(f"Slides provided: {slides}")
    logger.info(f"Deepfake videos provided: {deepfake_videos}")
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