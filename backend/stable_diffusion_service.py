import asyncio

import httpx
from typing import List

from llm_service import generate_stable_diffusion_prompt

STABLE_DIFFUSION_URL = "http://stable-diffusion-service:8002/generate"

async def generate_images(titles: List[str]) -> List[str]:

    """
    # Generate prompts for creating the images
    prompts = []
    for title in titles:
        prompt = generate_stable_diffusion_prompt(title)
        prompts.append(prompt)

    # Generate images
    image_urls = []
    async with httpx.AsyncClient() as client:
        tasks = []
        for prompt in prompts:
            payload = prompt
            tasks.append(client.post(STABLE_DIFFUSION_URL, json=payload))
        responses = await asyncio.gather(*tasks)
        for resp in responses:
            resp.raise_for_status()
            image_urls.append(resp.json().get("image_url"))
    """
    image_urls = []
    for title in titles:
        image_urls.append("videos/blockchain.png")

    return image_urls
