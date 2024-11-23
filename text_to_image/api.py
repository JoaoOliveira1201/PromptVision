from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import base64
import io
import json
import boto3
from PIL import Image
import botocore
from enum import Enum

app = FastAPI(
    title="Image Generation API",
    description="API for generating images using Amazon Titan Image Generator",
    version="1.0.0"
)

# Enums for validation
class Quality(str, Enum):
    standard = "standard"
    premium = "premium"

# Request Models
class ImageGenerationConfig(BaseModel):
    numberOfImages: int = Field(default=1, ge=1, le=5)
    quality: Quality = Field(default=Quality.standard)
    height: int = Field(default=1024)
    width: int = Field(default=1024)
    cfgScale: float = Field(default=7.5, gt=1.0, le=10.0)
    seed: Optional[int] = Field(default=None, ge=0, le=214783647)

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    negative_prompt: Optional[str] = None
    config: Optional[ImageGenerationConfig] = Field(default_factory=ImageGenerationConfig)

# Response Models
class ImageGenerationResponse(BaseModel):
    images: List[str]
    config: ImageGenerationConfig

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Initialize Bedrock client
try:
    boto3_bedrock = boto3.client('bedrock-runtime',region_name="us-west-2")
except Exception as e:
    print(f"Failed to initialize Bedrock client: {str(e)}")
    raise

@app.post(
    "/generate",
    response_model=ImageGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_image(request: ImageGenerationRequest):
    try:
        # Prepare the request body
        body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": request.prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": request.config.numberOfImages,
                "quality": request.config.quality,
                "height": request.config.height,
                "width": request.config.width,
                "cfgScale": request.config.cfgScale
            }
        }

        # Add optional parameters
        if request.negative_prompt:
            body["textToImageParams"]["negativeText"] = request.negative_prompt
        
        if request.config.seed is not None:
            body["imageGenerationConfig"]["seed"] = request.config.seed

        # Make the API call to Bedrock
        response = boto3_bedrock.invoke_model(
            body=json.dumps(body),
            modelId="amazon.titan-image-generator-v1",
            accept="application/json",
            contentType="application/json"
        )

        # Process the response
        response_body = json.loads(response.get("body").read())
        
        return ImageGenerationResponse(
            images=response_body["images"],
            config=request.config
        )

    except botocore.exceptions.ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        raise HTTPException(
            status_code=400,
            detail=f"AWS Bedrock Error ({error_code}): {error_message}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/generate-and-save")
async def generate_and_save_image(request: ImageGenerationRequest):
    try:
        # Generate the image first
        response = await generate_image(request)
        
        # Process and save each generated image
        saved_paths = []
        for idx, img_b64 in enumerate(response.images):
            # Decode base64 to image
            img = Image.open(
                io.BytesIO(
                    base64.decodebytes(
                        bytes(img_b64, "utf-8")
                    )
                )
            )
            
            # Create directory if it doesn't exist
            import os
            os.makedirs("data/titan", exist_ok=True)
            
            # Save the image
            path = f"data/titan/image_{idx + 1}.png"
            img.save(path)
            saved_paths.append(path)
        
        return {
            "message": "Images generated and saved successfully",
            "saved_paths": saved_paths,
            "config": response.config
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save images: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}