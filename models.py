from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
from config import DEFAULT_SIGNAL, DEFAULT_WEIGHT


class Point(Base):
    __tablename__ = 'points'

    id = Column(Integer, primary_key=True, index=True)  # Идентификатор точки
    name = Column(String, nullable=False, unique=True, index=True)  # Название точки, уникальное, индексируемое
    signal = Column(Float, nullable=False, default=DEFAULT_SIGNAL)  # Значение сигнала в точке

    # Связи, где данная точка является "началом"
    links_from = relationship("Link",
                              foreign_keys="Link.point_id", back_populates="point_from", cascade="all, delete-orphan")
    # Связи, где данная точка является "концом"
    links_to = relationship("Link",
                            foreign_keys="Link.connected_point_id", back_populates="point_to",
                            cascade="all, delete-orphan")


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, index=True)  # Идентификатор связи
    point_id = Column(Integer, ForeignKey('points.id'), nullable=False)  # Исходная точка
    connected_point_id = Column(Integer, ForeignKey('points.id'), nullable=False)  # Конечная точка
    weight = Column(Float, nullable=False, default=DEFAULT_WEIGHT)  # Вес связи

    # Двусторонняя связь к `Point`, указывающая на "начало" и "конец" связи
    point_from = relationship("Point", foreign_keys=[point_id], back_populates="links_from")
    point_to = relationship("Point", foreign_keys=[connected_point_id], back_populates="links_to")
