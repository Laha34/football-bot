"""
Логіка нагадувань: раз на кілька хвилин перевіряємо найближчі матчі
і вирішуємо, чи не час надіслати повідомлення.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import config
import db
import football_api

LOCAL_TZ = ZoneInfo(config.TIMEZONE)


def _format_match(match: dict) -> str:
    local_time = match["utc_date"].astimezone(LOCAL_TZ)
    return (
        f"⚽ {match['home']} — {match['away']}\n"
        f"🏆 {match['competition']}\n"
        f"🕒 {local_time.strftime('%d.%m.%Y о %H:%M')}"
    )


async def check_and_send_reminders(bot):
    """Викликається планувальником кожні кілька хвилин."""
    try:
        matches = football_api.get_all_upcoming_matches(config.TEAM_IDS, days_ahead=2)
    except Exception as e:
        print(f"[reminders] Помилка отримання матчів: {e}")
        return

    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(LOCAL_TZ)

    for match in matches:
        match_local = match["utc_date"].astimezone(LOCAL_TZ)
        minutes_until = (match["utc_date"] - now_utc).total_seconds() / 60

        # 1. Ранкове нагадування в день матчу
        is_match_day = match_local.date() == now_local.date()
        is_morning_time = (
            now_local.hour == config.MORNING_REMINDER_HOUR
            and now_local.minute < config.MORNING_REMINDER_MINUTE + 5
            and now_local.minute >= config.MORNING_REMINDER_MINUTE
        )
        if is_match_day and is_morning_time and not db.was_sent(match["id"], "morning"):
            text = f"☀️ Сьогодні матч!\n\n{_format_match(match)}"
            await bot.send_message(config.CHAT_ID, text)
            db.mark_sent(match["id"], "morning")

        # 2. Нагадування за годину до матчу (вікно 55-65 хв, бо перевірка йде раз на 5 хв)
        if 55 <= minutes_until <= 65 and not db.was_sent(match["id"], "hour_before"):
            text = f"⏰ Через годину матч!\n\n{_format_match(match)}"
            await bot.send_message(config.CHAT_ID, text)
            db.mark_sent(match["id"], "hour_before")
