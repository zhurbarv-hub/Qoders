# -*- coding: utf-8 -*-
"""API endpoints для управления развёрнутыми инстансами"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.registry import DeployedInstance

router = APIRouter(prefix="/api/instances", tags=["instances"])

@router.get("/")
async def list_instances(db: Session = Depends(get_db)):
    """Получить список всех развёрнутых инстансов"""
    instances = db.query(DeployedInstance).all()
    return {
        "total": len(instances),
        "instances": [
            {
                "id": i.id,
                "instance_name": i.instance_name,
                "client_company": i.client_company,
                "domain": i.domain,
                "status": i.status,
                "deployed_version": i.deployed_version,
                "deployed_at": i.deployed_at.isoformat() if i.deployed_at else None
            }
            for i in instances
        ]
    }

@router.get("/{instance_id}")
async def get_instance(instance_id: int, db: Session = Depends(get_db)):
    """Получить детальную информацию об инстансе"""
    instance = db.query(DeployedInstance).filter(DeployedInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return {
        "id": instance.id,
        "instance_name": instance.instance_name,
        "client_company": instance.client_company,
        "vds_ip": instance.vds_ip,
        "domain": instance.domain,
        "deployed_version": instance.deployed_version,
        "status": instance.status,
        "admin_email": instance.admin_email,
        "admin_phone": instance.admin_phone,
        "deployed_at": instance.deployed_at.isoformat() if instance.deployed_at else None,
        "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None
    }
