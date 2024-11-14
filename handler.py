# Обработка входящих сообщений
from ai_engine import PointManager


def handle_text(text):
    """Обработка текста"""
    service = PointManager()  # Создаем объект для работы с базой данных
    for symbol in text:
        service.add_point_with_link(symbol)  # Добавляем точку и связь для каждой буквы
    del service  # Закрываем сессию
