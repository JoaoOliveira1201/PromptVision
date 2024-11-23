import requests

def generate_video(audio_path, video_path, checkpoint_name, output_path, url="http://localhost:7000/generate-deepfake"):
    """
    Sends a POST request to generate a video by uploading audio and video files.

    :param audio_path: Path to the audio file to upload.
    :param video_path: Path to the video file to upload.
    :param checkpoint_name: The checkpoint name parameter.
    :param output_path: Path where the generated video will be saved.
    :param url: The server URL to send the POST request to.
    """
    try:
        # Open the audio and video files in binary mode
        with open(audio_path, 'rb') as audio_file, open(video_path, 'rb') as video_file:
            # Prepare the files and data payload
            files = {
                'audio': (audio_path, audio_file, 'audio/mpeg'),
                'video': (video_path, video_file, 'video/mp4')
            }
            data = {
                'checkpoint_name': checkpoint_name
            }

            print(f"Sending POST request to {url}...")
            # Send the POST request
            response = requests.post(url, files=files, data=data, stream=True)

            # Check if the request was successful
            if response.status_code == 200:
                # Write the response content to the output file in chunks
                with open(output_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # Filter out keep-alive chunks
                            out_file.write(chunk)
                print(f"Video generated successfully and saved to '{output_path}'.")
            else:
                print(f"Failed to generate video. Status code: {response.status_code}")
                print("Response:", response.text)
    except FileNotFoundError as e:
        print(f"Error: {e}. Please check the file paths.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")

if __name__ == "__main__":
    # Define the paths to your files and parameters
    AUDIO_PATH = "/home/joao/Desktop/PromptVision/deepfake_docker/testFiles/do_not_redeem_the_card.mp3"
    VIDEO_PATH = "/home/joao/Desktop/PromptVision/deepfake_docker/testFiles/kim_7s_raw.mp4"
    CHECKPOINT_NAME = "default"
    OUTPUT_PATH = "generated_video.mp4"

    # Call the function to generate the video
    generate_video(AUDIO_PATH, VIDEO_PATH, CHECKPOINT_NAME, OUTPUT_PATH)
