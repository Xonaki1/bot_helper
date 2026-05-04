"""
Thin Django view that forwards raw Telegram updates to the running aiogram bot.
Only used in webhook / production mode; in polling mode this view is never hit.
"""
import json
import asyncio
import threading

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

_bot: Bot | None = None
_dp = None
_lock = threading.Lock()


def _get_bot_and_dp():
    global _bot, _dp
    if _bot is None:
        with _lock:
            if _bot is None:
                from bot.main import create_dispatcher
                _bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
                _dp = create_dispatcher()
    return _bot, _dp


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    async def post(self, request):
        bot, dp = _get_bot_and_dp()
        try:
            data = json.loads(request.body)
            update = Update.model_validate(data)
            await dp.feed_update(bot=bot, update=update)
        except Exception:
            pass
        return HttpResponse('ok')
