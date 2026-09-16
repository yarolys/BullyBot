import os
os.environ['TOKEN'] = '123456:offline-test-token'
os.environ['BOT_ADMIN_ID'] = '1'
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost/test'
os.environ['AUTO_MUTE_CHAT_IDS'] = ''
os.environ['AUTO_MUTE_WORDS'] = ''
os.environ['MODERATOR_IDS'] = ''

import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock
from src.moderation import parse_command, contains_blocked_word
from src.handlers.moderation import moderate, command
from src.handlers.audio.voice import converting_voice_to_text
from unittest.mock import patch
from aiogram.types import ChatPermissions


class ParsingTests(unittest.TestCase):
    def test_reason_without_quotes(self):
        parsed = parse_command('!kick @KandyBobby нафик не нужон тут')
        self.assertEqual(parsed.target, '@KandyBobby')
        self.assertEqual(parsed.reason, 'нафик не нужон тут')

    def test_reply_mute(self):
        self.assertEqual(parse_command('!mute 30m флуд', reply=True).seconds, 1800)

    def test_missing_target(self):
        with self.assertRaises(ValueError):
            parse_command('!ban')

    def test_invalid_duration(self):
        for duration in ['0m', '367d']:
            with self.assertRaises(ValueError):
                parse_command(f'!mute 123 {duration}')

    def test_whole_words(self):
        self.assertTrue(contains_blocked_word('ДУРАК!', frozenset({'дурак'})))
        self.assertFalse(contains_blocked_word('дураками', frozenset({'дурак'})))


class ModerationTests(unittest.IsolatedAsyncioTestCase):
    def bot(self, target='member'):
        bot = AsyncMock()
        bot.id = 99
        bot.get_chat_member.side_effect = [NS(status=target), NS(status='administrator', can_restrict_members=True)]
        bot.get_chat.return_value = NS(type='supergroup', permissions=ChatPermissions(can_send_messages=True, can_send_polls=False))
        return bot

    async def test_kick_bans_then_unbans(self):
        bot = self.bot()
        await moderate(bot, -100, 2, 'kick')
        bot.ban_chat_member.assert_awaited_once_with(-100, 2)
        bot.unban_chat_member.assert_awaited_once_with(-100, 2, only_if_banned=True)

    async def test_protected_admin(self):
        bot = self.bot('administrator')
        with self.assertRaises(ValueError):
            await moderate(bot, -100, 2, 'ban')
        bot.ban_chat_member.assert_not_called()

    async def test_protected_owner_id(self):
        bot = self.bot()
        with self.assertRaises(ValueError):
            await moderate(bot, -100, 1, 'ban')
        bot.ban_chat_member.assert_not_called()

    async def test_unmute_restores_chat_defaults(self):
        bot = self.bot()
        await moderate(bot, -100, 2, 'unmute')
        permissions = bot.restrict_chat_member.call_args.kwargs['permissions']
        self.assertTrue(permissions.can_send_messages)
        self.assertFalse(permissions.can_send_polls)

    async def test_mute_disables_all_permissions(self):
        bot = self.bot()
        await moderate(bot, -100, 2, 'mute')
        permissions = bot.restrict_chat_member.call_args.kwargs['permissions']
        self.assertTrue(all(v is False for v in permissions.model_dump().values()))

    async def test_unauthorized_command(self):
        message = NS(sender_chat=None, from_user=NS(id=500), answer=AsyncMock(), bot=AsyncMock())
        await command(message)
        message.bot.ban_chat_member.assert_not_called()
        message.answer.assert_awaited_once()

    async def test_voice_queue_failure_is_handled(self):
        message = NS(voice=NS(duration=10, file_size=100, file_id='file'), chat=NS(id=-100), answer=AsyncMock())
        with patch('src.handlers.audio.voice.process_voice_task.apply_async', side_effect=ConnectionError):
            await converting_voice_to_text(message)
        self.assertIn('недоступно', message.answer.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
