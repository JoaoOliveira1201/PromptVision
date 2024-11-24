"""
import tempfile
import os
import subprocess
from pathlib import Path
from bottle import Bottle, run, request, response, static_file
import logging

# Initialize Bottle app
app = Bottle()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MODELS_LOCATION = {
    'default_man_en': '/app/voices/en_GB/en_GB-northern_english_male-medium.onnx',
    'default_man_pt': '/app/voices/pt_PT/pt_PT-tugão-medium.onnx'
}

@app.route('/synthesize', method=['POST'])
def synthesize_endpoint():
    logger.info("Received a request to synthesize speech.")

    text = request.forms.get('text') or request.query.text
    if not text:
        logger.error("Missing required parameter: text")
        response.status = 400
        return {'error': 'Missing required parameter: text'}

    output_file_name = (request.forms.get('output_file_name') or request.query.output_file_name or "placeholderAudio")
    model_character = (request.forms.get('model_character') or request.query.model_character or 'default_man_en')
    output_format = (request.forms.get('output_format') or request.query.output_format or 'wav').lower()
    use_cuda_param = request.forms.get('use_cuda') or request.query.use_cuda
    use_cuda = use_cuda_param.lower() in ['true', '1', 'yes'] if use_cuda_param is not None else False

    model_path = MODELS_LOCATION.get(model_character)
    logger.info(f"Text: {text}, Model: {model_character}, Output Format: {output_format}, CUDA: {use_cuda}")

    try:
        audio_data = synthesize(
            text=text,
            model_path=model_path,
            output_file_name=output_file_name,
            output_format=output_format,
            use_cuda=use_cuda,
            is_portuguese=model_character == 'default_man_pt'
        )
        logger.info("Speech synthesis completed successfully.")
    except Exception as e:
        logger.error(f"Error during synthesis: {str(e)}")
        response.status = 500
        return {'error': str(e)}

    if output_format == 'wav':
        response.content_type = 'audio/wav'
        file_extension = 'wav'
    elif output_format == 'mp3':
        response.content_type = 'audio/mpeg'
        file_extension = 'mp3'
    else:
        response.content_type = 'application/octet-stream'

    if output_file_name:
        response.headers[
            'Content-Disposition'] = f'attachment; filename="{Path(output_file_name).name}.{file_extension}"'

    return audio_data


def synthesize(text, model_path, output_file_name=None, speaker_id=None, output_format='wav', use_cuda=True,
               is_portuguese=False):
    logger.info("Starting speech synthesis process.")
    temp_files = []
    try:
        logger.debug(f"Creating temporary WAV file.")
        tmp_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_files.append(tmp_wav_file.name)

        cmd = [
            'python3',
            '-m', 'piper',
            '--model', model_path,
            '--output_file', tmp_wav_file.name
        ]
        if use_cuda:
            cmd.append('--cuda')
        if speaker_id is not None:
            cmd.extend(['--speaker', str(speaker_id)])

        logger.debug(f"Running Piper command: {' '.join(cmd)}")
        process = subprocess.run(
            cmd,
            input=text.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        logger.info("Piper command completed successfully.")

        input_file = tmp_wav_file.name

        if is_portuguese:
            logger.debug("Adjusting audio speed for Portuguese model.")
            tmp_slow_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_files.append(tmp_slow_wav.name)

            slow_cmd = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                '-filter:a', 'atempo=0.9',
                tmp_slow_wav.name
            ]
            logger.debug(f"Running ffmpeg command for speed adjustment: {' '.join(slow_cmd)}")
            subprocess.run(
                slow_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            input_file = tmp_slow_wav.name

        if output_format.lower() == 'mp3':
            logger.debug("Converting WAV to MP3 format.")
            tmp_mp3_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_files.append(tmp_mp3_file.name)

            ffmpeg_cmd = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                '-f', 'mp3',
                tmp_mp3_file.name
            ]
            logger.debug(f"Running ffmpeg command for MP3 conversion: {' '.join(ffmpeg_cmd)}")
            subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            final_file = tmp_mp3_file.name
        else:
            final_file = input_file

        with open(final_file, 'rb') as f:
            audio_data = f.read()
            logger.debug(f"Read synthesized audio data from file: {final_file}")

        if output_file_name:
            output_path = f"{output_file_name}.{output_format}"
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.debug(f"Created output directory: {output_dir}")
            with open(output_path, 'wb') as f_out:
                f_out.write(audio_data)
                logger.info(f"Saved output audio file: {output_path}")

        return audio_data

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        logger.error(f"Subprocess error: {error_message}")
        raise RuntimeError(f"Subprocess error: {error_message}")
    except PermissionError as pe:
        logger.error(f"Permission error: {str(pe)}")
        raise RuntimeError(f"Permission error: {str(pe)}")
    except Exception as ex:
        logger.error(f"Unexpected error: {str(ex)}")
        raise RuntimeError(f"Unexpected error: {str(ex)}")
    finally:
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.debug(f"Deleted temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file}: {str(e)}")

@app.route('/upload', method=['POST'])
def upload_audio():
    logger.info("Received a request to upload an audio file.")

    upload = request.files.get('file')  # The name of the file input field should be 'file'

    if not upload:
        logger.error("No file uploaded")
        response.status = 400
        return {'error': 'No file uploaded'}

    # The directory to save the file
    save_dir = '/app/characters'

    # Ensure the directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
        logger.debug(f"Created directory: {save_dir}")

    # Define the default filename
    default_filename = 'default_audio_file.wav'  # Adjust the filename as needed

    # Build the full file path
    file_path = os.path.join(save_dir, default_filename)

    try:
        # Save the file to the specified path
        upload.save(file_path, overwrite=True)
        logger.info(f"File saved to {file_path}")
        response.status = 200
        return {'status': 'File uploaded successfully'}
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        response.status = 500
        return {'error': str(e)}
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import tempfile
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Speech Synthesis API",
    description="API for speech synthesis using Piper models",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

MODELS_LOCATION = {
    "default_man_en": "/app/voices/en_GB/en_GB-northern_english_male-medium.onnx",
    "default_man_pt": "/app/voices/pt_PT/pt_PT-tugão-medium.onnx",
}


@app.post("/synthesize")
async def synthesize(
    text: str = Form(...),
    output_file_name: str = Form("placeholderAudio"),
    model_character: str = Form("default_man_en"),
    output_format: str = Form("wav"),
    use_cuda: bool = Form(True),
):
    """
    Synthesize speech from text using a specified model.
    """
    logger.info(f"Received request to synthesize speech with text: {text}")
    model_path = MODELS_LOCATION.get(model_character)

    if not model_path:
        logger.error(f"Model {model_character} not found.")
        raise HTTPException(status_code=400, detail=f"Model {model_character} not found.")

    try:
        audio_data = await perform_synthesis(
            text, model_path, output_file_name, output_format.lower(), use_cuda, model_character == "default_man_pt"
        )
        logger.info("Speech synthesis completed successfully.")

        file_extension = output_format.lower()
        response_path = f"{output_file_name}.{file_extension}"
        with open(response_path, "wb") as f:
            f.write(audio_data)

        return FileResponse(response_path, media_type=f"audio/{file_extension}", filename=response_path)

    except Exception as e:
        logger.error(f"Error during synthesis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def perform_synthesis(
    text, model_path, output_file_name, output_format, use_cuda, is_portuguese
):
    temp_files = []
    try:
        logger.debug("Creating temporary WAV file.")
        tmp_wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_files.append(tmp_wav_file.name)

        cmd = [
            "python3",
            "-m",
            "piper",
            "--model",
            model_path,
            "--output_file",
            tmp_wav_file.name,
        ]
        if use_cuda:
            cmd.append("--cuda")

        subprocess.run(cmd, input=text.encode("utf-8"), check=True)

        input_file = tmp_wav_file.name

        if is_portuguese:
            tmp_slow_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_files.append(tmp_slow_wav.name)

            slow_cmd = ["ffmpeg", "-y", "-i", input_file, "-filter:a", "atempo=0.9", tmp_slow_wav.name]
            subprocess.run(slow_cmd, check=True)
            input_file = tmp_slow_wav.name

        if output_format == "mp3":
            tmp_mp3_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_files.append(tmp_mp3_file.name)

            ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_file, "-f", "mp3", tmp_mp3_file.name]
            subprocess.run(ffmpeg_cmd, check=True)
            final_file = tmp_mp3_file.name
        else:
            final_file = input_file

        with open(final_file, "rb") as f:
            audio_data = f.read()

        return audio_data

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8") if e.stderr else str(e)
        logger.error(f"Subprocess error: {error_message}")
        raise RuntimeError(error_message)
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file.
    """
    logger.info("Received request to upload an audio file.")
    save_dir = "/app/characters"

    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file.filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File saved to {file_path}")
        return {"status": "File uploaded successfully", "file_path": file_path}
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
