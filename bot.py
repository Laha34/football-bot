"""
Локальний запуск бота для тестування на своєму комп'ютері (python bot.py).
Використовує long-polling (Telegram getUpdates) - не потребує webhook/сервера.

Для постійної роботи 24/7 використовуй app.py на PythonAnywhere (див. README.md).
"""
import time

import config
import db
import handlers
import reminders
import telegram_api

REMINDER_CHECK_INTERVAL_SECONDS = 300  # 5 хвилин


def main():
    db.init_db()
    print("Бот запущено (локальний режим). Натисни Ctrl+C, щоб зупинити.")

    offset = None
    last_reminder_check = 0

    while True:
        try:
            updates = telegram_api.get_updates(offset=offset, timeout=20)
            for update in updates:
                offset = update["update_id"] + 1
                handlers.handle_update(update)
        except Exception as e:
            print(f"[bot] Помилка при отриманні оновлень: {e}")
            time.sleep(5)

        now = time.time()
        if now - last_reminder_check >= REMINDER_CHECK_INTERVAL_SECONDS:
            reminders.check_and_send_reminders()
            last_reminder_check = now


if __name__ == "__main__":
    main()
