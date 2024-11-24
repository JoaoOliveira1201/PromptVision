from bottle import Bottle, request, response, static_file
import subprocess
from pathlib import Path
import logging
import sys
import datetime

app = Bottle()

# Configure logging
logger = logging.getLogger('wav2lip_service')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Constants
UPLOAD_DIR = Path("/app/uploads")
OUTPUT_DIR = Path("/app/outputs")
CHARACTERS_DIR = Path("/app/characters")
WAV2LIP_MODEL_PATH = "Wav2Lip/checkpoints/wav2lip_gan.pth"
WAV2LIP_SCRIPT_PATH = "Wav2Lip/inference.py"
CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)

@app.post('/generate-deepfake')
def generate_deepfake():
    logger.info("Received request to /generate-deepfake")

    # Get the 'character' parameter from the request
    character_name = request.forms.get('character')
    audio = request.files.get('audio')

    # Check if both character and audio are provided
    if not character_name or not audio:
        logger.warning("Missing character or audio in the request")
        response.status = 400
        return {"error": "Character and audio files are required"}

    logger.debug(f"Character selected: {character_name}")
    logger.debug(f"Audio filename: {audio.filename}")

    # Validate that the character video exists
    character_video_path = CHARACTERS_DIR / character_name
    if not character_video_path.exists() or not character_video_path.is_file():
        logger.warning(f"Character video '{character_name}' does not exist")
        response.status = 400
        return {"error": f"Character '{character_name}' does not exist"}

    # Save the uploaded audio file temporarily
    audio_path = UPLOAD_DIR / audio.filename
    output_path = OUTPUT_DIR / f"deepfake_{audio.filename}_{character_name}"

    try:
        audio.save(str(audio_path))
        logger.info(f"Saved audio file to {audio_path}")
    except Exception as e:
        logger.error(f"Failed to save audio file: {e}")
        response.status = 500
        return {"error": "Failed to save audio file"}

    # Run Wav2Lip inference with subprocess
    command = [
        "python3", WAV2LIP_SCRIPT_PATH,
        "--checkpoint_path", WAV2LIP_MODEL_PATH,
        "--face", str(character_video_path),
        "--audio", str(audio_path),
        "--outfile", str(output_path)
    ]

    logger.info(f"Executing command: {' '.join(command)}")
    start_time = datetime.datetime.now()

    try:
        result = subprocess.run(command)
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Wav2Lip inference completed in {duration} seconds")
        logger.debug(f"Subprocess stdout: {result.stdout}")
        logger.debug(f"Subprocess stderr: {result.stderr}")

        if result.returncode != 0:
            logger.error(f"Wav2Lip inference failed with return code {result.returncode}")
            response.status = 500
            return {"error": f"Wav2Lip inference failed: {result.stderr}"}
    except Exception as e:
        logger.exception(f"Unexpected error during Wav2Lip inference: {e}")
        response.status = 500
        return {"error": "An unexpected error occurred during processing"}

    if not output_path.exists():
        logger.error(f"Output file {output_path} does not exist after inference")
        response.status = 500
        return {"error": "Failed to generate the deepfake video"}

    logger.info(f"Deepfake video generated at {output_path}")

    # Serve the output video file
    try:
        logger.info(f"Sending output video {output_path} to client")
        return static_file(filename=output_path.name, root=str(output_path.parent), download=True)
    except Exception as e:
        logger.exception(f"Failed to send output video: {e}")
        response.status = 500
        return {"error": "Failed to send the generated video"}

@app.post('/upload-character')
def upload_character():
    logger.info("Received request to /upload-character")
    video = request.files.get('video')

    if not video:
        logger.warning("No video file in the request")
        response.status = 400
        return {"error": "Video file is required"}

    # Log the filename
    logger.debug(f"Character video filename: {video.filename}")

    # Save the video to the /app/characters directory
    character_video_path = CHARACTERS_DIR / video.filename

    try:
        video.save(str(character_video_path))
        logger.info(f"Saved character video file to {character_video_path}")
        return {"message": "Character video uploaded successfully"}
    except Exception as e:
        logger.error(f"Failed to save character video file: {e}")
        response.status = 500
        return {"error": "Failed to save character video file"}

@app.get('/list-characters')
def list_characters():
    logger.info("Received request to /list-characters")
    try:
        characters = [f.name for f in CHARACTERS_DIR.iterdir() if f.is_file()]
        logger.debug(f"Available characters: {characters}")
        return {"characters": characters}
    except Exception as e:
        logger.error(f"Failed to list characters: {e}")
        response.status = 500
        return {"error": "Failed to list characters"}