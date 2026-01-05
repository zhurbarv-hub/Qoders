# -*- coding: utf-8 -*-
"""Configuration settings"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    github_repo: str = "zhurbarv-hub/Qoders"
    github_token: str = ""
    master_domain: str = "kkt-box.net"
    
    class Config:
        env_file = ".env"

settings = Settings()
