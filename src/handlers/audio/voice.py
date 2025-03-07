from aiogram import Router, F
from aiogram.types import Message
from src.handlers.audio.celery_cfg import process_voice_task, handle_task_result

router = Router()

@router.message(F.voice)
async def converting_voice_to_text(message: Message):
    file_id = message.voice.file_id
    chat_id = message.chat.id
    process_voice_task.apply_async(args=[file_id, chat_id], link=handle_task_result.s())
    await message.answer("Ваше голосовое сообщение обрабатывается...")
