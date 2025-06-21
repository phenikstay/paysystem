# Платежная система

Асинхронное веб-приложение для обработки платежей, построенное на основе Sanic, SQLAlchemy и PostgreSQL.

## Описание

Приложение предоставляет REST API для управления пользователями, счетами и платежами. Поддерживает авторизацию пользователей и администраторов, обработку вебхуков от платежных систем с проверкой подписи.

## Основные возможности

### Для пользователей:
- Авторизация по email/password
- Получение данных о себе (id, email, full_name)
- Получение списка своих счетов и балансов
- Получение списка своих платежей

### Для администраторов:
- Авторизация по email/password
- Получение данных о себе (id, email, full_name)
- Создание/Удаление/Обновление пользователей
- Получение списка пользователей и их счетов

### Обработка платежей:
- Эмуляция вебхука от платежной системы
- Проверка подписи через SHA256
- Автоматическое создание счетов при необходимости
- Защита от дублирования транзакций

## Технический стек

- **Backend**: Sanic (асинхронный веб-фреймворк)
- **База данных**: PostgreSQL
- **ORM**: SQLAlchemy (async)
- **Миграции**: Alembic
- **Аутентификация**: JWT tokens
- **Контейнеризация**: Docker & Docker Compose
- **Тестирование**: pytest

## Быстрый старт

### Вариант 1: Запуск с Docker Compose (рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd paysystem
```

2. Запустите приложение:
```bash
docker-compose up --build
```

**Приложение будет доступно по адресам:**
- 🌐 API: http://localhost:8000
- 🏥 Health check: http://localhost:8000/health
- 🗄️ PostgreSQL: localhost:5432

### Вариант 2: Локальный запуск без Docker

1. Установите PostgreSQL и создайте базу данных:
```sql
CREATE DATABASE paysystem;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE paysystem TO postgres;
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` с переменными окружения:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/paysystem
JWT_SECRET=your-secret-key-change-in-production
WEBHOOK_SECRET_KEY=gfdmhghif38yrf9ew0jkf32
HOST=0.0.0.0
PORT=8000
```

4. Выполните миграции:
```bash
alembic upgrade head
```

5. Запустите приложение:
```bash
python -m app.main
```

## Тестовые данные

В миграции автоматически создаются тестовые аккаунты:

### Тестовый пользователь:
- **Email**: `user@example.com`
- **Password**: `userpassword`

### Тестовый администратор:
- **Email**: `admin@example.com`
- **Password**: `adminpassword`

## API Эндпоинты

### Системные эндпоинты

#### Проверка здоровья сервера
```http
GET /health
```

#### Корневой эндпоинт
```http
GET /
```

### Аутентификация

#### Авторизация пользователя
```http
POST /api/auth/user/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "userpassword"
}
```

#### Авторизация администратора  
```http
POST /api/auth/admin/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "adminpassword"
}
```

### Пользователи

#### Получить данные о себе
```http
GET /api/users/me
Authorization: Bearer <token>
```

#### Получить свои счета
```http
GET /api/users/me/accounts
Authorization: Bearer <token>
```

#### Получить свои платежи
```http
GET /api/users/me/payments
Authorization: Bearer <token>
```

### Администрирование

#### Получить данные о себе
```http
GET /api/admin/me
Authorization: Bearer <token>
```

#### Получить список пользователей
```http
GET /api/admin/users
Authorization: Bearer <token>
```

#### Создать пользователя
```http
POST /api/admin/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "full_name": "New User",
  "password": "password123"
}
```

#### Обновить пользователя
```http
PUT /api/admin/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Updated Name"
}
```

#### Удалить пользователя
```http
DELETE /api/admin/users/{user_id}
Authorization: Bearer <token>
```

### Вебхуки

#### Обработка платежа
```http
POST /api/webhooks/payment
Content-Type: application/json

{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

### Формирование подписи для вебхука

Подпись формируется через SHA256 хеш строки, состоящей из конкатенации значений в алфавитном порядке ключей и секретного ключа:

```python
import hashlib

def generate_signature(account_id, amount, transaction_id, user_id, secret_key):
    data_string = f"{account_id}{amount}{transaction_id}{user_id}{secret_key}"
    return hashlib.sha256(data_string.encode()).hexdigest()

# Пример для secret_key = "gfdmhghif38yrf9ew0jkf32"
signature = generate_signature(1, 100, "5eae174f-7cd0-472c-bd36-35660f00132b", 1, "gfdmhghif38yrf9ew0jkf32")
```

## Тестирование

### Структурированные тесты (pytest)

```bash
# Все тесты
pytest

# Unit тесты (быстрые, без базы данных)
pytest tests/test_models.py tests/test_services.py

# Для интеграционного тестирования используйте утилиту:
python utils/integration_test.py

# С покрытием кода
pytest --cov=app
```

### Быстрое интеграционное тестирование

Утилита `utils/integration_test.py` предоставляет красивое визуальное тестирование всего API:

```bash
# Запустите сервер
python -m app.main

# В другом терминале запустите утилиту тестирования
python utils/integration_test.py
```

**Что тестирует интеграционная утилита:**
- ✅ Авторизация пользователей и администраторов
- ✅ Все пользовательские API (профиль, счета, платежи)
- ✅ Все административные API (CRUD пользователей)
- ✅ Обработка вебхуков с проверкой подписи SHA256
- ✅ Защита от дублирования транзакций

**Преимущества:** Цветной вывод, детальная информация, быстрая диагностика проблем

## Структура проекта

```
paysystem/
├── app/
│   ├── __init__.py
│   ├── main.py              # Главный файл приложения
│   ├── config.py            # Конфигурация
│   ├── database.py          # Настройка БД
│   ├── models.py            # Модели данных
│   ├── schemas.py           # Pydantic схемы
│   ├── auth.py              # Аутентификация
│   ├── middleware.py        # Middleware
│   ├── services.py          # Бизнес-логика
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Роуты аутентификации
│       ├── users.py         # Роуты пользователей
│       ├── admin.py         # Роуты администратора
│       └── webhooks.py      # Роуты вебхуков
├── migrations/              # Миграции Alembic
├── tests/                   # Unit тесты
├── utils/                   # Утилиты (интеграционное тестирование)
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile              # Docker образ
├── requirements.txt        # Python зависимости
├── alembic.ini             # Конфигурация Alembic
└── README.md               # Документация
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql+asyncpg://postgres:password@db:5432/paysystem` |
| `JWT_SECRET` | Секретный ключ для JWT | `your-secret-key-change-in-production` |
| `WEBHOOK_SECRET_KEY` | Секретный ключ для вебхуков | `gfdmhghif38yrf9ew0jkf32` |
| `HOST` | Хост для запуска приложения | `0.0.0.0` |
| `PORT` | Порт для запуска приложения | `8000` |

## Безопасность

- Пароли хешируются с использованием bcrypt
- JWT токены для аутентификации с истечением через 1 час
- Подписи вебхуков проверяются через SHA256
- Защита от дублирования транзакций
- Валидация данных через Pydantic схемы

## Разработка

Для разработки используйте Docker Compose (volume mapping уже настроен):

```bash
# Запуск с логами в консоли
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f app
```

**Особенности режима разработки:**
- 📁 Volume mapping включен - изменения кода применяются сразу
- 🔄 Автоматический перезапуск при изменениях
- 🐛 Debug режим включен
- 📝 Подробное логирование ошибок

## Лицензия

MIT License 