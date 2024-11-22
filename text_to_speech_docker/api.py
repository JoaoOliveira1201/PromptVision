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

def synthesize(text, model_path, output_file_name=None, speaker_id=None, output_format='wav', use_cuda=True):
    """
    Synthesizes speech from the given text.

    :param use_cuda: Use CUDA for synthesis (default: True)
    :param text: The input text to synthesize
    :param model_path: Path to the Piper voice model (.onnx file)
    :param output_file_name: Optional path to save the output audio file
    :param speaker_id: Optional speaker ID for multi-speaker models
    :param output_format: Output audio format, 'wav' or 'mp3' (default 'wav')
    :return: The synthesized audio data as bytes
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_wav_file:
        cmd = [
            'python3',                # Use Python to run Piper
            '-m', 'piper',            # Invoke Piper as a module
            '--model', model_path,
            '--output_file', tmp_wav_file.name
        ]
        if use_cuda:
            cmd.append('--cuda')
        if speaker_id is not None:
            cmd.extend(['--speaker', str(speaker_id)])
        try:
            # Run the Piper command
            process = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            # Read the WAV audio data
            with open(tmp_wav_file.name, 'rb') as f:
                wav_data = f.read()

            # Convert to MP3 if requested
            if output_format.lower() == 'mp3':
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_mp3_file:
                    ffmpeg_cmd = [
                        'ffmpeg',
                        '-y',  # Overwrite output file if it exists
                        '-i', tmp_wav_file.name,
                        '-f', 'mp3',
                        tmp_mp3_file.name
                    ]
                    # Run the FFmpeg command to convert WAV to MP3
                    subprocess.run(
                        ffmpeg_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True
                    )
                    # Read the MP3 audio data
                    with open(tmp_mp3_file.name, 'rb') as f_mp3:
                        audio_data = f_mp3.read()
                # Remove the temporary MP3 file
                os.unlink(tmp_mp3_file.name)
            elif output_format.lower() == 'wav':
                audio_data = wav_data
            else:
                raise ValueError("Invalid output_format. Choose 'wav' or 'mp3'.")

        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise RuntimeError(f"Subprocess error: {error_message}")
        except PermissionError as pe:
            raise RuntimeError(f"Permission error: {str(pe)}")
        except Exception as ex:
            raise RuntimeError(f"Unexpected error: {str(ex)}")
        finally:
            # Remove the temporary WAV file
            if os.path.exists(tmp_wav_file.name):
                os.unlink(tmp_wav_file.name)

        # Save the audio data to the output file if provided
        if output_file_name:
            output_path = f"{output_file_name}.{output_format}"
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'wb') as f_out:
                f_out.write(audio_data)

        return audio_data
