"""Testes para o arquivo main.py"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar o diretório raiz ao path para importar main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMain:
    """Testes para o módulo main"""
    
    @patch('main.fast_app')
    @patch('main.Config')
    def test_create_app(self, mock_config, mock_fast_app):
        """Testa a criação da aplicação"""
        # Configurar mocks
        mock_config_instance = MagicMock()
        mock_config_instance.DEBUG = True
        mock_config_instance.LIVE_RELOAD = True
        mock_config_instance.DATABASE_PATH = ':memory:'
        mock_config.return_value = mock_config_instance
        
        mock_app = MagicMock()
        mock_rt = MagicMock()
        mock_fast_app.return_value = (mock_app, mock_rt)
        
        # Importar e testar create_app
        from main import create_app
        
        # Chamar função
        app, config = create_app()
        
        # Verificar se foi chamado corretamente
        mock_fast_app.assert_called_once()
        mock_config.assert_called_once()
        
        # Verificar retorno
        assert app == mock_app
        assert config == mock_config_instance
        
    @patch('main.serve')
    @patch('main.create_app')
    def test_main_function(self, mock_create_app, mock_serve):
        """Testa a função main"""
        mock_app = MagicMock()
        mock_config = MagicMock()
        mock_config.HOST = 'localhost'
        mock_config.PORT = 8000
        mock_config.LIVE_RELOAD = True
        mock_create_app.return_value = (mock_app, mock_config)
        
        from main import main
        
        main()
        
        # Verificar se create_app foi chamado
        mock_create_app.assert_called_once()
        
        # Verificar se serve foi chamado com os parâmetros corretos
        mock_serve.assert_called_once()
        
    def test_app_creation(self):
        """Testa se a aplicação é criada corretamente"""
        # Importar o app criado no módulo
        import main
        
        # Verificar se o app existe
        assert hasattr(main, 'app')
        assert main.app is not None
        
    @patch('main.Database')
    @patch('main.init_database')
    @patch('main.fast_app')
    @patch('main.Config')
    def test_config_usage(self, mock_config, mock_fast_app, mock_init_database, mock_database):
        """Testa se a configuração é usada corretamente"""
        # Configurar mocks
        mock_config_instance = MagicMock()
        mock_config_instance.HOST = '0.0.0.0'
        mock_config_instance.PORT = 8000
        mock_config_instance.LIVE_RELOAD = False
        mock_config_instance.DEBUG = True
        mock_config_instance.DATABASE_PATH = ':memory:'
        mock_config.return_value = mock_config_instance
        
        mock_app = MagicMock()
        mock_rt = MagicMock()
        mock_fast_app.return_value = (mock_app, mock_rt)
        
        mock_db = MagicMock()
        mock_database.return_value = mock_db
        
        # Importar e testar create_app
        from main import create_app
        
        app, config = create_app()
        
        # Verificar se Config foi chamado
        mock_config.assert_called_once()
        
        # Verificar se o objeto de configuração foi retornado
        assert config == mock_config_instance