import asyncio
import logging
import os
import sys

# Django must be configured before importing any app code
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import common, tasks, shopping

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(common.router)
    dp.include_router(tasks.router)
    dp.include_router(shopping.router)
    return dp


async def run_polling():
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = create_dispatcher()
    logger.info('Starting bot in polling mode...')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def run_webhook():
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = create_dispatcher()

    webhook_url = settings.WEBHOOK_HOST + settings.WEBHOOK_PATH
    await bot.set_webhook(webhook_url)
    logger.info(f'Webhook set to {webhook_url}')

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info('Webhook server started on :8080')

    await asyncio.Event().wait()


if __name__ == '__main__':
    if settings.USE_POLLING:
        asyncio.run(run_polling())
    else:
        asyncio.run(run_webhook())
