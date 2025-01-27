import inspect
import logging
from database import get_session
from crud import (create_unique_link, get_point_with_max_signal, update_point_signal, create_point,
                  get_links_from, create_link, get_attribute, set_attribute, get_point_by_name, get_point_by_id)

logger = logging.getLogger(__name__)  # Логгер


# Универсальный декоратор, позволяет получить сессию в методе класса или в статическом.
def with_session(method):
    all_args_of_method = inspect.signature(method).parameters
    def wrapper(*args, **kwargs):
        with get_session() as session:
            # Если метод связан с экземпляром (обычный метод)
            if 'self' in all_args_of_method:
                return method(args[0], session, *args[1:], **kwargs)
            # Если метод статический
            else:
                return method(session, *args, **kwargs)

    return wrapper


class Action:
    """Класс реализует логику реакции на события."""

    def __init__(self):
        # self.last_point_id = None  # Последняя обработанная точка
        pass

    @staticmethod
    @with_session
    def update_online_links(session):
        """Метод обновляет список онлайн связей. Список хранится в БД.
        Запускается для точки с максимальным сигналом.
        :param session: сессия из декоратора
        :param point:
        """
        point = get_point_with_max_signal(session)  # Найти точку с максимальным сигналом
        # Найти все исходящие связи полученной точки
        links = get_links_from(point)
        links_id = sorted(list(map(lambda l: l.id, links)), reverse=True)

        # Читаем из БД онлайн список
        online_links = get_attribute(session, 'online_links', [])

        # Пересоздаем онлайн список
        new_online_links = []
        for link_id in online_links:
            id = link_id + 1
            if id in links_id:
                # Если id+1 из списка онлайн связей есть в новом списке,
                # переносим его в новый список
                new_online_links.append(id)
                links_id.remove(id)
        new_online_links += links_id  # Добавляем оставшиеся id в новый список

        # Записываем новый список онлайн связей в БД
        set_attribute(session, 'online_links', new_online_links)
        logger.info(f"Отработала функция Онлайн связь.")

    @staticmethod
    @with_session
    def delete_online_links(session):
        """Очищает список онлайн связей. Список хранится в БД
        :param session: сессия из декоратора
        """
        # Записываем пустой список онлайн связей в БД
        set_attribute(session, 'online_links', [])

    @with_session
    def positive_react(self, session):
        """Положительная реакция
        :param session:  сессия из декоратора
        :param point:
        """
        last_point_id = get_attribute(session, 'last_point_id', None)
        point = get_point_by_id(session, last_point_id)
        logger.warning(f"Положительная реакция для {point.name}.")
        if point is None:
            logger.warning(f"Нет последней точки для реакции.")
        positive_point = get_point_by_name(session, 'POSITIVE')
        create_link(session, point, positive_point)  # Создать связь с положительной точкой
        # TODO: очистить список путь, очистить память
        old_point = get_point_with_max_signal(session)  # Находим точку с наибольшим сигналом
        new_max_signal = old_point.signal + 1  # Рассчитываем новый максимальный сигнал
        update_point_signal(session, 'NEUTRAL', new_max_signal)  # Устанавливаем его для нейтральной точки
        self.update_online_links()  # Запускаем функцию онлайн связи

    def add_neutral_point(self, old_point):
        """Создает или получает нейтральную точку, обновляет ее сигнал
        и создает связь от переданной точки к ней."""
        neutral_point = create_point(
            self.session, 'NEUTRAL',
            type='REACT'  # Если создается точка то ее тип будет REACT
        )  # Создаем или получаем нейтральную точку
        neutral_point.signal = old_point.signal + self.SIGNAL_ADDITION

        # Создаем связь старой точки с нейтральной
        create_unique_link(self.session, old_point, neutral_point, neutral_point.signal)


actions = Action()
