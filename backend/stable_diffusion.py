import asyncio

import httpx
from typing import List

STABLE_DIFFUSION_URL = "http://stable-diffusion-service:8002/generate"

async def generate_images(titles: List[str]) -> List[str]:
    image_urls = []
    async with httpx.AsyncClient() as client:
        tasks = []
        for title in titles:
            payload = {"prompt": title}
            tasks.append(client.post(STABLE_DIFFUSION_URL, json=payload))
        responses = await asyncio.gather(*tasks)
        for resp in responses:
            resp.raise_for_status()
            image_urls.append(resp.json().get("image_url"))
    return image_urls
