from aiogram import Router, F
from aiogram.types import Message
from src.config import bot
import speech_recognition as sr
from pydub import AudioSegment
import os
from src.handlers.audio.celery_cfg import process_voice_task

r = sr.Recognizer()
router = Router()


@router.message(F.voice)
async def converting_voice_to_text(message: Message):

    download_dir = 'downloads/'
    os.makedirs(download_dir, exist_ok=True)


    file_name = os.path.join(download_dir, f"{message.voice.file_id}.ogg")

    voice = await bot.get_file(message.voice.file_id)
    file_path = voice.file_path
    await bot.download_file(file_path, file_name)

    task = process_voice_task.apply_async(args=[file_name])
    await message.answer("Ваша аудиозапись обрабатывается...")

    result = task.get(timeout=30)

    if result['status'] == 'success':
        await message.answer(f"Текст: {result['text']}")
    else:
        await message.answer(f"Ошибка: {result['error']}")