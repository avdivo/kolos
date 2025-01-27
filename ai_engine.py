# Классы реализующие логику работы ИИ на уровне БД.
# Тут можно реализовать классы для решения разных задач
# или разные варианты класса для решения одной задачи.
# В классовых атрибутах можно хранить настройки для конкретной реализации.
import logging
from database import get_session
from contextlib import ContextDecorator

from config import DEFAULT_SIGNAL, DEFAULT_WEIGHT
from crud import create_unique_link, get_point_with_max_signal, get_all_points, create_point, create_link

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

class PointManager(ContextDecorator):
    """Класс реализует логику работы ИИ на уровне точек (вершин) и связей.
    Структура базы данных предполагает работу с графами, тут мы их называем точками и связями.
    И используем специальные функции для работы с БД.
    """

    # Настройки для этой реализации
    DEFAULT_SIGNAL = DEFAULT_SIGNAL  # Сигнал по умолчанию для точек
    DEFAULT_WEIGHT = DEFAULT_WEIGHT  # Вес связи по умолчанию
    SIGNAL_REDUCTION = 0.1  # На сколько уменьшаем сигнал

    def __init__(self):
        """Получаем сессию для работы с базой данных.
        Сессия будет закрыта и изменения зафиксированы автоматически.
        Но лучше удалить объект этого класса вручную:
        del service. Сессия закроется при удалении объекта
        """
        self.session_context = get_session()  # Получаем контекстный менеджер как генератор
        self.session = self.session_context.__enter__()  # Входим в контекст вручную

    def add_point_with_link(self, name):
        """ Добавляет точку и связи с другими точками.
        1. Приходит буква 'n'.
        2. Находим наибольший сигнал из всех точек, пусть это Max. Если точек нет, то Max = 1.2.
        3. Создаем точку с именем 'n' или обновляем ее сигнал n.signal = Max + 1.2 - 0.1.
        4. Для всех точек с сигналом Max:
            4.1. Обновляем сигнал Max - 0.1.
            4.2. Создаем связь с 'n' (исходящую, где 'n' - finish) весом Max - 0.1,
                если связи с таким весом еще нет и если сигнал исходящей точки не равен 0.
        """
        # Находим точки с наибольшим сигналом
        points = get_point_with_max_signal(self.session)
        new_max = 0 if not points else points[0].signal - self.SIGNAL_REDUCTION  # Новый максимальный сигнал
        this_point = create_point(self.session, name, 0)  # Создаем или получаем новую точку
        this_point.signal = new_max + self.DEFAULT_SIGNAL  # Обновляем ее сигнал

        # Для всех точек с наибольшим сигналом
        for p in points:
            p.signal = new_max  # Уменьшаем сигнал
            if p.signal:
                # Создаем связь, если сигнал не равен 0
                create_unique_link(self.session, p, this_point, new_max)  # Создаем связь

        self.session.commit()  # Фиксируем изменения

    @classmethod
    def clear_signals(cls):
        """Обнуление сигналов всех точек."""
        with get_session() as session:
            points = get_all_points(session)
            for p in points:
                p.signal = 0
            session.commit()

    def __del__(self):
        """Закрываем сессию при удалении экземпляра.
        Перед этим уменьшаем сигнал всех точек на SIGNAL_REDUCTION, если он не равен 0.
        """
        points = get_all_points(self.session)
        for p in points:
            if p.signal:
                p.signal -= self.SIGNAL_REDUCTION
        self.session.commit()  # Фиксируем изменения
        self.session_context.__exit__(None, None, None)


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

    def __init__(self):
        """Получаем сессию для работы с базой данных.
        Сессия будет закрыта и изменения зафиксированы автоматически.
        Но лучше удалить объект этого класса вручную:
        del service. Сессия закроется при удалении объекта
        """
        self.session_context = get_session()  # Получаем контекстный менеджер как генератор
        self.session = self.session_context.__enter__()  # Входим в контекст вручную

    def add_point_with_link(self, name):
        """ Добавляет точку и связи.
        """
        logger.warning(f"Ввод {name}.")
        old_point = get_point_with_max_signal(self.session)  # Находим точку с наибольшим сигналом
        new_max_signal = old_point.signal + self.SIGNAL_ADDITION  # Рассчитываем новый максимальный сигнал

        this_point = create_point(self.session, name, 0)  # Создаем или получаем новую точку типа IN
        this_point.signal = new_max_signal  # Обновляем ее сигнал

        create_link(self.session, old_point, this_point)  # Создаем связь старой точки с новой ВЕС 1

        self.session.commit()  # Фиксируем изменения

        return this_point  # Возвращаем созданную или последнюю точку

    def __del__(self):
        """Закрываем сессию при удалении экземпляра.
        Перед этим уменьшаем сигнал всех точек на SIGNAL_REDUCTION, если он не равен 0.
        """
        self.session_context.__exit__(None, None, None)


