# Обработка входящих сообщений
from ai_engine import PointManagerV2
from actions import actions
from crud import set_attribute
from memory import online_links, memory, negative_actions, in_out
from database import get_session


def empty_input(text):
    """Обработка пустого ввода"""
    online_links.update()  # Функция Онлайн связи
    actions.function_firmware()  # Запуск функции прошивки
    out = actions.print_to_console()  # Вывод ответа
    print(in_out.add(text, out))
    return out

def plus(text):
    """Обработка символа +"""
    actions.positive_react()  # Обработка положительной реакции
    online_links.save()  # Сохранение списка Онлайн связей в БД
    negative_actions.save()  # Сохранение списка Отрицательных действий
    print(in_out.add(text))
    in_out.clear()  # Очистка списка ввода-вывода
    return 'Ok'

def minus(text):
    actions.negative_react()  # Обработка отрицательной реакции
    online_links.save()  # Сохранение списка Онлайн связей в БД
    negative_actions.save()  # Сохранение списка Отрицательных действий
    print(in_out.add(text))
    return 'Ok'

def sundry(service, text):
    """Остальные символы"""
    with get_session() as session:
        last_point = service.add_point_with_link(session, text)  # Добавляем точку и связь для каждой буквы
        online_links.update()  # Функция Онлайн связи
        set_attribute(session, 'last_point_id', last_point.id)  # Запомнить id последней точки
        memory.add_point_name_to_memory(last_point.name)  # Добавить имя точки в память
        session.commit()

def handle_text(text):
    """Обработка текста"""
    service = PointManagerV2()  # Создаем объект для работы с точками и связями

    # Введена пустая строка
    if not text:
        return empty_input(text)

    # Обработка введенного текста и реакций
    for symbol in text:
        if symbol == "+":
            return plus(symbol)
        if symbol == "-":
            return minus(symbol)
        sundry(service, symbol)

    online_links.save()  # Сохранение списка Онлайн связей в БД
    negative_actions.save()  # Сохранение списка Отрицательных действий
    actions.function_firmware()  # Запуск функции прошивки
    out = actions.print_to_console()  # Вывод ответа
    print(in_out.add(text, out))
    return out
