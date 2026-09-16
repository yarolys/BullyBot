from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from src.database.models.sound import Sound

router = Router()
PAGE_SIZE = 20


async def show_sounds(message, page=0):
    sounds = await Sound.get_all_sounds()
    page = min(max(0, page), max(0, (len(sounds) - 1) // PAGE_SIZE))
    rows = [[InlineKeyboardButton(text=s.name, callback_data=f'play_sound:{s.id}')]
            for s in sounds[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]]
    nav = []
    if page:
        nav.append(InlineKeyboardButton(text='←', callback_data=f'sounds_page:{page - 1}'))
    if (page + 1) * PAGE_SIZE < len(sounds):
        nav.append(InlineKeyboardButton(text='→', callback_data=f'sounds_page:{page + 1}'))
    if nav:
        rows.append(nav)
    await message.answer('Доступные звуки:' if sounds else 'Пока звуков нет.',
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=rows) if rows else None)


@router.message(Command('sounds'))
@router.message(F.text == 'Просмотреть добавленные звуки')
async def list_sounds(message: Message):
    await show_sounds(message)


@router.callback_query(F.data.regexp(r'^sounds_page:\d+$'))
async def page_sounds(callback: CallbackQuery):
    await callback.answer()
    if isinstance(callback.message, Message):
        await show_sounds(callback.message, int(callback.data.split(':')[1]))


@router.callback_query(F.data.regexp(r'^play_sound:\d+$'))
async def play_sound(callback: CallbackQuery):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return
    sound = await Sound.get_sound_by_id(int(callback.data.split(':')[1]))
    if not sound:
        await callback.message.answer('Звук уже удалён.')
        return
    send = {'voice': callback.message.answer_voice,
            'document': callback.message.answer_document}.get(sound.media_type, callback.message.answer_audio)
    try:
        await send(sound.file_id)
    except TelegramBadRequest:
        await callback.message.answer('Telegram не смог отправить файл. Для старого голосового удали запись и загрузи звук заново.')
