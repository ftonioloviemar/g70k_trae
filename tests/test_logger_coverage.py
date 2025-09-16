#!/usr/bin/env python3
"""
Testes para melhorar cobertura do módulo logger
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.logger import setup_logging, get_logger

class TestLogger:
    """Testes para o sistema de logging"""
    
    def test_setup_logging_default(self):
        """Testa configuração padrão do logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"
            log_file = log_dir / "test.log"
            
            setup_logging(log_file=str(log_file))
            
            # Verificar se o diretório foi criado
            assert log_dir.exists()
    
    def test_setup_logging_with_level(self):
        """Testa configuração do logging com nível específico"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"
            log_file = log_dir / "test.log"
            
            setup_logging(log_file=str(log_file), log_level="DEBUG")
            
            # Verificar se o diretório foi criado
            assert log_dir.exists()
    
    def test_get_logger(self):
        """Testa obtenção de logger"""
        logger = get_logger("test_module")
        assert logger is not None
        assert logger.name == "test_module"
    
    def test_get_logger_default_name(self):
        """Testa obtenção de logger com nome padrão"""
        logger = get_logger()
        assert logger is not None
        assert logger.name == "app"
    
    def test_setup_logging_creates_directory(self):
        """Testa se o setup cria o diretório de logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "new_logs"
            log_file = log_dir / "app.log"
            
            # Diretório não deve existir inicialmente
            assert not log_dir.exists()
            
            setup_logging(log_file=str(log_file))
            
            # Diretório deve ser criado
            assert log_dir.exists()
    
    def test_logging_rotation_config(self):
        """Testa configuração de rotação de logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "logs" / "rotation_test.log"
            
            # Configurar logging com rotação
            setup_logging(
                log_file=str(log_file),
                log_level="INFO",
                max_size=1024 * 1024,  # 1MB
                backup_count=5
            )
            
            # Verificar se o arquivo de log foi configurado
            logger = get_logger("rotation_test")
            logger.info("Teste de rotação de logs")
    
    @patch('app.logger.RotatingFileHandler')
    def test_setup_logging_with_rotation_handler(self, mock_handler):
        """Testa configuração do handler de rotação"""
        mock_handler_instance = MagicMock()
        mock_handler.return_value = mock_handler_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "logs" / "handler_test.log"
            
            setup_logging(log_file=str(log_file))
            
            # Verificar se o handler foi criado
            mock_handler.assert_called()
    
    def test_multiple_loggers(self):
        """Testa criação de múltiplos loggers"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        logger3 = get_logger("module1")  # Mesmo nome do primeiro
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger3.name == "module1"
        assert logger1 is logger3  # Deve ser o mesmo objeto