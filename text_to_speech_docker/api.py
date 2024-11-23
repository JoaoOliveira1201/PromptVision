import tempfile
import os
import subprocess
from pathlib import Path
from bottle import Bottle, run, request, response, static_file
import logging

# Initialize Bottle app
app = Bottle()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_LOCATION = {'default_man_en': '/app/voices/en_GB/en_GB-northern_english_male-medium.onnx',
                   'default_man_pt': '/app/voices/pt_PT/pt_PT-tugão-medium.onnx'}


@app.route('/synthesize', method=['POST'])
def synthesize_endpoint():
    if request.forms.get('text') is None and request.query.text is None:
        response.status = 400
        return {'error': 'Missing required parameter: text'}
    text = request.forms.get('text') or request.query.text

    if request.forms.get('model_character') is None and request.query.model_character is None:
        response.status = 400
        return {'error': 'Missing required parameter: model_character'}
    model_character = request.forms.get('model_character') or request.query.model_character
    model_path = MODELS_LOCATION.get(model_character)

    if request.forms.get('output_file_name') is None and request.query.output_file_name is None:
        response.status = 400
        return {'error': 'Missing required parameter: output_file_name'}
    output_file_name = request.forms.get('output_file_name') or request.query.output_file_name

    if request.forms.get('output_format') is None and request.query.output_format is None:
        response.status = 400
        return {'error': 'Missing required parameter: output_format'}
    output_format = request.forms.get('output_format') or request.query.output_format or 'wav'
    output_format = output_format.lower()

    use_cuda_param = request.forms.get('use_cuda') or request.query.use_cuda
    if use_cuda_param is not None:
        use_cuda = use_cuda_param.lower() in ['true', '1', 'yes']
    else:
        use_cuda = True

    try:
        audio_data = synthesize(
            text=text,
            model_path=model_path,
            output_file_name=output_file_name,
            output_format=output_format,
            use_cuda=use_cuda,
            is_portuguese=model_character == 'default_man_pt'
        )
    except Exception as e:
        response.status = 500
        return {'error': str(e)}

    # Set the correct content-type
    if output_format == 'wav':
        response.content_type = 'audio/wav'
        file_extension = 'wav'
    elif output_format == 'mp3':
        response.content_type = 'audio/mpeg'
        file_extension = 'mp3'
    else:
        response.content_type = 'application/octet-stream'

    # Optionally set Content-Disposition header if output_file_name is provided
    if output_file_name:
        response.headers[
            'Content-Disposition'] = f'attachment; filename="{Path(output_file_name).name}.{file_extension}"'

    return audio_data


def synthesize(text, model_path, output_file_name=None, speaker_id=None, output_format='wav', use_cuda=True,
               is_portuguese=False):
    """
    Synthesizes speech from the given text.

    :param use_cuda: Use CUDA for synthesis (default: True)
    :param text: The input text to synthesize
    :param model_path: Path to the Piper voice model (.onnx file)
    :param output_file_name: Optional path to save the output audio file
    :param speaker_id: Optional speaker ID for multi-speaker models
    :param output_format: Output audio format, 'wav' or 'mp3' (default 'wav')
    :param is_portuguese: Boolean indicating if using Portuguese model (for speed adjustment)
    :return: The synthesized audio data as bytes
    """
    temp_files = []
    try:
        # Create temporary WAV file
        tmp_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_files.append(tmp_wav_file.name)

        cmd = [
            'python3',  # Use Python to run Piper
            '-m', 'piper',  # Invoke Piper as a module
            '--model', model_path,
            '--output_file', tmp_wav_file.name
        ]
        if use_cuda:
            cmd.append('--cuda')
        if speaker_id is not None:
            cmd.extend(['--speaker', str(speaker_id)])

        # Run the Piper command
        process = subprocess.run(
            cmd,
            input=text.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        input_file = tmp_wav_file.name

        # If Portuguese, slow down the audio
        if is_portuguese:
            tmp_slow_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_files.append(tmp_slow_wav.name)

            slow_cmd = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                '-filter:a', 'atempo=0.9',
                tmp_slow_wav.name
            ]
            subprocess.run(
                slow_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            input_file = tmp_slow_wav.name

        # Convert to MP3 if requested
        if output_format.lower() == 'mp3':
            tmp_mp3_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_files.append(tmp_mp3_file.name)

            ffmpeg_cmd = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                '-f', 'mp3',
                tmp_mp3_file.name
            ]
            subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            final_file = tmp_mp3_file.name
        else:
            final_file = input_file

        # Read the final audio data
        with open(final_file, 'rb') as f:
            audio_data = f.read()

        # Save the audio data to the output file if provided
        if output_file_name:
            output_path = f"{output_file_name}.{output_format}"
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'wb') as f_out:
                f_out.write(audio_data)

        return audio_data

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        raise RuntimeError(f"Subprocess error: {error_message}")
    except PermissionError as pe:
        raise RuntimeError(f"Permission error: {str(pe)}")
    except Exception as ex:
        raise RuntimeError(f"Unexpected error: {str(ex)}")
    finally:
        # Clean up all temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file}: {str(e)}")