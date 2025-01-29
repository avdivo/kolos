import json
from typing import Optional, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from models import Point, Link, Attribute
from config import DEFAULT_SIGNAL, DEFAULT_WEIGHT
import logging

logger = logging.getLogger(__name__)  # Логгер


# Функция для добавления новой точки с проверкой уникальности имени
def create_point(db: Session, name: str, signal: float = DEFAULT_SIGNAL, type='IN') -> Point:
    """Создает новую точку и добавляет её в базу данных.
    Возвращает существующую точку, если имя уже занято.
    """
    point = get_point_by_name(db, name)
    if point:
        logger.warning(f"Точка с именем '{name}' уже существует.")
        return point

    point = Point(name=name, signal=signal, type=type)
    db.add(point)
    logger.info(f"Создана точка '{name}'.")
    return point


# Функция для получения точки по ID
def get_point_by_id(db: Session, point_id: int) -> Point:
    """Возвращает точку по её ID или None, если точка не найдена."""
    return db.query(Point).filter(Point.id == point_id).first()


# Функция для получения точки по имени
def get_point_by_name(db: Session, name: str) -> Point:
    """Возвращает точку по её имени или None, если точка не найдена."""
    return db.query(Point).filter(Point.name == name).first()


# Функция для получения всех точек
def get_all_points(db: Session):
    """Возвращает список всех точек в базе данных."""
    return db.query(Point).all()


# Получение входящей и исходящей точек по связи
def get_points_by_link_id(db: Session, link_id: int) -> tuple[int] or None:
    """Находит 2 точки связи от какой к какой по id связи
    :param db:
    :param link_id:
    :return: 2 точки связи входящая и исходящая
    """
    result = (
        db.query(Link.point_id, Link.connected_point_id)
        .filter(Link.id == link_id)
        .one_or_none()
    )
    return result


# Функция для обновления сигнала точки с заданным именем
def update_point_signal(db: Session, point_name: str, new_signal: float) -> Point:
    """Обновляет сигнал существующей точки и возвращает её.
    Точку находит по имени."""
    point = db.query(Point).filter(Point.name == point_name).first()
    if point:
        point.signal = new_signal
        logger.info(f"Обновлена точка '{point.name}'.")
    return point


# Поиск точки с максимальным сигналом
def get_point_with_max_signal(db: Session) -> Point:
    """Возвращает точку с максимальным сигналом."""
    # Получаем максимальное значение сигнала
    max_signal = db.query(func.max(Point.signal)).scalar()
    # Возвращаем точку с этим значением сигнала
    return db.query(Point).filter(Point.signal == max_signal).first()


# Функция для удаления точки и её связей
def delete_point(db: Session, point: Point):
    """Удаляет точку и все её связи, используя каскадное удаление."""
    db.delete(point)  # Удаляем точку, SQLAlchemy автоматически удалит связанные связи благодаря cascade
    logger.warning(f"Удалена точка '{point.name}'.")


# Функция для создания связи между двумя точками, даже если она есть с таким весом
def create_link(db: Session, point_from: Point, point_to: Point, weight: float = DEFAULT_WEIGHT) -> Link:
    """Создает связь между двумя точками."""
    link = Link(point_from=point_from, point_to=point_to, weight=weight)
    db.add(link)
    logger.info(f"Создана связь '{point_from.name}' - '{point_to.name}' с весом {round(weight, 1)}.")

    return link


# Функция для создания связи между двумя точками, если связи с таким весом еще нет
def create_unique_link(db: Session, point_from: Point, point_to: Point, weight: float = DEFAULT_WEIGHT) -> Link:
    """Создает связь между двумя точками, если связи с таким весом еще нет."""
    # Ищем существующую связь с нужным весом среди связей данных точек
    existing_link = db.query(Link).filter(
        Link.point_id == point_from.id,
        Link.connected_point_id == point_to.id,
        Link.weight == weight
    ).first()

    if not existing_link:
        # Если связи с таким весом еще нет, создаем ee
        link = Link(point_from=point_from, point_to=point_to, weight=weight)
        db.add(link)
        logger.info(f"Создана связь '{point_from.name}' - '{point_to.name}' с весом {round(weight, 1)}.")
    else:
        link = existing_link
        logger.warning(f"Связь '{point_from.name}' - '{point_to.name}' с весом {round(weight, 1)} уже существует.")

    return link


