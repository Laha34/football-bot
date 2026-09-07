import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
import db
import football_api
from reminders import check_and_send_reminders, _format_match

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

MATCHES_BUTTON_TEXT = "📅 Матчі"

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=MATCHES_BUTTON_TEXT)]],
    resize_keyboard=True,  # кнопка не займає весь екран
)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Я стежу за матчами твоїх команд і нагадую:\n"
        "☀️ вранці в день матчу\n"
        "⏰ за годину до початку\n\n"
        "Натисни кнопку внизу, щоб побачити найближчі матчі.",
        reply_markup=main_keyboard,
    )


async def send_matches(message: Message):
    await message.answer("Шукаю найближчі матчі...")
    try:
        matches = football_api.get_all_upcoming_matches(config.TEAM_IDS, days_ahead=14)
    except Exception as e:
        await message.answer(f"Не вдалося отримати дані з football-data.org: {e}")
        return

    if not matches:
        await message.answer("Найближчим часом матчів не знайдено.")
        return

    text = "\n\n".join(_format_match(m) for m in matches[:10])
    await message.answer(text)


@dp.message(Command("matches"))
async def cmd_matches(message: Message):
    await send_matches(message)


@dp.message(F.text == MATCHES_BUTTON_TEXT)
async def button_matches(message: Message):
    await send_matches(message)


async def main():
    db.init_db()

    scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
    # перевіряємо матчі й надсилаємо нагадування кожні 5 хвилин
    scheduler.add_job(check_and_send_reminders, "interval", minutes=5, args=[bot])
    scheduler.start()

    print("Бот запущено. Натисни Ctrl+C, щоб зупинити.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())