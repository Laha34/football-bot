"""
Логіка нагадувань: перевіряємо найближчі матчі і вирішуємо, чи не час надіслати повідомлення.
Викликається зовнішнім cron (cron-job.org), який раз на кілька хвилин стукає в /check-reminders.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import config
import db
import football_api
import telegram_api

LOCAL_TZ = ZoneInfo(config.TIMEZONE)


def _format_match(match: dict) -> str:
    local_time = match["utc_date"].astimezone(LOCAL_TZ)
    return (
        f"⚽ {match['home']} — {match['away']}\n"
        f"🏆 {match['competition']}\n"
        f"🕒 {local_time.strftime('%d.%m.%Y о %H:%M')}"
    )


def check_and_send_reminders():
    """Викликається кожні кілька хвилин (через HTTP-запит від зовнішнього cron)."""
    try:
        matches = football_api.get_all_upcoming_matches(config.TEAM_IDS, days_ahead=2)
    except Exception as e:
        print(f"[reminders] Помилка отримання матчів: {e}")
        return {"status": "error", "detail": str(e)}

    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(LOCAL_TZ)
    sent = []

    for match in matches:
        match_local = match["utc_date"].astimezone(LOCAL_TZ)
        minutes_until = (match["utc_date"] - now_utc).total_seconds() / 60

        is_match_day = match_local.date() == now_local.date()
        is_morning_time = (
            now_local.hour == config.MORNING_REMINDER_HOUR
            and config.MORNING_REMINDER_MINUTE <= now_local.minute < config.MORNING_REMINDER_MINUTE + 10
        )
        if is_match_day and is_morning_time and not db.was_sent(match["id"], "morning"):
            text = f"☀️ Сьогодні матч!\n\n{_format_match(match)}"
            telegram_api.send_message(config.CHAT_ID, text)
            db.mark_sent(match["id"], "morning")
            sent.append(f"morning:{match['id']}")

        if 55 <= minutes_until <= 70 and not db.was_sent(match["id"], "hour_before"):
            text = f"⏰ Через годину матч!\n\n{_format_match(match)}"
            telegram_api.send_message(config.CHAT_ID, text)
            db.mark_sent(match["id"], "hour_before")
            sent.append(f"hour_before:{match['id']}")

    return {"status": "ok", "checked": len(matches), "sent": sent}
