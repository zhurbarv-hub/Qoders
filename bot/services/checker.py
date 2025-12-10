# -*- coding: utf-8 -*-
"""
Сервис проверки сроков истечения услуг
Запрашивает данные из базы данных и определяет, какие уведомления нужно отправить
"""

from typing import List, Dict, Optional
from datetime import date
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models
import logging

logger = logging.getLogger(__name__)


def get_expiring_deadlines(days: int) -> List[Dict]:
    """
    Получение списка дедлайнов, истекающих через указанное количество дней
    
    Args:
        days (int): Количество дней до истечения
        
    Returns:
        List[Dict]: Список словарей с информацией о дедлайнах
    """
    try:
        db: Session = SessionLocal()
        
        # Запрос к представлению v_expiring_soon (без @property полей)
        query = db.query(
            models.Deadline.id.label('deadline_id'),
            models.Client.name.label('client_name'),
            models.Client.inn.label('client_inn'),
            models.DeadlineType.type_name.label('deadline_type_name'),
            models.Deadline.expiration_date.label('expiration_date')
        ).join(
            models.Client, models.Deadline.client_id == models.Client.id
        ).join(
            models.DeadlineType, models.Deadline.deadline_type_id == models.DeadlineType.id
        ).filter(
            models.Deadline.status == 'active',
            models.Client.is_active == True
        )
        
        results = query.all()
        
        # Фильтруем и вычисляем в Python
        today = date.today()
        deadlines = []
        for row in results:
            days_remaining = (row.expiration_date - today).days
            
            # Фильтруем по количеству дней
            if days_remaining == days:
                # Определяем статус
                if days_remaining < 7:
                    status = 'red'
                elif days_remaining < 14:
                    status = 'yellow'
                else:
                    status = 'green'
                
                deadlines.append({
                    'deadline_id': row.deadline_id,
                    'client_name': row.client_name,
                    'client_inn': row.client_inn,
                    'deadline_type_name': row.deadline_type_name,
                    'expiration_date': row.expiration_date,
                    'days_remaining': days_remaining,
                    'status': status
                })
            
        logger.debug(f"Найдено {len(deadlines)} дедлайнов, истекающих через {days} дней")
        return deadlines
        
    except Exception as e:
        logger.error(f"Ошибка получения дедлайнов через {days} дней: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []
    finally:
        db.close()


def get_notification_recipients(deadline_id: int) -> List[Dict]:
    """
    Получение списка получателей уведомлений для конкретного дедлайна
    
    Args:
        deadline_id (int): ID дедлайна
        
    Returns:
        List[Dict]: Список словарей с информацией о получателях
    """
    try:
        db: Session = SessionLocal()
        
        # Получаем информацию о дедлайне
        deadline = db.query(models.Deadline).filter(models.Deadline.id == deadline_id).first()
        if not deadline:
            logger.warning(f"Дедлайн с ID {deadline_id} не найден")
            return []
            
        recipients = []
        
        # Добавляем администратора как получателя
        from bot.config import get_bot_config
        config = get_bot_config()
        recipients.append({
            'telegram_id': str(config['telegram_admin_id']),
            'recipient_type': 'admin',
            'client_id': None
        })
        
        # Получаем контакты клиента
        contacts = db.query(models.Contact).filter(
            models.Contact.client_id == deadline.client_id,
            models.Contact.notifications_enabled == True,
            models.Contact.telegram_id.isnot(None)
        ).all()
        
        # Добавляем контакты клиента
        for contact in contacts:
            recipients.append({
                'telegram_id': contact.telegram_id,
                'recipient_type': 'client',
                'client_id': contact.client_id
            })
            
        logger.debug(f"Найдено {len(recipients)} получателей для дедлайна {deadline_id}")
        return recipients
        
    except Exception as e:
        logger.error(f"Ошибка получения получателей для дедлайна {deadline_id}: {e}")
        return []
    finally:
        db.close()


def check_notification_sent(deadline_id: int, days: int, recipient_id: str) -> bool:
    """
    Проверка, было ли уже отправлено уведомление для конкретного дедлайна, дня и получателя
    
    Args:
        deadline_id (int): ID дедлайна
        days (int): Количество дней до истечения
        recipient_id (str): Telegram ID получателя
        
    Returns:
        bool: True если уведомление уже было отправлено, False в противном случае
    """
    try:
        db: Session = SessionLocal()
        
        # Проверяем наличие записи в логах уведомлений
        existing_log = db.query(models.NotificationLog).filter(
            models.NotificationLog.deadline_id == deadline_id,
            models.NotificationLog.recipient_telegram_id == recipient_id
        ).first()
        
        result = existing_log is not None
        if result:
            logger.debug(f"Уведомление для дедлайна {deadline_id}, получателя {recipient_id} уже было отправлено")
            
        return result
        
    except Exception as e:
        logger.error(f"Ошибка проверки отправки уведомления: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # Тестирование сервиса
    print("=" * 50)
    print("ТЕСТ СЕРВИСА ПРОВЕРКИ ДЕДЛАЙНОВ")
    print("=" * 50)
    
    try:
        # Тестируем получение дедлайнов через 14 дней
        deadlines = get_expiring_deadlines(14)
        print(f"Дедлайны через 14 дней: {len(deadlines)}")
        
        if deadlines:
            # Тестируем получение получателей для первого дедлайна
            first_deadline = deadlines[0]
            recipients = get_notification_recipients(first_deadline['deadline_id'])
            print(f"Получатели для дедлайна {first_deadline['deadline_id']}: {len(recipients)}")
            
            # Тестируем проверку отправки уведомления
            if recipients:
                first_recipient = recipients[0]
                sent = check_notification_sent(
                    first_deadline['deadline_id'], 
                    14, 
                    first_recipient['telegram_id']
                )
                print(f"Уведомление отправлено: {sent}")
        
        print("=" * 50)
        print("✅ Тесты пройдены успешно")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")