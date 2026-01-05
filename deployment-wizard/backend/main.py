# -*- coding: utf-8 -*-
"""
KKT Deployment Wizard Backend
FastAPI приложение для автоматизированного развёртывания KKT инстансов
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .api import instances_router, deployment_router, releases_router

app = FastAPI(
    title="KKT Deployment Wizard",
    description="Автоматизированная система развёртывания KKT на клиентских VDS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(instances_router)
app.include_router(deployment_router)
app.include_router(releases_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "kkt-deployment-wizard"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "KKT Deployment Wizard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8100,
        reload=True
    )
