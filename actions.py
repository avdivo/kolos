import logging
from pyexpat.errors import messages

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
        # 1
        if path.exists():
            path.clear()  # Очистка пути
            logger.info(f"Путь существует. Удален. Продолжаем.")
        # 2
        if not memory.exists:
            logger.info(f"Список памяти пустой. Выход.")
            return  # Если список память пустой - пропускаем функцию

        # 1 этап поиска, читает из списка Онлайн связей
        # Поиск целевой точки для связи из списка онлайн связей
        # которая не находится в списке отрицательных действий или находится, но не первая в Пути
        while online_links.exists():
            # 3
            link_id = online_links.get_first_online_links()  # Чтение связи из списка Онлайн связи
            # 4
            _, point_id = get_points_by_link_id(session, link_id)  # Получаем целевую точку связи (id)
            logger.info(f"По связи {link_id} найдена точка {point_id}")
            # 5
            if point_id in negative_actions.negative_actions:
                # Если точка в списке отрицательных действий
                logger.info(f"Точка {point_id} в списке Отрицательных действий")
                online_links.get_and_delete_first_online_links()  # Удалить онлайн связь
                continue  # и продолжить поиск
            point = get_point_by_id(session, point_id)  # Получаем объект точки
            # 6
            if point.type == 'REACT':
                # Если точка имеет тип REACT
                logger.info(f"Точка {point_id} является Реакцией.")
                online_links.get_and_delete_first_online_links()  # Удалить онлайн связь
                continue  # и продолжить поиск

            # 2 этап поиска, находит связи с нужным id
            # Точка не в списке отрицательных действий или в списке, но не первая в пути
            logger.info(f"Строим путь.")
            further = True
            while further:
                # 7
                path.add(link_id, point_id)  # Добавить связь и точку в Путь

                link_id, point_id = path.get_by_index(-1)  # Последний добавленный элемент пути
                # 8
                if point_id in negative_actions.negative_actions and path.is_point_first(point_id):
                    # Если точка в списке Отрицательных действий и при этом первая в Пути
                    logger.info(f"Точка {point_id}) в списке Отрицательных действий и первая в списке Путь.")
                    online_links.get_and_delete_first_online_links()  # Удалить онлайн связь
                    path.clear()  # Очищаем путь
                    break  # Выход из внутреннего цикла

                # Если добавлена точка - реакция (тип REACT)
                point = get_point_by_id(session, point_id)  # Получаем объект точки
                if point.type == "REACT":
                    # Добавлена точка с реакцией
                    message = "В Путь добавлена Положительная или нейтральная реакция."
                    if point.name == "NEGATIVE":
                        # 9
                        message = "В Путь добавлена Отрицательная реакция."
                        # Если реакция негативная
                        link_id, point_id = path.get_by_index(-2)  # Предыдущее добавление в Путь
                        # id точки, которая ведет к отрицательной реакции
                        # добавляется в список отрицательных действий
                        negative_actions.add(point_id)

                    # 10
                    # Если реакция положительная или нейтральная
                    further = False  # Естественное завершение цикла ведет в блок else
                    logger.info(message)
                    continue  # Естественный выход из цикла, попадает в блок else

                # Добавлена точка не с реакцией
                # Получаем связь исходящую от точки с link_id + 1 (т.е. с 2 условиями)
                link_id += 1
                # 11
                link = get_link_to_by_point_and_link_id(session, link_id, point_id)
                if not link:
                    # 12
                    logger.info(f"Нет связи link_id + 1 от точки {point_id}.")
                    # Нет связи link_id + 1 от данной точки
                    further = False  # Естественное завершение цикла ведет в блок else
                    continue

                logger.info(f"Найдена связь link_id + 1 = {link_id}, по ней точка {point_id}")

                # 13
                _, point_id = get_points_by_link_id(session, link_id)  # Получаем целевую точку связи (id)

                # 14
                # Продолжается 2 этап поиска

            else:
                # Естественное завершение while further
                # Если реакция положительная или нейтральная
                # Нет связи link_id + 1 от данной точки
                logger.info(f"Завершение Прошивки.")
                return  # Выход из функции прошивки

        else:
            # Кончились элементы в списке Онлайн связей
            logger.info(f"Закончился список Онлайн связей.")

        return

    @staticmethod
    @with_session
    def positive_react(session):
        """Положительная реакция
        :param session:  сессия из декоратора
        """
        # last_point_id = get_attribute(session, 'last_point_id', None)
        # point = get_point_by_id(session, last_point_id)
        point = get_point_with_max_signal(session)
        logger.warning(f"Положительная реакция для {point.name}.")
        if point is None:
            logger.warning(f"Нет последней точки для реакции.")
        positive_point = get_point_by_name(session, 'POSITIVE')
        create_link(session, point, positive_point)  # Создать связь с положительной точкой
        path.clear()  # Очистить путь
        memory.clear()  # Очистить память
        negative_actions.clear()  # Очистить список Отрицательных действий
        old_point = get_point_with_max_signal(session)  # Находим точку с наибольшим сигналом
        new_max_signal = old_point.signal + 1  # Рассчитываем новый максимальный сигнал
        update_point_signal(session, 'NEUTRAL', new_max_signal)  # Устанавливаем его для нейтральной точки
        logger.info(f"Завершение работы функции Положительной реакции.")
        session.commit()
        online_links.update()  # Запускаем функцию онлайн связи

    @with_session
    def negative_react(self, session):
        """Отрицательная реакция
        :param session:  сессия из декоратора
        """
        # last_point_id = get_attribute(session, 'last_point_id', None)
        # point = get_point_by_id(session, last_point_id)
        point = get_point_with_max_signal(session)
        logger.warning(f"Отрицательная реакция для {point.name}.")
        # logger.warning(f"Точка с максимальным сигналом (для проверки) {point_max_signal.name}.")
        if point is None:
            logger.warning(f"Нет последней точки для реакции.")
        negative_point = get_point_by_name(session, 'NEGATIVE')  # Получаем негативную точку
        create_link(session, point, negative_point)  # Создаем связь с негативной точкой
        negative_actions.add(point.id)  # Добавить точку с сигналом MAX в список отрицательных действий
        update_point_signal(session, point.name, 1)  # Уменьшить сигнал точки с сигналом MAX до 1
        path.clear()  # Очистить Путь
        session.commit()
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
            return 'Нет данных'
        logger.warning(f"Вывод в консоль.")
        _, point_id = path.pop_first()  # Первый элемент в пути
        point = get_point_by_id(session, point_id)  # Первая точка в пути
        point_max = get_point_with_max_signal(session)  # Точка с максимальным сигналом
        out = "REACT"
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
            if point_max_minus_one:
                create_link(session, point_max_minus_one, point)  # Создать связь от предыдущей точки к этой точке
            out = point.name
            print("*****************************")
            print(point.name)
            print("*****************************")
        return out


actions = Action()
