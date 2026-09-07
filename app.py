"""
Flask-додаток для розгортання на PythonAnywhere (безкоштовний веб-хостинг).

Два "секретні" адреси (щоб сторонні не могли їх смикати):
  POST /webhook/<WEBHOOK_SECRET>       - сюди Telegram надсилає нові повідомлення
  GET  /check-reminders/<WEBHOOK_SECRET> - сюди зовнішній cron (cron-job.org)
                                            стукає раз на кілька хвилин

На PythonAnywhere цей файл підключається як entry point у WSGI-конфігурації.
"""
from flask import Flask, request, jsonify

import config
import handlers
import reminders

app = Flask(__name__)


@app.route("/")
def index():
    return "Football bot is running."


@app.route(f"/webhook/{config.WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = request.get_json(force=True, silent=True) or {}
    handlers.handle_update(update)
    return jsonify({"ok": True})


@app.route(f"/check-reminders/{config.WEBHOOK_SECRET}", methods=["GET"])
def check_reminders():
    result = reminders.check_and_send_reminders()
    return jsonify(result)


if __name__ == "__main__":
    # Локальний запуск для тестування Flask-частини (не для продакшену)
    app.run(port=5000, debug=True)
