import os

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# 1. В докере используем DATABASE_URL (из docker-compose)
# 2. Для локальной разработки можно оставить SQLALCHEMY_URL как fallback
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL / SQLALCHEMY_URL не установлен")

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
metadata = MetaData()


class Base(DeclarativeBase):
    pass