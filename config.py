import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

TEAM_IDS = [int(x.strip()) for x in os.getenv("TEAM_IDS", "").split(",") if x.strip()]

MORNING_REMINDER_HOUR = int(os.getenv("MORNING_REMINDER_HOUR", "9"))
MORNING_REMINDER_MINUTE = int(os.getenv("MORNING_REMINDER_MINUTE", "0"))

TIMEZONE = os.getenv("TIMEZONE", "Europe/Kyiv")

# Базова перевірка, щоб одразу було зрозуміло, чого не вистачає
_missing = [
    name for name, value in [
        ("BOT_TOKEN", BOT_TOKEN),
        ("FOOTBALL_API_KEY", FOOTBALL_API_KEY),
        ("CHAT_ID", CHAT_ID),
    ] if not value
]
if _missing:
    raise RuntimeError(
        f"У файлі .env не заповнено: {', '.join(_missing)}. "
        f"Скопіюй .env.example в .env і встав свої значення."
    )
