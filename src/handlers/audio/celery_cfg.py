import os
import subprocess
import speech_recognition as sr
from celery import Celery
import requests
from loguru import logger


app = Celery('audio_recognition', broker='redis://localhost:6379/0')
app.conf.result_backend = 'redis://localhost:6379/0'


TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise ValueError("TOKEN не установлен в переменных окружения")

@app.task
def process_voice_task(file_id: str, chat_id: int):

    file_info_url = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"
    try:
        file_info_response = requests.get(file_info_url)
        file_info = file_info_response.json()
        logger.info(f"File info: {file_info}")

        if not file_info.get('ok'):
            return {'status': 'error', 'error': 'Не удалось получить информацию о файле.'}

        file_path = file_info['result']['file_path']
        logger.info(f"File path: {file_path}")

        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

        file_name = f"{file_id}.ogg"
        wav_file_name = f"{file_id}.wav"

        response = requests.get(file_url)
        response.raise_for_status()  
        with open(file_name, "wb") as f:
            f.write(response.content)

        subprocess.call(['ffmpeg', '-i', file_name, wav_file_name], stderr=subprocess.PIPE)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file_name) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language='ru-RU')

        return {'status': 'success', 'text': text, 'chat_id': chat_id}


    except requests.exceptions.RequestException as e:

        logger.error(f"Ошибка при скачивании файла: {e}")
        return {'status': 'error', 'error': f"Ошибка при скачивания файла: {e}"}


    except subprocess.CalledProcessError as e:

        logger.error(f"Ошибка при конвертации файла: {e}")
        return {'status': 'error', 'error': f"Ошибка при конвертации файла: {e}"}


    except sr.UnknownValueError:

        logger.error("Не удалось распознать речь.")
        return {'status': 'error', 'error': "Не удалось распознать речь.", 'chat_id': chat_id}


    except sr.RequestError as e:

        logger.error(f"Ошибка при обращении к сервису распознавания: {e}")
        return {'status': 'error', 'error': f"Ошибка при обращении к сервису распознавания: {e}", 'chat_id': chat_id}


    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
        if os.path.exists(wav_file_name):
            os.remove(wav_file_name)


@app.task

def handle_task_result(result: dict):
    if result['status'] == 'success':
        text = result['text']
        chat_id = result['chat_id']
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={'chat_id': chat_id, 'text': f"Распознанный текст: {text}"}
        )

    else:
        error = result['error']
        chat_id = result['chat_id']
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={'chat_id': chat_id, 'text': f"Ошибка: {error}"}
        )