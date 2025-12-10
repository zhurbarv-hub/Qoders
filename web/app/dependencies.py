# -*- coding: utf-8 -*-
"""
Dependency Injection для FastAPI
"""
from typing import Generator
from sqlalchemy.orm import Session
from .database import SessionLocal


def get_db() -> Generator:
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()