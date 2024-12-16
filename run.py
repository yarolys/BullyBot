import asyncio

from aiogram import Dispatcher
from src.config import bot, logger
from src.handlers import (
    start_router,
    join2group_router,
    voice_router,
    admin_panel_router,
    add_new_button_router,
    check_add_buttons_router,
    delete_button_router,
    welcome_message_router


)


async def main():
    dp = Dispatcher()
    dp.include_routers(
        start_router,
        join2group_router,
        voice_router,
        admin_panel_router,
        add_new_button_router,
        check_add_buttons_router,
        delete_button_router,
        welcome_message_router

    )
    r = await bot.get_me()
    logger.info(f"Бот запущен: https://t/me/{r.username}")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())