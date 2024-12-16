from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery


from src.utils.filter import AdminRoleFilter
from src.states.admin import FSM_DynamicPrompt
from src.config import logger
from src.database.models.sound import Sound

from src.utils.keyboard.admin import admin_panel_kb, del_audio_kb

router = Router()


@router.message(F.text == 'Меню удаления звука', AdminRoleFilter())
@logger.catch
async def delete_prompts_workflow(message: Message):
    await message.answer(
        'Работа с удалением звука',
        reply_markup=del_audio_kb
    )
    await message.delete()

@router.message(F.text == 'Удалить звук', AdminRoleFilter())
@logger.catch
async def delete_sound_prompt(message: Message, state: FSMContext):
    sounds = await Sound.get_all_sounds()
    if not sounds:
        await message.answer("В БД пока нет звуков.")
        return
    
    buttons = [
        (sound.name, f"delete_sound:{sound.id}") for sound in sounds
    ]
    kb = del_audio_kb(buttons)
    await message.answer("Выберите звук для удаления:", reply_markup=kb)
    await state.set_state(FSM_DynamicPrompt.delete_prompt)


@router.callback_query(F.data.startswith('delete_sound:'), FSM_DynamicPrompt.delete_prompt)
@logger.catch
async def delete_sound(callback: CallbackQuery, state: FSMContext):
    sound_id = int(callback.data.split(":")[1])
    try:
        await Sound.delete_sound(sound_id)
        await callback.message.edit_text("Звук успешно удален!", reply_markup=admin_panel_kb)
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при удалении звука:{e}")
        await callback.message.answer("Произошла ошибка при удалении.")
    

