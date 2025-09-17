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
        import logging
        
        # Limpar handlers existentes
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        setup_logging()
        
        # Verificar se handlers foram adicionados
        assert len(root_logger.handlers) >= 1
    
    def test_setup_logging_with_level(self):
        """Testa configuração do logging com nível específico"""
        import logging
        
        # Limpar handlers existentes
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        setup_logging()
        
        # Verificar se o nível foi configurado
        assert root_logger.level == logging.DEBUG
    
    def test_get_logger(self):
        """Testa obtenção de logger"""
        logger = get_logger("test_module")
        assert logger is not None
        assert logger.name == "test_module"
    
    def test_get_logger_with_name(self):
        """Testa obtenção de logger com nome específico"""
        logger = get_logger("test_module")
        assert logger is not None
        assert logger.name == "test_module"
    
    def test_setup_logging_creates_directory(self):
        """Testa se o setup cria o diretório de logs"""
        from pathlib import Path
        
        # Verificar se o diretório de logs existe após setup
        log_dir = Path(__file__).parent.parent / 'logs'
        
        setup_logging()
        
        # Diretório deve existir após o setup
        assert log_dir.exists()
    
    def test_logging_rotation_config(self):
        """Testa configuração de rotação de logs"""
        import logging
        
        setup_logging()
        
        # Verificar se o arquivo de log foi configurado
        logger = get_logger("rotation_test")
        logger.info("Teste de rotação de logs")
        
        # Verificar se o logger foi criado corretamente
        assert logger.name == "rotation_test"
    
    def test_setup_logging_with_rotation_handler(self):
        """Testa configuração do handler de rotação"""
        import logging
        
        # Limpar handlers existentes
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        setup_logging()
        
        # Verificar se pelo menos um handler foi adicionado
        assert len(root_logger.handlers) >= 1
        
        # Verificar se existe um TimedRotatingFileHandler
        has_timed_handler = any(
            isinstance(handler, logging.handlers.TimedRotatingFileHandler)
            for handler in root_logger.handlers
        )
        assert has_timed_handler
    
    def test_multiple_loggers(self):
        """Testa criação de múltiplos loggers"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        logger3 = get_logger("module1")  # Mesmo nome do primeiro
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger3.name == "module1"
        assert logger1 is logger3  # Deve ser o mesmo objeto