# 🏨 Booking API

REST API для бронирования отелей.  
**Стек:** FastAPI · SQLAlchemy · Alembic · PostgreSQL · Redis · Celery · aiogram

---

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Переменные окружения](#переменные-окружения)
- [Архитектура проекта](#архитектура-проекта)
- [API эндпоинты](#api-эндпоинты)
- [Аутентификация](#аутентификация)
- [Динамическое ценообразование](#динамическое-ценообразование)
- [Celery задачи](#celery-задачи)
- [Telegram бот](#telegram-бот)
- [Мониторинг](#мониторинг)
- [Запуск тестов](#запуск-тестов)

---

## Быстрый старт

### Docker (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/ravilkamans111-jpg/booking-api.git
cd booking-api

# 2. Создать .env файл
cp .env.example .env
# Заполнить переменные в .env

# 3. Запустить
docker-compose up --build
```

API будет доступен на `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

### Локальный запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn src.main:app --reload

# В отдельном терминале — Celery worker
celery -A src.tasks.celery_app:celery_instance worker --loglevel=info

# В отдельном терминале — Celery beat (периодические задачи)
celery -A src.tasks.celery_app:celery_instance beat --loglevel=info
```

---

## Переменные окружения

Создать файл `.env` в корне проекта:

```env
# База данных
DB_HOST=localhost
DB_PORT=5432
DB_NAME=booking_db
DB_USER=booking_user
DB_PASSWORD=your_password

# JWT
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Внешний API отелей
HOTELS_API_KEY=your-hotels-api-key
API_URL=https://external-hotels-api.com

# Telegram бот
TG_TOKEN=your-telegram-bot-token
```

Redis и PostgreSQL запускаются через `docker-compose.yml` и дополнительных переменных не требуют.

---

## Архитектура проекта

```
src/
├── api/                    # Роутеры (HTTP слой)
│   ├── auth.py             # Регистрация, логин, токены
│   ├── hotels.py           # Отели и избранное
│   ├── rooms.py            # Номера
│   ├── bookings.py         # Бронирования
│   ├── facilities.py       # Удобства
│   ├── dependencies.py     # FastAPI зависимости
│   └── utils/
│       └── send_welcome_email.py
│
├── repos/                  # Репозитории (работа с БД)
│   ├── base.py             # Базовый репозиторий
│   ├── hotels.py
│   ├── rooms.py
│   ├── bookings.py
│   ├── users.py
│   ├── favourites.py
│   ├── facilities.py
│   ├── utils.py            # CTE для подсчёта свободных комнат
│   └── mappers/            # ORM → Pydantic маппинг
│
├── services/               # Бизнес-логика
│   ├── base.py
│   ├── hotels.py
│   ├── rooms.py
│   ├── bookings.py
│   ├── users.py
│   ├── facilities.py
│   └── price_service.py    # Динамическое ценообразование
│
├── models/                 # SQLAlchemy ORM модели
│   ├── hotels.py
│   ├── rooms.py
│   ├── bookings.py
│   ├── users.py
│   ├── facilities.py
│   └── favourites.py
│
├── schemas/                # Pydantic схемы
│   ├── auth.py
│   ├── hotels.py
│   ├── rooms.py
│   ├── bookings.py
│   ├── facilities.py
│   └── favourites.py
│
├── tasks/                  # Celery
│   ├── celery_app.py
│   └── tasks.py
│
├── migrations/             # Alembic миграции
│   └── versions/
│
├── admin/                  # SQLAdmin панель
├── tg_bot/                 # Telegram бот
├── api_fetch_services/     # HTTP клиент для внешнего API
│
├── main.py                 # Точка входа
├── config.py               # Настройки (pydantic-settings)
├── database.py             # Движок и сессии SQLAlchemy
├── utils.py                # DBManager
├── exceptions.py           # Кастомные исключения
├── permisions.py           # RBAC: роли и права
├── paginations.py          # Пагинация
└── rate_limiter.py         # Rate limiting через Redis
```

**Паттерны:**

- **DBManager** — контекстный менеджер, предоставляет все репозитории через `async with`
- **DataMapper** — маппинг между ORM моделями и Pydantic схемами
- **BaseService** — базовый класс сервисов с доступом к `db`
- **BaseRepository** — CRUD операции, сортировка, фильтрация

---

## API эндпоинты

### Аутентификация `/auth`

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| `POST` | `/auth/register` | Регистрация | Все |
| `GET` | `/auth/login` | Вход, выдаёт токены в cookies | Все |
| `POST` | `/auth/logout` | Выход, очищает cookies | Все |
| `POST` | `/auth/refresh` | Обновление пары токенов | Все |
| `GET` | `/auth/me` | Информация о себе | Авторизованные |
| `GET` | `/auth/only_auth` | Проверка авторизации | Авторизованные |
| `PUT` | `/auth/{user_id}/premium` | Стать premium (нужно 5+ броней) | Авторизованные |

### Отели `/hotels`

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| `GET` | `/hotels/hotels` | Список свободных отелей с фильтрами | Rate limited |
| `POST` | `/hotels/ ` | Создать отель | Все |
| `GET` | `/hotels/hotel/{hotel_name}` | Поиск по названию | Авторизованные |
| `GET` | `/hotels/sorted` | Сортировка отелей | Авторизованные |
| `GET` | `/hotels/hotels/search/{city}` | Поиск через внешний API (кэш 60с) | Авторизованные |
| `POST` | `/hotels/hotels/favourites` | Добавить в избранное | Авторизованные |
| `GET` | `/hotels/favourites/{user_id}` | Получить избранное | Авторизованные |

**Параметры поиска отелей:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `date_from` | `date` | Дата заезда |
| `date_to` | `date` | Дата выезда |
| `title` | `string` | Фильтр по названию |
| `location` | `string` | Фильтр по городу |
| `limit` | `int` | Кол-во на страницу (макс. 100) |
| `offset` | `int` | Смещение |

### Номера `/rooms`

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| `GET` | `/rooms/` | Все номера | `READ_ROOMS` |
| `GET` | `/rooms/{hotel_id}/rooms` | Свободные номера отеля | Все |
| `POST` | `/rooms/room` | Создать номер | Все |

### Бронирования `/bookings`

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| `GET` | `/bookings/` | Все брони | `READ_BOOKINGS` |
| `POST` | `/bookings/booking` | Создать бронь | Авторизованные |
| `GET` | `/bookings/user/{user_id}` | Брони пользователя | Авторизованные |
| `DELETE` | `/bookings/unbooking` | Отменить бронь | Авторизованные |

**Тело запроса для создания брони:**

```json
{
  "user_id": 1,
  "room_id": 3,
  "date_from": "2026-08-01",
  "date_to": "2026-08-10",
  "price": 15000,
  "rate": "comfort"
}
```

### Удобства `/facilities`

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/facilities` | Создать удобство |

---

## Аутентификация

Токены хранятся в **httponly cookies**. Все защищённые запросы отправляются с `credentials: include`.

**Система ролей (RBAC):**

| Роль | Права |
|------|-------|
| `guest` | Просмотр отелей |
| `user` | + просмотр и создание броней, просмотр номеров |
| `moderator` | + создание/удаление отелей, номеров, броней |
| `admin` | Все права |

**Поток обновления токенов:**

```
Запрос → 401 → POST /auth/refresh → повтор запроса
                     ↓ 401
                  Logout → редирект на логин
```

---

## Динамическое ценообразование

Цена брони рассчитывается автоматически в `BookingsService.create_booking()` через `PriceChanger`.

**Факторы, влияющие на цену:**

| Фактор | Условие | Коэффициент |
|--------|---------|-------------|
| Короткое проживание | Менее 7 ночей | ×1.2 |
| Высокий сезон | Июнь — Декабрь | ×1.4 |
| Низкий сезон | Январь — Март | ×0.7 |
| Выходные | Пт, Сб, Вс | ×1.11 |
| Высокая загрузка | 8+ броней в отеле | ×1.2 |

Цена рассчитывается **по каждому дню** отдельно и суммируется за весь период.

---

## Celery задачи

```bash
# Запуск worker
celery -A src.tasks.celery_app:celery_instance worker --loglevel=info

# Запуск beat (периодические задачи)
celery -A src.tasks.celery_app:celery_instance beat --loglevel=info
```

| Задача | Триггер | Действие |
|--------|---------|----------|
| `send_booking_confirmation` | При создании брони | Email с подтверждением |
| `booking_today_check_in` | Каждую минуту (cron) | Логирует заезды сегодня |

---

## Telegram бот

Бот позволяет пользователям получить информацию о своей брони по email.

```bash
# Запуск бота отдельно
python -m src.tg_bot.send_messege
```

**Команды:**

- `/start` — приветствие
- Отправить email → бот вернёт дату заезда, название отеля и номера

---

## Мониторинг

Проект включает Prometheus + Grafana + Loki.

```bash
docker-compose up -d
```

| Сервис | URL |
|--------|-----|
| Grafana | `http://localhost:3000` |
| Prometheus | `http://localhost:9090` |
| Метрики FastAPI | `http://localhost:8000/metrics` |

Конфиги находятся в `grafana/` и `prometheus_data/`.

---

## Запуск тестов

```bash
pytest
```

---

## Admin панель

SQLAdmin доступен по адресу `http://localhost:8000/admin`.

Доступные разделы: Пользователи, Отели, Комнаты, Брони.