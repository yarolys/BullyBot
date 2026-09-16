import test_moderation  # offline environment shared with moderation tests
import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from aiogram import Bot, Dispatcher
from aiogram.types import Message, Chat, User, Voice, Audio, CallbackQuery
from aiogram.fsm.storage.memory import SimpleEventIsolation
from src.handlers.panel_for_admin import check_sounds
from src.schemas import SoundSchema
from src.states.admin import FSM_Prompt
from src.utils.filter import AdminRoleFilter


class SoundTests(unittest.IsolatedAsyncioTestCase):
    async def test_media_playback_uses_matching_method(self):
        message = Message(message_id=1, date=datetime.now(timezone.utc), chat=Chat(id=3, type='private'))
        callback = CallbackQuery(id='test', from_user=User(id=3, is_bot=False, first_name='Test'),
                                 chat_instance='test', data='play_sound:5', message=message)
        for media in ('audio', 'voice', 'document'):
            sound = SoundSchema(id=5, name='a:b', file_id='file', media_type=media)
            with patch.object(CallbackQuery, 'answer', new_callable=AsyncMock), \
                 patch.object(check_sounds.Sound, 'get_sound_by_id', new_callable=AsyncMock, return_value=sound), \
                 patch.object(Message, f'answer_{media}', new_callable=AsyncMock) as send:
                await check_sounds.play_sound(callback)
                send.assert_awaited_once_with('file')

    async def test_non_owner_cannot_pass_admin_filter(self):
        message = Message(message_id=1, date=datetime.now(timezone.utc),
                          chat=Chat(id=3, type='private'), from_user=User(id=3, is_bot=False, first_name='Test'))
        self.assertFalse(await AdminRoleFilter()(message))

    async def test_voice_upload_reaches_upload_handler_before_recognition(self):
        from src.handlers.panel_for_user.user_panel import router as user_router
        from src.handlers.audio.voice import router as voice_router
        dp = Dispatcher(events_isolation=SimpleEventIsolation())
        dp.include_routers(user_router, voice_router)
        bot = Bot('123456:offline-test-token')
        state = dp.fsm.get_context(bot=bot, chat_id=3, user_id=3)
        await state.set_state(FSM_Prompt.get_user_prompt_file)
        await state.update_data(sound_name='test')
        message = Message(message_id=1, date=datetime.now(timezone.utc),
                          chat=Chat(id=3, type='private'), from_user=User(id=3, is_bot=False, first_name='Test'),
                          voice=Voice(file_id='voice', file_unique_id='unique', duration=1)).as_(bot)
        with patch('src.handlers.panel_for_user.user_panel.DbSound.get_sound_by_file_id', new_callable=AsyncMock, return_value=None), \
             patch('src.handlers.panel_for_user.user_panel.DbSound.add_sound', new_callable=AsyncMock) as add, \
             patch.object(Message, 'answer', new_callable=AsyncMock), \
             patch('src.handlers.audio.voice.process_voice_task.apply_async') as queue:
            await dp.propagate_event('message', message, bot=bot, state=state, raw_state=await state.get_state())
            add.assert_awaited_once_with(name='test', file_id='voice', media_type='voice')
            queue.assert_not_called()
        await dp.storage.close()
        await bot.session.close()
