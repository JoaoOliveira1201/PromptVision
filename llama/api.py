from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import boto3
from botocore.exceptions import ClientError
import json

# Initialize FastAPI application
app = FastAPI(
    title="Bedrock Chat API",
    description="API for conversing with AWS Bedrock LLM models",
    version="1.0.0"
)

# Initialize AWS Bedrock Runtime client
try:
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    print(client)
except Exception as e:
    print(f"Failed to initialize Bedrock client: {str(e)}")
    raise

# Pydantic models for request validation
class MessageContent(BaseModel):
    text: str

class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")  # Updated `regex` to `pattern`
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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint to handle chat conversations using AWS Bedrock's `converse` method.
    """
    try:
        # Prepare the conversation payload
        conversation = [
            {
                "role": message.role,
                "content": [{"text": content.text} for content in message.content]
            }
            for message in request.messages
        ]

        # Send the request to Bedrock using the `converse` method
        response = client.converse(
            modelId=request.model_id,
            messages=conversation,
            inferenceConfig={
                "maxTokens": request.inference_config.maxTokens,
                "temperature": request.inference_config.temperature,
                "topP": request.inference_config.topP,
            },
        )

        # Extract the response text
        response_text = response["output"]["message"]["content"][0]["text"]

        # Append the response to the conversation history
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
        print(f"AWS Bedrock Error ({error_code}): {error_message}")
        raise HTTPException(
            status_code=400,
            detail=f"AWS Bedrock Error ({error_code}): {error_message}"
        )

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/test-bedrock")
def test_bedrock():
    """
    Test endpoint to ensure `converse` works with a simple payload.
    """
    try:
        response = client.converse(
            modelId="meta.llama3-1-405b-instruct-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "how do I create a branch?"}]
                }
            ],
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.5,
                "topP": 0.9
            },
        )
        return {"response": response}
    except Exception as e:
        print(f"Error testing Bedrock: {str(e)}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the API is running.
    """
    return {"status": "healthy"}