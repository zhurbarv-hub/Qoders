# -*- coding: utf-8 -*-
"""
Модели для автоматических бэкапов базы данных
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Text, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, time

from ..database import Base


class BackupSchedule(Base):
    """Модель расписания автоматических бэкапов"""
    __tablename__ = "backup_schedules"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    enabled = Column(Boolean, default=True, nullable=False)
    frequency = Column(String(20), nullable=False, default='daily')  # daily, weekly, monthly
    time_of_day = Column(Time, nullable=False, default=time(3, 0))  # 03:00
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday (for weekly)
    day_of_month = Column(Integer)  # 1-31 (for monthly)
    retention_days = Column(Integer, nullable=False, default=7)
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    
    # Relationships
    history = relationship("BackupHistory", back_populates="schedule", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<BackupSchedule(id={self.id}, frequency='{self.frequency}', enabled={self.enabled})>"


class BackupHistory(Base):
    """Модель истории выполнения бэкапов"""
    __tablename__ = "backup_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey('backup_schedules.id', ondelete='CASCADE'))
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    status = Column(String(20), nullable=False, default='running')  # running, success, failed
    filename = Column(String(255))
    size_bytes = Column(BigInteger)
    error_message = Column(Text)
    
    # Relationships
    schedule = relationship("BackupSchedule", back_populates="history")
    
    def __repr__(self):
        return f"<BackupHistory(id={self.id}, status='{self.status}', started_at='{self.started_at}')>"
