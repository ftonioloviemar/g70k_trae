#!/usr/bin/env python3
"""
Configurações da aplicação Viemar Garantia 70k
"""

import os
from pathlib import Path

class Config:
    """Configurações da aplicação"""
    
    def __init__(self):
        # Diretório base do projeto
        self.BASE_DIR = Path(__file__).parent.parent
        
        # Configurações do servidor
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', 8000))
        self.DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        self.LIVE_RELOAD = self.DEBUG
        
        # Configurações do banco de dados
        database_path_env = os.getenv('DATABASE_PATH')
        if database_path_env:
            self.DATABASE_PATH = database_path_env
        else:
            self.DATABASE_PATH = self.BASE_DIR / 'data' / 'viemar_garantia.db'
        
        # Configurações de segurança
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'viemar-garantia-70k-secret-key-change-in-production')
        self.SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hora
        
        # Configurações de email
        self.SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
        self.SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
        self.EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@viemar.com.br')
        self.EMAIL_USE_TLS = True
        
        # Configurações de logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_DIR = self.BASE_DIR / 'logs'
        self.LOG_FILE = self.LOG_DIR / 'viemar_garantia.log'
        self.LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
        self.LOG_BACKUP_COUNT = 5
        
        # Credenciais do administrador padrão
        self.ADMIN_EMAIL = 'ftoniolo@viemar.com.br'
        self.ADMIN_PASSWORD = 'abc123'
        
        # Configurações de upload
        self.UPLOAD_DIR = self.BASE_DIR / 'uploads'
        self.MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        
        # Criar diretórios necessários
        self.LOG_DIR.mkdir(exist_ok=True)
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        (self.BASE_DIR / 'data').mkdir(exist_ok=True)