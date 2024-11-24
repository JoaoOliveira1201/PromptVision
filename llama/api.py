from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import ClientError

# Initialize FastAPI application
app = FastAPI(
    title="Bedrock Chat API",
    description="API for conversing with AWS Bedrock LLM models",
    version="1.0.0"
)

# Initialize AWS Bedrock Runtime client
try:
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
except Exception as e:
    print(f"Failed to initialize Bedrock client: {str(e)}")
    raise

class ChatRequest(BaseModel):
    input_text: str
    duration_minutes: float = Field(default=1.0, gt=0, description="Duration in minutes")

class ChatResponse(BaseModel):
    response_text: str

def calculate_max_tokens(duration_minutes: float) -> int:
    """
    Calculate maximum tokens based on duration in minutes.
    """
    words_per_minute = 200
    tokens_per_word = 1.5
    base_tokens = 100
    
    calculated_tokens = int(duration_minutes * words_per_minute * tokens_per_word)
    return max(base_tokens, min(calculated_tokens, 4096))

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Endpoint to handle chat conversations using AWS Bedrock's `converse` method.
    """
    try:
        max_tokens = calculate_max_tokens(request.duration_minutes)
        
        conversation = [
            {
                "role": "user",
                "content": [{"text": request.input_text}]
            }
        ]

        response = client.converse(
            modelId="meta.llama3-1-70b-instruct-v1:0",
            messages=conversation,
            inferenceConfig={
                "maxTokens": 4000,
                "temperature": 0.5,
                "topP": 0.9,
            },
        )

        response_text = response["output"]["message"]["content"][0]["text"]
        return {"response_text": response_text.strip()}

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

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the API is running.
    """
    return {"status": "healthy"}