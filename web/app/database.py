# -*- coding: utf-8 -*-
"""
Конфигурация базы данных для веб-интерфейса
Использует общую конфигурацию из backend.config
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from backend.config import settings
import os

# Получаем URL базы данных из настроек
DATABASE_URL = settings.get_database_url()

# Определяем тип БД
is_sqlite = DATABASE_URL.startswith('sqlite')

# Создание engine
if is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
        pool_pre_ping=True
    )
else:
    # PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Включение внешних ключей для SQLite
if is_sqlite:
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()