# -*- coding: utf-8 -*-
"""API endpoints для процесса развёртывания"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from ..database import get_db
from ..models.registry import DeployedInstance, DeploymentHistory

router = APIRouter(prefix="/api/deploy", tags=["deployment"])

class DeploymentRequest(BaseModel):
    mode: str  # "test" or "production"
    vds_ip: str
    ssh_password: str
    admin_name: str
    admin_email: str
    admin_phone: str
    company_name: str
    bot_token: str
    admin_telegram_ids: str
    notification_time: str = "09:00"
    timezone: str = "Europe/Moscow"
    alert_days: str = "14,7,3"

@router.post("/start")
async def start_deployment(request: DeploymentRequest, db: Session = Depends(get_db)):
    """Начать процесс развёртывания"""
    
    # Создаём запись в истории
    history = DeploymentHistory(
        action="deploy",
        to_version="1.0.0",
        initiated_by=request.admin_email,
        status="in_progress"
    )
    db.add(history)
    db.commit()
    
    return {
        "deployment_id": history.id,
        "status": "started",
        "message": "Deployment process initiated"
    }

@router.websocket("/ws/{deployment_id}")
async def deployment_logs(websocket: WebSocket, deployment_id: int):
    """WebSocket для отправки логов в реальном времени"""
    await websocket.accept()
    
    try:
        # Симуляция логов (в реальности здесь будет выполнение deployment)
        logs = [
            "Connecting to VDS...",
            "Installing system packages...",
            "Setting up database...",
            "Downloading application...",
            "Configuring services...",
            "Starting services...",
            "Deployment complete!"
        ]
        
        for log in logs:
            await websocket.send_json({"log": log, "timestamp": datetime.now().isoformat()})
            
    except WebSocketDisconnect:
        pass

@router.get("/status/{deployment_id}")
async def get_deployment_status(deployment_id: int, db: Session = Depends(get_db)):
    """Получить статус развёртывания"""
    history = db.query(DeploymentHistory).filter(DeploymentHistory.id == deployment_id).first()
    if not history:
        return {"error": "Deployment not found"}
    
    return {
        "id": history.id,
        "status": history.status,
        "started_at": history.started_at.isoformat() if history.started_at else None,
        "completed_at": history.completed_at.isoformat() if history.completed_at else None
    }
