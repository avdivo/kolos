import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from config import SQLALCHEMY_DATABASE_URL


# Импорт моделей
from models import Point, Link, Attribute  # Должны быть импортированы все модели

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
        session.commit()
    except Exception:
        session.rollback()  # Откатываем транзакцию в случае ошибки
        raise  # Пробрасываем исключение дальше
    finally:
        session.close()  # Закрываем сессию после завершения блока


# Декоратор, позволяет получить сессию в методе класса или в статическом.
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