import asyncio

from aiogram import Dispatcher
from src.config import bot, logger
from src.handlers import (
    start_router,
    join2group_router,
    voice_router,
    admin_panel_router,
    add_sound_router,
    check_sounds_router,
    delete_sound_router,
    welcome_message_router,
    dynamic_buttons_router


)


async def main():
    dp = Dispatcher()
    dp.include_routers(
        start_router,
        join2group_router,
        voice_router,
        admin_panel_router,
        dynamic_buttons_router,
        add_sound_router,
        check_sounds_router,
        delete_sound_router,
        welcome_message_router,

    )
    r = await bot.get_me()
    logger.info(f"Бот запущен: https://t/me/{r.username}")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())