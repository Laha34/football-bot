"""
Мінімальна обгортка над Telegram Bot API через звичайні HTTP-запити (requests).
Без aiogram - так простіше сумісно і з локальним запуском, і з PythonAnywhere.
"""
import requests

import config

API_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN}"


def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=15)
    if not response.ok:
        print(f"[telegram_api] Помилка sendMessage: {response.text}")
    return response.json()


def get_updates(offset=None, timeout=30):
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    response = requests.get(f"{API_URL}/getUpdates", params=params, timeout=timeout + 10)
    response.raise_for_status()
    return response.json().get("result", [])


def set_webhook(url):
    response = requests.post(f"{API_URL}/setWebhook", json={"url": url}, timeout=15)
    return response.json()


def delete_webhook():
    response = requests.post(f"{API_URL}/deleteWebhook", timeout=15)
    return response.json()


# Постійна клавіатура з кнопкою "Матчі"
MAIN_KEYBOARD = {
    "keyboard": [[{"text": "📅 Матчі"}]],
    "resize_keyboard": True,
}
