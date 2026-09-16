import asyncio
import os
from logging.config import fileConfig
from dotenv import load_dotenv
from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from src.database.connection import Base
from src.database import models
from src.database.models.member import ChatMember

load_dotenv()
config = context.config
url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_URL')
if not url:
    raise RuntimeError('Укажи DATABASE_URL или SQLALCHEMY_URL')
config.set_main_option('sqlalchemy.url', url.replace('%', '%%'))
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def migrate(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def online():
    engine = async_engine_from_config(config.get_section(config.config_ini_section),
                                     prefix='sqlalchemy.', poolclass=pool.NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(migrate)
    await engine.dispose()


if context.is_offline_mode():
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(online())
