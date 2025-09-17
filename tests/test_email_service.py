#!/usr/bin/env python3
"""
Testes para o serviço de envio de emails
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from app.email_service import EmailService, get_config
from app.config import Config


class TestEmailService:
    """Testes para a classe EmailService"""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture com configuração mock para testes"""
        config = Mock(spec=Config)
        config.EMAIL_FROM = "test@viemar.com.br"
        config.EMAIL_ADMIN = "admin@viemar.com.br"
        config.EMAIL_GARANTIA = "garantia@viemar.com.br"
        return config
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_init_with_vieutil(self, mock_get_config, mock_config):
        """Testa inicialização com vieutil disponível"""
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        assert service.email_from == mock_config.EMAIL_FROM
        assert service.vieutil_available is True
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', False)
    def test_init_without_vieutil(self, mock_get_config, mock_config):
        """Testa inicialização sem vieutil disponível"""
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        assert service.email_from == mock_config.EMAIL_FROM
        assert service.vieutil_available is False
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_email_success(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa envio de email com sucesso"""
        mock_get_config.return_value = mock_config
        mock_vieutil_send.return_value = True
        
        service = EmailService()
        
        result = service.send_email(
            to_email="cliente@email.com",
            subject="Teste",
            body="Corpo do email"
        )
        
        assert result is True
        mock_vieutil_send.assert_called_once_with(
            to="cliente@email.com",
            subject="Teste",
            text="Corpo do email",
            send_from="garantia70mil@viemar.com.br"
        )
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_welcome_email(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa envio de email de boas-vindas"""
        mock_get_config.return_value = mock_config
        mock_config.BASE_URL = "https://garantia.viemar.com.br"
        mock_vieutil_send.return_value = True
        
        service = EmailService()
        
        result = service.send_welcome_email(
            user_email="cliente@email.com",
            user_name="João Silva"
        )
        
        assert result is True
        mock_vieutil_send.assert_called_once()
        
        # Verifica se os dados estão no corpo do email
        call_args = mock_vieutil_send.call_args
        assert call_args[1]['to'] == "cliente@email.com"
        assert "João Silva" in call_args[1]['text']
        assert "Bem-vindo" in call_args[1]['subject']
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', False)
    def test_send_email_without_vieutil(self, mock_get_config, mock_config):
        """Testa envio de email sem vieutil disponível"""
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        result = service.send_email(
            to_email="cliente@email.com",
            subject="Teste",
            body="Corpo do email"
        )
        
        assert result is False
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_email_failure(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa falha no envio de email"""
        mock_get_config.return_value = mock_config
        mock_vieutil_send.side_effect = Exception("Erro no envio")
        
        service = EmailService()
        
        result = service.send_email(
            to_email="cliente@email.com",
            subject="Teste",
            body="Corpo do email"
        )
        
        assert result is False
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_warranty_activation_email(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa envio de email de ativação de garantia"""
        mock_get_config.return_value = mock_config
        mock_config.BASE_URL = "https://garantia.viemar.com.br"
        mock_vieutil_send.return_value = True
        
        service = EmailService()
        
        result = service.send_warranty_activation_email(
            user_email="joao@email.com",
            user_name="João Silva",
            produto_nome="Produto Teste",
            veiculo_info="Honda Civic 2020",
            data_vencimento="15/01/2025"
        )
        
        assert result is True
        mock_vieutil_send.assert_called_once()
        
        # Verifica se os dados da garantia estão no corpo do email
        call_args = mock_vieutil_send.call_args
        body = call_args[1]['text']
        assert "João Silva" in body
        assert "Produto Teste" in body
        assert "Honda Civic 2020" in body
        assert "15/01/2025" in body
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_admin_notification(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa envio de notificação para admin"""
        mock_get_config.return_value = mock_config
        mock_config.ADMIN_EMAIL = "admin@viemar.com.br"
        mock_vieutil_send.return_value = True
        
        service = EmailService()
        
        result = service.send_admin_notification(
            subject="Nova garantia cadastrada",
            message="Uma nova garantia foi cadastrada no sistema"
        )
        
        assert result is True
        mock_vieutil_send.assert_called_once()
        
        # Verifica se os dados estão corretos
        call_args = mock_vieutil_send.call_args
        assert call_args[1]['to'] == "admin@viemar.com.br"
        assert call_args[1]['subject'] == "Nova garantia cadastrada"
        assert "Uma nova garantia foi cadastrada no sistema" in call_args[1]['text']
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_warranty_expiry_notification(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa envio de notificação de vencimento de garantia"""
        mock_get_config.return_value = mock_config
        mock_config.BASE_URL = "https://garantia.viemar.com.br"
        mock_vieutil_send.return_value = True
        
        service = EmailService()
        
        result = service.send_warranty_expiry_notification(
            user_email="joao@email.com",
            user_name="João Silva",
            produto_nome="Produto A",
            veiculo_info="Honda Civic 2020",
            days_until_expiry=30
        )
        
        assert result is True
        mock_vieutil_send.assert_called_once()
        
        # Verifica se os dados estão no corpo do email
        call_args = mock_vieutil_send.call_args
        body = call_args[1]['text']
        assert "João Silva" in body
        assert "Produto A" in body
        assert "30 dias" in body
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_confirmation_email(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa envio de email de confirmação"""
        mock_get_config.return_value = mock_config
        mock_config.BASE_URL = "https://garantia.viemar.com.br"
        mock_vieutil_send.return_value = True
        
        service = EmailService()
        
        result = service.send_confirmation_email(
            user_email="joao@email.com",
            user_name="João Silva",
            confirmation_token="abc123"
        )
        
        assert result is True
        mock_vieutil_send.assert_called_once()
        
        # Verifica se os dados estão no corpo do email
        call_args = mock_vieutil_send.call_args
        body = call_args[1]['text']
        assert "João Silva" in body
        assert "abc123" in body
        assert "Confirme" in call_args[1]['subject']
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', False)
    def test_send_email_without_vieutil_available(self, mock_get_config, mock_config):
        """Testa envio de email sem vieutil disponível"""
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        result = service.send_email(
            to_email="joao@email.com",
            subject="Teste",
            body="Corpo do email"
        )
        
        assert result is False
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_init_properties(self, mock_get_config, mock_config):
        """Testa propriedades da inicialização"""
        mock_get_config.return_value = mock_config
        mock_config.EMAIL_FROM = "test@viemar.com.br"
        
        service = EmailService()
        
        assert service.email_from == "test@viemar.com.br"
        assert service.vieutil_available is True
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_email_success_multiple_calls(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa múltiplas chamadas de envio de email"""
        mock_get_config.return_value = mock_config
        mock_vieutil_send.return_value = True
        
        service = EmailService()
        
        # Testa múltiplos envios individuais
        result1 = service.send_email(
            to_email="user1@email.com",
            subject="Teste múltiplos",
            body="Corpo do email"
        )
        result2 = service.send_email(
            to_email="user2@email.com",
            subject="Teste múltiplos",
            body="Corpo do email"
        )
        
        assert result1 is True
        assert result2 is True
        assert mock_vieutil_send.call_count == 2
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_with_invalid_recipient(self, mock_vieutil_send, mock_get_config, mock_config):
        """Testa envio com destinatário inválido"""
        mock_get_config.return_value = mock_config
        mock_vieutil_send.side_effect = Exception("Invalid recipient")
        
        service = EmailService()
        
        result = service.send_email(
            to_email="invalid-email",
            subject="Teste",
            body="Corpo do email"
        )
        
        assert result is False


class TestGetConfig:
    """Testes para a função get_config"""
    
    @patch('app.email_service.Config')
    def test_get_config_creates_instance(self, mock_config_class):
        """Testa criação de instância da configuração"""
        # Limpa a instância global
        import app.email_service
        app.email_service.config = None
        
        mock_instance = Mock()
        mock_config_class.return_value = mock_instance
        
        result = get_config()
        
        assert result == mock_instance
        mock_config_class.assert_called_once()
    
    @patch('app.email_service.Config')
    def test_get_config_reuses_instance(self, mock_config_class):
        """Testa reutilização da instância da configuração"""
        # Define uma instância global
        import app.email_service
        mock_instance = Mock()
        app.email_service.config = mock_instance
        
        result = get_config()
        
        assert result == mock_instance
        mock_config_class.assert_not_called()