from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_panel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Посмотреть приветственное сообщение')],
        [KeyboardButton(text='Изменить приветственное сообщение')],
        [KeyboardButton(text='Добавить новый звук')],
        [KeyboardButton(text='Удалить звук')],
    ],
    resize_keyboard=True)

add_audio_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить статический звук')],
        [KeyboardButton(text='Добавить динамический звук')],
        [KeyboardButton(text='Вернуться в меню')]
    ],
    resize_keyboard=True)

del_audio_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Удалить статический звук')],
        [KeyboardButton(text='Удалить динамический звук')],
        [KeyboardButton(text='Вернуться в меню')]
    ],
    resize_keyboard=True)
