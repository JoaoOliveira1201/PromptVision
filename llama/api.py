from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
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

class ChatResponse(BaseModel):
    response_text: str

@app.post("/chat", response_model=ChatResponse)
async def chat(input_text: str = Body(..., embed=True)):
    """
    Endpoint to handle chat conversations using AWS Bedrock's `converse` method.
    """
    try:
        # Prepare the conversation payload
        conversation = [
            {
                "role": "user",
                "content": [{"text": input_text}]
            }
        ]

        # Send the request to Bedrock using the `converse` method
        response = client.converse(
            modelId="meta.llama3-1-405b-instruct-v1:0",
            messages=conversation,
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.5,
                "topP": 0.9,
            },
        )

        # Extract the response text
        response_text = response["output"]["message"]["content"][0]["text"]
        return ChatResponse(response_text=response_text.strip())

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