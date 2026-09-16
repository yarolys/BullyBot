import asyncio
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from src.config import VOICE_RECOGNITION_ENABLED, logger
from src.handlers.audio.celery_cfg import process_voice_task, handle_task_result

router = Router()


@router.message(F.voice, StateFilter(None))
async def converting_voice_to_text(message: Message):
    if not VOICE_RECOGNITION_ENABLED:
        return
    if message.voice.duration > 120 or (message.voice.file_size or 0) > 20_000_000:
        await message.answer('Распознаю голосовые до 2 минут и 20 МБ.')
        return
    try:
        await asyncio.to_thread(process_voice_task.apply_async,
            args=[message.voice.file_id, message.chat.id], link=handle_task_result.s())
    except Exception as exc:
        logger.warning('Voice queue unavailable: {}', type(exc).__name__)
        await message.answer('Распознавание временно недоступно.')
        return
    await message.answer('Голосовое отправлено на распознавание...')
