from sqlalchemy import select, delete, update, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column
from src.database.connection import Base, async_session_maker
from src.schemas import SoundSchema


class Sound(Base):
    __tablename__ = 'sounds'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    file_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)


    @classmethod
    async def add_sound(cls, name: str, file_data: bytes) -> SoundSchema:
        """
        Добавляет новый звук в базу данных.

        Parameters:
        ----------
        name : str
            Название звука.
        file_data : bytes
            Данные файла звука.

        Returns:
        -------
        SoundSchema
            Объект, представляющий добавленный звук.
        """
        async with async_session_maker() as session:
            new_sound = cls(name=name, file_data=file_data)
            session.add(new_sound)
            await session.commit()
            await session.refresh(new_sound)
            return SoundSchema.model_validate(new_sound)


    @classmethod
    async def get_all_sounds(cls) -> list[SoundSchema]:
        """
        Получает все звуки из базы данных.

        Returns:
        -------
        list[SoundSchema]
            Список объектов, представляющих звуки.
        """
        async with async_session_maker() as session:
            sounds = (await session.execute(select(cls))).scalars().all()
            return [SoundSchema.model_validate(sound) for sound in sounds] if sounds else []


    @classmethod
    async def get_sound_by_name(cls, name: str) -> SoundSchema | None:
        """
        Получает звук по названию.

        Parameters:
        ----------
        name : str
            Название звука.

        Returns:
        -------
        SoundSchema | None
            Объект, представляющий звук, или None, если звук не найден.
        """
        async with async_session_maker() as session:
            sound = (await session.execute(
                select(cls).where(cls.name == name)
            )).scalar_one_or_none()
            return SoundSchema.model_validate(sound) if sound else None
        
    @classmethod
    async def update_sound(cls, sound_id: int, new_name: str = None, new_file_data: bytes = None):
        """
        Обновляет информацию о звуке.

        Parameters:
        ----------
        sound_id : int
            ID звука.
        new_name : str, optional
            Новое название звука.
        new_file_data : bytes, optional
            Новые данные звука.

        Notes:
        -----
        Обновляет только те поля, которые переданы.
        """
        async with async_session_maker() as session:
            query = update(cls).where(cls.id == sound_id)
            if new_name:
                query = query.values(name=new_name)
            if new_file_data:
                query = query.values(file_data=new_file_data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_sound(cls, sound_id: int):
        """
        Удаляет звук из базы данных.

        Parameters:
        ----------
        sound_id : int
            ID звука.
        """
        async with async_session_maker() as session:
            await session.execute(delete(cls).where(cls.id == sound_id))
            await session.commit()