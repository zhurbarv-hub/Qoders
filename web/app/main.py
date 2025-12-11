# -*- coding: utf-8 -*-
"""
Главный модуль FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import logging
import os

# ОТНОСИТЕЛЬНЫЕ ИМПОРТЫ
from .config import settings
from .api import auth, clients, deadline_types, deadlines, dashboard

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание приложения FastAPI
app = FastAPI(
    title="KKT Service Expiration Management System",
    description="Система управления дедлайнами истечения услуг ККТ",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров API
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(deadline_types.router)
app.include_router(deadlines.router)
app.include_router(dashboard.router)

# Путь к статическим файлам
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Проверка существования директории static
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"📁 Статические файлы подключены: {STATIC_DIR}")
else:
    logger.warning(f"⚠️ Директория static не найдена: {STATIC_DIR}")


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    logger.info("🚀 FastAPI приложение запущено!")
    logger.info(f"📊 База данных: {settings.database_url}")
    logger.info(f"🌐 CORS origins: {settings.cors_origins}")
    logger.info(f"🔐 JWT срок действия: {settings.access_token_expire_minutes} минут")
    logger.info(f"📡 API endpoints:")
    logger.info(f"  - /api/auth (Authentication)")
    logger.info(f"  - /api/clients (Clients)")
    logger.info(f"  - /api/deadline-types (Deadline Types)")
    logger.info(f"  - /api/deadlines (Deadlines)")
    logger.info(f"  - /api/dashboard (Dashboard)")


@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    logger.info("🛑 FastAPI приложение остановлено")


@app.get("/", response_class=RedirectResponse)
async def root():
    """Главная страница - перенаправление на страницу входа"""
    return RedirectResponse(url="/static/login.html")


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервера"""
    return {
        "status": "healthy",
        "service": "KKT Management System",
        "version": "1.0.0"
    }


@app.get("/info")
async def info():
    """Информация о приложении"""
    return {
        "name": "KKT Service Expiration Management System",
        "version": "1.0.0",
        "description": "Система управления дедлайнами истечения услуг ККТ",
        "endpoints": {
            "docs": "/api/docs",
            "redoc": "/api/redoc",
            "login": "/static/login.html",
            "api": {
                "auth": "/api/auth/login",
                "clients": "/api/clients",
                "deadline_types": "/api/deadline-types",
                "deadlines": "/api/deadlines",
                "dashboard": "/api/dashboard/stats"
            }
        }
    }