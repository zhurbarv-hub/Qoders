# -*- coding: utf-8 -*-
"""
API endpoints для управления резервными копиями базы данных
Только для администраторов
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import subprocess
import datetime
import json
import shutil
import logging
from pathlib import Path

from ..dependencies import get_db
from ..models.user import User
from ..models.backup import BackupSchedule, BackupHistory
from ..models.schemas import MessageResponse
from ..services.auth_service import decode_token, verify_password
from pydantic import BaseModel, Field

# Логгер для модуля
logger = logging.getLogger(__name__)

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
            # PostgreSQL бэкап через pg_dump (без владельцев для совместимости)
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
                '--clean',  # Очистка перед восстановлением
                '--if-exists',  # Безопасная очистка
                '--no-owner',  # Не сохранять владельцев (улучшает совместимость)
                '--no-privileges'  # Не сохранять привилегии
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
async def list_backups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить список всех резервных копий
    
    Только для администраторов
    """
    check_admin_access(current_user)
    
    backups = []
    total_size = 0
    seen_filenames = set()
    
    # 1. Ручные бэкапы из metadata.json
    metadata = load_backup_metadata()
    for filename, info in metadata.items():
        filepath = BACKUP_DIR / filename
        if filepath.exists():
            size_bytes = filepath.stat().st_size
            size_mb = round(size_bytes / (1024 * 1024), 2)
            total_size += size_mb
            seen_filenames.add(filename)
            
            backups.append(BackupInfo(
                filename=filename,
                created_at=info['created_at'],
                size_bytes=size_bytes,
                size_mb=size_mb,
                created_by=info['created_by'],
                description=info.get('description', '')
            ))
    
    # 2. Автоматические бэкапы из BackupHistory
    from ..models.backup import BackupHistory
    
    auto_backups = db.query(BackupHistory).filter(
        BackupHistory.status == 'success',
        BackupHistory.filename.isnot(None)
    ).all()
    
    for backup_record in auto_backups:
        filename = backup_record.filename
        if filename in seen_filenames:
            continue  # Уже добавлен из metadata
            
        filepath = BACKUP_DIR / filename
        if filepath.exists():
            size_bytes = filepath.stat().st_size
            size_mb = round(size_bytes / (1024 * 1024), 2)
            total_size += size_mb
            seen_filenames.add(filename)
            
            # Форматируем дату в ISO формат
            created_at_str = backup_record.started_at.isoformat() if backup_record.started_at else datetime.datetime.now().isoformat()
            
            backups.append(BackupInfo(
                filename=filename,
                created_at=created_at_str,
                size_bytes=size_bytes,
                size_mb=size_mb,
                created_by="Автоматический бэкап",
                description="Автоматическое резервное копирование"
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
    logger.info(f"🔐 RESTORE: Проверка прав доступа для user_id={current_user.id}")
    check_admin_access(current_user)
    logger.info(f"✅ RESTORE: Права администратора подтверждены")
    
    # Проверка пароля администратора
    from ..services.auth_service import verify_password
    
    logger.info(f"🔑 RESTORE: Проверка пароля администратора...")
    try:
        password_valid = verify_password(request.password, current_user.password_hash)
        logger.info(f"🔑 RESTORE: Результат проверки пароля: {password_valid}")
    except Exception as pwd_err:
        logger.error(f"❌ RESTORE: Ошибка при проверке пароля: {pwd_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка проверки пароля: {str(pwd_err)}"
        )
    
    if not password_valid:
        logger.warning(f"⚠️ RESTORE: Неверный пароль от user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль администратора"
        )
    
    filepath = BACKUP_DIR / request.filename
    logger.info(f"📁 RESTORE: Проверка файла: {filepath}")
    
    if not filepath.exists():
        logger.error(f"❌ RESTORE: Файл не найден: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл резервной копии не найден"
        )
    
    try:
        import time
        start_time = time.time()
        
        logger.info(f"🔄 RESTORE START: Начало восстановления из {request.filename}")
        logger.info(f"📂 RESTORE: Путь к файлу: {filepath}")
        logger.info(f"📊 RESTORE: Размер файла: {filepath.stat().st_size / 1024:.2f} KB")
        
        db_config = get_database_connection_string()
        logger.info(f"🔌 RESTORE: Тип БД: {db_config['type']}, Database: {db_config['database']}")
        
        if db_config['type'] == 'postgresql':
            # PostgreSQL восстановление через psql с POSTGRES суперпользователем
            # Используем postgres вместо kkt_user для полного доступа ко всем таблицам
            env = os.environ.copy()
            env['PGPASSWORD'] = 'PostgresSecure2024KKT'  # Пароль postgres
            
            # ШАГ 1: Принудительно закрываем все активные соединения с БД
            logger.info(f"🚫 RESTORE: Закрытие всех активных соединений с БД...")
            
            # Закрываем все соединения кроме текущего
            terminate_cmd = [
                'psql',
                '-h', db_config['host'],
                '-p', db_config['port'],
                '-U', 'postgres',
                '-d', db_config['database'],
                '-c', f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db_config['database']}' AND pid != pg_backend_pid();"
            ]
            
            import asyncio
            term_process = await asyncio.create_subprocess_exec(
                *terminate_cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            term_stdout, term_stderr = await term_process.communicate()
            if term_process.returncode == 0:
                logger.info(f"✅ RESTORE: Соединения закрыты")
            else:
                logger.warning(f"⚠️ RESTORE: Ошибка при закрытии соединений: {term_stderr.decode('utf-8', errors='ignore')}")
            
            # Небольшая пауза чтобы соединения точно закрылись
            await asyncio.sleep(0.5)
            
            # ШАГ 2: Восстановление базы
            # Оптимизированные параметры для быстрого восстановления
            cmd = [
                'psql',
                '-h', db_config['host'],
                '-p', db_config['port'],
                '-U', 'postgres',  # Используем суперпользователя postgres
                '-d', db_config['database'],
                '-f', str(filepath),
                '--single-transaction',  # Одна транзакция = быстрее и безопаснее
                '--set', 'ON_ERROR_STOP=on',  # Остановка при ошибке
                '-v', 'ON_ERROR_STOP=1',
                '-q'  # Тихий режим (меньше вывода)
            ]
            
            logger.info(f"💻 RESTORE: Команда: {' '.join(cmd[:9])}...")  # Без пароля
            logger.info(f"⏳ RESTORE: Запуск psql с таймаутом 120 секунд...")            
            
            # Запускаем асинхронно с увеличенным таймаутом 120 секунд
            
            exec_start = time.time()
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info(f"🚀 RESTORE: Процесс запущен, PID: {process.pid}")
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=120.0  # Увеличено до 120 секунд
                )
                exec_time = time.time() - exec_start
                logger.info(f"⏱️ RESTORE: Процесс завершен за {exec_time:.2f} секунд")
                
            except asyncio.TimeoutError:
                logger.error(f"❌ RESTORE TIMEOUT: Превышено время ожидания (120 сек)")
                process.kill()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Превышено время ожидания восстановления (120 сек)"
                )
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                logger.error(f"❌ RESTORE ERROR: returncode={process.returncode}")
                logger.error(f"❌ RESTORE STDERR: {error_msg[:500]}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка восстановления БД: {error_msg}"
                )
            
            logger.info(f"✅ RESTORE SUCCESS: returncode=0")
            if stdout:
                logger.info(f"📝 RESTORE STDOUT: {stdout.decode('utf-8', errors='ignore')[:200]}")
                
        else:
            # SQLite - копирование файла
            logger.info(f"📁 RESTORE: SQLite копирование файла...")
            shutil.copy2(filepath, db_config['path'])
        
        total_time = time.time() - start_time
        logger.info(f"✅ RESTORE COMPLETE: Общее время: {total_time:.2f} секунд")
        
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


