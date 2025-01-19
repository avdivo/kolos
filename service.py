# Вспомогательные программы
from database import get_session
from sqlalchemy import text
from alembic.config import Config
from alembic import command
import logging

from crud import create_point

logger = logging.getLogger(__name__)


def create_initial_records(session):
    create_point(
        session, 'NEUTRAL',
        type='REACT'  # Тип REACT
    )  # Создаем нейтральную точку
    create_point(
        session, 'NEGATIVE',
        type='REACT'  # Тип REACT
    )  # Создаем негативную точку
    create_point(
        session, 'POSITIVE',
        type='REACT'  # Тип REACT
    )  # Создаем позитивную точку


def initialize_database():
    # Выполнить миграции (для создания БД, если ее нет)
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    # Создать начальные записи
    with get_session() as session:
        create_initial_records(session)


# Очистка БД
def clear_db():
    with get_session() as session:
        session.execute(text('DELETE FROM links;'))
        session.execute(text('DELETE FROM points;'))

        create_initial_records(session)  # Создать начальные записи

    logger.warning("База данных очищена.")
