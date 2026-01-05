# -*- coding: utf-8 -*-
"""
Сервис планировщика автоматических бэкапов базы данных
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import os
import subprocess
from pathlib import Path

from ..database import SessionLocal
from ..models.backup import BackupSchedule, BackupHistory
from ..api.database_management import get_database_connection_string, BACKUP_DIR

logger = logging.getLogger(__name__)

# Глобальный планировщик
scheduler = AsyncIOScheduler()


def create_backup_task(schedule_id: int):
    """
    Выполнение задачи создания бэкапа
    
    Args:
        schedule_id: ID расписания, которое запустило бэкап
    """
    db = SessionLocal()
    history_record = None
    
    try:
        logger.info(f"Начало выполнения автоматического бэкапа (schedule_id={schedule_id})")
        
        # Создаем запись в истории
        history_record = BackupHistory(
            schedule_id=schedule_id,
            status='running',
            started_at=datetime.now()
        )
        db.add(history_record)
        db.commit()
        db.refresh(history_record)
        
        # Получаем параметры БД
        db_config = get_database_connection_string()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if db_config['type'] == 'postgresql':
            # PostgreSQL бэкап через pg_dump
            filename = f"kkt_auto_backup_{timestamp}.sql"
            filepath = BACKUP_DIR / filename
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            cmd = [
                'pg_dump',
                '-h', db_config['host'],
                '-p', db_config['port'],
                '-U', db_config['user'],
                '-d', db_config['database'],
                '-f', str(filepath),
                '--clean',
                '--if-exists'
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump error: {result.stderr}")
            
            # Получаем размер файла
            file_size = filepath.stat().st_size
            
            # Обновляем историю - успех
            history_record.status = 'success'
            history_record.completed_at = datetime.now()
            history_record.filename = filename
            history_record.size_bytes = file_size
            db.commit()
            
            logger.info(f"Автоматический бэкап успешно создан: {filename} ({file_size} bytes)")
            
        else:
            raise Exception("SQLite автоматический бэкап не поддерживается")
        
        # Обновляем расписание
        schedule = db.query(BackupSchedule).filter(BackupSchedule.id == schedule_id).first()
        if schedule:
            schedule.last_run_at = datetime.now()
            schedule.next_run_at = calculate_next_run(schedule)
            db.commit()
        
        # Очистка старых бэкапов
        cleanup_old_backups(db, schedule_id)
        
    except Exception as e:
        logger.error(f"Ошибка при создании автоматического бэкапа: {e}")
        
        if history_record:
            history_record.status = 'failed'
            history_record.completed_at = datetime.now()
            history_record.error_message = str(e)
            db.commit()
    
    finally:
        db.close()


def cleanup_old_backups(db: Session, schedule_id: int):
    """
    Удаление старых бэкапов согласно retention_days
    
    Args:
        db: Сессия БД
        schedule_id: ID расписания
    """
    try:
        schedule = db.query(BackupSchedule).filter(BackupSchedule.id == schedule_id).first()
        if not schedule:
            return
        
        # Вычисляем дату отсечки
        cutoff_date = datetime.now() - timedelta(days=schedule.retention_days)
        
        # Находим старые записи в истории
        old_records = db.query(BackupHistory).filter(
            BackupHistory.schedule_id == schedule_id,
            BackupHistory.started_at < cutoff_date,
            BackupHistory.status == 'success'
        ).all()
        
        for record in old_records:
            # Удаляем физический файл
            if record.filename:
                filepath = BACKUP_DIR / record.filename
                if filepath.exists():
                    filepath.unlink()
                    logger.info(f"Удален старый бэкап: {record.filename}")
            
            # Удаляем запись из истории
            db.delete(record)
        
        db.commit()
        logger.info(f"Очистка завершена: удалено {len(old_records)} старых бэкапов")
        
    except Exception as e:
        logger.error(f"Ошибка при очистке старых бэкапов: {e}")


def calculate_next_run(schedule: BackupSchedule) -> datetime:
    """
    Вычислить время следующего запуска
    
    Args:
        schedule: Расписание
        
    Returns:
        Время следующего запуска
    """
    from datetime import time as dt_time
    
    now = datetime.now()
    today = now.date()
    run_time = schedule.time_of_day or dt_time(3, 0)
    
    if schedule.frequency == 'daily':
        # Ежедневно в указанное время
        next_run = datetime.combine(today, run_time)
        if next_run <= now:
            next_run = datetime.combine(today + timedelta(days=1), run_time)
        return next_run
    
    elif schedule.frequency == 'weekly':
        # Еженедельно в указанный день недели
        target_weekday = schedule.day_of_week or 0  # 0 = Monday
        days_ahead = target_weekday - today.weekday()
        if days_ahead <= 0:  # Если день уже прошел на этой неделе
            days_ahead += 7
        next_run = datetime.combine(today + timedelta(days=days_ahead), run_time)
        return next_run
    
    elif schedule.frequency == 'monthly':
        # Ежемесячно в указанный день месяца
        target_day = schedule.day_of_month or 1
        if today.day >= target_day and datetime.combine(today, run_time) <= now:
            # Следующий месяц
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=target_day)
            else:
                next_month = today.replace(month=today.month + 1, day=target_day)
            next_run = datetime.combine(next_month, run_time)
        else:
            # Этот месяц
            next_run = datetime.combine(today.replace(day=target_day), run_time)
        return next_run
    
    # По умолчанию - завтра
    return datetime.combine(today + timedelta(days=1), run_time)


def update_scheduler_job(schedule: BackupSchedule):
    """
    Обновить задачу в планировщике
    
    Args:
        schedule: Расписание бэкапов
    """
    job_id = f"backup_schedule_{schedule.id}"
    
    # Удаляем старую задачу если есть
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    if not schedule.enabled:
        logger.info(f"Автобэкап отключен (schedule_id={schedule.id})")
        return
    
    # Создаем cron триггер
    hour, minute = schedule.time_of_day.hour, schedule.time_of_day.minute
    
    if schedule.frequency == 'daily':
        trigger = CronTrigger(hour=hour, minute=minute)
    elif schedule.frequency == 'weekly':
        day_of_week = schedule.day_of_week or 0
        trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
    elif schedule.frequency == 'monthly':
        day = schedule.day_of_month or 1
        trigger = CronTrigger(day=day, hour=hour, minute=minute)
    else:
        logger.error(f"Неизвестная частота: {schedule.frequency}")
        return
    
    # Добавляем задачу
    scheduler.add_job(
        create_backup_task,
        trigger=trigger,
        id=job_id,
        args=[schedule.id],
        name=f"Автоматический бэкап ({schedule.frequency})"
    )
    
    logger.info(f"Задача автобэкапа обновлена: {schedule.frequency} в {hour:02d}:{minute:02d}")


def init_scheduler():
    """
    Инициализация планировщика при старте приложения
    """
    logger.info("Инициализация планировщика автоматических бэкапов")
    
    db = SessionLocal()
    try:
        # Загружаем расписание из БД
        schedules = db.query(BackupSchedule).all()
        
        for schedule in schedules:
            update_scheduler_job(schedule)
            
            # Вычисляем next_run_at если не установлено
            if not schedule.next_run_at:
                schedule.next_run_at = calculate_next_run(schedule)
                db.commit()
        
        # Запускаем планировщик
        if not scheduler.running:
            scheduler.start()
            logger.info("Планировщик автоматических бэкапов запущен")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации планировщика: {e}")
    finally:
        db.close()


def shutdown_scheduler():
    """
    Остановка планировщика при завершении приложения
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Планировщик автоматических бэкапов остановлен")
