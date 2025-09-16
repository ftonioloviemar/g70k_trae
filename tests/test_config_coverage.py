#!/usr/bin/env python3
"""
Testes para melhorar cobertura do módulo config
"""

import pytest
import os
from unittest.mock import patch
from pathlib import Path
from app.config import Config

class TestConfig:
    """Testes para a classe Config"""
    
    def test_config_default_values(self):
        """Testa valores padrão da configuração"""
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret', 'ADMIN_EMAIL': 'admin@test.com', 'ADMIN_PASSWORD': 'admin123'}, clear=True):
            config = Config()
            
            assert config.HOST == '0.0.0.0'
            assert config.PORT == 8000
            assert config.DEBUG == True
            assert config.SECRET_KEY == 'test_secret'
            assert config.LIVE_RELOAD == config.DEBUG
    
    def test_config_environment_variables(self):
        """Testa configuração com variáveis de ambiente"""
        env_vars = {
            'HOST': '127.0.0.1',
            'PORT': '9000',
            'DEBUG': 'false',
            'SECRET_KEY': 'env_secret',
            'ADMIN_EMAIL': 'admin@env.com',
            'ADMIN_PASSWORD': 'envpass123'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config()
            
            assert config.HOST == '127.0.0.1'
            assert config.PORT == 9000
            assert config.DEBUG == False
            assert config.SECRET_KEY == 'env_secret'
    
    def test_config_database_path_default(self):
        """Testa caminho padrão do banco de dados"""
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret', 'ADMIN_EMAIL': 'admin@test.com', 'ADMIN_PASSWORD': 'admin123'}, clear=True):
            config = Config()
            
            assert 'data' in str(config.DATABASE_PATH)
            assert 'viemar_garantia.db' in str(config.DATABASE_PATH)
    
    def test_config_database_path_env(self):
        """Testa caminho do banco via variável de ambiente"""
        env_vars = {
            'DATABASE_PATH': '/custom/path/database.db',
            'SECRET_KEY': 'test_secret',
            'ADMIN_EMAIL': 'admin@test.com',
            'ADMIN_PASSWORD': 'admin123'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config()
            
            assert config.DATABASE_PATH == '/custom/path/database.db'
    
    def test_config_missing_secret_key(self):
        """Testa erro quando SECRET_KEY não está definida"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SECRET_KEY deve ser definida"):
                Config()
    
    def test_config_missing_admin_credentials(self):
        """Testa erro quando credenciais de admin não estão definidas"""
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret'}, clear=True):
            with pytest.raises(ValueError, match="ADMIN_EMAIL e ADMIN_PASSWORD devem ser definidas"):
                Config()
    
    def test_config_log_settings(self):
        """Testa configurações de log"""
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret', 'ADMIN_EMAIL': 'admin@test.com', 'ADMIN_PASSWORD': 'admin123'}, clear=True):
            config = Config()
            
            assert config.LOG_LEVEL == 'INFO'
            assert 'logs' in str(config.LOG_DIR)
            assert 'viemar_garantia.log' in str(config.LOG_FILE)
            assert config.LOG_MAX_SIZE == 10 * 1024 * 1024
            assert config.LOG_BACKUP_COUNT == 5
    
    def test_config_email_settings(self):
        """Testa configurações de email"""
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret', 'ADMIN_EMAIL': 'admin@test.com', 'ADMIN_PASSWORD': 'admin123'}, clear=True):
            config = Config()
            
            assert config.SMTP_SERVER == 'smtp.gmail.com'
            assert config.SMTP_PORT == 587
            assert config.EMAIL_FROM == 'noreply@viemar.com.br'
            assert config.EMAIL_USE_TLS == True
    
    def test_config_upload_settings(self):
        """Testa configurações de upload"""
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret', 'ADMIN_EMAIL': 'admin@test.com', 'ADMIN_PASSWORD': 'admin123'}, clear=True):
            config = Config()
            
            assert 'uploads' in str(config.UPLOAD_DIR)
            assert config.MAX_FILE_SIZE == 5 * 1024 * 1024
    
    def test_config_base_url(self):
        """Testa configuração da URL base"""
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret', 'ADMIN_EMAIL': 'admin@test.com', 'ADMIN_PASSWORD': 'admin123'}, clear=True):
            config = Config()
            
            assert 'localhost' in config.BASE_URL
            assert str(config.PORT) in config.BASE_URL
    
    def test_config_type_conversion(self):
        """Testa conversão de tipos das variáveis de ambiente"""
        env_vars = {
            'PORT': '3000',
            'SESSION_TIMEOUT': '7200',
            'SMTP_PORT': '465',
            'SECRET_KEY': 'test_secret',
            'ADMIN_EMAIL': 'admin@test.com',
            'ADMIN_PASSWORD': 'admin123'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config()
            
            assert isinstance(config.PORT, int)
            assert config.PORT == 3000
            assert isinstance(config.SESSION_TIMEOUT, int)
            assert config.SESSION_TIMEOUT == 7200
            assert isinstance(config.SMTP_PORT, int)
            assert config.SMTP_PORT == 465