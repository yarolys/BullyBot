from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


user_panel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Пукнуть')],
        [KeyboardButton(text='Пукнуть жидко...')],
        [KeyboardButton(text='Пукнуть очень страшно .О.')],
        [KeyboardButton(text='Н... Не пукать???')]
    ],
    resize_keyboard=True)
