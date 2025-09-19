#!/usr/bin/env python3
"""Diagnostic script for the main bot"""

import asyncio
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Import handlers
from bot.handlers import base, callbacks
from bot.database import db

load_dotenv()

async def main():
    print("=== ДИАГНОСТИКА БОТА ===")

    # Проверка переменных окружения
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN не найден!")
        return
    print(f"✅ BOT_TOKEN загружен: ...{token[-10:]}")

    # Проверка OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️ OPENAI_API_KEY не найден - переводы могут не работать")
    else:
        print(f"✅ OPENAI_API_KEY загружен: ...{openai_key[-10:]}")

    # Инициализация бота
    bot = Bot(token=token)
    dp = Dispatcher()

    print("\n=== РЕГИСТРАЦИЯ HANDLERS ===")

    # Регистрация handlers
    print("Регистрируем base.router...")
    dp.include_router(base.router)
    print(f"✅ base.router зарегистрирован. Handlers: {len(base.router._handlers)}")

    print("Регистрируем callbacks.router...")
    dp.include_router(callbacks.router)
    print(f"✅ callbacks.router зарегистрирован. Handlers: {len(callbacks.router._handlers)}")

    # Инициализация базы данных
    print("\n=== БАЗА ДАННЫХ ===")
    await db.init()
    print("✅ База данных инициализирована")

    # Проверка бота
    print("\n=== ИНФОРМАЦИЯ О БОТЕ ===")
    me = await bot.get_me()
    print(f"✅ Бот: @{me.username} (ID: {me.id})")

    # Добавим простой handler для теста
    @dp.message()
    async def test_handler(message):
        print(f"📨 Получено сообщение: {message.text}")
        await message.answer("Диагностический handler работает!")

    print("\n=== ЗАПУСК POLLING ===")
    print("Бот запущен! Отправьте /start или любое сообщение...")
    print("Для остановки нажмите Ctrl+C")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n⏹️ Остановка бота...")
    finally:
        await bot.session.close()
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())