# Обработка входящих сообщений
from ai_engine import PointManagerV2
from actions import actions
from crud import set_attribute
from memory import online_links, memory, negative_actions
from database import get_session


def handle_text(text):
    """Обработка текста"""
    service = PointManagerV2()  # Создаем объект для работы с точками и связями

    # Введена пустая строка
    if not text:
        actions.print_to_console()  # Вывод ответа
        return

    # Обработка введенного текста
    for symbol in text:
        if symbol == "+":
            actions.positive_react()  # Обработка положительной реакции
            return
        if symbol == "-":
            actions.negative_react()  # Обработка отрицательной реакции
            return
        with get_session() as session:
            last_point = service.add_point_with_link(session, symbol)  # Добавляем точку и связь для каждой буквы
            online_links.update()  # Функция Онлайн связи
            set_attribute(session, 'last_point_id', last_point.id)  # Запомнить id последней точки
            memory.add_point_name_to_memory(last_point.name)  # Добавить имя точки в память
            session.commit()

    online_links.save()  # Сохранение списка Онлайн связей в БД
    negative_actions.save()  # Сохранение списка Отрицательных действий

    # TODO: убрать print
    input('Пауза перед Прошивкой...')
    actions.function_firmware()  # Запуск функции прошивки
    input('Пауза перед Выводом...')
    actions.print_to_console()  # Вывод ответа
