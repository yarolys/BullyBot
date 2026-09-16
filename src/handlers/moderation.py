from datetime import datetime, timedelta, timezone
from html import escape

from aiogram import BaseMiddleware, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatPermissions, Message

from src.config import MODERATOR_IDS, AUTO_MUTE_CHAT_IDS, AUTO_MUTE_WORDS, AUTO_MUTE_SECONDS, logger
from src.database.models.member import ChatMember
from src.moderation import parse_command, contains_blocked_word

router = Router(name='moderation')
PROTECTED = {'creator', 'administrator'}


async def moderate(bot, chat_id, user_id, action, seconds=3600):
    target = await bot.get_chat_member(chat_id, user_id)
    if user_id in MODERATOR_IDS or user_id == bot.id or target.status in PROTECTED:
        raise ValueError('Нельзя применить команду к администратору, модератору или самому боту.')
    me = await bot.get_chat_member(chat_id, bot.id)
    if me.status != 'administrator' or not me.can_restrict_members:
        raise ValueError('Выдай боту право ограничивать участников.')
    if action in {'mute', 'unmute'}:
        chat = await bot.get_chat(chat_id)
        if chat.type != 'supergroup':
            raise ValueError('Мут доступен только в супергруппе.')
        if action == 'mute':
            permissions = ChatPermissions(**{key: False for key in ChatPermissions.model_fields})
        else:
            permissions = chat.permissions
            if permissions is None:
                raise ValueError('Не удалось получить разрешения группы.')
        await bot.restrict_chat_member(chat_id, user_id, permissions=permissions,
            use_independent_chat_permissions=True,
            until_date=datetime.now(timezone.utc) + timedelta(seconds=seconds) if action == 'mute' else 0)
    elif action == 'unban':
        await bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
    else:
        if action == 'kick' and target.status in {'left', 'kicked'}:
            raise ValueError('Участника уже нет в группе.')
        await bot.ban_chat_member(chat_id, user_id)
        if action == 'kick':
            try:
                await bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
            except TelegramAPIError:
                raise ValueError('Участник удалён, но снять бан не удалось. Используй !unban по его ID.')


@router.message(F.chat.type.in_({'group', 'supergroup'}),
                F.text.regexp(r'^!(?i:ban|unban|kick|mute|unmute)(?:\s|$)'))
async def command(message: Message):
    if message.sender_chat or not message.from_user or message.from_user.id not in MODERATOR_IDS:
        await message.answer('Команда доступна только разрешённым ID модераторов.')
        return
    try:
        parsed = parse_command(message.text, reply=bool(message.reply_to_message))
        if parsed.target and parsed.target.startswith('@'):
            user_id = await ChatMember.resolve(message.chat.id, parsed.target)
            if not user_id:
                raise ValueError('Не знаю этого @username. Ответь на сообщение участника или укажи ID.')
            member = await message.bot.get_chat_member(message.chat.id, user_id)
            if (member.user.username or '').lower() != parsed.target[1:].lower():
                raise ValueError('Username изменился. Используй ответ на сообщение или ID.')
        elif parsed.target:
            user_id = int(parsed.target)
        else:
            replied = message.reply_to_message
            if replied.sender_chat or not replied.from_user:
                raise ValueError('Нельзя модерировать сообщение от имени канала.')
            user_id = replied.from_user.id
        await moderate(message.bot, message.chat.id, user_id, parsed.action, parsed.seconds)
    except ValueError as exc:
        await message.answer(escape(str(exc)))
        return
    except TelegramAPIError as exc:
        logger.warning('Moderation API failure: {}', type(exc).__name__)
        await message.answer('Telegram отклонил команду. Проверь ID участника и права бота.')
        return
    duration = f' на {parsed.seconds // 60} мин.' if parsed.action == 'mute' else ''
    await message.answer(f'{parsed.action}: <code>{user_id}</code>{duration}\nПричина: {escape(parsed.reason)}')
    logger.info('Moderation chat={} actor={} target={} action={}', message.chat.id,
                message.from_user.id, user_id, parsed.action)


class GroupMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not isinstance(event, Message) or event.chat.type not in {'group', 'supergroup'}:
            return await handler(event, data)
        if event.from_user and not event.sender_chat:
            await ChatMember.remember(event.chat.id, event.from_user)
        for user in event.new_chat_members or []:
            await ChatMember.remember(event.chat.id, user)
        if (event.chat.id in AUTO_MUTE_CHAT_IDS and event.from_user and not event.sender_chat
            and not event.from_user.is_bot and event.from_user.id not in MODERATOR_IDS
            and contains_blocked_word(event.text or event.caption or '', AUTO_MUTE_WORDS)):
            try:
                await moderate(event.bot, event.chat.id, event.from_user.id, 'mute', AUTO_MUTE_SECONDS)
            except (ValueError, TelegramAPIError):
                # Protected users and API failures must not break unrelated handlers.
                pass
            else:
                await event.answer(f'Автомут: <code>{event.from_user.id}</code> на {AUTO_MUTE_SECONDS // 60} мин. за слово из словаря.')
                return
        return await handler(event, data)
