# -*- coding: utf-8 -*-
"""
Сервис для управления .env файлом
Управление списком TELEGRAM_ADMIN_IDS
"""
import os
import subprocess
from typing import List, Optional
from pathlib import Path


class EnvManager:
    """Менеджер для работы с .env файлом"""
    
    def __init__(self, env_path: Optional[str] = None):
        """
        Инициализация менеджера
        
        Args:
            env_path: Путь к .env файлу. Если None, используется путь по умолчанию
        """
        if env_path:
            self.env_path = Path(env_path)
        else:
            # Определяем путь к .env файлу проекта
            project_root = Path(__file__).parent.parent.parent.parent
            self.env_path = project_root / '.env'
    
    def get_admin_telegram_ids(self) -> List[str]:
        """
        Получить список Telegram ID администраторов из .env файла
        
        Returns:
            Список Telegram ID (строки)
        """
        if not self.env_path.exists():
            return []
        
        with open(self.env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('TELEGRAM_ADMIN_IDS='):
                    # Извлекаем значение после знака равно
                    value = line.split('=', 1)[1].strip()
                    if value:
                        return [id.strip() for id in value.split(',')]
                    return []
        
        return []
    
    def set_admin_telegram_ids(self, telegram_ids: List[str]) -> bool:
        """
        Установить список Telegram ID администраторов в .env файле
        
        Args:
            telegram_ids: Список Telegram ID
            
        Returns:
            True если успешно, False если произошла ошибка
        """
        if not self.env_path.exists():
            print(f"❌ .env файл не найден: {self.env_path}")
            return False
        
        try:
            # Читаем все строки файла
            with open(self.env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Формируем новое значение
            new_value = ','.join(telegram_ids) if telegram_ids else ''
            new_line = f'TELEGRAM_ADMIN_IDS={new_value}\n'
            
            # Находим и заменяем строку с TELEGRAM_ADMIN_IDS
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith('TELEGRAM_ADMIN_IDS='):
                    lines[i] = new_line
                    updated = True
                    break
            
            # Если не нашли - добавляем в конец
            if not updated:
                lines.append(new_line)
            
            # Записываем обратно
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ TELEGRAM_ADMIN_IDS обновлён: {new_value}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении .env файла: {e}")
            return False
    
    def add_admin_telegram_id(self, telegram_id: str) -> bool:
        """
        Добавить Telegram ID в список администраторов
        
        Args:
            telegram_id: Telegram ID для добавления
            
        Returns:
            True если успешно добавлен, False если уже существует или ошибка
        """
        current_ids = self.get_admin_telegram_ids()
        
        # Проверяем, что ID ещё нет в списке
        if telegram_id in current_ids:
            print(f"⚠️  Telegram ID {telegram_id} уже в списке администраторов")
            return False
        
        # Добавляем новый ID
        current_ids.append(telegram_id)
        return self.set_admin_telegram_ids(current_ids)
    
    def remove_admin_telegram_id(self, telegram_id: str) -> bool:
        """
        Удалить Telegram ID из списка администраторов
        
        Args:
            telegram_id: Telegram ID для удаления
            
        Returns:
            True если успешно удалён, False если не найден или ошибка
        """
        current_ids = self.get_admin_telegram_ids()
        
        # Проверяем, что ID есть в списке
        if telegram_id not in current_ids:
            print(f"⚠️  Telegram ID {telegram_id} не найден в списке администраторов")
            return False
        
        # Удаляем ID
        current_ids.remove(telegram_id)
        return self.set_admin_telegram_ids(current_ids)
    
    def restart_bot_service(self) -> bool:
        """
        Перезапустить сервис бота для применения изменений .env
        
        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Проверяем, что мы на Linux (в продакшене)
            if os.name != 'posix':
                print("⚠️  Перезапуск бота доступен только на Linux сервере")
                return False
            
            # Перезапускаем systemd сервис
            result = subprocess.run(
                ['systemctl', 'restart', 'kkt-bot.service'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Бот успешно перезапущен")
                return True
            else:
                print(f"❌ Ошибка при перезапуске бота: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Превышено время ожидания при перезапуске бота")
            return False
        except Exception as e:
            print(f"❌ Ошибка при перезапуске бота: {e}")
            return False


# Создаём глобальный экземпляр для использования в API
env_manager = EnvManager()
