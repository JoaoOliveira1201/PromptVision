import httpx
from typing import Dict

LLM_SERVICE_URL = "http://llm-service:8001/generate"

async def generate_presentation_text(content: str, duration: int, detail_level: str) -> Dict:
    payload = {
        "content": content,
        "duration": duration,
        "detail_level": detail_level
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(LLM_SERVICE_URL, json=payload)
        response.raise_for_status()
        return response.json()
