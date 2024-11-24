import requests
from pathlib import Path

def test_endpoints(base_url, character_video_path, audio_file_path):

    # Step 1: Upload a character
    upload_character_url = f"{base_url}/upload-character"
    character_video_filename = Path(character_video_path).name

    with open(character_video_path, 'rb') as video_file:
        files = {'video': (character_video_filename, video_file, 'video/mp4')}
        try:
            response = requests.post(upload_character_url, files=files)
            if response.status_code == 200:
                print(f"Character '{character_video_filename}' uploaded successfully.")
            else:
                print(f"Failed to upload character: {response.text}")
                return
        except Exception as e:
            print(f"Error uploading character: {e}")
            return

    # Step 2: List all available characters
    list_characters_url = f"{base_url}/list-characters"

    try:
        response = requests.get(list_characters_url)
        if response.status_code == 200:
            characters = response.json().get('characters', [])
            print("Available characters:")
            for character in characters:
                print(f" - {character}")
        else:
            print(f"Failed to list characters: {response.text}")
            return
    except Exception as e:
        print(f"Error listing characters: {e}")
        return

    # Step 3: Generate a deepfake
    generate_deepfake_url = f"{base_url}/generate-deepfake"
    audio_filename = Path(audio_file_path).name

    # Use the character we just uploaded
    character_name = character_video_filename

    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': (audio_filename, audio_file, 'audio/wav')}
        data = {'character': character_name}
        try:
            response = requests.post(generate_deepfake_url, data=data, files=files, stream=True)
            if response.status_code == 200:
                # Save the output video
                output_video_filename = f"deepfake_{character_name}_{audio_filename}.mp4"
                with open(output_video_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Deepfake video saved as '{output_video_filename}'.")
            else:
                print(f"Failed to generate deepfake: {response.text}")
        except Exception as e:
            print(f"Error generating deepfake: {e}")
            return

if __name__ == "__main__":
    base_url = "http://localhost:7000"  # Replace with your server's base URL
    audio_file = "/home/joao/Desktop/PromptVision/deepfake_docker/testFiles/do_not_redeem_the_card.mp3"
    character_video_file = "/home/joao/Desktop/PromptVision/deepfake_docker/kim_wexler.mp4"

    test_endpoints(base_url, character_video_file, audio_file)
