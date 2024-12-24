import os
import logging  # loguru
from celery import Celery
import speech_recognition as sr
from pydub import AudioSegment

logging.basicConfig(level=logging.DEBUG)

redis_broker = os.getenv('REDIS_BROKER', 'redis://localhost:6379/0')
redis_backend = os.getenv('REDIS_BACKEND', 'redis://localhost:6379/0')

app = Celery('audio_recognition', broker=redis_broker)
app.conf.result_backend = redis_backend

app.conf.update(
    broker_connection_retry_on_startup=True
)

@app.task
def process_voice_task(file_id: str):
    logging.debug(f"Обработка файла: {file_id}")


    file_name = os.path.abspath(file_id)
    logging.debug(f"Путь к файлу: {file_name}")


    if not os.path.exists(file_name):
        logging.error(f"Файл не найден: {file_name}")
        return {'status': 'error', 'error': f"Файл не найден: {file_name}"}

    try:

        audio = AudioSegment.from_ogg(file_name)
        wav_file_name = file_name.replace('.ogg', '.wav')
        audio.export(wav_file_name, format="wav")
        logging.debug(f"Конвертация в WAV успешна: {wav_file_name}")
    except Exception as e:
        logging.error(f"Ошибка при конвертации: {e}")
        return {'status': 'error', 'error': f"Ошибка при конвертации аудио: {e}"}


    r = sr.Recognizer()
    with sr.AudioFile(wav_file_name) as source:
        audio = r.record(source)

    try:

        text = r.recognize_google(audio, language='ru-RU')
        os.remove(file_name)
        os.remove(wav_file_name)
        logging.debug(f"Распознавание успешно: {text}")
        return {'status': 'success', 'text': text}
    except sr.UnknownValueError:
        os.remove(file_name)
        os.remove(wav_file_name)
        logging.error("Не удалось распознать речь")
        return {'status': 'error', 'error': "Не удалось распознать речь."}
    except sr.RequestError as e:
        os.remove(file_name)
        os.remove(wav_file_name)
        logging.error(f"Ошибка при обращении к сервису распознавания: {e}")
        return {'status': 'error', 'error': f"Ошибка при обращении к сервису распознавания: {e}"}