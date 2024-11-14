from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from config import SQLALCHEMY_DATABASE_URL

# Создаем базовый класс для моделей
Base = declarative_base()

# Импорт моделей
from models import Point, Link  # Должны быть импортированы все модели

# Создаем движок для подключения к базе данных
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Только для SQLite
)

# Создаем фабрику для создания сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Контекстный менеджер для управления сессией
# Использование:
# with get_session() as session:
#     session.query(...)
@contextmanager
def get_session():
    """Контекстный менеджер для управления сессией."""
    session = SessionLocal()
    try:
        yield session  # Предоставляем сессию блоку кода
        session.commit()  # Коммитим изменения в случае успеха
    except Exception:
        session.rollback()  # Откатываем транзакцию в случае ошибки
        raise  # Пробрасываем исключение дальше
    finally:
        session.close()  # Закрываем сессию после завершения блока
