import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import SimpleEventIsolation
from src.database.connection import engine
from src.handlers.moderation import router as moderation_router, GroupMiddleware
from src.config import bot, logger
from src.handlers import (
    start_router,
    user_panel_router,
    join2group_router,
    voice_router,
    admin_panel_router,
    add_sound_router,
    check_sounds_router,
    delete_sound_router,
    welcome_message_router,
    dynamic_buttons_router,
    static_buttons_router


)


async def main():
    dp = Dispatcher(events_isolation=SimpleEventIsolation())
    dp.message.outer_middleware(GroupMiddleware())
    dp.include_routers(
        moderation_router,
        start_router,
        user_panel_router,
        join2group_router,
        admin_panel_router,
        dynamic_buttons_router,
        static_buttons_router,
        add_sound_router,
        check_sounds_router,
        delete_sound_router,
        welcome_message_router,
        voice_router,

    )
    r = await bot.get_me()
    logger.info(f"Бот запущен: https://t.me/{r.username}")
    try:
        await dp.start_polling(bot)
    finally:
        await engine.dispose()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())