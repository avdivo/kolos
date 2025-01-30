# Классы реализующие логику работы ИИ на уровне БД.
# Тут можно реализовать классы для решения разных задач
# или разные варианты класса для решения одной задачи.
# В классовых атрибутах можно хранить настройки для конкретной реализации.
import logging
from contextlib import ContextDecorator

from config import DEFAULT_SIGNAL, DEFAULT_WEIGHT
from crud import get_point_with_max_signal, create_point, create_link

logger = logging.getLogger(__name__)  # Логгер


'''Шаблон класса для реализации логики работы ИИ.

class MyService(ContextDecorator):
    def __init__(self):
        """Получаем сессию для работы с базой данных.
        Сессия будет закрыта и изменения зафиксированы автоматически.
        Но лучше удалить объект этого класса вручную:
        del service  # Сессия закроется при удалении объекта
        """
        self.session_context = get_session()  # Получаем контекстный менеджер как генератор
        self.session = self.session_context.__enter__()  # Входим в контекст вручную

    def do_something(self):
        # Методы для реализующие логику работы ИИ
        pass

    def __del__(self):
        # Закрываем сессию при удалении экземпляра
        self.session_context.__exit__(None, None, None)
'''

class PointManagerV2(ContextDecorator):
    """Класс реализует логику работы ИИ на уровне точек (вершин) и связей.
    Структура базы данных предполагает работу с графами, тут мы их называем точками и связями.
    И используем специальные функции для работы с БД.
    """

    # Настройки для этой реализации
    DEFAULT_SIGNAL = DEFAULT_SIGNAL  # Сигнал по умолчанию для точек
    SIGNAL_ADDITION = 1  # На сколько увеличить сигнал у сл. точки

    DEFAULT_WEIGHT = DEFAULT_WEIGHT  # Вес связи по умолчанию
    SIGNAL_REDUCTION = 0.1  # На сколько уменьшаем сигнал

    def add_point_with_link(self, session,  name):
        """ Добавляет точку и связи.
        """
        logger.warning(f"Ввод {name}.")
        old_point = get_point_with_max_signal(session)  # Находим точку с наибольшим сигналом
        new_max_signal = old_point.signal + self.SIGNAL_ADDITION  # Рассчитываем новый максимальный сигнал

        this_point = create_point(session, name, 0)  # Создаем или получаем новую точку типа IN
        print(this_point.id)
        this_point.signal = new_max_signal  # Обновляем ее сигнал

        create_link(session, old_point, this_point)  # Создаем связь старой точки с новой ВЕС 1
        return this_point  # Возвращаем созданную или последнюю точку



