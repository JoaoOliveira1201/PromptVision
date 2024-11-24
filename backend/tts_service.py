from typing import List
import httpx
import logging
import os

TTS_SERVICE_URL = "http://text_to_speech_container:8080/synthesize"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def generate_audio_scripts(script: List[str]) -> List[str]:
    audio_file_paths = []
    os.makedirs("audio", exist_ok=True)

    for idx, text in enumerate(script):
        logger.info(f"Converting text to speech for slide {idx + 1}")
        logger.info(f"Text: {text}")
        payload = {
            "text": text,
            "output_file_name": f"audio_{idx}",
            "model_character": "default_man_en",
            "output_format": "wav",
            "use_cuda": "false"
        }

        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(TTS_SERVICE_URL, data=payload)  # Use 'data' for form data
            response.raise_for_status()

            audio_file_path = f"audio/audio_{idx}.wav"
            with open(audio_file_path, "wb") as f:
                f.write(response.content)
            audio_file_paths.append(audio_file_path)

    return audio_file_paths
