"""`TELEGRAM_TOKEN=... python -m app.entrypoints.bot` — process entry point."""

import asyncio
import os

from aiogram import Bot

from app.entrypoints.bot.app import create_dispatcher


async def main() -> None:
    await create_dispatcher().start_polling(Bot(os.environ["TELEGRAM_TOKEN"]))


asyncio.run(main())
