import asyncio
import aiohttp

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from src.utils.filter import AdminRoleFilter
from src.states.admin import FSM_DynamicButtons
from src.utils.keyboard.admin import get_buttons_for_delete, get_buttons_kb, \
working_with_buttons_kb, admin_panel_kb, main_menu
from src.utils.keyboard.join2group import welcome_keyboard
from src.database.models import DbButton
from src.config import logger
from src.schemas import ButtonTypeEnum as BTE


router = Router()


async def check_url_accesibility(url: str) -> bool:
    try:
        async with aiohttp.ClientSession as session:
            async with session.head(url, timeout=5) as response:
                if response.status < 400:
                    return True
                else:
                    return False
    except Exception as e:
        logger.error(f"Ошибка при проверке доступности URL: {e}")
        return False


@router.message(F.text == 'Динамические кнопки', AdminRoleFilter())
@logger.catch
async def dynamic_buttons(message: Message, state: FSMContext):
    await message.answer(
        'Работа с динамическими кнопками',
        reply_markup=working_with_buttons_kb
    )
    await message.delete()
    await state.set_state(FSM_DynamicButtons.working_with_buttons)




