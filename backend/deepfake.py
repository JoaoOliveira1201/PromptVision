import httpx
from typing import List
from storage import get_storage_service
import tempfile
import os

DEEPFAKE_SERVICE_URL = "http://deepfake-service:8005/generate"

async def generate_deepfake_video(images: List[str], audio_url: str, host_url: str) -> str:
    payload = {
        "images": images,
        "audio_url": audio_url
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(DEEPFAKE_SERVICE_URL, json=payload)
        response.raise_for_status()
        video_content = response.content

    # Save video to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(video_content)
        tmp_file_path = tmp_file.name

    # Upload to the chosen storage backend and get the URL
    storage_service = get_storage_service()
    video_url = storage_service.upload_video(tmp_file_path, host_url=host_url)

    # Clean up the temporary file if using local storage
    if os.getenv("STORAGE_BACKEND") != "s3":
        os.remove(tmp_file_path)

    return video_url