# Функция для создания или обновления связи между двумя точками
def create_or_update_link(db: Session, point_from: Point, point_to: Point, weight: float = DEFAULT_WEIGHT) -> Link:
    """Создает или обновляет связь между двумя точками. Если связь уже существует, обновляет её вес."""
    # Ищем существующую связь с использованием двойного фильтра на уровне базы данных
    existing_link = db.query(Link).filter(
        Link.point_id == point_from.id,
        Link.connected_point_id == point_to.id
    ).first()

    if existing_link:
        # Если связь уже существует, обновляем её вес
        existing_link.weight = weight
        logger.info(f"Обновлена связь '{point_from.name}' - '{point_to.name}'.")
    else:
        # Создаем новую связь, если её нет
        link = Link(point_from=point_from, point_to=point_to, weight=weight)
        db.add(link)
        existing_link = link  # Присваиваем ссылку на новый объект existing_link для возвращаемого значения
        logger.info(f"Создана связь '{point_from.name}' - '{point_to.name}'.")
    return existing_link


# Функция для получения всех связей для заданной точки
def get_links_for_point(point: Point):
    """Возвращает все связи для указанной точки, используя отношения links_from и links_to."""
    return point.links_from + point.links_to


# Функция для получения исходящих связей для заданной точки
def get_links_from(point: Point):
    """Возвращает исходящие связи для указанной точки, используя отношения links_from."""
    return point.links_from


# Получение связи с нужным id от заданной точки
def get_link_to_by_point_and_link_id(db: Session, point_id: int, link_id: int) -> Link or None:
    """Получение связи с нужным id от заданной точки
    :param db:
    :param point_id:
    :param link_id:
    :return: link or None
    """
    link = db.query(Link).filter(
        Link.point_id == point_id,
        Link.id == link_id
    ).one_or_none()
    return link


def get_link_by_id(db: Session, link_id: int) -> Link or None:
    """Возвращает связь по ее id"""
    return db.query(Link).filter(Link.id == link_id).one_or_none()


# Функция для обновления веса существующей связи по её ID
def update_link_weight(db: Session, link_id: int, new_weight: float) -> Link:
    """Обновляет вес связи по её ID."""
    link = db.query(Link).filter(Link.id == link_id).first()
    if link:
        link.weight = new_weight
        logger.info(f"Обновлена связь '{link.point_from.name}' - '{link.point_to.name}'.")
    return link


# Функция для записи атрибута
def set_attribute(db: Session, key: str, value: object) -> None:
    """
    Добавляет или обновляет запись в таблице attributes.
    """
    value_as_json = json.dumps(value)  # Сериализация значения в JSON
    # Попытка найти существующий ключ
    attribute = db.query(Attribute).filter_by(key=key).first()

    if attribute:
        # Если ключ найден — обновляем значение
        attribute.value = value_as_json
    else:
        # Если ключа нет — создаем новую запись
        new_attribute = Attribute(key=key, value=value_as_json)
        db.add(new_attribute)


# Функция для чтения атрибута
def get_attribute(db: Session, key: str, default: Optional[Any] = None) -> Optional[Any]:
    """
    Получает значение из таблицы attributes по ключу.
    Если ключа нет, вернет значение по умолчанию.
    """
    attribute = db.query(Attribute).filter_by(key=key).first()

    if attribute:
        return json.loads(attribute.value)  # Десериализация значения из JSON
    else:
        return default
