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
6. Если БД `kolos.db` нет, нужно ее создать, для этого выполнить:
    ```bash
   python main.py --init-db
    ```
   (это создаст саму бд и обязательные точки в ней).
7. Запустить программу:
    ```bash
    python main.py
    ```
8. Чтобы очистить БД `kolos.db` нужно выполнить:
    ```bash
   python main.py --clear-db
    ```
   (обязательные точки будут созданы).
9. Чтобы создать чистую БД `kolos.db` без точек, нужно выполнить миграцию:
    ```bash
    alembic upgrade head
    ```
10. Чтобы внести изменения в модели, нужно создать миграцию:
    ```bash
    alembic revision --autogenerate -m "Описать изменения"
    alembic upgrade head
    ```
   (будет создан файл миграции в папке alembic/versions, нужно проследить, чтобы он попал в репозиторий).

## Тестирование
В папке tests находятся тесты для проверки корректности работы программы. 
Запуск тестов производится командами:
```bash
   pytest tests
```
Без отчетов

```bash
   pytest -v tests
```
С общим отчетом

```bash
   pytest -s tests
```
С подробным отчетом (много текста)

### Добавление тестов
Для добавления простых стартовых тестов используется строка ввода-вывода при работе программы. Пример:
```
a b -> Нет данных | b c -> Нет данных | a -> Пробел
```
Для проверки соответствия вывода программы при определенных входных данных, нужно составить такую строку (или скопировать из терминала при выводе программы) и добавить в параметры функции в файле test_start.py:
```python
# Параметризованный тест для функции handle_text
@pytest.mark.parametrize("input_data", [
    "a b -> Нет данных | b c -> Нет данных | a -> Пробел",
    # Добавьте больше тестовых случаев по мере необходимости
])
```