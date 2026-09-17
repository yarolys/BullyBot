"""Exercise the real aiogram/aiohttp/proxy connector stack without external traffic."""
import asyncio
import json
import unittest

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer


class ProxyCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_me_through_http_connect_proxy(self):
        seen = []
        errors = []

        async def proxy(reader, writer):
            try:
                connect = await reader.readuntil(b'\r\n\r\n')
                seen.append(connect.split(b'\r\n')[0])
                writer.write(b'HTTP/1.1 200 Connection established\r\n\r\n')
                await writer.drain()
                headers = await reader.readuntil(b'\r\n\r\n')
                seen.append(headers.split(b'\r\n')[0])
                for line in headers.split(b'\r\n'):
                    if line.lower().startswith(b'content-length:'):
                        await reader.readexactly(int(line.split(b':', 1)[1]))
                body = json.dumps({'ok': True, 'result': {
                    'id': 123456, 'is_bot': True, 'first_name': 'Test', 'username': 'test_bot'
                }}).encode()
                writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n'
                             + f'Content-Length: {len(body)}\r\nConnection: close\r\n\r\n'.encode() + body)
                await writer.drain()
            except Exception as exc:
                errors.append(exc)
            finally:
                writer.close()
                await writer.wait_closed()

        server = await asyncio.start_server(proxy, '127.0.0.1', 0)
        port = server.sockets[0].getsockname()[1]
        session = AiohttpSession(proxy=f'http://127.0.0.1:{port}',
                                 api=TelegramAPIServer.from_base('http://telegram.test'))
        bot = Bot('123456:offline-test-token', session=session)
        try:
            me = await bot.get_me(request_timeout=3)
            self.assertEqual(me.username, 'test_bot')
            self.assertTrue(seen[0].startswith(b'CONNECT telegram.test:80 '))
            self.assertIn(b'/getMe ', seen[1])
            self.assertEqual(errors, [])
        finally:
            await bot.session.close()
            server.close()
            await server.wait_closed()
