"""
СУБД для фиксации сроков истечения сервисов
Модуль для работы с базой данных отслеживания подписок и сервисов
"""

import sqlite3
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json


class ServiceTracker:
    """Класс для управления базой данных сервисов и подписок"""
    
    def __init__(self, db_path: str = "services.db"):
        """
        Инициализация подключения к базе данных
        
        Args:
            db_path: путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._connect()
        self._initialize_database()
    
    def _connect(self):
        """Устанавливает соединение с базой данных"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # для доступа к колонкам по имени
        self.cursor = self.connection.cursor()
    
    def _initialize_database(self):
        """Инициализирует структуру базы данных из schema.sql"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                self.cursor.executescript(schema_sql)
                self.connection.commit()
    
    def close(self):
        """Закрывает соединение с базой данных"""
        if self.connection:
            self.connection.close()
    
    # ==================== СЕРВИСЫ ====================
    
    def add_service(self, service_name: str, description: str = None, 
                   provider: str = None, category: str = None, 
                   cost: float = None, currency: str = "RUB") -> int:
        """
        Добавляет новый сервис в базу данных
        
        Args:
            service_name: название сервиса (уникальное)
            description: описание сервиса
            provider: поставщик сервиса
            category: категория сервиса
            cost: стоимость сервиса
            currency: валюта
        
        Returns:
            ID созданного сервиса
        """
        query = """
            INSERT INTO services (service_name, description, provider, category, cost, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(query, (service_name, description, provider, category, cost, currency))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Сервис с именем '{service_name}' уже существует")
    
    def get_service(self, service_id: int) -> Optional[Dict]:
        """Получает информацию о сервисе по ID"""
        query = "SELECT * FROM services WHERE id = ?"
        self.cursor.execute(query, (service_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_services(self, active_only: bool = True) -> List[Dict]:
        """Получает список всех сервисов"""
        query = "SELECT * FROM services"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY service_name"
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_service(self, service_id: int, **kwargs) -> bool:
        """
        Обновляет информацию о сервисе
        
        Args:
            service_id: ID сервиса
            **kwargs: поля для обновления
        
        Returns:
            True если обновление успешно
        """
        allowed_fields = ['service_name', 'description', 'provider', 'category', 'cost', 'currency', 'is_active']
        
        # Фильтруем только разрешенные поля
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        # Добавляем updated_at
        updates['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE services SET {set_clause} WHERE id = ?"
        
        values = list(updates.values()) + [service_id]
        self.cursor.execute(query, values)
        self.connection.commit()
        
        return self.cursor.rowcount > 0
    
    def delete_service(self, service_id: int) -> bool:
        """
        Удаляет сервис (мягкое удаление - устанавливает is_active = 0)
        
        Args:
            service_id: ID сервиса
        
        Returns:
            True если удаление успешно
        """
        return self.update_service(service_id, is_active=0)
    
    # ==================== ПОДПИСКИ ====================
    
    def add_subscription(self, service_id: int, start_date: str, 
                        expiration_date: str, subscription_type: str = "monthly",
                        auto_renewal: bool = False, notification_days: int = 30,
                        notes: str = None) -> int:
        """
        Добавляет новую подписку на сервис
        
        Args:
            service_id: ID сервиса
            start_date: дата начала подписки (YYYY-MM-DD)
            expiration_date: дата истечения подписки (YYYY-MM-DD)
            subscription_type: тип подписки (monthly, yearly, one-time)
            auto_renewal: автоматическое продление
            notification_days: за сколько дней уведомлять об истечении
            notes: дополнительные заметки
        
        Returns:
            ID созданной подписки
        """
        query = """
            INSERT INTO subscriptions 
            (service_id, start_date, expiration_date, subscription_type, 
             auto_renewal, notification_days, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        self.cursor.execute(query, (service_id, start_date, expiration_date, 
                                   subscription_type, auto_renewal, 
                                   notification_days, notes))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_subscription(self, subscription_id: int) -> Optional[Dict]:
        """Получает информацию о подписке по ID"""
        query = "SELECT * FROM subscriptions WHERE id = ?"
        self.cursor.execute(query, (subscription_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_active_subscriptions(self) -> List[Dict]:
        """Получает список всех активных подписок с информацией о сервисе"""
        query = "SELECT * FROM v_active_subscriptions ORDER BY days_until_expiration"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_expiring_subscriptions(self, days: int = None) -> List[Dict]:
        """
        Получает список истекающих подписок
        
        Args:
            days: количество дней до истечения (если None, использует notification_days из подписки)
        
        Returns:
            Список подписок, которые скоро истекут
        """
        if days is None:
            query = "SELECT * FROM v_expiring_subscriptions"
            self.cursor.execute(query)
        else:
            query = """
                SELECT 
                    s.service_name,
                    s.provider,
                    sub.expiration_date,
                    sub.status,
                    CAST((julianday(sub.expiration_date) - julianday('now')) AS INTEGER) as days_until_expiration,
                    sub.auto_renewal
                FROM services s
                INNER JOIN subscriptions sub ON s.id = sub.service_id
                WHERE sub.status = 'active' 
                    AND s.is_active = 1
                    AND julianday(sub.expiration_date) - julianday('now') <= ?
                ORDER BY sub.expiration_date ASC
            """
            self.cursor.execute(query, (days,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_subscription(self, subscription_id: int, **kwargs) -> bool:
        """
        Обновляет информацию о подписке
        
        Args:
            subscription_id: ID подписки
            **kwargs: поля для обновления
        
        Returns:
            True если обновление успешно
        """
        allowed_fields = ['subscription_type', 'start_date', 'expiration_date', 
                         'renewal_date', 'auto_renewal', 'notification_days', 
                         'status', 'notes']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE subscriptions SET {set_clause} WHERE id = ?"
        
        values = list(updates.values()) + [subscription_id]
        self.cursor.execute(query, values)
        self.connection.commit()
        
        return self.cursor.rowcount > 0
    
    def renew_subscription(self, subscription_id: int, new_expiration_date: str) -> bool:
        """
        Продлевает подписку
        
        Args:
            subscription_id: ID подписки
            new_expiration_date: новая дата истечения
        
        Returns:
            True если продление успешно
        """
        return self.update_subscription(
            subscription_id,
            expiration_date=new_expiration_date,
            renewal_date=datetime.now().strftime('%Y-%m-%d'),
            status='active'
        )
    
    def cancel_subscription(self, subscription_id: int) -> bool:
        """Отменяет подписку"""
        return self.update_subscription(subscription_id, status='cancelled')
    
    def expire_subscription(self, subscription_id: int) -> bool:
        """Помечает подписку как истекшую"""
        return self.update_subscription(subscription_id, status='expired')
    
    # ==================== ПЛАТЕЖИ ====================
    
    def add_payment(self, subscription_id: int, payment_date: str, 
                   amount: float, currency: str = "RUB",
                   payment_method: str = None, transaction_id: str = None,
                   status: str = "completed", notes: str = None) -> int:
        """
        Добавляет запись о платеже
        
        Args:
            subscription_id: ID подписки
            payment_date: дата платежа
            amount: сумма платежа
            currency: валюта
            payment_method: метод оплаты
            transaction_id: ID транзакции
            status: статус платежа
            notes: заметки
        
        Returns:
            ID созданной записи о платеже
        """
        query = """
            INSERT INTO payment_history 
            (subscription_id, payment_date, amount, currency, payment_method, 
             transaction_id, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.cursor.execute(query, (subscription_id, payment_date, amount, 
                                   currency, payment_method, transaction_id, 
                                   status, notes))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_payment_history(self, subscription_id: int = None) -> List[Dict]:
        """
        Получает историю платежей
        
        Args:
            subscription_id: ID подписки (если None, возвращает всю историю)
        
        Returns:
            Список платежей
        """
        if subscription_id:
            query = """
                SELECT * FROM payment_history 
                WHERE subscription_id = ? 
                ORDER BY payment_date DESC
            """
            self.cursor.execute(query, (subscription_id,))
        else:
            query = "SELECT * FROM payment_history ORDER BY payment_date DESC"
            self.cursor.execute(query)
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_payment_statistics(self) -> List[Dict]:
        """Получает статистику по платежам"""
        query = "SELECT * FROM v_payment_statistics"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== УВЕДОМЛЕНИЯ ====================
    
    def create_notification(self, subscription_id: int, notification_date: str,
                           notification_type: str, message: str) -> int:
        """
        Создает уведомление
        
        Args:
            subscription_id: ID подписки
            notification_date: дата уведомления
            notification_type: тип уведомления
            message: текст сообщения
        
        Returns:
            ID созданного уведомления
        """
        query = """
            INSERT INTO notifications 
            (subscription_id, notification_date, notification_type, message)
            VALUES (?, ?, ?, ?)
        """
        
        self.cursor.execute(query, (subscription_id, notification_date, 
                                   notification_type, message))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_pending_notifications(self) -> List[Dict]:
        """Получает список неотправленных уведомлений"""
        query = """
            SELECT n.*, s.service_name, s.provider, sub.expiration_date
            FROM notifications n
            INNER JOIN subscriptions sub ON n.subscription_id = sub.id
            INNER JOIN services s ON sub.service_id = s.id
            WHERE n.is_sent = 0 AND n.notification_date <= date('now')
            ORDER BY n.notification_date
        """
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def mark_notification_sent(self, notification_id: int) -> bool:
        """Помечает уведомление как отправленное"""
        query = """
            UPDATE notifications 
            SET is_sent = 1, sent_at = ? 
            WHERE id = ?
        """
        self.cursor.execute(query, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                                   notification_id))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    # ==================== УТИЛИТЫ ====================
    
    def check_and_update_expired_subscriptions(self) -> int:
        """
        Проверяет и обновляет статус истекших подписок
        
        Returns:
            Количество обновленных подписок
        """
        query = """
            UPDATE subscriptions 
            SET status = 'expired' 
            WHERE status = 'active' 
                AND date(expiration_date) < date('now')
        """
        self.cursor.execute(query)
        self.connection.commit()
        return self.cursor.rowcount
    
    def generate_notifications_for_expiring_subscriptions(self) -> int:
        """
        Генерирует уведомления для истекающих подписок
        
        Returns:
            Количество созданных уведомлений
        """
        # Получаем подписки, для которых нужно создать уведомления
        query = """
            SELECT sub.id, sub.expiration_date, sub.notification_days, 
                   s.service_name, s.provider
            FROM subscriptions sub
            INNER JOIN services s ON sub.service_id = s.id
            WHERE sub.status = 'active'
                AND julianday(sub.expiration_date) - julianday('now') <= sub.notification_days
                AND julianday(sub.expiration_date) - julianday('now') >= 0
                AND NOT EXISTS (
                    SELECT 1 FROM notifications n 
                    WHERE n.subscription_id = sub.id 
                        AND n.notification_type = 'expiring_soon'
                        AND date(n.notification_date) = date('now')
                )
        """
        
        self.cursor.execute(query)
        subscriptions = self.cursor.fetchall()
        
        count = 0
        for sub in subscriptions:
            days_left = int((datetime.strptime(sub['expiration_date'], '%Y-%m-%d').date() - 
                           date.today()).days)
            
            message = (f"Подписка на '{sub['service_name']}' ({sub['provider']}) "
                      f"истекает через {days_left} дн. "
                      f"Дата истечения: {sub['expiration_date']}")
            
            self.create_notification(
                subscription_id=sub['id'],
                notification_date=date.today().strftime('%Y-%m-%d'),
                notification_type='expiring_soon',
                message=message
            )
            count += 1
        
        return count
    
    def get_statistics(self) -> Dict:
        """
        Получает общую статистику по базе данных
        
        Returns:
            Словарь со статистикой
        """
        stats = {}
        
        # Количество сервисов
        self.cursor.execute("SELECT COUNT(*) as count FROM services WHERE is_active = 1")
        stats['active_services'] = self.cursor.fetchone()['count']
        
        # Количество активных подписок
        self.cursor.execute("SELECT COUNT(*) as count FROM subscriptions WHERE status = 'active'")
        stats['active_subscriptions'] = self.cursor.fetchone()['count']
        
        # Количество истекающих подписок
        self.cursor.execute("SELECT COUNT(*) as count FROM v_expiring_subscriptions")
        stats['expiring_subscriptions'] = self.cursor.fetchone()['count']
        
        # Общая сумма платежей
        self.cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM payment_history 
            WHERE status = 'completed'
        """)
        stats['total_payments'] = self.cursor.fetchone()['total']
        
        # Количество неотправленных уведомлений
        self.cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE is_sent = 0")
        stats['pending_notifications'] = self.cursor.fetchone()['count']
        
        return stats
    
    def export_to_json(self, filepath: str):
        """Экспортирует всю базу данных в JSON"""
        data = {
            'services': self.get_all_services(active_only=False),
            'subscriptions': [],
            'payments': self.get_payment_history(),
            'statistics': self.get_statistics()
        }
        
        # Получаем все подписки
        self.cursor.execute("SELECT * FROM subscriptions")
        data['subscriptions'] = [dict(row) for row in self.cursor.fetchall()]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие соединения"""
        self.close()
