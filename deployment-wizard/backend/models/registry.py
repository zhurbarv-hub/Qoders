# -*- coding: utf-8 -*-
"""SQLAlchemy модели для Client Registry"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="deployer")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DeployedInstance(Base):
    __tablename__ = "deployed_instances"
    
    id = Column(Integer, primary_key=True)
    instance_name = Column(String(100), nullable=False)
    client_company = Column(String(255), nullable=False)
    vds_ip = Column(String(45), nullable=False)
    domain = Column(String(255))
    deployed_version = Column(String(20), nullable=False)
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    last_health_check = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default="active")
    notes = Column(Text)
    admin_email = Column(String(255))
    admin_phone = Column(String(20))
    telegram_bot_token = Column(String(100))
    telegram_admin_ids = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DeploymentHistory(Base):
    __tablename__ = "deployment_history"
    
    id = Column(Integer, primary_key=True)
    instance_id = Column(Integer, ForeignKey("deployed_instances.id", ondelete="CASCADE"))
    action = Column(String(50), nullable=False)
    from_version = Column(String(20))
    to_version = Column(String(20))
    initiated_by = Column(String(100))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default="in_progress")
    error_log = Column(Text)
    notes = Column(Text)

class AvailableRelease(Base):
    __tablename__ = "available_releases"
    
    id = Column(Integer, primary_key=True)
    version = Column(String(20), unique=True, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    github_url = Column(String(500), nullable=False)
    download_url = Column(String(500), nullable=False)
    checksum_sha256 = Column(String(64))
    notes = Column(Text)
    is_test_release = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
