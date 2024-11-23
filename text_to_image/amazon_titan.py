# Built-in libraries
import base64
import io
import json
import os
import sys

# External dependencies
import boto3
from PIL import Image
import botocore

boto3_bedrock = boto3.client('bedrock-runtime')

prompt = "A futuristic digital representation of blockchain technology with interconnected glowing blue and green data blocks forming a decentralized network. Golden bitcoins float around the network, each shining with intricate details of their coin engravings. The background is dark with a gradient of deep blue and black, featuring faint binary code streams and holographic financial charts. The style is hyper-realistic with cinematic lighting and a tech-inspired theme."
negative_prompts = "Avoid poorly rendered coins, disconnected or chaotic data blocks, dull lighting, excessive brightness, or simplistic representations of blockchain."

# Create payload
body = json.dumps(
    {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": prompt,                    # Required
            "negativeText": negative_prompts   # Optional
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,   # Range: 1 to 5 
            "quality": "standard",  # Options: standard or premium
            "height": 1024,        # Supported height list in the docs 
            "width": 1024,         # Supported width list in the docs
            "cfgScale": 7.5,       # Range: 1.0 (exclusive) to 10.0
            "seed": 42             # Range: 0 to 214783647
        }
    }
)

# Make model request
response = boto3_bedrock.invoke_model(
    body=body,
    modelId="amazon.titan-image-generator-v1",
    accept="application/json", 
    contentType="application/json"
)

# Process the image
response_body = json.loads(response.get("body").read())
img1_b64 = response_body["images"][0]

# Debug
print(f"Output: {img1_b64[0:80]}...")

os.makedirs("data/titan", exist_ok=True)

# Decode + save
img1 = Image.open(
    io.BytesIO(
        base64.decodebytes(
            bytes(img1_b64, "utf-8")
        )
    )
)
img1.save(f"data/titan/image_1.png")

# Display
img1