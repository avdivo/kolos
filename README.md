# КОЛОС

**Скопировать ссылку на репозиторий**  
```bash
git clone ...
```

## Функции

## Описание

## Используемые технологии
- Python 3.11
- SQLite (для хранения данных)
- SQLAlchemy (для работы с базой данных)
- Alembic (для миграций)


## Структура проекта
```
/kolos
├── alembic                   # Папка для миграций
├── ai_engine.py              # Основной алгоритм 
├── alembic.ini               # Конфигурация alembic
├── config.py                 # Конфигурации и параметры программы
├── crud.py                   # Базовые операции для работы с графом (добавление, удаление точек и связей)
├── database.py               # Модуль для работы с базой данных (сохранение и загрузка графа)
├── handler.py                # Модуль для обработки сообщений (пока только тестовый)
├── kolos.db                  # Файл базы данных SQLite
├── main.py                   # Основной файл для запуска программы
├── models.py                 # Модели "Point" и "Link" для представления узлов и связей графа
├── README.md                 # Файл с описанием проекта
├── requirements.txt          # Файл зависимостей
├── service.py                # Модуль для сервисных функций
└── tests.py                  # Тесты для классов и методов программы
``` 

## Настройки
- Файл `config.py` хранит общие конфигурации и параметры программы.
- Настройки и работа основного алгоритма файле `ai_engine.py`.

## Файл .env

## Установка и запуск
1. Открыть терминал (можно выполнить в PyCharm).
2. Перейти в нужную папку, где будет проект.
3. Клонировать репозиторий:
    ```bash
    git clone https://github.com/avdivo/kolos
    ```
4. Войти в папку проекта. Создать виртуальное окружение и активировать его:
    ```bash
    cd kolos
    python -m venv venv
    source venv/bin/activate  # Для Linux/Mac
    venv\Scripts\activate     # Для Windows
    ```
5. Установить зависимости из requirements.txt
    ```bash
    pip install -r requirements.txt
    ```
6. Если БД `kolos.db` нет, нужно ее создать, для этого выполнить миграции:
    ```bash
    alembic upgrade head
    ```
7. Чтобы внести изменения в модели, нужно создать миграцию:
    ```bash
    alembic revision --autogenerate -m "Описать изменения"
    alembic upgrade head
    ```
   (будет создан файл миграции в папке alembic/versions, нужно проследить, чтобы он попал в репозиторий).

8. Чтобы очистить все таблицы, нужно выполнить команду:
    ```bash
    python main.py --clear-db
    ```

9. Запустить программу:
    ```bash
    python main.py
    ```
