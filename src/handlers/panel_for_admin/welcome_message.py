from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.config import BOT_ADMIN_ID
from src.states.admin import FSM_admin_panel
from src.utils.keyboard.join2group import welcome_keyboard
from src.utils.welcome_message import configure_welcome_message

from src.database.models import DbSettings

router = Router()

@router.message(F.text == 'Посмотреть приветственное сообщение')
async def get_welcome_message(message: Message, state: FSMContext):
    if message.from_user.id != BOT_ADMIN_ID:
        await message.answer('Только для администратора')
        await message.delete()
        return
    welcome_message = await configure_welcome_message(
        user_full_name=message.from_user.full_name,
        username=message.from_user.username,
        user_id=message.from_user.id,
    )
    if welcome_message:
        await message.answer(
            text=welcome_message,
            reply_markup=(await welcome_keyboard()),
        )
    await message.delete()
    await state.clear()


@router.message(F.text == 'Изменить приветственное сообщение')
async def edit_welcome_message(message: Message, state: FSMContext):
    if message.from_user.id != BOT_ADMIN_ID:
        await message.answer('Только для администратора')
        await message.delete()
        return
    await message.answer(
        'Отправь мне текст для сообщения, можешь использовать встроенное форматирование от ТГ\n\n'
        'Чтобы я понял, куда поставить имя пользователя и username используй:\n\n'
        '<b>{{NAME}}</b> и <b>{{USERNAME}}</b>',
    )
    await message.delete()
    await state.set_state(FSM_admin_panel.get_message)


@router.message(FSM_admin_panel.get_message)
async def get_message(message: Message, state: FSMContext):
    await DbSettings.set_settings(welcome_message=message.html_text)
    await message.answer('Текст для приветственного сообщения установлен')
    await state.clear()
        