import os

# Устанавливаем базовую директорию проекта и путь к базе данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'kolos.db')}"

# Значение сигнала по умолчанию для точек
DEFAULT_SIGNAL = 1
# Значение веса связи по умолчанию
DEFAULT_WEIGHT = 1