# ========== API для управления расписанием автобэкапов ==========

class BackupScheduleResponse(BaseModel):
    """Информация о расписании автобэкапов"""
    id: int
    enabled: bool
    frequency: str  # daily, weekly, monthly
    time_of_day: str  # HH:MM:SS
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    retention_days: int
    last_run_at: Optional[str] = None
    next_run_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BackupScheduleUpdate(BaseModel):
    """Обновление расписания автобэкапов"""
    enabled: Optional[bool] = None
    frequency: Optional[str] = None
    time_of_day: Optional[str] = None  # HH:MM
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    retention_days: Optional[int] = None


class BackupHistoryResponse(BaseModel):
    """Информация о выполненном бэкапе"""
    id: int
    schedule_id: Optional[int] = None
    started_at: str
    completed_at: Optional[str] = None
    status: str  # running, success, failed
    filename: Optional[str] = None
    size_bytes: Optional[int] = None
    size_mb: Optional[float] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/backup-schedule", response_model=BackupScheduleResponse)
async def get_backup_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить текущее расписание автобэкапов
    
    Только для администраторов
    """
    check_admin_access(current_user)
    
    # Получаем первую (единственную) запись расписания
    schedule = db.query(BackupSchedule).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено"
        )
    
    return BackupScheduleResponse(
        id=schedule.id,
        enabled=schedule.enabled,
        frequency=schedule.frequency,
        time_of_day=str(schedule.time_of_day),
        day_of_week=schedule.day_of_week,
        day_of_month=schedule.day_of_month,
        retention_days=schedule.retention_days,
        last_run_at=schedule.last_run_at.isoformat() if schedule.last_run_at else None,
        next_run_at=schedule.next_run_at.isoformat() if schedule.next_run_at else None,
        created_at=schedule.created_at.isoformat(),
        updated_at=schedule.updated_at.isoformat()
    )


@router.put("/backup-schedule", response_model=BackupScheduleResponse)
async def update_backup_schedule(
    data: BackupScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить расписание автобэкапов
    
    Только для администраторов
    """
    check_admin_access(current_user)
    
    schedule = db.query(BackupSchedule).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено"
        )
    
    # Обновляем поля
    if data.enabled is not None:
        schedule.enabled = data.enabled
    if data.frequency is not None:
        schedule.frequency = data.frequency
    if data.time_of_day is not None:
        # Преобразуем HH:MM в time
        from datetime import time as dt_time
        hour, minute = map(int, data.time_of_day.split(':'))
        schedule.time_of_day = dt_time(hour, minute)
    if data.day_of_week is not None:
        schedule.day_of_week = data.day_of_week
    if data.day_of_month is not None:
        schedule.day_of_month = data.day_of_month
    if data.retention_days is not None:
        schedule.retention_days = data.retention_days
    
    schedule.updated_at = datetime.datetime.now()
    
    try:
        db.commit()
        db.refresh(schedule)
        
        return BackupScheduleResponse(
            id=schedule.id,
            enabled=schedule.enabled,
            frequency=schedule.frequency,
            time_of_day=str(schedule.time_of_day),
            day_of_week=schedule.day_of_week,
            day_of_month=schedule.day_of_month,
            retention_days=schedule.retention_days,
            last_run_at=schedule.last_run_at.isoformat() if schedule.last_run_at else None,
            next_run_at=schedule.next_run_at.isoformat() if schedule.next_run_at else None,
            created_at=schedule.created_at.isoformat(),
            updated_at=schedule.updated_at.isoformat()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении расписания: {str(e)}"
        )


@router.get("/backup-history", response_model=List[BackupHistoryResponse])
async def get_backup_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить историю выполненных бэкапов
    
    Только для администраторов
    """
    check_admin_access(current_user)
    
    history = db.query(BackupHistory).order_by(BackupHistory.started_at.desc()).limit(limit).all()
    
    result = []
    for record in history:
        size_mb = round(record.size_bytes / (1024 * 1024), 2) if record.size_bytes else None
        result.append(BackupHistoryResponse(
            id=record.id,
            schedule_id=record.schedule_id,
            started_at=record.started_at.isoformat(),
            completed_at=record.completed_at.isoformat() if record.completed_at else None,
            status=record.status,
            filename=record.filename,
            size_bytes=record.size_bytes,
            size_mb=size_mb,
            error_message=record.error_message
        ))
    
    return result
