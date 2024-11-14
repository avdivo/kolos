# Вспомогательные программы
from database import get_session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


# Очистка БД
def clear_db():
    with get_session() as session:
        session.execute(text('DELETE FROM links;'))
        session.execute(text('DELETE FROM points;'))
    logger.warning("База данных очищена.")
