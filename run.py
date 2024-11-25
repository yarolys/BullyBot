import asyncio

from aiogram import Dispatcher
from src.config import bot, logger
from src.handlers.start import router as start_router
from src.handlers.audio.voice import router as voice_router


async def main():
    dp = Dispatcher()
    dp.include_routers(
        start_router,
        voice_router
    )
    r = await bot.get_me()
    logger.info(f"Бот запущен: https://t/me/{r.username}")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())