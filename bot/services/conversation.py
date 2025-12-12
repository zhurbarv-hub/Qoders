# -*- coding: utf-8 -*-
"""
Управление многошаговыми диалогами (conversation state)
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConversationState:
    """Состояние диалога для одного пользователя"""
    
    def __init__(self, user_id: int, command: str):
        self.user_id = user_id
        self.command = command
        self.step = 0
        self.data: Dict[str, Any] = {}
        self.started_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=5)
        self.last_activity = datetime.now()
    
    def is_expired(self) -> bool:
        """Проверка истечения времени диалога"""
        return datetime.now() > self.expires_at
    
    def update_activity(self):
        """Обновление времени последней активности и продление срока действия"""
        self.last_activity = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=5)
    
    def next_step(self):
        """Переход к следующему шагу"""
        self.step += 1
        self.update_activity()
    
    def set_data(self, key: str, value: Any):
        """Сохранение данных диалога"""
        self.data[key] = value
        self.update_activity()
    
    def get_data(self, key: str, default=None) -> Any:
        """Получение данных диалога"""
        return self.data.get(key, default)
    
    def __repr__(self):
        return f"<ConversationState user={self.user_id} command={self.command} step={self.step}>"


class ConversationManager:
    """Менеджер диалогов для всех пользователей"""
    
    def __init__(self):
        self._conversations: Dict[int, ConversationState] = {}
        logger.info("ConversationManager инициализирован")
    
    def start_conversation(self, user_id: int, command: str) -> ConversationState:
        """
        Начать новый диалог
        
        Args:
            user_id: ID пользователя Telegram
            command: Название команды (add_client, add_deadline и т.д.)
            
        Returns:
            ConversationState
        """
        # Если есть активный диалог - завершаем его
        if user_id in self._conversations:
            old_conv = self._conversations[user_id]
            logger.info(f"Завершение старого диалога для user {user_id}: {old_conv.command}")
            del self._conversations[user_id]
        
        # Создаём новый диалог
        conversation = ConversationState(user_id, command)
        self._conversations[user_id] = conversation
        
        logger.info(f"Начат новый диалог для user {user_id}: {command}")
        return conversation
    
    def get_conversation(self, user_id: int) -> Optional[ConversationState]:
        """
        Получить активный диалог пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            ConversationState или None
        """
        if user_id not in self._conversations:
            return None
        
        conversation = self._conversations[user_id]
        
        # Проверка истечения срока
        if conversation.is_expired():
            logger.info(f"Диалог истёк для user {user_id}: {conversation.command}")
            del self._conversations[user_id]
            return None
        
        return conversation
    
    def has_conversation(self, user_id: int) -> bool:
        """Проверка наличия активного диалога"""
        return self.get_conversation(user_id) is not None
    
    def update_conversation(self, user_id: int, key: str, value: Any):
        """
        Обновить данные диалога
        
        Args:
            user_id: ID пользователя
            key: Ключ данных
            value: Значение
        """
        conversation = self.get_conversation(user_id)
        if conversation:
            conversation.set_data(key, value)
    
    def next_step(self, user_id: int) -> Optional[int]:
        """
        Перейти к следующему шагу
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Номер нового шага или None
        """
        conversation = self.get_conversation(user_id)
        if conversation:
            conversation.next_step()
            return conversation.step
        return None
    
    def end_conversation(self, user_id: int) -> bool:
        """
        Завершить диалог (успешное завершение)
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если диалог был завершён
        """
        if user_id in self._conversations:
            conversation = self._conversations[user_id]
            logger.info(f"Диалог завершён для user {user_id}: {conversation.command} (шаг {conversation.step})")
            del self._conversations[user_id]
            return True
        return False
    
    def cancel_conversation(self, user_id: int) -> Optional[str]:
        """
        Отменить диалог (пользователь отменил)
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Название отменённой команды или None
        """
        if user_id in self._conversations:
            conversation = self._conversations[user_id]
            command = conversation.command
            logger.info(f"Диалог отменён пользователем {user_id}: {command}")
            del self._conversations[user_id]
            return command
        return None
    
    def cleanup_expired(self):
        """Очистка истёкших диалогов"""
        expired_users = []
        
        for user_id, conversation in self._conversations.items():
            if conversation.is_expired():
                expired_users.append(user_id)
        
        for user_id in expired_users:
            conversation = self._conversations[user_id]
            logger.info(f"Удаление истёкшего диалога: user {user_id}, команда {conversation.command}")
            del self._conversations[user_id]
        
        if expired_users:
            logger.info(f"Очищено истёкших диалогов: {len(expired_users)}")
    
    def get_active_count(self) -> int:
        """Получить количество активных диалогов"""
        return len(self._conversations)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику диалогов"""
        commands_count = {}
        
        for conversation in self._conversations.values():
            cmd = conversation.command
            commands_count[cmd] = commands_count.get(cmd, 0) + 1
        
        return {
            'total_active': len(self._conversations),
            'by_command': commands_count
        }


# Глобальный экземпляр менеджера
conversation_manager = ConversationManager()


# Вспомогательные функции для удобства
def start_conversation(user_id: int, command: str) -> ConversationState:
    """Начать новый диалог"""
    return conversation_manager.start_conversation(user_id, command)


def get_conversation(user_id: int) -> Optional[ConversationState]:
    """Получить активный диалог"""
    return conversation_manager.get_conversation(user_id)


def has_conversation(user_id: int) -> bool:
    """Проверить наличие активного диалога"""
    return conversation_manager.has_conversation(user_id)


def end_conversation(user_id: int) -> bool:
    """Завершить диалог"""
    return conversation_manager.end_conversation(user_id)


def cancel_conversation(user_id: int) -> Optional[str]:
    """Отменить диалог"""
    return conversation_manager.cancel_conversation(user_id)


# Экспорт
__all__ = [
    'ConversationState',
    'ConversationManager',
    'conversation_manager',
    'start_conversation',
    'get_conversation',
    'has_conversation',
    'end_conversation',
    'cancel_conversation'
]