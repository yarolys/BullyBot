from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from src.schemas import ButtonTypeEnum as BTE
from src.schemas import PromptTypeEnum as PTE
from src.database.models import DbButton, DbSound

# Админская панель
admin_panel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Посмотреть приветственное сообщение')],
        [KeyboardButton(text='Изменить приветственное сообщение')],
        [KeyboardButton(text='Просмотреть добавленные звуки')],
        [KeyboardButton(text='Добавить новый звук'),
        KeyboardButton(text='Меню удаления звуков')],
    ],
    resize_keyboard=True
)

# Меню добавления аудио
add_audio_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Посмотреть добавленные звуки')],
        [KeyboardButton(text='Добавить статический звук'),
        KeyboardButton(text='Добавить динамический звук')],
        [KeyboardButton(text='Вернуться в меню')]
    ],
    resize_keyboard=True
)

# Меню удаления аудио
del_audio_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Посмотреть добавленные звуки')],
        [KeyboardButton(text='Удалить звук')],
        [KeyboardButton(text='Вернуться в меню')]
    ],
    resize_keyboard=True
)

# Главное меню
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

# Получение подсказок для удаления
async def get_prompts_for_delete(static: bool = False, dynamic: bool = False) -> InlineKeyboardMarkup | None:
    if not (static or dynamic):
        return None

    prompts = await DbSound.get_all_prompts()
    if not prompts:
        return None

    keyboard = InlineKeyboardMarkup()
    for prompt in prompts:
        if static and prompt.type == PTE.static:
            keyboard.add(InlineKeyboardButton(
                text=f"Удалить {prompt.name}",
                callback_data=f"delete_prompt_{prompt.id}"
            ))
        if dynamic and prompt.type == PTE.dynamic:
            keyboard.add(InlineKeyboardButton(
                text=f"Удалить {prompt.name}",
                callback_data=f"delete_prompt_{prompt.id}"
            ))

    return keyboard if keyboard.inline_keyboard else None

# Получение кнопок для удаления
async def get_buttons_for_delete(static: bool = False, dynamic: bool = False) -> InlineKeyboardMarkup | None:
    if not (static or dynamic):
        return None

    buttons = await DbButton.get_all_buttons()
    if not buttons:
        return None

    keyboard = InlineKeyboardMarkup()
    for kb_button in buttons:
        if static and kb_button.type == BTE.static:
            keyboard.add(InlineKeyboardButton(
                text=f"Удалить {kb_button.name}",
                callback_data=f"delete_{kb_button.id}"
            ))
        if dynamic and kb_button.type == BTE.dynamic:
            keyboard.add(InlineKeyboardButton(
                text=f"Удалить {kb_button.name}",
                callback_data=f"delete_{kb_button.id}"
            ))

    return keyboard if keyboard.inline_keyboard else None

# Обработчик удаления кнопки
async def handle_delete_button(callback: types.CallbackQuery):
    button_id = callback.data.split("_")[-1]
    await DbButton.delete_button(button_id)
    await callback.answer(f"Кнопка с ID {button_id} была удалена.")

    keyboard = await get_buttons_for_delete(static=True, dynamic=True)
    if keyboard and keyboard.inline_keyboard:
        await callback.message.edit_text("Выберите кнопку для удаления:", reply_markup=keyboard)
    else:
        await callback.message.edit_text("Нет кнопок для удаления.")
