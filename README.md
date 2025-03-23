# Telegram Expenses Tracker

Этот проект представляет собой Telegram-бот для отслеживания расходов. Он построен с использованием FastAPI и PostgreSQL и может быть запущен локально или с использованием Docker.

## Функциональность

- Отслеживание расходов по категориям
- Управление пользователями
- Просмотр отчетов о расходах

## Используемые технологии

- Python
- Aiogram
- SQLAlchemy
- Alembic
- Pydantic
- FastAPI
- PostgreSQL
- Docker

## Начало работы

### Установка

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/DmitriiButk/telegram-expenses-tracker.git
    cd telegram-expenses-tracker
    ```

2. Создайте виртуальное окружение и активируйте его:

    ```sh
    python -m venv venv
    source venv/bin/activate  # На Windows используйте `venv\Scripts\activate`
    ```

3. Установите зависимости:

    ```sh
    pip install -r requirements.txt
    ```

4. Создайте файл `.env` на основе файла `.env.example` и заполните его конфигурацией:

    ```sh
    cp .env.example .env
    ```

### Настройка базы данных

#### Создание базы данных PostgreSQL

Для создания базы данных PostgreSQL выполните следующие шаги:

1. Установите PostgreSQL, если он еще не установлен. Инструкции по установке можно найти на официальном сайте [PostgreSQL](https://www.postgresql.org/download/).

2. Создайте новую базу данных и пользователя:

    ```sh
    # Подключитесь к серверу PostgreSQL
    psql -U postgres

    # Внутри psql выполните следующие команды:
    CREATE DATABASE database_name;
    CREATE USER user_name WITH ENCRYPTED PASSWORD 'your_password';
    GRANT ALL PRIVILEGES ON DATABASE database_name TO user_name;
    ```

3. После создания базы данных выполните миграции для обновления структуры базы данных:

    ```sh
    alembic upgrade head
    ```

### Запуск приложения

#### Локально

1. Запустите базу данных PostgreSQL и создайте необходимые таблицы.

2. Запустите приложение FastAPI и Telegram-бота:

    ```sh
    python main.py
    ```

### С использованием Docker

1. Поменяйте URL в .env файле. Или замените в URL localhost на db.
2. Соберите и запустите контейнеры Docker:

    ```sh
    docker-compose up --build
    ```
При запуске контейнера миграции выполнятся автоматически.

### Использование

- Доступ к приложению FastAPI по адресу `http://localhost:8000`
- Взаимодействие с Telegram-ботом с использованием токена, указанного в файле `.env`

