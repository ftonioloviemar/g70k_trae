"""Testes abrangentes para o módulo de logging."""

import pytest
import logging
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.logger import setup_logging, get_logger

class TestLoggerModule:
    """Testes para o módulo de logging."""
    
    def setup_method(self):
        """Configuração antes de cada teste."""
        # Limpar handlers existentes
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.setLevel(logging.WARNING)
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Limpar handlers existentes
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def test_import_logger_module(self):
        """Testa se o módulo logger pode ser importado."""
        from app import logger
        assert logger is not None
        assert hasattr(logger, 'setup_logging')
        assert hasattr(logger, 'get_logger')
    
    def test_get_logger_function(self):
        """Testa a função get_logger."""
        logger_name = 'test_logger'
        logger = get_logger(logger_name)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name
    
    def test_get_logger_different_names(self):
        """Testa get_logger com nomes diferentes."""
        logger1 = get_logger('module1')
        logger2 = get_logger('module2')
        
        assert logger1.name == 'module1'
        assert logger2.name == 'module2'
        assert logger1 != logger2
    
    def test_get_logger_same_name(self):
        """Testa get_logger com o mesmo nome retorna o mesmo logger."""
        logger1 = get_logger('same_name')
        logger2 = get_logger('same_name')
        
        assert logger1 is logger2
    
    @patch('pathlib.Path.mkdir')
    @patch('logging.handlers.TimedRotatingFileHandler')
    @patch('logging.StreamHandler')
    def test_setup_logging_creates_handlers(self, mock_stream, mock_file, mock_mkdir):
        """Testa se setup_logging cria os handlers corretamente."""
        mock_file_handler = MagicMock()
        mock_stream_handler = MagicMock()
        mock_file.return_value = mock_file_handler
        mock_stream.return_value = mock_stream_handler
        
        setup_logging()
        
        # Verificar se o diretório foi criado
        mock_mkdir.assert_called_once_with(exist_ok=True)
        
        # Verificar se os handlers foram criados
        mock_file.assert_called_once()
        mock_stream.assert_called_once()
        
        # Verificar se os formatters foram configurados
        mock_file_handler.setFormatter.assert_called_once()
        mock_stream_handler.setFormatter.assert_called_once()
        
        # Verificar se os níveis foram configurados
        mock_file_handler.setLevel.assert_called_once_with(logging.INFO)
        mock_stream_handler.setLevel.assert_called_once_with(logging.DEBUG)
    
    def test_setup_logging_with_temp_dir(self):
        """Testa setup_logging com diretório temporário."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('pathlib.Path.__truediv__') as mock_div:
                mock_div.return_value = temp_path / 'logs'
                
                # Executar setup_logging
                setup_logging()
                
                # Verificar se o logger raiz foi configurado
                root_logger = logging.getLogger()
                assert root_logger.level == logging.DEBUG
                assert len(root_logger.handlers) >= 2
    
    def test_logging_levels(self):
        """Testa diferentes níveis de logging."""
        logger = get_logger('test_levels')
        
        # Configurar um handler de teste
        test_handler = logging.StreamHandler()
        test_handler.setLevel(logging.DEBUG)
        logger.addHandler(test_handler)
        logger.setLevel(logging.DEBUG)
        
        # Testar se os métodos de logging existem
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')
    
    def test_log_format_structure(self):
        """Testa a estrutura do formato de log."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Criar um record de teste
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Verificar se contém os elementos esperados
        assert 'test_logger' in formatted
        assert 'INFO' in formatted
        assert 'Test message' in formatted
        assert '-' in formatted  # Separadores
    
    def test_path_operations(self):
        """Testa operações com Path para logs."""
        # Simular estrutura de diretórios
        current_file = Path(__file__)
        parent_dir = current_file.parent.parent
        log_dir = parent_dir / 'logs'
        
        assert isinstance(log_dir, Path)
        assert str(log_dir).endswith('logs')
    
    def test_datetime_import(self):
        """Testa importação e uso do datetime."""
        from datetime import datetime
        
        now = datetime.now()
        assert isinstance(now, datetime)
        
        # Testar formatação de data
        formatted = now.strftime('%Y-%m-%d %H:%M:%S')
        assert len(formatted) == 19  # YYYY-MM-DD HH:MM:SS
        assert '-' in formatted
        assert ':' in formatted
    
    def test_logging_handlers_import(self):
        """Testa importação de handlers de logging."""
        import logging.handlers
        
        assert hasattr(logging.handlers, 'TimedRotatingFileHandler')
        
        # Testar criação de handler (sem arquivo real)
        with tempfile.NamedTemporaryFile() as temp_file:
            handler = logging.handlers.TimedRotatingFileHandler(
                filename=temp_file.name,
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            
            assert isinstance(handler, logging.handlers.TimedRotatingFileHandler)
            assert handler.when == 'MIDNIGHT'
            assert handler.interval == 1
            assert handler.backupCount == 30
    
    def test_stream_handler_creation(self):
        """Testa criação de StreamHandler."""
        handler = logging.StreamHandler()
        
        assert isinstance(handler, logging.StreamHandler)
        assert hasattr(handler, 'setFormatter')
        assert hasattr(handler, 'setLevel')
    
    def test_logger_hierarchy(self):
        """Testa hierarquia de loggers."""
        parent_logger = get_logger('parent')
        child_logger = get_logger('parent.child')
        
        assert parent_logger.name == 'parent'
        assert child_logger.name == 'parent.child'
        assert child_logger.parent.name == 'parent'
    
    def test_logging_constants(self):
        """Testa constantes de logging."""
        assert logging.DEBUG == 10
        assert logging.INFO == 20
        assert logging.WARNING == 30
        assert logging.ERROR == 40
        assert logging.CRITICAL == 50
        
        # Testar ordem dos níveis
        assert logging.DEBUG < logging.INFO
        assert logging.INFO < logging.WARNING
        assert logging.WARNING < logging.ERROR
        assert logging.ERROR < logging.CRITICAL
    
    def test_utf8_encoding(self):
        """Testa suporte a encoding UTF-8."""
        test_message = "Teste com acentuação: ção, ã, é, ü"
        
        # Verificar se a string pode ser codificada em UTF-8
        encoded = test_message.encode('utf-8')
        decoded = encoded.decode('utf-8')
        
        assert decoded == test_message
        assert 'ção' in decoded
        assert 'ã' in decoded
        assert 'é' in decoded
        assert 'ü' in decoded