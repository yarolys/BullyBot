from sqlalchemy import select, delete, update
from sqlalchemy.orm import Mapped, mapped_column
from src.database.connection import Base, async_session_maker
from src.schemas import SoundSchema


class Sound(Base):
    __tablename__ = 'sounds'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    file_id: Mapped[str] = mapped_column(nullable=False)  

    @classmethod
    async def add_sound(cls, name: str, file_id: str) -> SoundSchema:
        """
        Добавляет новый звук в базу данных.

        Parameters:
        ----------
        name : str
            Название звука.
        file_id : str
            ID файла звука.

        Returns:
        -------
        SoundSchema
            Объект, представляющий добавленный звук.
        """
        async with async_session_maker() as session:
            new_sound = cls(name=name, file_id=file_id)
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
    async def update_sound(cls, sound_id: int, new_name: str = None, new_file_id: str = None):
        """
        Обновляет информацию о звуке.

        Parameters:
        ----------
        sound_id : int
            ID звука.
        new_name : str, optional
            Новое название звука.
        new_file_id : str, optional
            Новый ID файла звука.

        Notes:
        -----
        Обновляет только те поля, которые переданы.
        """
        async with async_session_maker() as session:
            query = update(cls).where(cls.id == sound_id)
            if new_name:
                query = query.values(name=new_name)
            if new_file_id:
                query = query.values(file_id=new_file_id)
            await session.execute(query)
            await session.commit()


    @classmethod
    async def get_sound_by_file_id(cls, file_id: str) -> SoundSchema | None:
        """
        Получает звук по file_id.

        Parameters:
        ----------
        file_id : str
            ID файла звука.

        Returns:
        -------
        SoundSchema | None
            Объект, представляющий звук, или None, если звук не найден.
        """
        async with async_session_maker() as session:
            sound = (await session.execute(
                select(cls).where(cls.file_id == file_id)
            )).scalar_one_or_none()
            return SoundSchema.model_validate(sound) if sound else None
    

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