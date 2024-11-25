from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from src.config import BOT_ADMIN_ID

router = Router()

@router.message(Command('start'), F.chat.type == 'private')
async def start(message: Message):
    await message.answer(
        'Привет.\nЭтот бот был создан исключительно для баловницы ее высочества - Булгиты: @Ms_Bobby.\n'
        'Этот бот поддерживает перевод твоего ГС в текстовое сообщение, а так же кнопочки - прикольчики.\n'
        'Если хочешь его попробовать, пиши вот сюда: @KandyBobby'
    )
    if message.from_user.id == BOT_ADMIN_ID:
        await message.answer('Для запуска админки нажми /admin')

    await message.delete()