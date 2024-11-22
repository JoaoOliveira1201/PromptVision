import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Presentation Generator",
    description="Generates AI-powered presentations based on user input.",
    version="1.0.0"
)

app.include_router(router)

if os.getenv("STORAGE_BACKEND") != "s3":
    videos_dir = os.path.join(os.path.dirname(__file__), "videos")
    app.mount("/videos", StaticFiles(directory=videos_dir), name="videos")
    logger.info(f"Serving videos from {videos_dir}")
else:
    logger.info("Using Amazon S3 for video store.")
