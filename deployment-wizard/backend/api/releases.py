# -*- coding: utf-8 -*-
"""API endpoints для работы с релизами из GitHub"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import requests
from ..database import get_db
from ..config import settings
from ..models.registry import AvailableRelease

router = APIRouter(prefix="/api/releases", tags=["releases"])

@router.get("/latest")
async def get_latest_release():
    """Получить информацию о последнем релизе из GitHub"""
    url = f"https://api.github.com/repos/{settings.github_repo}/releases/latest"
    headers = {}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch release"}
    
    data = response.json()
    return {
        "version": data["tag_name"],
        "name": data["name"],
        "published_at": data["published_at"],
        "html_url": data["html_url"],
        "assets": [
            {
                "name": asset["name"],
                "size": asset["size"],
                "download_url": asset["browser_download_url"]
            }
            for asset in data.get("assets", [])
        ]
    }

@router.get("/")
async def list_releases(db: Session = Depends(get_db)):
    """Получить список всех релизов из базы"""
    releases = db.query(AvailableRelease).order_by(AvailableRelease.release_date.desc()).all()
    return {
        "total": len(releases),
        "releases": [
            {
                "version": r.version,
                "release_date": r.release_date.isoformat(),
                "github_url": r.github_url,
                "is_test": r.is_test_release
            }
            for r in releases
        ]
    }
