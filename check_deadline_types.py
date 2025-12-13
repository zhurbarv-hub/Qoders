# -*- coding: utf-8 -*-
"""
Скрипт для проверки типов услуг (deadline types) в базе данных
"""
import sys
from pathlib import Path

# Добавляем путь к проекту
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from web.app.models.client import DeadlineType

# Путь к базе данных
DATABASE_PATH = BASE_DIR / "database" / "kkt_services.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Создание подключения
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def main():
    """Проверка типов услуг"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("ТИПЫ УСЛУГ (DEADLINE TYPES)")
        print("="*60 + "\n")
        
        types = db.query(DeadlineType).all()
        
        if not types:
            print("❌ Типы услуг не найдены в базе данных")
            return
        
        print(f"📊 Всего типов: {len(types)}\n")
        
        for t in types:
            print(f"ID: {t.id}")
            print(f"  Название: {t.type_name}")
            print(f"  Описание: {t.description or '-'}")
            print(f"  Активен: {'✅ Да' if t.is_active else '❌ Нет'}")
            print(f"  Системный: {'🔒 Да' if t.is_system else 'Нет'}")
            print("-" * 60)
        
        # Статистика
        active_count = sum(1 for t in types if t.is_active)
        system_count = sum(1 for t in types if t.is_system)
        
        print(f"\n📈 Статистика:")
        print(f"  Активных: {active_count}/{len(types)}")
        print(f"  Системных: {system_count}/{len(types)}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
