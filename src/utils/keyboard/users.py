from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


users_kb = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text='Просмотреть добавленные звуки')],
    [KeyboardButton(text='Добавить звук')]
    ],
    resize_keyboard=True
)
users_menu = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text='Вернуться обратно')]
    ],
    resize_keyboard=True
)


