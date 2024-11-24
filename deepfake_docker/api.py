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

    video = request.files.get('video')
    audio = request.files.get('audio')

    # Check if both files are provided
    if not video or not audio:
        logger.warning("Missing video or audio file in the request")
        response.status = 400
        return {"error": "Video and audio files are required"}

    # Log the filenames
    logger.debug(f"Video filename: {video.filename}")
    logger.debug(f"Audio filename: {audio.filename}")

    # Save uploaded files temporarily
    video_path = UPLOAD_DIR / video.filename
    audio_path = UPLOAD_DIR / audio.filename
    output_path = OUTPUT_DIR / f"deepfake_{video.filename}"

    try:
        video.save(str(video_path))
        logger.info(f"Saved video file to {video_path}")
    except Exception as e:
        logger.error(f"Failed to save video file: {e}")
        response.status = 500
        return {"error": "Failed to save video file"}

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
        "--face", str(video_path),
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
    except subprocess.CalledProcessError as e:
        logger.error(f"Wav2Lip inference failed: {e.stderr}")
        response.status = 500
        return {"error": f"Wav2Lip inference failed: {e.stderr}"}
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