import asyncio
import base64
import io
import json
import os.path

import cv2
import httpx
from typing import List

import numpy as np
from PIL.Image import Image

from llm_service import generate_stable_diffusion_prompt

STABLE_DIFFUSION_URL = "http://text_to_image_container:7050/generate"

async def generate_images(titles: List[str]) -> List[str]:
    # Generate prompts for creating the images
    prompts = []
    for title in titles:
        prompt = await generate_stable_diffusion_prompt(title)
        prompts.append(prompt)

    file_paths = []
    # the stable diffusion service accepts a payload of "prompt" and "negative_prompt"
    for idx,prompt in enumerate(prompts):
        print(prompt)
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.post(STABLE_DIFFUSION_URL, json=prompt)
                response.raise_for_status()
                json_response = response.json()
                base64image = json_response.get("images")[0]
                image_path = f"photos/image_{idx}.png"
                abs_path = os.path.abspath(image_path)
                save_base64_as_png(base64image, abs_path)
                file_paths.append(abs_path)

            except httpx.HTTPStatusError as exc:
                print(f"Request failed with status {exc.response.status_code}")
                print(f"Response body: {exc.response.text}")

    return file_paths


def save_base64_as_png(base64_string: str, output_path: str) -> None:
    """
    Convert a base64 string to a PNG image and save it using OpenCV.

    Args:
        base64_string (str): The base64 encoded image string
        output_path (str): Where to save the PNG file (e.g., "image.png")
    """
    # Decode base64 string to bytes
    image_bytes = base64.b64decode(base64_string)

    # Convert bytes to numpy array
    image_array = np.frombuffer(image_bytes, np.uint8)

    # Decode numpy array as image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Save as PNG
    cv2.imwrite(output_path, image)

if __name__ == "__main__":
    asyncio.run(generate_images(["A beautiful sunset", "A cute puppy"]))
