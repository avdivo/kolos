# Вспомогательные программы
from database import get_session
from sqlalchemy import text
from alembic.config import Config
from alembic import command
import logging

from crud import create_point

logger = logging.getLogger(__name__)


def create_initial_records(session):
    """Создаются 3 обязательные точки
    :param session:
    :return:
    """
    create_point(
        session, 'NEUTRAL', signal=1, type='REACT'
    )
    create_point(
        session, 'NEGATIVE', signal=0, type='REACT'
    )
    create_point(
        session, 'POSITIVE',  signal=0, type='REACT'
    )


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
        session.execute(text('DELETE FROM attributes;'))

        create_initial_records(session)  # Создать начальные записи

    logger.warning("База данных очищена.")
