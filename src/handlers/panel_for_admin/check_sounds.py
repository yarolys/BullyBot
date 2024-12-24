from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from src.config import logger
from src.database.models.sound import Sound

router = Router()

@router.message(F.text == 'Просмотреть добавленные звуки')
@logger.catch
async def list_sounds(message: Message):
    sounds = await Sound.get_all_sounds()
    if not sounds:
        await message.answer("Пока что добавленных звуков нет.")
        return

    # Создаем клавиатуру с кнопками в столбик
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=sound.name, callback_data=f"play_sound:{sound.name}")]
            for sound in sounds
        ]
    )

    await message.answer("Доступные звуки:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("play_sound"))
@logger.catch
async def play_sound(callback: CallbackQuery):
    sound_name = callback.data.split(":")[1]
    sound = await Sound.get_sound_by_name(sound_name)
    if not sound:
        await callback.message.answer("Не удалось найти звук.")
        return
    await callback.message.answer_audio(sound.file_id)
    await callback.answer()
