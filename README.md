# ⚽ Football Reminder Bot — Man City & Barcelona

Telegram-бот, який стежить за матчами Манчестер Сіті та Барселони і надсилає
нагадування: вранці в день матчу та за годину до початку.

Працює у двох режимах:
- **Локально** (`python bot.py`) — для тестування на своєму комп'ютері.
- **На PythonAnywhere** (`app.py`) — для роботи 24/7 безкоштовно.

## Що всередині

- `bot.py` — локальний запуск (long-polling), для тестів на комп'ютері
- `app.py` — Flask-додаток для PythonAnywhere (webhook-режим), для роботи 24/7
- `telegram_api.py` — надсилання/отримання повідомлень Telegram напряму через requests
- `handlers.py` — що робити, коли прийшло повідомлення (/start, кнопка "Матчі")
- `football_api.py` — запити до football-data.org
- `reminders.py` — логіка "чи час надіслати нагадування"
- `db.py` — маленька SQLite база, щоб не дублювати нагадування
- `config.py` — зчитує налаштування з `.env`

## Крок 1. Локальний тест (як і раніше)

```bash
pip install -r requirements.txt
cp .env.example .env
```

Відкрий `.env` і встав свої значення: `BOT_TOKEN`, `FOOTBALL_API_KEY`, `CHAT_ID`,
а також придумай будь-який `WEBHOOK_SECRET` (просто випадковий довгий рядок).

```bash
python bot.py
```

Це запустить бота у режимі long-polling — так само як раніше, для тестів.

## Крок 2. Розгортання на PythonAnywhere (безкоштовно, 24/7)

### 2.1. Реєстрація і завантаження коду

1. Зареєструйся на **pythonanywhere.com** (тариф "Beginner", безкоштовний, без картки).
2. Відкрий вкладку **"Consoles"** → **"Bash"** — це термінал прямо в браузері.
3. У консолі виконай:
   ```bash
   git clone https://github.com/Laha34/football-bot.git
   cd football-bot
   pip install --user -r requirements.txt
   ```

### 2.2. Створи файл .env на сервері

У консолі виконай (постав свої реальні значення):
```bash
cat > .env << 'ENVEOF'
BOT_TOKEN=твій_токен_бота
FOOTBALL_API_KEY=твій_ключ_football-data
CHAT_ID=твій_chat_id
TEAM_IDS=65,81
MORNING_REMINDER_HOUR=9
MORNING_REMINDER_MINUTE=0
TIMEZONE=Europe/Kyiv
WEBHOOK_SECRET=придумай_довгий_випадковий_рядок
ENVEOF
```

### 2.3. Налаштуй веб-додаток

1. Перейди на вкладку **"Web"** → **"Add a new web app"**.
2. Обери **"Manual configuration"** → **Python 3.10** (або новішу, яка є в списку).
3. У розділі **"Code"**:
   - **Source code**: `/home/твій_юзернейм/football-bot`
   - Натисни на посилання **WSGI configuration file** і заміни весь вміст файлу на:
     ```python
     import sys
     path = '/home/твій_юзернейм/football-bot'
     if path not in sys.path:
         sys.path.append(path)

     from app import app as application
     ```
4. Натисни зелену кнопку **"Reload"** вгорі сторінки Web.

Твій бот тепер доступний за адресою `https://твій_юзернейм.pythonanywhere.com`.

### 2.4. Підключи Telegram-webhook

У Bash-консолі виконай (постав свій токен, юзернейм і секрет):
```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://твій_юзернейм.pythonanywhere.com/webhook/<WEBHOOK_SECRET>"
```

Якщо все правильно, у відповідь прийде `{"ok":true,"result":true,...}`.

Тепер напиши `/start` своєму боту в Telegram — має відповісти.

### 2.5. Налаштуй нагадування через cron-job.org

Оскільки безкоштовний PythonAnywhere не дає запускати перевірку раз на 5 хвилин
самостійно, використаємо безкоштовний зовнішній сервіс:

1. Зареєструйся на **cron-job.org**.
2. Створи новий cron job:
   - **URL**: `https://твій_юзернейм.pythonanywhere.com/check-reminders/<WEBHOOK_SECRET>`
   - **Schedule**: кожні 5 хвилин
3. Збережи. Готово — тепер цей сервіс сам стукатиме на твій бот кожні 5 хвилин,
   а бот перевірятиме, чи не час надіслати нагадування.

## Як це працює

- Telegram надсилає нові повідомлення напряму на `/webhook/<секрет>` твого сайту.
- cron-job.org раз на 5 хвилин стукає на `/check-reminders/<секрет>`.
- Якщо сьогодні день матчу і настала 9:00 — надсилається ранкове нагадування.
- Якщо до матчу лишилось ~1 година — надсилається друге нагадування.
- SQLite-база (`bot.db`) запам'ятовує, які нагадування вже надіслані.

## Оновлення коду в майбутньому

Коли зміниш щось у коді на GitHub, на PythonAnywhere в Bash-консолі виконай:
```bash
cd football-bot
git pull
```
Потім зайди на вкладку "Web" і натисни "Reload".

## Поширені проблеми

**Бот не відповідає після налаштування webhook**
Перевір результат команди `setWebhook` — якщо там `"ok":false`, значить URL або секрет неправильні.
Можна перевірити поточний статус: `curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"`

**Нагадування не приходять**
Перевір на cron-job.org, чи job виконується успішно (там є історія запусків).

**"У файлі .env не заповнено..."**
Один з ключів у `.env` порожній.
