# -*- coding: utf-8 -*-
"""
Модуль подключения к базе данных
Настройка SQLAlchemy и создание сессий для работы с БД
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from backend.config import settings
import os

# ============================================
# Настройка пути к базе данных
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, settings.database_path)

# Создаём директорию для БД если не существует
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# ============================================
# Настройка SQLAlchemy Engine
# ============================================
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False  # Необходимо для SQLite в многопоточном режиме
    },
    echo=False,  # Установите True для отладки SQL запросов
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600  # Переподключение каждый час
)

# ============================================
# Включение внешних ключей для SQLite
# ============================================
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Включение поддержки внешних ключей в SQLite
    Вызывается автоматически при каждом подключении
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# ============================================
# Создание фабрики сессий
# ============================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================
# Базовый класс для моделей
# ============================================
Base = declarative_base()

# ============================================
# Dependency для получения сессии БД
# ============================================
def get_db():
    """
    Генератор сессий базы данных для использования в FastAPI endpoints
    
    Использование:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    
    Yields:
        Session: Сессия SQLAlchemy для работы с БД
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# Функция инициализации БД
# ============================================
def init_db():
    """
    Инициализация базы данных - создание всех таблиц
    ВНИМАНИЕ: Используется только для создания таблиц из моделей SQLAlchemy
    Для полной инициализации с данными используйте database/init_database.py
    """
    # Импортируем все модели для регистрации в Base.metadata
    from backend import models  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
    print(f"✅ База данных инициализирована: {db_path}")

def check_db_connection():
    """
    Проверка подключения к базе данных
    
    Returns:
        bool: True если подключение успешно, False в случае ошибки
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

def get_db_info():
    """
    Получение информации о базе данных
    
    Returns:
        dict: Словарь с информацией о БД
    """
    info = {
        "database_url": DATABASE_URL,
        "database_path": db_path,
        "database_exists": os.path.exists(db_path),
        "connection_ok": check_db_connection()
    }
    
    if info["database_exists"]:
        info["database_size"] = os.path.getsize(db_path)
    
    return info

# ============================================
# Проверка при импорте модуля
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("ИНФОРМАЦИЯ О БАЗЕ ДАННЫХ")
    print("=" * 60)
    
    info = get_db_info()
    
    print(f"\n📁 Путь к БД: {info['database_path']}")
    print(f"🔗 URL подключения: {info['database_url']}")
    print(f"📊 Файл существует: {'✓' if info['database_exists'] else '✗'}")
    
    if info.get('database_size'):
        size_kb = info['database_size'] / 1024
        print(f"💾 Размер файла: {size_kb:.2f} KB")
    
    print(f"🔌 Подключение: {'✓ Успешно' if info['connection_ok'] else '✗ Ошибка'}")
    
    if info['connection_ok']:
        print("\n📋 Проверка таблиц...")
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                )
                tables = result.fetchall()
                
                if tables:
                    print(f"\n✓ Найдено таблиц: {len(tables)}")
                    for table in tables:
                        # Подсчёт записей
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table[0]}"))
                        count = count_result.fetchone()[0]
                        print(f"  • {table[0]:<25} ({count} записей)")
                else:
                    print("⚠️  Таблицы не найдены. Выполните database/init_database.py")
        except Exception as e:
            print(f"❌ Ошибка чтения таблиц: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 60)
