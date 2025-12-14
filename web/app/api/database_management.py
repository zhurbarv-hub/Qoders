# -*- coding: utf-8 -*-
"""
API endpoints для управления резервными копиями базы данных
Только для администраторов
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import os
import subprocess
import datetime
import json
import shutil
from pathlib import Path

from ..dependencies import get_db
from ..models.user import User
from ..models.schemas import MessageResponse
from ..services.auth_service import decode_token, verify_password
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/database", tags=["Database Management"])
security = HTTPBearer()

# Директория для хранения резервных копий
BACKUP_DIR = Path("backups/database")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Файл с метаданными о бэкапах
BACKUP_METADATA_FILE = BACKUP_DIR / "backup_metadata.json"


class BackupInfo(BaseModel):
    """Информация о резервной копии"""
    filename: str = Field(..., description="Имя файла бэкапа")
    created_at: str = Field(..., description="Дата и время создания")
    size_bytes: int = Field(..., description="Размер файла в байтах")
    size_mb: float = Field(..., description="Размер файла в МБ")
    created_by: str = Field(..., description="Email администратора")
    description: str = Field(default="", description="Описание бэкапа")


class BackupListResponse(BaseModel):
    """Список всех резервных копий"""
    backups: List[BackupInfo]
    total_count: int
    total_size_mb: float


class RestoreRequest(BaseModel):
    """Запрос на восстановление БД"""
    filename: str = Field(..., description="Имя файла бэкапа для восстановления")
    password: str = Field(..., description="Пароль администратора для подтверждения")


class ClearDatabaseRequest(BaseModel):
    """Запрос на очистку БД"""
    password: str = Field(..., description="Пароль администратора для подтверждения")
    confirmation: str = Field(..., description="Текст подтверждения 'УДАЛИТЬ ВСЕ ДАННЫЕ'")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Получение текущего пользователя из JWT токена"""
    import logging
    logger = logging.getLogger(__name__)
    
    token = credentials.credentials
    logger.info(f"database_management: Получен токен длиной {len(token)} символов")
    
    payload = decode_token(token)
    if not payload:
        logger.error("database_management: decode_token вернул None")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем user_id из payload (используется "sub" в JWT стандарте)
    user_id = payload.get('sub') or payload.get('user_id')
    logger.info(f"database_management: Токен декодирован, user_id={user_id}")
    
    if not user_id:
        logger.error("database_management: user_id отсутствует в токене")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен: отсутствует user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем пользователя из БД
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user:
        logger.error(f"database_management: Пользователь с ID {user_id} не найден")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    logger.info(f"database_management: Пользователь найден: {user.email}, role={user.role}")
    return user


def check_admin_access(current_user: User):
    """Проверка прав администратора"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Требуются права администратора."
        )


def load_backup_metadata() -> dict:
    """Загрузить метаданные о бэкапах"""
    if BACKUP_METADATA_FILE.exists():
        with open(BACKUP_METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_backup_metadata(metadata: dict):
    """Сохранить метаданные о бэкапах"""
    with open(BACKUP_METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def get_database_connection_string() -> tuple:
    """Получить параметры подключения к БД"""
    from ..config import settings
    
    # Парсим DATABASE_URL
    db_url = settings.database_url
    
    if db_url.startswith('postgresql://'):
        # Формат: postgresql://user:password@host:port/database
        parts = db_url.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        host_port = host_db[0].split(':')
        
        return {
            'type': 'postgresql',
            'user': user_pass[0],
            'password': user_pass[1] if len(user_pass) > 1 else '',
            'host': host_port[0],
            'port': host_port[1] if len(host_port) > 1 else '5432',
            'database': host_db[1]
        }
    else:
        # SQLite
        return {
            'type': 'sqlite',
            'path': db_url.replace('sqlite:///', '')
        }


@router.post("/backup", response_model=BackupInfo)
async def create_backup(
    description: str = "",
    current_user: User = Depends(get_current_user)
):
    """
    Создать резервную копию базы данных
    
    Только для администраторов
    """
    check_admin_access(current_user)
    
    try:
        db_config = get_database_connection_string()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if db_config['type'] == 'postgresql':
            # PostgreSQL бэкап через pg_dump
            filename = f"kkt_backup_{timestamp}.sql"
            filepath = BACKUP_DIR / filename
            
            # Используем pg_dump для создания бэкапа
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
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка создания бэкапа: {result.stderr}"
                )
        else:
            # SQLite - простое копирование файла
            filename = f"kkt_backup_{timestamp}.db"
            filepath = BACKUP_DIR / filename
            shutil.copy2(db_config['path'], filepath)
        
        # Получаем размер файла
        file_size = filepath.stat().st_size
        size_mb = round(file_size / (1024 * 1024), 2)
        
        # Сохраняем метаданные
        metadata = load_backup_metadata()
        metadata[filename] = {
            'created_at': datetime.datetime.now().isoformat(),
            'size_bytes': file_size,
            'created_by': current_user.email,
            'description': description
        }
        save_backup_metadata(metadata)
        
        return BackupInfo(
            filename=filename,
            created_at=metadata[filename]['created_at'],
            size_bytes=file_size,
            size_mb=size_mb,
            created_by=current_user.email,
            description=description
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании резервной копии: {str(e)}"
        )


@router.get("/backups", response_model=BackupListResponse)
async def list_backups(current_user: User = Depends(get_current_user)):
    """
    Получить список всех резервных копий
    
    Только для администраторов
    """
    check_admin_access(current_user)
    
    metadata = load_backup_metadata()
    backups = []
    total_size = 0
    
    for filename, info in metadata.items():
        filepath = BACKUP_DIR / filename
        if filepath.exists():
            size_bytes = filepath.stat().st_size
            size_mb = round(size_bytes / (1024 * 1024), 2)
            total_size += size_mb
            
            backups.append(BackupInfo(
                filename=filename,
                created_at=info['created_at'],
                size_bytes=size_bytes,
                size_mb=size_mb,
                created_by=info['created_by'],
                description=info.get('description', '')
            ))
    
    # Сортируем по дате создания (новые сверху)
    backups.sort(key=lambda x: x.created_at, reverse=True)
    
    return BackupListResponse(
        backups=backups,
        total_count=len(backups),
        total_size_mb=round(total_size, 2)
    )


@router.get("/backup/{filename}")
async def download_backup(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Скачать резервную копию
    
    Только для администраторов
    """
    check_admin_access(current_user)
    
    filepath = BACKUP_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл резервной копии не найден"
        )
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/octet-stream'
    )


