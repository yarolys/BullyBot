from aiogram import F, Router
from aiogram.types import Message


from src.utils.filter import AdminRoleFilter
from src.config import logger
from src.database.models.sound import Sound

router = Router()

@router.message(F.text == 'Посмотреть добавленные звуки', AdminRoleFilter())
@logger.catch
async def list_sounds(message: Message):
    sounds = await Sound.get_all_sounds()
    if not sounds:
        await message.answer("Пока что добавленных звуков нет.")
        return
    response = "\n".join([f"{sound.id}. {sound.name}" for sound in sounds])
    await message.answer(f"Доступные звуки:\n\n{response}") 
