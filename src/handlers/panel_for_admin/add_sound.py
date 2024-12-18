import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.database.models import DbSound
from src.utils.filter import AdminRoleFilter
from src.states.admin import FSM_DynamicPrompt, FSM_StaticPrompt
from src.database.models import DbButton
from src.config import logger
from src.schemas import ButtonTypeEnum as BTE
from src.utils.keyboard.admin import add_audio_kb, admin_panel_kb, main_menu


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
    AdminRoleFilter(),
    F.text == 'Добавить динамический звук'
)
@logger.catch
async def add_new_sound_prompt(message: Message, state: FSMContext):
    await message.answer('Пожалуйста назовите ваш звук(не более 20 букв).',
                         reply_markup=main_menu)
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


@router.message(F.audio | F.voice | F.document, FSM_DynamicPrompt.get_prompt_file)
@logger.catch
async def save_sound(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        sound_name = data.get("sound_name")
        if message.audio:
            file_id = message.audio.file_id
        elif message.voice:
            file_id = message.voice.file_id
        elif message.document:
            file_id = message.document.file_id
        else:
            await message.answer("Не удалось распознать файл.")
            return

        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        file_bytes = await message.bot.download(file_path)
        file_content = file_bytes.read()
        await DbSound.add_sound(name=sound_name, file_data=file_content)
        await message.answer(f"Звук '{sound_name}' успешно добавлен в базу данных!", reply_markup=admin_panel_kb)

        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при сохранении звука в БД: {e}")
        await message.answer("Произошла ошибка при добавлении звука. Попробуйте еще раз.")
        await state.clear()

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
        await message.answer('Название кнопки не может превышать 20 букв. Попробуйте еще раз.')
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