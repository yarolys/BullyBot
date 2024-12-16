import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.database.models import DbSound
from src.utils.keyboard.admin import get_prompts_for_delete
from src.utils.filter import AdminRoleFilter
from src.states.admin import FSM_DynamicPrompt, FSM_StaticPrompt
from src.database.models import DbButton
from src.config import logger
from src.schemas import ButtonTypeEnum as BTE
from src.utils.keyboard.admin import add_audio_kb, admin_panel_kb


router = Router()





@router.message(F.text == 'Добавить новый звук', AdminRoleFilter())
@logger.catch
async def start_sound_workflow(message: Message):
    await message.answer(
        'Работа с добавлением аудио',
        reply_markup=add_audio_kb
    )
    await message.delete()




@router.message(
    F.text == 'Добавить динамический звук',
    FSM_DynamicPrompt.working_with_prompts,
    AdminRoleFilter()
)
@logger.catch
async def add_new_sound_prompt(message: Message, state: FSMContext):
    await message.answer('Пожалуйста назовите ваш звук(не более 20 букв).')
    await state.set_state(FSM_DynamicPrompt.get_prompt_name)


@router.message(F.text, FSM_DynamicPrompt.get_prompt_name)
@logger.catch
async def receive_sound_name(message: Message, state: FSMContext):
    sound_name = message.text
    
    if len(sound_name) > 20:
        await message.answer("Название звука не может превышать 20 символов. Попробуйте снова.")
        return
    
    await state.update_data(sound_name=sound_name)
    await message.answer("Теперь отправь аудио файл (не более 1 минуты).")
    await state.set_state(FSM_DynamicPrompt.get_prompt_file)


@router.message(F.audio, FSM_DynamicPrompt.get_prompt_file)
@logger.catch
async def save_sound(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        sound_name = data.get("sound_name")
        audio_file_id = message.audio.file_id

        file_data = await message.bot.download_file_by_id(audio_file_id)
        file_bytes = await file_data.read()

        await DbSound.add_sound(name=sound_name, file_data=file_bytes)

        await message.answer(f"Звук '{sound_name}'успешно добавлен!", reply_markup=admin_panel_kb)
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при сохранении звука: {e}")
        await message.answer("Произошла ошибка при добавлении звука. Попробуйте еще раз.")
        await state.clear()





@router.message(
    F.text == 'Удалить звук',
    FSM_DynamicPrompt.working_with_prompts,
    AdminRoleFilter()
)
@logger.catch
async def prepare_static_buttons(message: Message, state: FSMContext):
    r = await message.answer(
        'ВНИМАНИЕ!\n'
        'Любое нажатие на кнопку - удалит её\n\n'
        'Этот режим автоматически выключится через 15 секунд',
    )
    await asyncio.sleep(5)
    await r.delete()
    await state.set_state(FSM_DynamicPrompt.delete_prompt)
    r = await message.answer(
        'Удалить лишние кнопки',
        reply_markup=(await get_prompts_for_delete(dynamic=True))
    )
    await asyncio.sleep(15)
    await r.delete()
    await state.set_state(FSM_DynamicPrompt.working_with_prompts)
    await message.delete()


@router.callback_query(
    FSM_DynamicPrompt.delete_prompt,
    AdminRoleFilter()
)
@logger.catch
async def delete_static_prompt(qq: CallbackQuery):
    await DbSound.delete_prompt(int(qq.data))
    await qq.message.edit_reply_markup(
        reply_markup=(await get_prompts_for_delete(dynamic=True))
    )






@router.message(F.text == 'Добавить статический звук', AdminRoleFilter)
@logger.catch
async def add_static_button_prompt(message: Message, state: FSMContext):
    await message.answer('Введите название кнопки:')
    await state.set_state(FSM_StaticPrompt.get_prompt_name)

@router.message(F.text, FSM_StaticPrompt.get_prompt_name)
@logger.catch
async def receive_static_sound_name(message: Message, state: FSMContext):
    button_name = message.text
    if len(button_name) > 20:
        await message.answer('Название кнопки не может превышать 20 буква. Попробуйте еще раз.')
    await state.update_data(button_name=button_name)
    await message.answer("Теперь отправь аудиофайл не более 1 минуты")
    await state.set_state(FSM_StaticPrompt.get_prompt_text)

@router.message(F.audio, FSM_StaticPrompt.get_prompt_text)
@logger.catch
async def save_sound_button(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        button_name = data.get('button_name')
        audio_file_id = message.audio.file_id
        file_data = await message.bot.download_file_by_id(audio_file_id)
        file_bytes = await file_data.read()
        sound = await DbSound.add_sound(name=button_name, file_data=file_bytes)


        button_url = f"sound:{sound.id}"  
        await DbButton.add_button(name=button_name, url=button_url, type=BTE.static)
        await message.answer(f"Кнопка '{button_name}' с привязанным звуком успешно добавлена!", reply_markup=admin_panel_kb)
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при добавлении кнопки со звуком: {e}")
        await message.answer("Произошла ошибка при добавлении кнопки со звуком. Попробуйте снова.")
        await state.clear()