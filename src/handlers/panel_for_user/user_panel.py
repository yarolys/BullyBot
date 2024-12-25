from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.config import logger
from src.utils.keyboard.users import users_kb, users_menu
from src.states.admin import FSM_Prompt
from src.database.models import DbSound




router = Router()


@router.message(Command('user'))
@router.message(F.text == 'Вернуться обратно')
async def user_panel(message: Message, state: FSMContext):
    logger.debug(f'ID Пользователя: {message.from_user.id}')
    await state.clear()
    await message.answer(
        'Добро пожаловать в меню пользователя!',
        reply_markup=users_kb
    )

@router.message(F.text == 'Добавить звук!')
@logger.catch
async def add_new_sound_prompt(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, назовите ваш звук (не более 20 символов).",
        reply_markup=users_menu
    )
    await state.set_state(FSM_Prompt.get_prompt_name)


@router.message(F.text, FSM_Prompt.get_prompt_name)
@logger.catch
async def receive_sound_name(message: Message, state: FSMContext):
    sound_name = message.text
    if len(sound_name) > 20:
        await message.answer("Название звука не может превышать 20 символов. Попробуйте снова.")
        return
    
    existing_sound = await DbSound.get_sound_by_name(sound_name)
    if existing_sound:
        await message.answer(f"Звук с названием '{sound_name}' уже существует. Пожалуйста, выберите другое название.")
        return
    
    await state.update_data(sound_name=sound_name)
    await message.answer("Теперь отправь аудио файл.")
    await state.set_state(FSM_Prompt.get_prompt_file)


@router.message(F.audio | F.voice | F.document, FSM_Prompt.get_prompt_file)
@logger.catch
async def save_sound(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        sound_name = data.get("sound_name")
        file_id = message.audio.file_id if message.audio else \
                  message.voice.file_id if message.voice else \
                  message.document.file_id
        
        existing_sound_by_file = await DbSound.get_sound_by_file_id(file_id)
        if existing_sound_by_file:
            await message.answer("Этот звук уже добавлен в базу данных. Повторное добавление невозможно.")
            await state.clear()
            return
        

        await DbSound.add_sound(name=sound_name, file_id=file_id)
        await message.answer(f"Звук '{sound_name}' успешно добавлен!", reply_markup=users_menu)
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при сохранении звука: {e}")
        await message.answer("Произошла ошибка. Попробуйте снова.")
        await state.clear()


@router.callback_query(F.data.startswith("voice_"))
@logger.catch
async def send_voice(callback: CallbackQuery):
    sound_id = callback.data.split("voice_")[1]
    sound = await DbSound.get_sound_by_id(sound_id)
    if sound:
        await callback.message.answer_audio(sound.file_id)
    else:
        await callback.message.answer("Звук не найден.")