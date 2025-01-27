# Обработка входящих сообщений
from ai_engine import PointManagerV2
from actions import actions
from crud import set_attribute


def handle_text(text):
    """Обработка текста"""
    service = PointManagerV2()  # Создаем объект для работы с точками и связями

    # Обработка введенного текста
    for symbol in text:
        if symbol == "+":
            actions.positive_react()  # Обработка положительной реакции
            continue
        last_point = service.add_point_with_link(symbol)  # Добавляем точку и связь для каждой буквы

        actions.update_online_links(last_point)  # Функция Онлайн связи
        set_attribute(service.session, 'last_point_id', last_point.id)  # Запомнить id последней точки
        # TODO: Добавить имя точки в список memory (память)
        service.session.commit()  # Применяем изменения


    del service  # Закрываем сессию
