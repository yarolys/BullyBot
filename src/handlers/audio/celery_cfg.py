import os
import tempfile
import subprocess
from typing import Any, Dict

import requests
import speech_recognition as sr
from celery import Celery
from loguru import logger

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("audio_recognition", broker=REDIS_URL)
app.conf.update(result_backend=REDIS_URL, result_expires=3600,
                broker_connection_timeout=5, task_publish_retry=False,
                task_soft_time_limit=120, task_time_limit=150)

PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")
TELEGRAM_PROXIES = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else {}

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не установлен в переменных окружения")


def send_telegram_message(chat_id: int, text: str) -> None:
    """Отправка сообщения в Telegram с логированием ошибок."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10, proxies=TELEGRAM_PROXIES)
        if not resp.ok:
            logger.error(
                "Не удалось отправить сообщение в Telegram. "
                f"status={resp.status_code}, body={resp.text}"
            )
    except requests.RequestException as e:
        logger.error(f"Ошибка сети при отправке сообщения в Telegram: {type(e).__name__}")


def get_telegram_file_path(file_id: str) -> str:
    """Возвращает file_path для voice-файла в Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/getFile"
    try:
        resp = requests.get(url, params={"file_id": file_id}, timeout=10, proxies=TELEGRAM_PROXIES)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе getFile: {type(e).__name__}")
        raise

    data = resp.json()
    logger.info(f"File info: {data}")

    if not data.get("ok") or "result" not in data or "file_path" not in data["result"]:
        raise RuntimeError("Не удалось получить информацию о файле от Telegram")

    return data["result"]["file_path"]


def download_telegram_file(file_path: str) -> str:
    """Скачивает файл Telegram во временный .ogg и возвращает путь к нему."""
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    try:
        resp = requests.get(file_url, timeout=30, proxies=TELEGRAM_PROXIES)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Ошибка при скачивании файла: {type(e).__name__}")
        raise

    tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    tmp.write(resp.content)
    tmp.close()
    logger.info(f"Файл скачан во временный путь: {tmp.name}")
    return tmp.name


def convert_ogg_to_wav(src_path: str) -> str:
    """Конвертация .ogg → .wav через ffmpeg, возвращает путь к .wav."""
    dst_fd, dst_path = tempfile.mkstemp(suffix=".wav")
    os.close(dst_fd)  # дескриптор больше не нужен

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", src_path, dst_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True, timeout=60,
        )
    except (subprocess.SubprocessError, OSError) as e:
        logger.error(f"Ошибка при конвертации файла ffmpeg: {type(e).__name__}")
        # удаляем пустой/битый wav
        if os.path.exists(dst_path):
            os.remove(dst_path)
        raise

    logger.info(f"Файл конвертирован в WAV: {dst_path}")
    return dst_path


def recognize_speech_from_wav(wav_path: str, language: str = "ru-RU") -> str:
    """Распознаёт речь из wav-файла с помощью speech_recognition."""
    recognizer = sr.Recognizer()
    recognizer.operation_timeout = 30
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)

    return recognizer.recognize_google(audio, language=language) # noqa


@app.task
def process_voice_task(file_id: str, chat_id: int) -> Dict[str, Any]:
    """
    Основная задача:
    1. Получить путь к файлу в Telegram.
    2. Скачать .ogg.
    3. Конвертировать в .wav.
    4. Распознать текст.
    """
    ogg_path: str | None = None
    wav_path: str | None = None

    try:
        file_path = get_telegram_file_path(file_id)
        logger.info(f"File path: {file_path}")

        ogg_path = download_telegram_file(file_path)
        wav_path = convert_ogg_to_wav(ogg_path)
        text = recognize_speech_from_wav(wav_path, language="ru-RU")

        return {"status": "success", "text": text, "chat_id": chat_id}

    except sr.UnknownValueError:
        logger.error("Не удалось распознать речь.")
        return {
            "status": "error",
            "error": "Не удалось распознать речь.",
            "chat_id": chat_id,
        }

    except sr.RequestError as e:
        logger.error(f"Ошибка при обращении к сервису распознавания: {type(e).__name__}")
        return {
            "status": "error",
            "error": f"Ошибка при обращении к сервису распознавания: {type(e).__name__}",
            "chat_id": chat_id,
        }

    except Exception as e:
        # всё остальное: сеть, ffmpeg, JSON, etc.
        logger.exception(f"Необработанная ошибка при обработке voice: {type(e).__name__}")
        return {
            "status": "error",
            "error": f"Внутренняя ошибка при обработке аудио: {type(e).__name__}",
            "chat_id": chat_id,
        }

    finally:
        # Чистим временные файлы, если они создавались
        for path in (ogg_path, wav_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as e:
                    logger.warning(f"Не удалось удалить временный файл {path}: {type(e).__name__}")


@app.task
def handle_task_result(result: Dict[str, Any]) -> None:
    """Отправка результата распознавания в Telegram."""
    status = result.get("status")
    chat_id = result.get("chat_id")

    if chat_id is None:
        logger.error(f"В result нет chat_id: {result}")
        return

    if status == "success":
        text = result.get("text", "")
        send_telegram_message(chat_id, f"Распознанный текст: {text}")
    else:
        error = result.get("error", "Неизвестная ошибка.")
        send_telegram_message(chat_id, f"Ошибка: {error}")