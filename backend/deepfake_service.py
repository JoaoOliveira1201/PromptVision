import requests
from pathlib import Path
from typing import List
import logging
import time

DEEPFAKE_SERVICE_URL = "http://37.189.137.45:7000"

logging.basicConfig(level=logging.DEBUG)

async def generate_deepfake_videos(character: str, audio_file_paths: List[str]) -> List[str]:
    generated_video_paths = []
    generate_deepfake_url = f"{DEEPFAKE_SERVICE_URL}/generate-deepfake"

    logging.info(f"Starting deepfake video generation for character: {character}")
    logging.debug(f"Deepfake Service URL: {generate_deepfake_url}")
    
    output_directory = Path("videos")
    output_directory.mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory created or already exists: {output_directory.resolve()}")

    for audio_file_path in audio_file_paths:
        logging.debug(f"Processing audio file: {audio_file_path}")
        audio_filename = Path(audio_file_path).name
        output_video_filename = output_directory / f"deepfake_{character}_{audio_filename}.mp4"

        logging.info(f"Target output video file: {output_video_filename.resolve()}")

        if not Path(audio_file_path).exists():
            logging.error(f"Audio file does not exist: {audio_file_path}")
            continue

        try:
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': (audio_filename, audio_file, 'audio/wav')}
                data = {'character': character}

                logging.info(f"Sending request to deepfake service for audio file: {audio_filename}")
                start_time = time.time()
                response = requests.post(generate_deepfake_url, data=data, files=files, stream=True)
                end_time = time.time()

                logging.debug(f"Request duration: {end_time - start_time:.2f} seconds")
                logging.debug(f"HTTP Response Status Code: {response.status_code}")
                if response.status_code == 200:
                    logging.info(f"Response received successfully for: {audio_filename}")
                    logging.debug(f"Response Headers: {response.headers}")

                    logging.info(f"Saving deepfake video to: {output_video_filename.resolve()}")
                    with open(output_video_filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    logging.info(f"Deepfake video saved: {output_video_filename.resolve()}")
                    generated_video_paths.append(str(output_video_filename))
                else:
                    logging.error(f"Failed to generate deepfake for {audio_filename}")
                    logging.error(f"Response Text: {response.text}")

        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error while accessing the deepfake service: {e}")
        except requests.exceptions.Timeout as e:
            logging.error(f"Request timed out for audio file {audio_filename}: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"An HTTP request error occurred for {audio_filename}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while processing {audio_filename}: {e}")

    logging.info(f"Deepfake video generation completed. Total videos generated: {len(generated_video_paths)}")
    logging.debug(f"Generated video paths: {generated_video_paths}")

    return generated_video_paths

if __name__ == "__main__":
    import asyncio

    audio_file_paths = ["do_not_redeem_the_card.mp3"]

    logging.info("Starting the main process...")
    start_time = time.time()
    try:
        generated_videos = asyncio.run(generate_deepfake_videos("walter_white", audio_file_paths))
        logging.info("Generated videos:")
        for video in generated_videos:
            logging.info(video)
    except Exception as e:
        logging.critical(f"A critical error occurred during execution: {e}")
    finally:
        end_time = time.time()
        logging.info(f"Execution completed in {end_time - start_time:.2f} seconds")
