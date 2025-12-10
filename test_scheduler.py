"""
Тест планировщика - проверка настройки и расписания
"""
import asyncio
from datetime import datetime
from bot.main import create_bot, setup_scheduler
from backend.database import SessionLocal
from backend.config import settings

async def test_scheduler():
    print("=" * 60)
    print("ТЕСТ ПЛАНИРОВЩИКА")
    print("=" * 60)
    
    bot = create_bot()
    db_session = SessionLocal()
    
    print("\n📋 Конфигурация из .env:")
    print(f"   Время проверки: {settings.notification_check_time}")
    print(f"   Часовой пояс: {settings.notification_timezone}")
    print(f"   Дни уведомлений: {settings.notification_days_list}")
    
    print("\n🔧 Настройка планировщика...")
    scheduler = setup_scheduler(bot, db_session)
    
    # ВАЖНО: Нужно запустить планировщик, чтобы получить next_run_time
    scheduler.start()
    
    print("\n📅 Запланированные задачи:")
    for job in scheduler.get_jobs():
        print(f"   • ID: {job.id}")
        print(f"     Название: {job.name}")
        print(f"     Следующий запуск: {job.next_run_time}")
        print(f"     Триггер: {job.trigger}")
        print()
    
    print("⏰ Текущее время:")
    print(f"   Системное: {datetime.now()}")
    print(f"   В часовом поясе {settings.notification_timezone}: {datetime.now(scheduler.timezone)}")
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЁН")
    print("=" * 60)
    
    scheduler.shutdown(wait=False)
    db_session.close()
    await bot.session.close()

if __name__ == '__main__':
    asyncio.run(test_scheduler())