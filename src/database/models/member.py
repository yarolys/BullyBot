from sqlalchemy import BigInteger, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, mapped_column
from src.database.connection import Base, async_session_maker


class ChatMember(Base):
    __tablename__ = 'chat_members'
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(index=True)

    @classmethod
    async def remember(cls, chat_id, user):
        async with async_session_maker() as session:
            query = insert(cls).values(chat_id=chat_id, user_id=user.id,
                                       username=user.username.lower() if user.username else None)
            await session.execute(query.on_conflict_do_update(
                index_elements=[cls.chat_id, cls.user_id],
                set_={'username': query.excluded.username}))
            await session.commit()

    @classmethod
    async def resolve(cls, chat_id, username):
        async with async_session_maker() as session:
            ids = (await session.execute(select(cls.user_id).where(
                cls.chat_id == chat_id, cls.username == username.lstrip('@').lower()
            ))).scalars().all()
            return ids[0] if len(ids) == 1 else None
