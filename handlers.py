"""
Обробка вхідних повідомлень від Telegram.
Викликається і з локального polling-скрипта (для тестів), і з webhook (Flask на PythonAnywhere).
"""
import config
import football_api
import telegram_api
from reminders import _format_match

MATCHES_BUTTON_TEXT = "📅 Матчі"


def handle_update(update: dict):
    message = update.get("message")
    if not message:
        return  # ігноруємо інші типи оновлень (edited_message, callback_query і т.д.)

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        telegram_api.send_message(
            chat_id,
            "Привіт! Я стежу за матчами твоїх команд і нагадую:\n"
            "☀️ вранці в день матчу\n"
            "⏰ за годину до початку\n\n"
            "Натисни кнопку внизу, щоб побачити найближчі матчі.",
            reply_markup=telegram_api.MAIN_KEYBOARD,
        )
        return

    if text == "/matches" or text == MATCHES_BUTTON_TEXT:
        send_matches(chat_id)
        return


def send_matches(chat_id):
    telegram_api.send_message(chat_id, "Шукаю найближчі матчі...")
    try:
        matches = football_api.get_all_upcoming_matches(config.TEAM_IDS, days_ahead=14)
    except Exception as e:
        telegram_api.send_message(chat_id, f"Не вдалося отримати дані з football-data.org: {e}")
        return

    if not matches:
        telegram_api.send_message(chat_id, "Найближчим часом матчів не знайдено.")
        return

    text = "\n\n".join(_format_match(m) for m in matches[:10])
    telegram_api.send_message(chat_id, text)
