from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
import json

app = FastAPI(
    title="Bedrock Chat API",
    description="API for conversing with AWS Bedrock LLM models",
    version="1.0.0"
)

# Pydantic models for request validation
class MessageContent(BaseModel):
    text: str

class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: List[MessageContent]

class InferenceConfig(BaseModel):
    maxTokens: int = Field(default=512, ge=1, le=4096)
    temperature: float = Field(default=0.5, ge=0.0, le=1.0)
    topP: float = Field(default=0.9, ge=0.0, le=1.0)

class ChatRequest(BaseModel):
    messages: List[Message]
    model_id: str = Field(default="meta.llama3-1-405b-instruct-v1:0")
    inference_config: Optional[InferenceConfig] = Field(default_factory=InferenceConfig)

class ChatResponse(BaseModel):
    response_text: str
    conversation: List[Message]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Initialize Bedrock client
try:
    bedrock_client = boto3.client('bedrock-runtime', region_name="us-west-2")
except Exception as e:
    print(f"Failed to initialize Bedrock client: {str(e)}")
    raise

@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def chat(request: ChatRequest):
    try:
        # Send the message to the model
        response = bedrock_client.converse(
            modelId=request.model_id,
            messages=[message.dict() for message in request.messages],
            inferenceConfig={
                "maxTokens": request.inference_config.maxTokens,
                "temperature": request.inference_config.temperature,
                "topP": request.inference_config.topP
            }
        )

        # Extract the response text
        response_text = response["output"]["message"]["content"][0]["text"]

        # Update conversation history
        updated_conversation = request.messages.copy()
        updated_conversation.append(
            Message(
                role="assistant",
                content=[MessageContent(text=response_text.strip())]
            )
        )

        return ChatResponse(
            response_text=response_text.strip(),
            conversation=updated_conversation
        )

    except ClientError as e:
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

@app.post("/chat/simple")
async def simple_chat(message: str, 
                     model_id: str = "meta.llama3-1-405b-instruct-v1:0",
                     max_tokens: int = 512,
                     temperature: float = 0.5,
                     top_p: float = 0.9):
    """
    Simplified endpoint for single-message conversations
    """
    conversation = [
        Message(
            role="user",
            content=[MessageContent(text=message)]
        )
    ]
    
    request = ChatRequest(
        messages=conversation,
        model_id=model_id,
        inference_config=InferenceConfig(
            maxTokens=max_tokens,
            temperature=temperature,
            topP=top_p
        )
    )
    
    return await chat(request)

@app.get("/models")
async def list_available_models():
    """
    List available Bedrock models
    """
    return {
        "models": [
            {
                "id": "meta.llama3-1-405b-instruct-v1:0",
                "name": "Llama 3 8b Instruct",
                "description": "Meta's Llama 3 model optimized for instruction following"
            }
            # Add other models as they become available
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}