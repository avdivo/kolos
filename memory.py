# Объект для работы с:
# путем
# памятью
# списком онлайн связей
# списком отрицательных действий

import logging

from crud import get_attribute, get_point_with_max_signal, get_links_from, set_attribute
from database import with_session

logger = logging.getLogger(__name__)  # Логгер


class Path:
    """Хранение и работа со списком Путь.
    Список путь: список кортежей [(link_id, point_id),...]"""

    def __init__(self):
        self.path = []  # Список Путь

    def add(self, link_id, point_id):
        """Добавление элемента"""
        self.path.append((link_id, point_id))
        logger.info(f"В список Путь добавлен элемент ({link_id}, {point_id}). Теперь список: {self.path}")

    def exists(self):
        """Проверка, что список Путь не пустой"""
        return bool(self.path)

    def clear(self):
        """Очистить путь"""
        self.path.clear()
        logger.info(f"Список Путь очищен.")

    def get_by_index(self, index: int = 1) -> tuple[int] or None:
        """Вернет элемент по индексу"""
        if self.exists():
            return self.path[index]

    def pop_first(self) -> tuple[int] or None:
        """Удалит и вернет первый элемент."""
        if self.exists():
            el = self.path.pop(0)
            logger.info(f"Удален элемент из списка Путь {el}. Теперь список: {self.path}")
            return el
        return None

    def is_point_first(self, point_id: int) -> bool:
        """Проверяет, находится ли данный идентификатор точки в первой позиции"""
        return self.exists() and self.get_by_index(0)[1] == point_id


class Memory:
    """Хранение и работа со списком Память"""

    def __init__(self):
        self.memory = []  # Память

    def exists(self):
        """Проверка, что список Память не пустой"""
        return bool(self.memory)

    def add_point_name_to_memory(self, name):
        """Добавить имя точки в память"""
        logger.info(f"Добавление в память. {self.memory} + {name}")
        self.memory.append(name)

    def clear(self):
        """Очистить память"""
        self.memory.clear()
        logger.info(f"Память очищена.")


class OnlineLink:
    """Хранение и работа со списком Онлайн связей"""

    @with_session
    def __init__(self, session):
        # Читаем из БД и храним актуальную версию списка
        self.online_links = get_attribute(session, 'online_links', [])
        logger.info(f"Список Онлайн связей: {self.online_links}")

    def exists(self):
        """Проверка, что список Онлайн связей не пустой"""
        return bool(self.online_links)

    @with_session
    def update(self, session):
        """Метод обновляет список Онлайн связей. Список хранится в БД.
        Запускается для точки с максимальным сигналом.
        :param session: сессия из декоратора
        """
        logger.warning(f"Работа функции Онлайн связь.")
        point = get_point_with_max_signal(session)  # Найти точку с максимальным сигналом
        # Найти все исходящие связи полученной точки
        links = get_links_from(point)
        links_id = sorted(list(map(lambda l: l.id, links)), reverse=True)

        # Пересоздаем онлайн список
        new_online_links = []
        for link_id in self.online_links:
            id = link_id + 1
            if id in links_id:
                # Если id+1 из списка онлайн связей есть в новом списке,
                # переносим его в новый список
                new_online_links.append(id)
                links_id.remove(id)
        new_online_links += links_id  # Добавляем оставшиеся id в новый список

        # Записываем новый список онлайн связей в БД
        self.save(new_online_links)
        logger.info(f"Отработала функция Онлайн связь. {self.online_links}")

    def get_first_online_links(self) -> int or None:
        """Получение первой связи из списка онлайн связей.
        Список не меняется.
        """
        if self.online_links:
            return self.online_links[0]
        return None

    def get_and_delete_first_online_links(self):
        """Удаление и возвращение первого элемента из списка онлайн связей. Список в БД не меняется.
        """
        el = None
        if self.online_links:
            el = self.online_links.pop(0)
        logger.info(f"Удален первый элемент из списка Онлайн связей: {el}. Теперь список: {self.online_links}.")
        return el

    def clear(self):
        """Очищает список Онлайн связей. Список в БД не меняется."""
        # Записываем пустой список онлайн связей в БД
        self.online_links.clear()
        logger.info(f"Очищен список Онлайн связей.")

    @with_session
    def save(self, session, new_online_links=None):
        """Сохранение в БД переданного онлайн списка, или текущего.
        Если что-то передано - сохранить это иначе сохранить что есть в свойстве."""
        if new_online_links is not None:
            self.online_links = new_online_links
        set_attribute(session, 'online_links', self.online_links)

    # def __del__(self):
    #     """Сохраняем список Онлайн связей"""
    #     self.save()


class NegativeAction:
    """Хранение и работа со списком Отрицательных действий"""

    @with_session
    def __init__(self, session):
        # Читаем из БД список Отрицательных действий и храним актуальную версию
        self.negative_actions = set(get_attribute(session, 'negative_actions', []))
        logger.info(f"Список Отрицательных действий: {self.negative_actions}")

    def exists(self):
        """Проверка, что список Отрицательных действий не пустой"""
        return bool(self.negative_actions)

    def add(self, point_id):
        """Добавляем id точки в список Отрицательных действий."""
        logger.info(f"Добавлен id в список Отрицательных действий: {self.negative_actions} + {point_id} ")
        self.negative_actions.add(point_id)

    @with_session
    def save(self, session, new_negative_actions=None):
        """Сохранение в БД переданного онлайн списка, или текущего."""
        if new_negative_actions:
            self.negative_actions = new_negative_actions
        set_attribute(session, 'negative_actions', self.negative_actions)

    def clear(self):
        """Очищает список Отрицательных действий. Список в БД не меняется."""
        # Записываем пустой список онлайн связей в БД
        self.negative_actions.clear()
        logger.info(f"Очищен список Отрицательных действий.")

    # def __del__(self):
    #     """Сохраняем список Отрицательных действий."""
    #     self.save()


class InOut:
    """Класс хранит вводимые и выводимые значения в виде списка кортежей (in, out)"""

    def __init__(self):
        self.in_out_string = []

    def add(self, in_str, out_str='Ok'):
        if in_str == '':
            in_str = 'Пустой ввод'
        if in_str == ' ':
            in_str = 'Пробел'
        if out_str == ' ':
            out_str = 'Пробел'
        self.in_out_string.append((in_str, out_str))
        return self.get()

    def get(self):
        return ' | '.join([f"{i} -> {o}" for i, o in self.in_out_string])

    def clear(self):
        self.in_out_string = []


memory = Memory()
online_links = OnlineLink()
negative_actions = NegativeAction()
path = Path()
in_out = InOut()
