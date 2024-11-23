from typing import List
import httpx

TTS_SERVICE_URL = "http://localhost:8080/synthesize"

async def generate_audio_scripts(script: List[str]) -> List[str]:
    audio_file_paths = []

    for idx, text in enumerate(script):
        payload = {"text": text}
        async with httpx.AsyncClient() as client:
            response = await client.post(TTS_SERVICE_URL, json=payload)
            response.raise_for_status()
            audio_file_path = f"audio/audio_{idx}.wav"
            with open(audio_file_path, "wb") as f:
                f.write(response.content)
            audio_file_paths.append(audio_file_path)

    return audio_file_paths
