from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.utils.filter import AdminRoleFilter
from src.database.models.sound import Sound  
from src.config import logger
from src.utils.keyboard.admin import del_audio_kb
router = Router()


async def get_sounds_keyboard():
    sounds = await Sound.get_all_sounds() 
    if not sounds:
        return None

    buttons = [
        [InlineKeyboardButton(text=sound.name, callback_data=f"delete_sound_{sound.id}")]
        for sound in sounds
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == 'Меню удаления звука', AdminRoleFilter())
@logger.catch
async def delete_prompts_workflow(message: Message):
    await message.answer(
        'Работа с удалением звука',
        reply_markup=del_audio_kb
    )
    await message.delete()


@router.message(F.text == "Удалить звук", AdminRoleFilter())
async def show_sounds_for_deletion(message: Message):
    keyboard = await get_sounds_keyboard()
    if not keyboard:
        await message.answer("Нет доступных звуков для удаления.")
        return

    await message.answer("Выберите звук для удаления:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("delete_sound_"), AdminRoleFilter())
async def delete_sound(callback: CallbackQuery):
    sound_id = int(callback.data.split("_")[-1])  
    await Sound.delete_sound(sound_id)  


    new_keyboard = await get_sounds_keyboard()
    if new_keyboard:
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    else:
        await callback.message.edit_text("Все звуки удалены.")
    
    await callback.answer("Звук удалён.")