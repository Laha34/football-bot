"""
Обгортка над football-data.org API.
Документація: https://www.football-data.org/documentation/quickstart
"""
import requests
from datetime import datetime, timedelta, timezone

import config

BASE_URL = "https://api.football-data.org/v4"


def _headers():
    return {"X-Auth-Token": config.FOOTBALL_API_KEY}


def get_upcoming_matches(team_id: int, days_ahead: int = 14) -> list[dict]:
    """
    Повертає список запланованих матчів команди на найближчі days_ahead днів.
    Кожен матч - словник з полями: id, utc_date (datetime), home, away, competition.
    """
    date_from = datetime.now(timezone.utc).date()
    date_to = date_from + timedelta(days=days_ahead)

    url = f"{BASE_URL}/teams/{team_id}/matches"
    params = {
        "dateFrom": date_from.isoformat(),
        "dateTo": date_to.isoformat(),
        "status": "SCHEDULED",
    }

    response = requests.get(url, headers=_headers(), params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    matches = []
    for m in data.get("matches", []):
        matches.append({
            "id": m["id"],
            "utc_date": datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00")),
            "home": m["homeTeam"]["name"],
            "away": m["awayTeam"]["name"],
            "competition": m["competition"]["name"],
        })
    return matches


def get_all_upcoming_matches(team_ids: list[int], days_ahead: int = 14) -> list[dict]:
    """Збирає матчі для кількох команд і сортує за датою."""
    all_matches = []
    for team_id in team_ids:
        all_matches.extend(get_upcoming_matches(team_id, days_ahead))
    # прибираємо дублікати (якщо дві наші команди грають одна проти одної)
    unique = {m["id"]: m for m in all_matches}
    return sorted(unique.values(), key=lambda m: m["utc_date"])
