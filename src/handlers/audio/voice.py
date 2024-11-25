from aiogram import Router, F
from aiogram.types import Message
from src.config import bot
import speech_recognition as sr
from pydub import AudioSegment
import os

r = sr.Recognizer()
router = Router()

@router.message(F.voice)
async def converting_voice_to_text(message: Message):

    file_name = f'{message.voice.file_id}.ogg'
    await bot.download(message.voice.file_id, file_name)

    try:
        audio = AudioSegment.from_ogg(file_name)
        wav_file_name = file_name.replace('.ogg', '.wav')
        audio.export(wav_file_name, format="wav")
    except Exception as e:
        await message.answer(f"Ошибка при конвертации аудио: {e}")
        return

    with sr.AudioFile(wav_file_name) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio, language='ru-RU')
        await message.answer(f"Текст: {text}")
    except sr.UnknownValueError:
        await message.answer("Не удалось распознать речь.")
    except sr.RequestError as e:
        await message.answer(f"Ошибка при обращении к сервису распознавания: {e}")

    os.remove(file_name)
    os.remove(wav_file_name)