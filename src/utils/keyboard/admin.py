from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_panel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить новый звук')],
        [KeyboardButton(text='Удалить звук')],
        [KeyboardButton(text='Посмотреть приветственное сообщение')],
        [KeyboardButton(text='Изменить приветственное сообщение')]
    ],
    resize_keyboard=True)