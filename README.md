# 🤖 Bot Assistant via Telegram

> Telegram-бот-помощник для фрилансеров: поиск заказов на нескольких площадках, персональный список задач, планировщик проектов и AI-ассистент на базе Groq.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.10-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Бот работает в режиме long polling: отдельный HTTP-сервер для webhook не требуется. После запуска он подключается к Telegram, принимает сообщения, обращается к MySQL, внешним freelance-источникам и Groq API, а затем отправляет результат пользователю.

> **Важно:** проект активно развивается. В репозитории пока нет готовых `Dockerfile` и `docker-compose.yml`, поэтому Docker-вариант ниже содержит рекомендуемую конфигурацию для самостоятельного добавления.

---

## Содержание

- [Возможности](#возможности)
- [Как это работает](#как-это-работает)
- [Архитектура проекта](#архитектура-проекта)
- [Требования](#требования)
- [API и внешние сервисы](#api-и-внешние-сервисы)
- [Переменные окружения](#переменные-окружения)
- [Установка на Linux](#установка-на-linux)
- [Установка на Windows](#установка-на-windows)
- [Настройка базы данных](#настройка-базы-данных)
- [Запуск](#запуск)
- [Запуск через Docker](#запуск-через-docker)
- [Пользовательский сценарий](#пользовательский-сценарий)
- [Источники заказов](#источники-заказов)
- [Разработка и миграции](#разработка-и-миграции)
- [Диагностика](#диагностика)
- [Безопасность](#безопасность)
- [Известные ограничения](#известные-ограничения)
- [Лицензия](#лицензия)

---

## Возможности

### 🔍 Поиск работы

`FreelanceService` параллельно получает объявления из RSS, HTML-страниц, Telegram-каналов и RemoteOK API. Для результата отображаются:

- название заказа или вакансии;
- бюджет, если источник его предоставляет;
- площадка-источник;
- ссылка на оригинальное объявление;
- кнопка сохранения в планировщик.

Доступны направления:

- Python / Backend;
- Web Frontend;
- Fullstack Web;
- Mobile (Flutter/Android/iOS);
- C++ / Embedded;
- все направления.

Фильтрация выполняется по ключевым словам в `app/services/parser_service.py`.

### 📋 Задачи

Пользователь может:

- посмотреть личные задачи;
- добавить задачу;
- указать дедлайн текстом или выбрать вариант без дедлайна;
- удалить задачу по ID.

### 📅 Планировщик

Найденные заказы можно сохранить в планировщик. Сохранение создаёт запись в таблице `planers` с названием проекта и датой добавления.

### 🤖 AI-ассистент

Режим AI отправляет текст пользователя в Groq Chat Completions с моделью `llama-3.3-70b-versatile`. Для интеграции нужен ключ `GROQ_API_KEY`.

### 🌐 Русский и английский языки

Сообщения хранятся в `app/locales.py`. Язык пользователя сохраняется в базе данных в поле `users.language`; по умолчанию используется русский язык.

---

## Как это работает

```text
Telegram
   │
   ▼
app/main.py ── Dispatcher ── routers из app/handlers/
   │                              ├─ menu.py
   │                              ├─ ai_chat.py
   │                              ├─ job_search.py
   │                              └─ tasks_planner.py
   │
   ├── app/database/engine.py ── SQLAlchemy async ── MySQL
   ├── app/services/ai_service.py / ai_chat.py ── Groq API
   └── app/services/parser_service.py ── RSS, HTML и внешние API
```

При `/start` бот создаёт пользователя в таблице `users`, если его ещё нет. Далее обработчики aiogram используют FSM для многошаговых сценариев — добавления задачи и режима общения с AI. Данные сохраняются через асинхронные SQLAlchemy-сессии.

---

## Архитектура проекта

```text
.
├── app/
│   ├── main.py                 # Точка входа, Dispatcher и long polling
│   ├── config.py               # Загрузка и проверка переменных окружения
│   ├── locales.py              # RU/EN сообщения и текущие языки пользователей
│   ├── database/
│   │   ├── engine.py           # Асинхронный SQLAlchemy engine и sessionmaker
│   │   └── models.py            # User, Task и Planer
│   ├── handlers/
│   │   ├── menu.py             # /start, меню, настройки, смена языка
│   │   ├── ai_chat.py           # FSM и запросы к Groq
│   │   ├── job_search.py        # Поиск, категории и сохранение заказов
│   │   └── tasks_planner.py     # Задачи и просмотр планировщика
│   ├── services/
│   │   ├── ai_service.py        # Дополнительная обёртка Groq-клиента
│   │   └── parser_service.py    # Сбор и фильтрация заказов
│   └── middlewares/
│       ├── error_handler.py     # Обработка ошибок
│       └── throttling.py        # Ограничение частоты запросов
├── alembic/
│   ├── env.py                   # Подстановка MYSQL_URL в Alembic
│   └── versions/                # Миграции схемы базы
├── alembic.ini                  # Конфигурация миграций
├── requirements.txt             # Python-зависимости
├── Diagram.svg                  # Диаграмма проекта
└── README.md
```

### Основные модели БД

| Таблица | Назначение |
|---|---|
| `users` | Telegram ID, язык, уведомления, категория поиска, дата регистрации |
| `tasks` | Личные задачи пользователя, статус и заголовок |
| `planers` | Сохранённые проекты и дата планирования |

Связи `tasks.user_id` и `planers.user_id` ссылаются на `users.id` и используют `ON DELETE CASCADE`.

---

## Требования

- Python **3.10 или новее**;
- MySQL **8.0+** или совместимый сервер;
- Telegram-бот, созданный через BotFather;
- ключ Groq API для AI-функции;
- сетевой доступ к Telegram и внешним источникам заказов.

Проверка версий:

```bash
python --version
pip --version
```

---

## API и внешние сервисы

### 1. Telegram Bot API

1. Откройте [@BotFather](https://t.me/BotFather).
2. Выполните `/newbot`.
3. Задайте имя и username бота.
4. Скопируйте токен в `BOT_TOKEN`.

Токен нельзя публиковать в Git, README, Docker-образах или логах.

### 2. Groq API

1. Создайте аккаунт на [console.groq.com](https://console.groq.com/keys).
2. Создайте API key.
3. Сохраните его в `GROQ_API_KEY`.

Основной Telegram-обработчик использует модель `llama-3.3-70b-versatile`, параметры `temperature=0.7` и `max_tokens=1024`.

### 3. MySQL

Приложение подключается к базе асинхронно через SQLAlchemy. Примеры корректного URL:

```env
# Вариант с asyncmy
MYSQL_URL=mysql+asyncmy://bot_user:strong_password@127.0.0.1:3306/telegram_bot

# Вариант с aiomysql
MYSQL_URL=mysql+aiomysql://bot_user:strong_password@127.0.0.1:3306/telegram_bot
```

Для Docker имя хоста должно быть именем сервиса, например `mysql`, а не `127.0.0.1`.

### 4. Источники вакансий и заказов

Парсер обращается к Freelancehunt RSS, Habr Freelance, Weblancer, Freelance.ua, JustFreelance, RemoteOK API, WeWorkRemotely RSS, Jobspresso RSS и публичным Telegram-каналам. Эти интеграции не требуют пользовательских API-ключей, но зависят от доступности сайтов, RSS/API и актуальности HTML-селекторов.

---

## Переменные окружения

Создайте в корне проекта файл `.env`:

```env
BOT_TOKEN=123456789:replace_with_telegram_token
GROQ_API_KEY=gsk_replace_with_groq_key
MYSQL_URL=mysql+asyncmy://bot_user:strong_password@127.0.0.1:3306/telegram_bot
```

`app/config.py` загружает `.env` через `python-dotenv` и завершает программу, если отсутствует хотя бы одна из трёх переменных.

Проверьте, что `.env` игнорируется Git:

```bash
git status --ignored
```

---

## Установка на Linux

### Вариант A: Ubuntu/Debian и локальный MySQL

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git mysql-server
sudo systemctl enable --now mysql

git clone https://github.com/Ghostoraner/Bot-Assistant-via-Telegramm.git
cd Bot-Assistant-via-Telegramm

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Создайте базу и пользователя MySQL:

```bash
sudo mysql
```

```sql
CREATE DATABASE telegram_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON telegram_bot.* TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Создайте `.env`, примените миграции и запустите бота:

```bash
cp .env.example .env  # если шаблон создан вами; иначе создайте .env вручную
nano .env
alembic upgrade head
python -m app.main
```

### Запуск как systemd-сервис

Создайте `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Freelance Assistant
After=network-online.target mysql.service
Wants=network-online.target

[Service]
Type=simple
User=telegrambot
WorkingDirectory=/opt/Bot-Assistant-via-Telegramm
EnvironmentFile=/opt/Bot-Assistant-via-Telegramm/.env
ExecStart=/opt/Bot-Assistant-via-Telegramm/.venv/bin/python -m app.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-bot
sudo journalctl -u telegram-bot -f
```

---

## Установка на Windows

### PowerShell

Установите Python 3.10+ с [python.org](https://www.python.org/downloads/windows/) и включите опцию **Add Python to PATH**.

```powershell
git clone https://github.com/Ghostoraner/Bot-Assistant-via-Telegramm.git
Set-Location Bot-Assistant-via-Telegramm

py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Если PowerShell запрещает активацию окружения:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Установите MySQL Server, создайте базу и пользователя командами из раздела [Настройка базы данных](#настройка-базы-данных), затем создайте `.env`:

```env
BOT_TOKEN=123456789:replace_with_telegram_token
GROQ_API_KEY=gsk_replace_with_groq_key
MYSQL_URL=mysql+asyncmy://bot_user:strong_password@127.0.0.1:3306/telegram_bot
```

Запуск:

```powershell
alembic upgrade head
python -m app.main
```

### CMD

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
alembic upgrade head
python -m app.main
```

---

## Настройка базы данных

Миграции находятся в `alembic/versions/`. Файл `alembic/env.py` берёт URL из `MYSQL_URL`, поэтому менять `sqlalchemy.url` в `alembic.ini` обычно не нужно.

```bash
# применить все миграции
alembic upgrade head

# посмотреть текущую ревизию
alembic current

# посмотреть историю
alembic history

# откатить одну миграцию
alembic downgrade -1
```

При изменении моделей сначала создайте ревизию:

```bash
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

Перед `--autogenerate` убедитесь, что импортируемые модели добавлены в `Base.metadata`.

---

## Запуск

Из корня проекта и с активным виртуальным окружением:

```bash
python -m app.main
```

Успешный запуск сопровождается сообщением:

```text
Бот успешно запущен!
```

Остановить процесс можно через `Ctrl+C`.

### Минимальная проверка

1. Откройте бота в Telegram.
2. Отправьте `/start`.
3. Проверьте появление главного меню.
4. Переключите язык в разделе настроек.
5. Добавьте тестовую задачу.
6. Запустите поиск работы.
7. Откройте режим AI и отправьте короткий вопрос.

---

## Запуск через Docker

В текущем состоянии репозитория Docker-файлы отсутствуют. Ниже — минимальная конфигурация, которую можно добавить в корень проекта.

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]
```

### `docker-compose.yml`

```yaml
services:
  mysql:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: telegram_bot
      MYSQL_USER: bot_user
      MYSQL_PASSWORD: strong_password
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 20

  bot:
    build: .
    restart: unless-stopped
    env_file: .env
    environment:
      MYSQL_URL: mysql+asyncmy://bot_user:strong_password@mysql:3306/telegram_bot
    depends_on:
      mysql:
        condition: service_healthy

volumes:
  mysql_data:
```

`.env` для Docker:

```env
BOT_TOKEN=123456789:replace_with_telegram_token
GROQ_API_KEY=gsk_replace_with_groq_key
MYSQL_URL=mysql+asyncmy://bot_user:strong_password@mysql:3306/telegram_bot
```

Запуск:

```bash
docker compose up -d --build
docker compose logs -f bot
```

Остановка без удаления данных:

```bash
docker compose down
```

Полное удаление контейнеров и volume базы:

```bash
docker compose down -v
```

> В production не храните пароли MySQL в публичном `docker-compose.yml`; используйте secrets или переменные окружения CI/CD.

---

## Пользовательский сценарий

```text
/start
  └─ создание пользователя и главное меню
      ├─ Поиск работы
      │   ├─ выбор категории
      │   ├─ параллельный запрос к источникам
      │   └─ открыть заказ / сохранить в планировщик
      ├─ Задачи
      │   ├─ добавить название и дедлайн
      │   └─ удалить по ID
      ├─ Планировщик
      │   └─ список сохранённых проектов
      ├─ Ассистент ИИ
      │   ├─ отправить вопрос в Groq
      │   └─ выйти из AI-режима
      ├─ Настройки
      │   └─ переключить RU/EN
      └─ Инфо
```

---

## Источники заказов

| Источник | Формат | Метод в `FreelanceService` |
|---|---|---|
| Freelancehunt | RSS | `parse_freelancehunt` |
| Habr Freelance | HTML | `parse_habr` |
| Weblancer | HTML | `parse_weblancer` |
| Freelance.ua | HTML | `parse_freelance_ua` |
| JustFreelance | HTML | `parse_justfreelance` |
| RemoteOK | JSON API | `parse_remoteok` |
| WeWorkRemotely | RSS | `parse_weworkremotely` |
| Jobspresso | RSS | `parse_jobspresso` |
| Telegram-каналы | публичный HTML preview | `parse_telegram_channel` |

Кажды�� запрос ограничен таймаутом 8 секунд. Ошибка одного источника логируется и не должна блокировать обработку остальных: `asyncio.gather(..., return_exceptions=True)` собирает доступные результаты.

---

## Разработка и миграции

Рекомендуемый цикл:

```bash
git checkout -b feature/my-change
source .venv/bin/activate       # Linux/macOS
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell

# после изменения моделей
alembic revision --autogenerate -m "add field"
alembic upgrade head

python -m app.main
```

При добавлении новой функции обычно нужно:

1. создать или изменить router в `app/handlers/`;
2. добавить бизнес-логику в `app/services/`;
3. добавить сообщения в обе секции `MESSAGES` (`ru` и `en`);
4. при необходимости изменить модели и миграцию;
5. проверить, что новый router подключён в `app/main.py`.

---

## Диагностика

### `Critical environment variables are missing`

Проверьте наличие `.env` в корне проекта и имена переменных: `BOT_TOKEN`, `GROQ_API_KEY`, `MYSQL_URL`.

### Ошибка подключения к MySQL

Проверьте, что MySQL запущен, база существует, пользователь имеет права, а в URL указан async-драйвер (`mysql+asyncmy://` или `mysql+aiomysql://`). В Docker используйте `mysql` как host.

### Бот не отвечает

- убедитесь, что процесс `python -m app.main` запущен;
- проверьте токен через BotFather;
- остановите другой процесс, использующий тот же токен polling;
- посмотрите логи процесса или `docker compose logs -f bot`.

### AI возвращает ошибку

Проверьте `GROQ_API_KEY`, доступность `api.groq.com`, лимиты аккаунта и актуальность модели. В `app/handlers/ai_chat.py` используется `llama-3.3-70b-versatile`.

### Поиск не возвращает вакансии

Площадки могут быть недоступны, изменить HTML-разметку или ограничить автоматические запросы. Проверяйте логи и HTML-селекторы в `app/services/parser_service.py`. Парсер возвращает максимум 15 объединённых результатов.

### Alembic не видит переменную

Запускайте команды из корня проекта, где находятся `alembic.ini` и `.env`:

```bash
pwd
alembic current
```

---

## Безопасность

- не коммитьте `.env`, токены и пароли;
- замените демонстрационные пароли из Docker-примера перед production-запуском;
- ограничьте права пользователя MySQL только нужной базой;
- не выводите значения `BOT_TOKEN`, `GROQ_API_KEY` и `MYSQL_URL` в логи;
- если токен Telegram опубликован, немедленно перевыпустите его через BotFather;
- регулярно обновляйте зависимости и проверяйте изменения API источников.

---

## Известные ограничения

- состояние `USER_LANG`, `USER_CATEGORIES` и `JOBS_CACHE` хранится в памяти процесса и сбрасывается после перезапуска;
- в текущем интерфейсе дедлайн задачи сохраняется как часть строки названия, а не в отдельном поле;
- отдельного планировщика фоновых уведомлений нет;
- парсинг HTML зависит от структуры сторонних сайтов;
- тестовый набор и CI-конфигурация в репозитории не представлены;
- отдельные `app/services/ai_service.py` и AI-обработчик используют разные модели Groq — учитывайте это при дальнейшем рефакторинге;
- Docker-конфигурация в данный момент приведена в README как шаблон и ещё не является частью репозитория.

---

## Лицензия

Проект распространяется по лицензии [MIT](LICENSE).

## Ссылки

- Репозиторий: [Ghostoraner/Bot-Assistant-via-Telegramm](https://github.com/Ghostoraner/Bot-Assistant-via-Telegramm)
- Диаграмма: [Diagram.svg](Diagram.svg)
- Документация aiogram: [docs.aiogram.dev](https://docs.aiogram.dev/)
- Документация Groq: [console.groq.com/docs](https://console.groq.com/docs)
- Документация Alembic: [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org/)
