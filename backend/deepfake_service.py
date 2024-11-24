import requests
from pathlib import Path
from typing import List
import logging

DEEPFAKE_SERVICE_URL = "http://37.189.137.45:7000"

logging.basicConfig(level=logging.INFO)

async def generate_deepfake_videos(character: str, audio_file_paths: List[str]) -> List[str]:
    generated_video_paths = []
    generate_deepfake_url = f"{DEEPFAKE_SERVICE_URL}/generate-deepfake"

    output_directory = Path("videos")
    output_directory.mkdir(parents=True, exist_ok=True)

    for audio_file_path in audio_file_paths:
        audio_filename = Path(audio_file_path).name
        output_video_filename = output_directory / f"deepfake_{character}_{audio_filename}.mp4"

        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': (audio_filename, audio_file, 'audio/wav')}
            data = {'character': character}

            try:
                logging.info(f"Generating deepfake for {audio_filename}...")
                response = requests.post(generate_deepfake_url, data=data, files=files, stream=True)
                if response.status_code == 200:
                    logging.info(f"Saving deepfake for {audio_filename} as {output_video_filename}...")
                    with open(output_video_filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    logging.info(f"Generated deepfake for {audio_filename} as {output_video_filename}")
                    generated_video_paths.append(str(output_video_filename))
                else:
                    logging.error(f"Error generating deepfake for {audio_filename}: {response.text}")
            except Exception as e:
                logging.error(f"An error occurred while generating deepfake for {audio_filename}: {e}")

    return generated_video_paths

if __name__ == "__main__":
    import asyncio

    audio_file_paths = ["do_not_redeem_the_card.mp3"]
    asyncio.run(generate_deepfake_videos("walter_white", audio_file_paths))