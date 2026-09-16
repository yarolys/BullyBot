import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger.add(
    'logs/log.log',
    format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
    level=os.getenv('LOG_LEVEL', 'INFO'),
    rotation='50MB'
)

TOKEN = os.getenv('TOKEN')
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode='HTML')
)
BOT_ADMIN_ID = int(os.getenv('BOT_ADMIN_ID'))
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_URL')

# The owner manages configuration; moderators only manage group members.
def parse_ids(value: str) -> frozenset[int]:
    return frozenset(int(item.strip()) for item in value.split(',') if item.strip())

MODERATOR_IDS = parse_ids(os.getenv('MODERATOR_IDS', '')) | {BOT_ADMIN_ID}
AUTO_MUTE_CHAT_IDS = parse_ids(os.getenv('AUTO_MUTE_CHAT_IDS', ''))
AUTO_MUTE_WORDS = frozenset(word.strip().casefold() for word in os.getenv('AUTO_MUTE_WORDS', '').split(',') if word.strip())
AUTO_MUTE_SECONDS = int(os.getenv('AUTO_MUTE_SECONDS', '600'))
if not 60 <= AUTO_MUTE_SECONDS <= 366 * 86400:
    raise ValueError('AUTO_MUTE_SECONDS должен быть от 60 до 31622400')
VOICE_RECOGNITION_ENABLED = os.getenv('VOICE_RECOGNITION_ENABLED', 'true').lower() == 'true'
