#!/usr/bin/env python3
"""
Testes para funcionalidade de confirmação de email
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastlite import Database

# Configurar path para importar módulos da aplicação
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.email_service import send_confirmation_email, EmailService
from models.usuario import Usuario
from datetime import datetime

@pytest.fixture
def test_config():
    """Configuração de teste"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Configurar variáveis de ambiente para teste
        os.environ['SECRET_KEY'] = 'test-secret-key-12345'
        os.environ['ADMIN_EMAIL'] = 'admin@test.com'
        os.environ['ADMIN_PASSWORD'] = 'admin123'
        os.environ['DATABASE_PATH'] = str(Path(temp_dir) / 'test.db')
        os.environ['BASE_URL'] = 'http://localhost:8000'
        
        config = Config()
        yield config
        
        # Limpar variáveis de ambiente
        for key in ['SECRET_KEY', 'ADMIN_EMAIL', 'ADMIN_PASSWORD', 'DATABASE_PATH', 'BASE_URL']:
            os.environ.pop(key, None)

@pytest.fixture
def test_db(test_config):
    """Banco de dados de teste"""
    db = Database(test_config.DATABASE_PATH)
    
    # Criar tabela de usuários
    db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            nome TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL DEFAULT 'cliente',
            confirmado BOOLEAN DEFAULT FALSE,
            cep TEXT,
            endereco TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT,
            telefone TEXT,
            cpf_cnpj TEXT,
            data_nascimento DATE,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            token_confirmacao TEXT
        )
    """)
    
    yield db
    db.close()

def test_send_confirmation_email_with_vieutil():
    """Testa envio de email de confirmação usando vieutil"""
    with patch('app.email_service.VIEUTIL_AVAILABLE', True), \
         patch('app.email_service.vieutil_send_email') as mock_vieutil, \
         patch('app.email_service.get_config') as mock_get_config:
        
        # Mock da configuração
        mock_config = MagicMock()
        mock_config.BASE_URL = 'http://localhost:8000'
        mock_get_config.return_value = mock_config
        
        mock_vieutil.return_value = True
        
        result = send_confirmation_email(
            user_email='test@example.com',
            user_name='João Silva',
            confirmation_token='abc123token'
        )
        
        assert result is True
        mock_vieutil.assert_called_once()
        
        # Verificar argumentos da chamada
        call_args = mock_vieutil.call_args
        assert call_args[1]['to'] == 'test@example.com'
        assert 'Confirme seu email' in call_args[1]['subject']
        assert 'João Silva' in call_args[1]['body']
        assert 'confirmar-email?token=abc123token' in call_args[1]['body']
        assert 'confirmar-email?token=abc123token' in call_args[1]['html']

def test_send_confirmation_email_fallback_to_smtp():
    """Testa fallback para SMTP quando vieutil falha"""
    with patch('app.email_service.VIEUTIL_AVAILABLE', True), \
         patch('app.email_service.vieutil_send_email') as mock_vieutil, \
         patch.object(EmailService, 'send_email') as mock_smtp, \
         patch('app.email_service.get_config') as mock_get_config:
        
        # Mock da configuração
        mock_config = MagicMock()
        mock_config.BASE_URL = 'http://localhost:8000'
        mock_config.SMTP_SERVER = 'smtp.test.com'
        mock_config.SMTP_PORT = 587
        mock_config.SMTP_USERNAME = 'test@test.com'
        mock_config.SMTP_PASSWORD = 'password'
        mock_config.EMAIL_FROM = 'noreply@viemar.com.br'
        mock_config.EMAIL_USE_TLS = True
        mock_get_config.return_value = mock_config
        
        # Simular falha do vieutil
        mock_vieutil.side_effect = Exception("Vieutil error")
        mock_smtp.return_value = True
        
        result = send_confirmation_email(
            user_email='test@example.com',
            user_name='João Silva',
            confirmation_token='abc123token'
        )
        
        assert result is True
        mock_vieutil.assert_called_once()
        mock_smtp.assert_called_once()
        
        # Verificar argumentos do SMTP
        call_args = mock_smtp.call_args
        assert call_args[0][0] == 'test@example.com'
        assert 'Confirme seu email' in call_args[0][1]
        assert 'João Silva' in call_args[0][2]

def test_send_confirmation_email_without_vieutil():
    """Testa envio quando vieutil não está disponível"""
    with patch('app.email_service.VIEUTIL_AVAILABLE', False), \
         patch.object(EmailService, 'send_email') as mock_smtp, \
         patch('app.email_service.get_config') as mock_get_config:
        
        # Mock da configuração
        mock_config = MagicMock()
        mock_config.BASE_URL = 'http://localhost:8000'
        mock_config.SMTP_SERVER = 'smtp.test.com'
        mock_config.SMTP_PORT = 587
        mock_config.SMTP_USERNAME = 'test@test.com'
        mock_config.SMTP_PASSWORD = 'password'
        mock_config.EMAIL_FROM = 'noreply@viemar.com.br'
        mock_config.EMAIL_USE_TLS = True
        mock_get_config.return_value = mock_config
        
        mock_smtp.return_value = True
        
        result = send_confirmation_email(
            user_email='test@example.com',
            user_name='João Silva',
            confirmation_token='abc123token'
        )
        
        assert result is True
        mock_smtp.assert_called_once()
        
        # Verificar argumentos do SMTP
        call_args = mock_smtp.call_args
        assert call_args[0][0] == 'test@example.com'
        assert 'Confirme seu email' in call_args[0][1]
        assert 'João Silva' in call_args[0][2]
        assert 'confirmar-email?token=abc123token' in call_args[0][2]

def test_confirmation_email_content():
    """Testa o conteúdo do email de confirmação"""
    with patch('app.email_service.VIEUTIL_AVAILABLE', False), \
         patch.object(EmailService, 'send_email') as mock_smtp, \
         patch('app.email_service.get_config') as mock_get_config:
        
        # Mock da configuração
        mock_config = MagicMock()
        mock_config.BASE_URL = 'http://localhost:8000'
        mock_config.SMTP_SERVER = 'smtp.test.com'
        mock_config.SMTP_PORT = 587
        mock_config.EMAIL_USER = 'test@test.com'
        mock_config.EMAIL_PASSWORD = 'password'
        mock_config.EMAIL_USE_TLS = True
        mock_get_config.return_value = mock_config
        
        mock_smtp.return_value = True
        
        send_confirmation_email(
            user_email='maria@example.com',
            user_name='Maria Santos',
            confirmation_token='token123abc'
        )
        
        call_args = mock_smtp.call_args
        email_body = call_args[0][2]
        html_body = call_args[0][3]
        
        # Verificar conteúdo do email texto
        assert 'Maria Santos' in email_body
        assert 'Sistema de Garantia Viemar' in email_body
        assert 'confirmar-email?token=token123abc' in email_body
        assert '24 horas' in email_body
        
        # Verificar conteúdo do email HTML
        assert 'Maria Santos' in html_body
        assert 'Confirmar Email' in html_body
        assert 'confirmar-email?token=token123abc' in html_body
        assert 'background-color: #28a745' in html_body  # Botão verde

def test_usuario_token_generation():
    """Testa geração de token de confirmação"""
    token1 = Usuario.gerar_token_confirmacao()
    token2 = Usuario.gerar_token_confirmacao()
    
    # Tokens devem ser diferentes
    assert token1 != token2
    
    # Tokens devem ter tamanho adequado (pelo menos 32 caracteres)
    assert len(token1) >= 32
    assert len(token2) >= 32
    
    # Tokens devem ser strings
    assert isinstance(token1, str)
    assert isinstance(token2, str)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])