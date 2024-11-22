import httpx

TTS_SERVICE_URL = "http://tts-service:8003/convert"

async def convert_text_to_speech(script: str) -> str:
    payload = {"text": script}
    async with httpx.AsyncClient() as client:
        response = await client.post(TTS_SERVICE_URL, json=payload)
        response.raise_for_status()
        return response.json().get("audio_url")
