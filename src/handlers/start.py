from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from src.database.models import DbUser
from src.config import BOT_ADMIN_ID, logger


router = Router()

@router.message(Command('start'), F.chat.type == 'private')
async def start(message: Message):
    if not await DbUser.get_user(user_id=message.from_user.id):
        await DbUser.add_user(
            user_id=message.from_user.id,
            full_name=message.from_user.first_name
        )
        logger.debug(
            f'Пользователь({message.from_user.full_name}) с id: {message.from_user.id} добавлен в базу данных')
            
    await message.answer(
        'Привет.\nЭтот бот был создан исключительно для баловницы ее высочества - Булгиты: @Ms_Bobby.\n'
        'Этот бот поддерживает перевод твоего ГС в текстовое сообщение, а так же кнопочки - прикольчики.\n'
        'Если хочешь его попробовать, пиши вот сюда: @KandyBobby'
    )
    if message.from_user.id == BOT_ADMIN_ID:
        await message.answer('Для запуска админки нажми /admin')
    else:
        await message.answer('Для запуска пользовательского интерфейса, нажми /user')
    await message.delete()