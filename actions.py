import logging

from crud import (get_point_with_max_signal, update_point_signal, get_points_by_link_id,
                  create_link, get_attribute, get_point_by_name, get_point_by_id,
                  get_link_to_by_point_and_link_id)
from memory import memory, online_links, negative_actions, path
from database import with_session

logger = logging.getLogger(__name__)  # Логгер


class Action:
    """Класс реализует логику реакции на события."""

    @with_session
    def function_firmware(self, session):
        """Функция Прошивка
        """
        logger.warning(f"Работа функции Прошивки.")
        if path.exists():
            logger.info(f"Путь существует.")
            return  # Если есть собранный путь - пропускаем функцию
        if not memory.exists:
            logger.info(f"Список памяти пустой.")
            return  # Если список память пустой - пропускаем функцию

        further = False  # Искать на втором этапе или нет
        while online_links.exists():
            # Поиск целевой точки для связи из списка онлайн связей
            # которая не находится в списке отрицательных действий
            link_id = online_links.get_first_online_links()
            _, point_id = get_points_by_link_id(session, link_id)  # Получаем целевую точку связи (id)

            if point_id not in negative_actions.negative_actions:
                # Если точки нет в списке отрицательных связей - продолжаем работу
                path.add(link_id, point_id)

                further = True
                logger.info(f"Точка найдена. Добавлено: ({link_id}, {point_id}). Строим путь.")

                while further:
                    # Если добавлена точка - реакция (тип REACT) поиск прекратить
                    link_id, point_id = path.get_by_index(-1)  # Последний добавленный элемент пути
                    point = get_point_by_id(session, point_id)
                    if point.type == "REACT":
                        break  # Обойдет else и будет обрабатывать точки реакций

                    link = get_link_to_by_point_and_link_id(session, link_id + 1, point_id)
                    if not link:
                        logger.info(f"Нет связи link_id + 1 от точки {point_id}.")
                        # Нет связи link_id + 1 от данной точки
                        break  #

                    _, point_id = get_points_by_link_id(session, link.id)  # Получаем целевую точку связи (id)
                    if point_id not in negative_actions.negative_actions:
                        # Если точки нет в списке Отрицательных действий - продолжаем работу
                        logger.info(f"Добавлено: ({link_id}, {point_id}).")
                        path.add(link_id, point_id)
                    else:
                        # Иначе продолжаем поиск в списке Онлайн связей
                        logger.info(f"Точка {point_id}) в списке Отрицательных действий.")
                        path.delete_first_online_links()
                        # При естественном завершении цикла сработает else.
                        # Продолжаем перебирать список Онлайн связей.
                        further = False
                else:
                    logger.info(f"При построении пути встречена точка в списке отрицательных действий. Продолжаем поиск.")
                    continue

                # Выход через break значит встречена точка реакции
                logger.info(f"Завершение работы функции прошивки. Путь: {path.path}.")
                break

            else:
                # Иначе продолжаем поиск
                logger.info(f"Точка {point_id} в списке Отрицательных действий")
                path.delete_first_online_links()
        else:
            # Точка не найдена
            logger.info(f"В списке Онлайн связей закончились возможные пути.")
            return

        logger.info(f"Функция Прошивки завершена.")


    @staticmethod
    @with_session
    def positive_react(session):
        """Положительная реакция
        :param session:  сессия из декоратора
        """
        last_point_id = get_attribute(session, 'last_point_id', None)
        point = get_point_by_id(session, last_point_id)
        logger.warning(f"Положительная реакция для {point.name}.")
        if point is None:
            logger.warning(f"Нет последней точки для реакции.")
        positive_point = get_point_by_name(session, 'POSITIVE')
        create_link(session, point, positive_point)  # Создать связь с положительной точкой
        path.clear()  # Очистить путь
        memory.clear()  # Очистить память
        old_point = get_point_with_max_signal(session)  # Находим точку с наибольшим сигналом
        new_max_signal = old_point.signal + 1  # Рассчитываем новый максимальный сигнал
        update_point_signal(session, 'NEUTRAL', new_max_signal)  # Устанавливаем его для нейтральной точки
        online_links.update()  # Запускаем функцию онлайн связи


actions = Action()
