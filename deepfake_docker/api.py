from bottle import Bottle, request, response, static_file
import subprocess
from pathlib import Path
import logging
import sys
import datetime
import os
import subprocess
import tempfile
from pathlib import Path
import datetime
import os
import io

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

    try:
        audio.save(str(audio_path))
        logger.info(f"Saved audio file to {audio_path}")
    except Exception as e:
        logger.error(f"Failed to save audio file: {e}")
        response.status = 500
        return {"error": "Failed to save audio file"}

    output_path = OUTPUT_DIR / f"deepfake_{os.path.splitext(audio.filename)[0]}_{character_name}.mp4"

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
    finally:
        # Cleanup temporary files
        try:
            audio_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")

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

    logger.debug(f"Character video filename: {video.filename}")

    try:
        # Convert the video to MP4 if it's in WebM format
        if video.filename.lower().endswith('.webm'):
            logger.info("Converting WebM video to MP4 format")
            try:
                mp4_content = convert_webm_to_mp4(video)

                # Create a new filename with .mp4 extension
                mp4_filename = os.path.splitext(video.filename)[0] + '.mp4'
                character_video_path = CHARACTERS_DIR / mp4_filename

                # If file exists, remove it first
                if character_video_path.exists():
                    logger.info(f"Removing existing file: {character_video_path}")
                    character_video_path.unlink()

                # Save the converted MP4 content
                with open(str(character_video_path), 'wb') as f:
                    f.write(mp4_content)

                logger.info(f"Saved converted MP4 video to {character_video_path}")
                return {"message": "Character video converted and uploaded successfully"}

            except (subprocess.CalledProcessError, Exception) as e:
                logger.error(f"Video conversion failed: {str(e)}")
                response.status = 500
                return {"error": "Failed to convert video format"}
        else:
            # Save the original video if it's not WebM
            character_video_path = CHARACTERS_DIR / video.filename

            # If file exists, remove it first
            if character_video_path.exists():
                logger.info(f"Removing existing file: {character_video_path}")
                character_video_path.unlink()

            video.save(str(character_video_path))
            logger.info(f"Saved original video file to {character_video_path}")
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


def convert_webm_to_mp4(webm_video):
    """
    Convert WebM video to MP4 format using FFmpeg.

    Args:
        webm_video: Video file object (from request.files)

    Returns:
        bytes: Converted MP4 video content

    Raises:
        subprocess.CalledProcessError: If FFmpeg conversion fails
        Exception: For other errors during conversion
    """
    temp_input = None
    temp_output = None

    try:
        # Generate unique temporary filenames
        temp_input_fd, temp_input_path = tempfile.mkstemp(suffix='.webm')
        temp_output_fd, temp_output_path = tempfile.mkstemp(suffix='.mp4')

        # Close the file descriptors (we'll use the paths with open())
        os.close(temp_input_fd)
        os.close(temp_output_fd)

        # Save input video to temporary file
        with open(temp_input_path, 'wb') as f:
            webm_video.save(f)

        # Run FFmpeg conversion
        command = [
            'ffmpeg',
            '-y',
            '-i', temp_input_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-b:a', '192k',
            temp_output_path
        ]

        result = subprocess.run(command)

        # Verify the output file exists and has size greater than 0
        if not os.path.exists(temp_output_path) or os.path.getsize(temp_output_path) == 0:
            raise Exception("Conversion failed: Output file is empty or does not exist")

        # Read the converted video content
        with open(temp_output_path, 'rb') as f:
            mp4_content = f.read()

        return mp4_content

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e.stderr.decode()}")
        raise
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        raise
    finally:
        # Cleanup temporary files
        try:
            if temp_input_path and os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if temp_output_path and os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary files: {e}")