@router.delete("/backup/{filename}", response_model=MessageResponse)
async def delete_backup(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Удалить резервную копию
    
    Только для администраторов
    """
    check_admin_access(current_user)
    
    filepath = BACKUP_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл резервной копии не найден"
        )
    
    # Удаляем файл
    filepath.unlink()
    
    # Удаляем из метаданных
    metadata = load_backup_metadata()
    if filename in metadata:
        del metadata[filename]
        save_backup_metadata(metadata)
    
    return MessageResponse(message=f"Резервная копия {filename} успешно удалена")


@router.post("/restore", response_model=MessageResponse)
async def restore_database(
    request: RestoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Восстановить базу данных из резервной копии
    
    ВНИМАНИЕ: Все текущие данные будут перезаписаны!
    Только для администраторов
    """
    check_admin_access(current_user)
    
    # Проверка пароля администратора
    from ..services.auth_service import verify_password
    
    if not verify_password(request.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль администратора"
        )
    
    filepath = BACKUP_DIR / request.filename
    
    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл резервной копии не найден"
        )
    
    try:
        db_config = get_database_connection_string()
        
        if db_config['type'] == 'postgresql':
            # PostgreSQL восстановление через psql
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            cmd = [
                'psql',
                '-h', db_config['host'],
                '-p', db_config['port'],
                '-U', db_config['user'],
                '-d', db_config['database'],
                '-f', str(filepath)
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка восстановления БД: {result.stderr}"
                )
        else:
            # SQLite - копирование файла
            shutil.copy2(filepath, db_config['path'])
        
        return MessageResponse(
            message=f"База данных успешно восстановлена из {request.filename}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при восстановлении базы данных: {str(e)}"
        )


@router.post("/clear", response_model=MessageResponse)
async def clear_database(
    request: ClearDatabaseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    ОПАСНО: Полная очистка базы данных
    
    Удаляет ВСЕ данные из БД!
    Требует подтверждения паролем и текстом 'УДАЛИТЬ ВСЕ ДАННЫЕ'
    Только для администраторов
    """
    check_admin_access(current_user)
    
    # Проверка пароля
    from ..services.auth_service import verify_password
    
    if not verify_password(request.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль администратора"
        )
    
    # Проверка текста подтверждения
    if request.confirmation != "УДАЛИТЬ ВСЕ ДАННЫЕ":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текст подтверждения. Введите 'УДАЛИТЬ ВСЕ ДАННЫЕ'"
        )
    
    try:
        db_config = get_database_connection_string()
        
        if db_config['type'] == 'postgresql':
            # Список таблиц для очистки (в правильном порядке из-за foreign keys)
            tables = [
                'notification_logs',
                'deadlines',
                'cash_registers',
                'contacts',
                'users',
                'ofd_providers',
                'deadline_types'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            # Очищаем каждую таблицу
            for table in tables:
                cmd = [
                    'psql',
                    '-h', db_config['host'],
                    '-p', db_config['port'],
                    '-U', db_config['user'],
                    '-d', db_config['database'],
                    '-c', f'TRUNCATE TABLE {table} CASCADE;'
                ]
                
                subprocess.run(cmd, env=env, capture_output=True)
        else:
            # SQLite - удаление файла БД
            if os.path.exists(db_config['path']):
                os.remove(db_config['path'])
        
        return MessageResponse(
            message="База данных успешно очищена. Все данные удалены!"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при очистке базы данных: {str(e)}"
        )
