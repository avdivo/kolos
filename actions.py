import logging

from crud import (get_point_with_max_signal, update_point_signal, get_points_by_link_id,
                  create_link, get_attribute, get_point_by_name, get_point_by_id,
                  get_link_to_by_point_and_link_id, get_point_with_any_signal)
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

        while online_links.exists():
            # Поиск целевой точки для связи из списка онлайн связей
            # которая не находится в списке отрицательных действий
            link_id = online_links.get_first_online_links()
            _, point_id = get_points_by_link_id(session, link_id)  # Получаем целевую точку связи (id)

            if point_id not in negative_actions.negative_actions:
                # Если точки нет в списке отрицательных связей - продолжаем работу
                path.add(link_id, point_id)

                further = True
                logger.info(f"Точка найдена. Строим путь.")

                while further:
                    # Если добавлена точка - реакция (тип REACT) поиск прекратить
                    link_id, point_id = path.get_by_index(-1)  # Последний добавленный элемент пути
                    point = get_point_by_id(session, point_id)
                    if point.type == "REACT":
                        break  # Обойдет else и будет обрабатывать точки реакций
                    # Получаем связь исходящую от точки с link_id + 1 (т.е. с 2 условиями)
                    link = get_link_to_by_point_and_link_id(session, link_id + 1, point_id)
                    if not link:
                        logger.info(f"Нет связи link_id + 1 от точки {point_id}.")
                        # Нет связи link_id + 1 от данной точки
                        break  # Продолжаем просмотр списка Онлайн связей

                    _, point_id = get_points_by_link_id(session, link.id)  # Получаем целевую точку связи (id)
                    if point_id not in negative_actions.negative_actions:
                        # Если точки нет в списке Отрицательных действий - продолжаем работу
                        path.add(link.id, point_id)
                    else:
                        # Иначе продолжаем поиск в списке Онлайн связей
                        logger.info(f"Точка {point_id}) в списке Отрицательных действий.")
                        path.get_and_delete_first_online_links()
                        path.clear()  # Очищаем путь
                        negative_actions.add(point_id)  # Добавляем точку в список Отрицательных действий
                        # При естественном завершении цикла сработает else.
                        # Продолжаем перебирать список Онлайн связей.
                        further = False
                else:
                    logger.info(
                        f"При построении пути встречена точка в списке отрицательных действий. Продолжаем поиск.")
                    continue

                # Выход через break значит встречена точка реакции или нет связи link_id + 1
                logger.info(f"Завершение работы функции прошивки. Путь: {path.path}.")
                break

            else:
                # Иначе продолжаем поиск
                logger.info(f"Точка {point_id} в списке Отрицательных действий")
                path.clear()  # Очищаем путь
                negative_actions.add(point_id)  # Добавляем точку в список Отрицательных действий
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
        logger.info(f"Завершение работы функции Положительной реакции.")
        online_links.update()  # Запускаем функцию онлайн связи

    @with_session
    def negative_react(self, session):
        """Отрицательная реакция
        :param session:  сессия из декоратора
        """
        last_point_id = get_attribute(session, 'last_point_id', None)
        point = get_point_by_id(session, last_point_id)
        logger.warning(f"Отрицательная реакция для {point.name}.")
        point_max_signal = get_point_with_max_signal(session)
        logger.warning(f"Точка с максимальным сигналом (для проверки) {point_max_signal.name}.")
        if point is None:
            logger.warning(f"Нет последней точки для реакции.")
        negative_actions.add(point.id)  # Добавить точку с сигналом MAX в список отрицательных действий
        update_point_signal(session, point.name, 1)  # Уменьшить сигнал точки с сигналом MAX до 1
        path.clear()  # Очистить Путь
        online_links.update()  # Функция онлайн связей
        self.function_firmware()  # функция Прошивка


    @with_session
    def print_to_console(self, session):
        """Вывод текста в консоль.
        Данные для вывода берутся из списка Путь,
        второй элемент которого представляет точку,
        ее название выводится."""
        if not path.exists():
            logger.warning(f"Нет данных для вывода. Путь пустой.")
            return
        logger.warning(f"Вывод в консоль.")
        _, point_id = path.pop_first()  # Первый элемент в пути
        point = get_point_by_id(session, point_id)  # Первая точка в пути
        point_max = get_point_with_max_signal(session)  # Точка с максимальным сигналом
        if point.type == "REACT":
            neutral_point = get_point_by_name(session, 'NEUTRAL')  # Нейтральная точка
            create_link(session, point_max, neutral_point)  # Создать связь от точки с max сигналом к нейтральной точке
            neutral_point.signal = point_max.signal + 1  # Сигнал Нейтральной точки max+1
            logger.info(f"Сигнал точки NEUTRAL установлен {point_max.signal + 1}.")
            memory.clear()  # Удалить список Память
            logger.info(f"Удален список Память.")
        else:
            point.signal = point_max.signal + 1  # Сигнал первой точки в пути max+1
            logger.info(f"Сигнал точки {point.name} установлен {point_max.signal + 1}.")
            point_max_minus_one = get_point_with_any_signal(session, point_max.signal)  # Точка с прежним сигналом max
            create_link(session, point_max_minus_one, point)  # Создать связь от предыдущей точки к этой точке
            print("*****************************")
            print(point.name)
            print("*****************************")


actions = Action()
