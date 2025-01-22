# Обработка входящих сообщений
from ai_engine import PointManagerV2


def handle_text(text):
    """Обработка текста"""
    service = PointManagerV2()  # Создаем объект для работы с базой данных

    # Обработка введенного текста
    for symbol in text:
        old_point = service.add_point_with_link(symbol)  # Добавляем точку и связь для каждой буквы
        service.online_links(old_point)  # Функция Онлайн связи
        # TODO: Добавить имя точки в список memory (память)

    service.add_neutral_point(old_point)  # Создаем связь с нейтральной точкой

    del service  # Закрываем сессию
