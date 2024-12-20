from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.schemas import ButtonTypeEnum as BTE
from src.database.models import DbButton, DbSound

# Админская панель
admin_panel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Посмотреть приветственное сообщение')],
        [KeyboardButton(text='Изменить приветственное сообщение')],
        [KeyboardButton(text='Просмотреть добавленные звуки')],
        [KeyboardButton(text='Добавить новый звук'), KeyboardButton(text='Меню удаления звука')],
        [KeyboardButton(text='Посмотреть кнопки')],
        [KeyboardButton(text='Статические кнопки'), KeyboardButton(text='Динамические кнопки')],
    ],
    resize_keyboard=True
)

working_with_buttons_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='Получить список всех кнопок')],
        [KeyboardButton(text='Удалить лишние кнопки'),
         KeyboardButton(text='Добавить новую кнопку')],
        [KeyboardButton(text='Вернуться в меню')]
    ]
)

add_audio_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Просмотреть добавленные звуки')],
        [KeyboardButton(text='Добавить звук')],
        [KeyboardButton(text='Вернуться в меню')]
    ],
    resize_keyboard=True
)


del_audio_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Просмотреть добавленные звуки')],
        [KeyboardButton(text='Удалить звук')],
        [KeyboardButton(text='Вернуться в меню')]
    ],
    resize_keyboard=True
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Вернуться в меню')]
    ],
    resize_keyboard=True
)

# Получение кнопок
async def get_buttons_kb(static: bool = False, dynamic: bool = False) -> InlineKeyboardMarkup | None:
    if not (static or dynamic):
        return None

    buttons = await DbButton.get_all_buttons()
    if not buttons:
        return None

    keyboard = InlineKeyboardMarkup()
    for kb_button in buttons:
        if static and kb_button.type == BTE.static:
            keyboard.add(InlineKeyboardButton(text=kb_button.name, url=str(kb_button.url)))
        if dynamic and kb_button.type == BTE.dynamic:
            keyboard.add(InlineKeyboardButton(text=kb_button.name, url=str(kb_button.url)))

    return keyboard if keyboard.inline_keyboard else None


async def get_buttons_for_delete(static: bool = False, dynamic: bool = False):
    buttons = await DbButton.get_all_buttons()
    keyboard = InlineKeyboardBuilder()
    if not (static or dynamic):
        return None
    if static:
        for kb_button in buttons:
            if kb_button.type == BTE.static:
                keyboard.button(text=kb_button.name, callback_data=str(kb_button.id))
    if dynamic:
        for kb_button in buttons:
            if kb_button.type == BTE.dynamic:
                keyboard.button(text=kb_button.name, callback_data=str(kb_button.id))
    if not buttons:
        return None
    keyboard.adjust(1)
    return keyboard.as_markup()

async def get_prompts_for_delete():
    buttons = await DbSound.get_all_sounds()  
    if not buttons: 
        return None

    keyboard = InlineKeyboardBuilder()  
    for kb_button in buttons:
        keyboard.button(text=kb_button.name, callback_data=str(kb_button.id))
    if not keyboard.inline_keyboard:
        return None
    keyboard.adjust(1)
    return keyboard.as_markup()


async def handle_delete_prompts(callback: types.CallbackQuery):
    button_id = callback.data.split("_")[-1]  
    await DbButton.delete_button(button_id)  
    await callback.answer(f"Кнопка с ID {button_id} была удалена.")  

    keyboard = await get_prompts_for_delete()  
    if keyboard and keyboard.inline_keyboard:  
        await callback.message.edit_text("Выберите кнопку для удаления:", reply_markup=keyboard)
    else:  
        await callback.message.edit_text("Нет кнопок для удаления.")