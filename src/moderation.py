"""Command parsing independent of Telegram and database connections."""
import re
from dataclasses import dataclass

COMMANDS = {'ban', 'unban', 'kick', 'mute', 'unmute'}


@dataclass(frozen=True)
class ModerationCommand:
    action: str
    target: str | None
    seconds: int
    reason: str


def parse_command(text: str, reply: bool = False) -> ModerationCommand:
    parts = text.split()
    action = parts.pop(0).removeprefix('!').lower()
    if action not in COMMANDS:
        raise ValueError('Неизвестная команда.')
    target = None
    if parts and (parts[0].startswith('@') or parts[0].isdigit()):
        target = parts.pop(0)
    elif not reply:
        raise ValueError('Укажи @username, числовой ID или ответь на сообщение участника.')
    seconds = 3600
    if action == 'mute' and parts and re.fullmatch(r'\d+[mhd]', parts[0], re.I):
        value = parts.pop(0).lower()
        seconds = int(value[:-1]) * {'m': 60, 'h': 3600, 'd': 86400}[value[-1]]
        if not 60 <= seconds <= 366 * 86400:
            raise ValueError('Срок мута: от 1m до 366d.')
    return ModerationCommand(action, target, seconds, ' '.join(parts) or 'Причина не указана')


def contains_blocked_word(text: str, words: frozenset[str]) -> bool:
    return bool(set(re.findall(r'\w+', text.casefold())) & words)
