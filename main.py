import logging
import argparse
import colorlog
from handler import handle_text
from service import initialize_database, clear_db
from ai_engine import PointManager

from ai_engine import Action


# ----------- Подготовка логгера -----------
# Определяем цветовую схему для разных уровней логов
log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

# Создаем обработчик с цветами для консоли
handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s[%(asctime)s %(name)s] %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors=log_colors  # Используем цветовую схему
)
handler.setFormatter(formatter)

# Настройка базового логгера с использованием цветного обработчика
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# ----------- Выполнение команд командной строки -----------
# Настройка аргументов командной строки
parser = argparse.ArgumentParser(description="Управление базой данных")
parser.add_argument("--clear-db", action="store_true", help="Очистить базу данных")
parser.add_argument("--init-db", action="store_true", help="Инициализировать базу данных")

args = parser.parse_args()

# Если передан аргумент --clear-db, выполняем очистку базы
if args.clear_db:
    clear_db()
    exit(0)

# Если передан аргумент --init-db, выполняем создание бд и обязательных записей в ней
if args.init_db:
    initialize_database()  # Создаем БД, если ее нет и начальные записи в ней
    exit(0)

# ----------- Основной цикл программы -----------
logger.info("Старт программы.")

# В цикле принимаем данные от пользователя
# Выходим, если пользователь ввел "0"
# Иначе запускаем функцию обработки данных

action = Action()  # Объект реакции программы (ответы)

while True:
    data = input('Введите данные: ')
    if data == '0':
        # Обнуление сигналов всех точек перед выходом из программы
        PointManager.clear_signals()
        logger.critical('Выход из программы.')
        break
    logger.info(f'Получены данные: {data}')

    # Обработка данных
    handle_text(data)

