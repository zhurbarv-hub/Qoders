# -*- coding: utf-8 -*-
"""
HTTP клиент для взаимодействия с Web API
Обрабатывает все запросы к FastAPI backend
"""

import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import date
from .token_manager import TokenManager
from .exceptions import (
    APIError,
    ConnectionError,
    NotFoundError,
    ValidationError,
    ServerError
)

logger = logging.getLogger(__name__)


class WebAPIClient:
    """
    Клиент для взаимодействия с Web API
    
    Attributes:
        base_url: Базовый URL API
        timeout: Тайм-аут запросов (секунды)
        token_manager: Менеджер JWT токенов
    """
    
    def __init__(
        self,
        base_url: str,
        token_manager: TokenManager,
        timeout: int = 30
    ):
        """
        Инициализация API клиента
        
        Args:
            base_url: URL Web API (например, http://localhost:8000)
            token_manager: Экземпляр TokenManager для аутентификации
            timeout: Тайм-аут запросов в секундах
        """
        self.base_url = base_url.rstrip('/')
        self.token_manager = token_manager
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"WebAPIClient инициализирован для {base_url}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Получение или создание HTTP сессии
        
        Returns:
            aiohttp.ClientSession: Активная сессия
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Базовый метод для выполнения HTTP запросов с аутентификацией
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: API endpoint (например, /api/deadlines)
            **kwargs: Дополнительные параметры для aiohttp (params, json, data)
        
        Returns:
            Dict: Распарсенный JSON ответ
            
        Raises:
            ConnectionError: Ошибка сети
            NotFoundError: Ресурс не найден (404)
            ValidationError: Ошибка валидации (422)
            ServerError: Ошибка сервера (500+)
            APIError: Прочие ошибки API
        """
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        # Попытка 1: С текущим токеном
        try:
            token = await self.token_manager.get_token()
            headers = kwargs.pop('headers', {})
            headers['Authorization'] = f"Bearer {token}"
            
            async with session.request(method, url, headers=headers, **kwargs) as response:
                return await self._handle_response(response)
        
        except aiohttp.ClientError as e:
            # Если 401, пробуем обновить токен и повторить
            if hasattr(e, 'status') and e.status == 401:
                logger.warning("Получен 401, обновляем токен и повторяем запрос...")
                await self.token_manager.invalidate_token()
                
                # Попытка 2: С обновлённым токеном
                try:
                    token = await self.token_manager.get_token()
                    headers['Authorization'] = f"Bearer {token}"
                    
                    async with session.request(method, url, headers=headers, **kwargs) as response:
                        return await self._handle_response(response)
                
                except Exception as retry_error:
                    logger.error(f"Повторная попытка не удалась: {retry_error}")
                    raise
            
            # Прочие сетевые ошибки
            logger.error(f"Ошибка подключения к {url}: {e}")
            raise ConnectionError(f"Не удалось подключиться к API: {e}")
        
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе {method} {url}: {e}")
            raise APIError(f"Ошибка API запроса: {e}")
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """
        Обработка HTTP ответа
        
        Args:
            response: Ответ от сервера
            
        Returns:
            Dict: Распарсенный JSON
            
        Raises:
            NotFoundError: 404
            ValidationError: 422
            ServerError: 500+
            APIError: Прочие ошибки
        """
        status = response.status
        
        # Успешный ответ
        if 200 <= status < 300:
            try:
                data = await response.json()
                logger.debug(f"✅ {response.method} {response.url} → {status}")
                return data
            except Exception as e:
                logger.error(f"Ошибка парсинга JSON: {e}")
                text = await response.text()
                raise APIError(f"Неверный формат ответа: {text[:200]}")
        
        # Ошибки клиента
        elif status == 404:
            error_text = await response.text()
            raise NotFoundError(f"Ресурс не найден: {error_text}")
        
        elif status == 422:
            error_data = await response.json()
            raise ValidationError(f"Ошибка валидации: {error_data}")
        
        # Ошибки сервера
        elif status >= 500:
            error_text = await response.text()
            raise ServerError(f"Ошибка сервера ({status}): {error_text}")
        
        # Прочие ошибки
        else:
            error_text = await response.text()
            raise APIError(f"HTTP {status}: {error_text}")
    
    # ============================================
    # Общие HTTP методы
    # ============================================
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        GET запрос
        
        Args:
            endpoint: API endpoint
            params: Query параметры
            
        Returns:
            Dict: Ответ API
        """
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        POST запрос
        
        Args:
            endpoint: API endpoint
            data: JSON данные
            
        Returns:
            Dict: Ответ API
        """
        return await self._make_request("POST", endpoint, json=data)
    
    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        PUT запрос
        
        Args:
            endpoint: API endpoint
            data: JSON данные
            
        Returns:
            Dict: Ответ API
        """
        return await self._make_request("PUT", endpoint, json=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        DELETE запрос
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Dict: Ответ API
        """
        return await self._make_request("DELETE", endpoint)
    
    # ============================================
    # Специализированные методы для дедлайнов
    # ============================================
    
    async def get_expiring_deadlines(self, days: int) -> List[Dict]:
        """
        Получить дедлайны, истекающие через N дней
        
        Args:
            days: Количество дней
            
        Returns:
            List[Dict]: Список дедлайнов с полной информацией
        """
        logger.info(f"Запрос дедлайнов, истекающих через {days} дней")
        
        response = await self.get(
            "/api/deadlines/expiring-soon",
            params={"days": days}
        )
        
        logger.info(f"Получено {len(response)} дедлайнов")
        return response
    
    async def get_deadlines_by_client(
        self,
        client_id: int,
        include_inactive: bool = False
    ) -> List[Dict]:
        """
        Получить все дедлайны конкретного клиента
        
        Args:
            client_id: ID клиента
            include_inactive: Включить неактивные дедлайны
            
        Returns:
            List[Dict]: Список дедлайнов клиента
        """
        logger.info(f"Запрос дедлайнов клиента {client_id}")
        
        response = await self.get(
            f"/api/deadlines/by-client/{client_id}",
            params={"include_inactive": include_inactive}
        )
        
        return response
    
    async def get_deadlines_filtered(self, filters: Dict) -> Dict:
        """
        Получить отфильтрованный список дедлайнов с пагинацией
        
        Args:
            filters: Фильтры (client_id, deadline_type_id, status, date_from, date_to, days_until, page, page_size)
            
        Returns:
            Dict: Ответ с total, deadlines, page, page_size, total_pages
        """
        logger.info(f"Запрос дедлайнов с фильтрами: {filters}")
        
        # Преобразуем date объекты в строки
        params = {}
        for key, value in filters.items():
            if isinstance(value, date):
                params[key] = value.isoformat()
            elif value is not None:
                params[key] = value
        
        response = await self.get("/api/deadlines", params=params)
        
        logger.info(
            f"Получено {response.get('total', 0)} дедлайнов "
            f"(страница {response.get('page', 1)} из {response.get('total_pages', 1)})"
        )
        
        return response
    
    async def get_dashboard_stats(self) -> Dict:
        """
        Получить статистику для dashboard
        
        Returns:
            Dict: Статистика системы
        """
        logger.info("Запрос статистики dashboard")
        
        response = await self.get("/api/dashboard/stats")
        
        logger.info(
            f"Статистика: {response.get('active_clients_count', 0)} клиентов, "
            f"{response.get('active_deadlines_count', 0)} активных дедлайнов"
        )
        
        return response
    
    async def close(self):
        """Закрытие HTTP сессии"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("HTTP сессия закрыта")


# Для тестирования
if __name__ == "__main__":
    import asyncio
    import sys
    
    async def test_api_client():
        """Тестирование API клиента"""
        print("=" * 60)
        print("ТЕСТ WEB API CLIENT")
        print("=" * 60)
        
        # Создаём менеджер токенов
        token_manager = TokenManager(
            api_base_url="http://localhost:8000",
            username="admin",  # Замените на реальные данные
            password="admin"
        )
        
        # Создаём клиент
        client = WebAPIClient(
            base_url="http://localhost:8000",
            token_manager=token_manager,
            timeout=30
        )
        
        try:
            # Тест 1: Получение статистики
            print("\n1. Получение статистики...")
            stats = await client.get_dashboard_stats()
            print(f"✅ Статистика получена: {stats}")
            
            # Тест 2: Получение дедлайнов
            print("\n2. Получение дедлайнов (14 дней)...")
            deadlines = await client.get_expiring_deadlines(14)
            print(f"✅ Получено {len(deadlines)} дедлайнов")
            
            # Тест 3: Фильтрация
            print("\n3. Получение списка с фильтрами...")
            filtered = await client.get_deadlines_filtered({
                "status": "active",
                "page": 1,
                "page_size": 10
            })
            print(f"✅ Получено {filtered.get('total', 0)} дедлайнов (страница 1)")
            
            print("\n" + "=" * 60)
            print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
            print("=" * 60)
        
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        finally:
            await client.close()
    
    # Запуск теста
    asyncio.run(test_api_client())