#!/usr/bin/env python3
"""
Testes para o serviço de integração com Firebird
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager

from app.services.firebird_service import FirebirdService
from app.config import Config
from models.produto import Produto


class TestFirebirdService:
    """Testes para a classe FirebirdService"""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture com configuração mock para testes"""
        config = Mock(spec=Config)
        config.FIREBIRD_HOST = "localhost"
        config.FIREBIRD_DATABASE = "/path/to/database.fdb"
        config.FIREBIRD_USER = "test_user"
        config.FIREBIRD_PASSWORD = "test_password"
        config.FIREBIRD_ROLE = "test_role"
        config.FIREBIRD_CHARSET = "UTF8"
        return config
    
    @pytest.fixture
    def firebird_service(self, mock_config):
        """Fixture com instância do FirebirdService"""
        return FirebirdService(mock_config)
    
    def test_init(self, mock_config):
        """Testa a inicialização do serviço"""
        service = FirebirdService(mock_config)
        assert service.config == mock_config
        assert service._connection_string is not None
    
    def test_build_connection_string(self, firebird_service, mock_config):
        """Testa a construção da string de conexão"""
        expected = (
            f"firebird://{mock_config.FIREBIRD_USER}:{mock_config.FIREBIRD_PASSWORD}@"
            f"{mock_config.FIREBIRD_HOST}/{mock_config.FIREBIRD_DATABASE}"
            f"?role={mock_config.FIREBIRD_ROLE}&charset={mock_config.FIREBIRD_CHARSET}"
        )
        assert firebird_service._connection_string == expected
    
    @patch('app.services.firebird_service.fb')
    def test_get_connection_success(self, mock_fb, firebird_service):
        """Testa conexão bem-sucedida com o Firebird"""
        mock_connection = Mock()
        mock_fb.connect.return_value = mock_connection
        
        with firebird_service.get_connection() as conn:
            assert conn == mock_connection
        
        mock_fb.connect.assert_called_once_with(firebird_service._connection_string)
        mock_connection.close.assert_called_once()
    
    @patch('app.services.firebird_service.fb')
    def test_get_connection_failure(self, mock_fb, firebird_service):
        """Testa falha na conexão com o Firebird"""
        mock_fb.connect.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection failed"):
            with firebird_service.get_connection():
                pass
    
    @patch('app.services.firebird_service.fb')
    def test_test_connection_success(self, mock_fb, firebird_service):
        """Testa o método de teste de conexão com sucesso"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        mock_fb.connect.return_value = mock_connection
        
        result = firebird_service.test_connection()
        
        assert result is True
        mock_fb.connect.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT 1 FROM RDB$DATABASE")
    
    @patch('app.services.firebird_service.fb')
    def test_test_connection_failure(self, mock_fb, firebird_service):
        """Testa o método de teste de conexão com falha"""
        mock_fb.connect.side_effect = Exception("Connection failed")
        
        result = firebird_service.test_connection()
        
        assert result is False
    
    @patch('app.services.firebird_service.fb')
    def test_get_produtos_success(self, mock_fb, firebird_service):
        """Testa a busca de produtos com sucesso"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock dos dados retornados
        mock_cursor.fetchall.return_value = [
            ("PROD001", "Produto Teste 1", "Descrição 1", 100.50, "UN"),
            ("PROD002", "Produto Teste 2", "Descrição 2", 200.75, "KG")
        ]
        
        mock_fb.connect.return_value = mock_connection
        
        produtos = firebird_service.get_produtos()
        
        assert len(produtos) == 2
        assert produtos[0]["codigo"] == "PROD001"
        assert produtos[0]["nome"] == "Produto Teste 1"
        assert produtos[1]["codigo"] == "PROD002"
        assert produtos[1]["nome"] == "Produto Teste 2"
    
    @patch('app.services.firebird_service.fb')
    def test_get_produtos_empty(self, mock_fb, firebird_service):
        """Testa a busca de produtos sem resultados"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_fb.connect.return_value = mock_connection
        
        produtos = firebird_service.get_produtos()
        
        assert produtos == []
    
    @patch('app.services.firebird_service.fb')
    def test_get_produtos_failure(self, mock_fb, firebird_service):
        """Testa falha na busca de produtos"""
        mock_fb.connect.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            firebird_service.get_produtos()
    
    @patch('app.services.firebird_service.get_db')
    @patch('app.services.firebird_service.fb')
    def test_sync_produtos_success(self, mock_fb, mock_get_db, firebird_service):
        """Testa a sincronização de produtos com sucesso"""
        # Mock da conexão Firebird
        mock_fb_connection = Mock()
        mock_fb_cursor = Mock()
        mock_fb_connection.cursor.return_value = mock_fb_cursor
        mock_fb_cursor.fetchall.return_value = [
            ("PROD001", "Produto Teste", "Descrição", 100.50, "UN")
        ]
        mock_fb.connect.return_value = mock_fb_connection
        
        # Mock da conexão SQLite
        mock_sqlite_connection = Mock()
        mock_sqlite_cursor = Mock()
        mock_sqlite_connection.cursor.return_value = mock_sqlite_cursor
        mock_sqlite_cursor.fetchone.return_value = None  # Produto não existe
        mock_get_db.return_value = mock_sqlite_connection
        
        result = firebird_service.sync_produtos()
        
        assert "produtos_inseridos" in result
        assert "produtos_atualizados" in result
        assert "total_processados" in result
        assert result["total_processados"] == 1
    
    @patch('app.services.firebird_service.get_db')
    @patch('app.services.firebird_service.fb')
    def test_sync_produtos_update_existing(self, mock_fb, mock_get_db, firebird_service):
        """Testa a atualização de produtos existentes"""
        # Mock da conexão Firebird
        mock_fb_connection = Mock()
        mock_fb_cursor = Mock()
        mock_fb_connection.cursor.return_value = mock_fb_cursor
        mock_fb_cursor.fetchall.return_value = [
            ("PROD001", "Produto Atualizado", "Nova Descrição", 150.75, "UN")
        ]
        mock_fb.connect.return_value = mock_fb_connection
        
        # Mock da conexão SQLite - produto já existe
        mock_sqlite_connection = Mock()
        mock_sqlite_cursor = Mock()
        mock_sqlite_connection.cursor.return_value = mock_sqlite_cursor
        mock_sqlite_cursor.fetchone.return_value = (1, "PROD001", "Produto Antigo", "Descrição Antiga", 100.50, "UN")
        mock_get_db.return_value = mock_sqlite_connection
        
        result = firebird_service.sync_produtos()
        
        assert result["produtos_atualizados"] == 1
        assert result["produtos_inseridos"] == 0
    
    @patch('app.services.firebird_service.fb')
    def test_sync_produtos_firebird_failure(self, mock_fb, firebird_service):
        """Testa falha na conexão com Firebird durante sincronização"""
        mock_fb.connect.side_effect = Exception("Firebird connection failed")
        
        with pytest.raises(Exception, match="Firebird connection failed"):
            firebird_service.sync_produtos()
    
    def test_format_produto_data(self, firebird_service):
        """Testa a formatação dos dados do produto"""
        raw_data = ("PROD001", "Produto Teste", "Descrição do produto", 99.99, "UN")
        
        formatted = firebird_service._format_produto_data(raw_data)
        
        expected = {
            "codigo": "PROD001",
            "nome": "Produto Teste",
            "descricao": "Descrição do produto",
            "preco": 99.99,
            "unidade": "UN"
        }
        
        assert formatted == expected
    
    def test_format_produto_data_with_none_values(self, firebird_service):
        """Testa a formatação com valores None"""
        raw_data = ("PROD001", None, None, None, None)
        
        formatted = firebird_service._format_produto_data(raw_data)
        
        expected = {
            "codigo": "PROD001",
            "nome": "",
            "descricao": "",
            "preco": 0.0,
            "unidade": ""
        }
        
        assert formatted == expected
    
    def test_validate_produto_data_valid(self, firebird_service):
        """Testa validação de dados válidos"""
        produto_data = {
            "codigo": "PROD001",
            "nome": "Produto Teste",
            "descricao": "Descrição",
            "preco": 99.99,
            "unidade": "UN"
        }
        
        result = firebird_service._validate_produto_data(produto_data)
        assert result is True
    
    def test_validate_produto_data_invalid_codigo(self, firebird_service):
        """Testa validação com código inválido"""
        produto_data = {
            "codigo": "",
            "nome": "Produto Teste",
            "descricao": "Descrição",
            "preco": 99.99,
            "unidade": "UN"
        }
        
        result = firebird_service._validate_produto_data(produto_data)
        assert result is False
    
    def test_validate_produto_data_invalid_preco(self, firebird_service):
        """Testa validação com preço inválido"""
        produto_data = {
            "codigo": "PROD001",
            "nome": "Produto Teste",
            "descricao": "Descrição",
            "preco": -10.0,
            "unidade": "UN"
        }
        
        result = firebird_service._validate_produto_data(produto_data)
        assert result is False