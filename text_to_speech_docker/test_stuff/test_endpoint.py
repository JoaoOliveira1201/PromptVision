import requests
import os

# Endpoint configuration
BASE_URL = "http://localhost:8080"  # Update with the correct host and port if necessary
SYNTHESIZE_ENDPOINT = f"{BASE_URL}/synthesize"

# Test parameters
test_text = "President Biden has told Americans that they have to stand up for their democracy; it is not a guaranteed right. Here is an article that looks at the origins of US democracy and its roots in medieval England.What future is there for the British monarchy? Under Queen Elizabeth it had its ups and downs, finishing on a high note. Can King Charles ensure its survival?"
model_character = "default_man_en"
output_file_name = "test_audio2"
output_format = "mp3"  # Choose 'mp3' or 'wav'
use_cuda = False  # Set to False if you want to test without CUDA

def test_synthesize():
    # Prepare the payload
    payload = {
        'text': test_text,
        'model_character': model_character,
        'output_file_name': output_file_name,
        'output_format': output_format,
        'use_cuda': str(use_cuda).lower()  # Convert to 'true' or 'false'
    }

    try:
        # Make the POST request
        response = requests.post(SYNTHESIZE_ENDPOINT, data=payload)

        # Check the response
        if response.status_code == 200:
            # Save the audio file locally for verification
            output_file_path = f"{output_file_name}.{output_format}"
            with open(output_file_path, "wb") as f:
                f.write(response.content)
            print(f"Audio file saved successfully: {output_file_path}")
        else:
            # Print the error message
            print(f"Error: {response.status_code}")
            print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_synthesize()
