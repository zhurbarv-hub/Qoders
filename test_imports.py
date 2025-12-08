print("Проверка импорта пакетов...")

try:
    import fastapi
    print("✓ FastAPI:", fastapi.__version__)
except ImportError as e:
    print("✗ FastAPI не установлен:", e)

try:
    import uvicorn
    print("✓ Uvicorn установлен")
except ImportError as e:
    print("✗ Uvicorn не установлен:", e)

try:
    import sqlalchemy
    print("✓ SQLAlchemy:", sqlalchemy.__version__)
except ImportError as e:
    print("✗ SQLAlchemy не установлен:", e)

try:
    import aiogram
    print("✓ Aiogram:", aiogram.__version__)
except ImportError as e:
    print("✗ Aiogram не установлен:", e)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    print("✓ APScheduler установлен")
except ImportError as e:
    print("✗ APScheduler не установлен:", e)

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv установлен")
except ImportError as e:
    print("✗ python-dotenv не установлен:", e)

print("\n✅ Проверка завершена!")