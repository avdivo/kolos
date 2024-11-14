# Классы реализующие логику работы ИИ на уровне БД.
# Тут можно реализовать классы для решения разных задач
# или разные варианты класса для решения одной задачи.
# В классовых атрибутах можно хранить настройки для конкретной реализации.

from database import get_session
from contextlib import ContextDecorator

from config import DEFAULT_SIGNAL, DEFAULT_WEIGHT
from crud import get_point_by_name, get_point_with_max_signal, create_or_update_link, create_point

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
        del service  # Сессия закроется при удалении объекта
        """
        self.session_context = get_session()  # Получаем контекстный менеджер как генератор
        self.session = self.session_context.__enter__()  # Входим в контекст вручную

    def add_point_with_link(self, name):
        """ Добавляет точку и связь с другой точкой.
        1. Приходит буква N
        2. Если точки с именем N нет, создается точка с таким именем и сигналом 1.2
        3. Если точка с именем N есть:
            3.1. Находим точки (даже если она одна) с наибольшим сигналом из всех имеющихся.
                 Предположим это K.
            3.2. Уменьшаем их сигнал на 0.1 и сохраняем.
            3.3. Устанавливаем сигнал для точки N = K + 1.2
            3.4. Создаем связи от K к N с весом K.
        """
        # Проверяем существует ли точка с таким именем
        point = get_point_by_name(self.session, name)
        if point:
            # Если точка существует, находим точки с наибольшим сигналом
            points = get_point_with_max_signal(self.session)
            # Для таких точек
            for p in points:
                p.signal -= self.SIGNAL_REDUCTION  # Уменьшаем сигнал
                create_or_update_link(self.session, p, point, p.signal)  # Создаем связь или обновляем вес
            # Устанавливаем сигнал для обновляемой точки
            point.signal = points[0].signal + self.DEFAULT_SIGNAL
        else:
            # Если точка не существует, создаем новую
            create_point(self.session, name, self.DEFAULT_SIGNAL)

    def __del__(self):
        # Закрываем сессию при удалении экземпляра
        self.session_context.__exit__(None, None, None)
