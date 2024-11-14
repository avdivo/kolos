import logging
import colorlog
from handler import handle_text

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
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors=log_colors  # Используем цветовую схему
)
handler.setFormatter(formatter)

# Настройка базового логгера с использованием цветного обработчика
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info("Старт программы.")

# В цикле принимаем данные от пользователя
# Выходим, если пользователь ввел "0"
# Иначе запускаем функцию обработки данных
while True:
    data = input('Введите данные: ')
    if data == '0':
        logger.critical('Выход из программы.')
        break
    logger.info(f'Получены данные: {data}')
    # Обработка данных
    handle_text(data)
