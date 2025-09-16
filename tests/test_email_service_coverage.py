"""Testes abrangentes para o serviço de email."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# Adicionar o diretório raiz ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEmailServiceImports:
    """Testes de importação do módulo email_service."""
    
    def test_import_email_service_module(self):
        """Testa se o módulo email_service pode ser importado."""
        from app import email_service
        assert email_service is not None
    
    def test_import_email_service_class(self):
        """Testa importação da classe EmailService."""
        from app.email_service import EmailService
        assert EmailService is not None
    
    def test_import_convenience_functions(self):
        """Testa importação das funções de conveniência."""
        from app.email_service import (
            send_welcome_email,
            send_confirmation_email,
            send_warranty_activation_email,
            send_warranty_expiry_notification,
            send_admin_notification,
            send_email_with_vieutil
        )
        
        assert send_welcome_email is not None
        assert send_confirmation_email is not None
        assert send_warranty_activation_email is not None
        assert send_warranty_expiry_notification is not None
        assert send_admin_notification is not None
        assert send_email_with_vieutil is not None
    
    def test_import_constants(self):
        """Testa importação de constantes."""
        from app.email_service import VIEUTIL_AVAILABLE
        assert isinstance(VIEUTIL_AVAILABLE, bool)

class TestEmailServiceConfiguration:
    """Testes de configuração do serviço de email."""
    
    @patch('app.email_service.Config')
    def test_get_config_function(self, mock_config_class):
        """Testa a função get_config."""
        from app.email_service import get_config
        
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance
        
        # Limpar cache global
        import app.email_service
        app.email_service.config = None
        
        config = get_config()
        
        assert config is not None
        mock_config_class.assert_called_once()
    
    @patch('app.email_service.Config')
    def test_get_config_singleton(self, mock_config_class):
        """Testa se get_config retorna a mesma instância (singleton)."""
        from app.email_service import get_config
        
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance
        
        # Limpar cache global
        import app.email_service
        app.email_service.config = None
        
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
        mock_config_class.assert_called_once()  # Deve ser chamado apenas uma vez

class TestEmailServiceClass:
    """Testes para a classe EmailService."""
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_email_service_init_with_vieutil(self, mock_get_config):
        """Testa inicialização do EmailService com vieutil disponível."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        assert service.email_from == 'test@example.com'
        assert service.vieutil_available is True
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', False)
    def test_email_service_init_without_vieutil(self, mock_get_config):
        """Testa inicialização do EmailService sem vieutil disponível."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        assert service.email_from == 'test@example.com'
        assert service.vieutil_available is False
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_email_success(self, mock_vieutil, mock_get_config):
        """Testa envio de email com sucesso."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_get_config.return_value = mock_config
        
        mock_vieutil.return_value = True
        
        service = EmailService()
        result = service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body='Test Body'
        )
        
        assert result is True
        mock_vieutil.assert_called_once_with(
            to='recipient@example.com',
            subject='Test Subject',
            text='Test Body',
            send_from='garantia70mil@viemar.com.br'
        )
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', False)
    def test_send_email_vieutil_unavailable(self, mock_get_config):
        """Testa envio de email quando vieutil não está disponível."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        result = service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body='Test Body'
        )
        
        assert result is False
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_email_exception(self, mock_vieutil, mock_get_config):
        """Testa tratamento de exceção no envio de email."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_get_config.return_value = mock_config
        
        mock_vieutil.side_effect = Exception('Test error')
        
        service = EmailService()
        result = service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body='Test Body'
        )
        
        assert result is False

class TestEmailServiceMethods:
    """Testes para métodos específicos do EmailService."""
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_send_welcome_email(self, mock_get_config):
        """Testa envio de email de boas-vindas."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_config.BASE_URL = 'https://example.com'
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        with patch.object(service, 'send_email', return_value=True) as mock_send:
            result = service.send_welcome_email('user@example.com', 'João Silva')
            
            assert result is True
            mock_send.assert_called_once()
            
            # Verificar argumentos da chamada
            args, kwargs = mock_send.call_args
            assert args[0] == 'user@example.com'
            assert 'Bem-vindo' in args[1]  # subject
            assert 'João Silva' in args[2]  # body
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_send_confirmation_email(self, mock_get_config):
        """Testa envio de email de confirmação."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_config.BASE_URL = 'https://example.com'
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        with patch.object(service, 'send_email', return_value=True) as mock_send:
            result = service.send_confirmation_email(
                'user@example.com', 'João Silva', 'token123'
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Verificar argumentos da chamada
            args, kwargs = mock_send.call_args
            assert args[0] == 'user@example.com'
            assert 'Confirme' in args[1]  # subject
            assert 'token123' in args[2]  # body
            assert 'João Silva' in args[2]  # body
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_send_warranty_activation_email(self, mock_get_config):
        """Testa envio de email de ativação de garantia."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_config.BASE_URL = 'https://example.com'
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        with patch.object(service, 'send_email', return_value=True) as mock_send:
            result = service.send_warranty_activation_email(
                'user@example.com', 'João Silva', 'Garantia Estendida',
                'Honda Civic 2020', '2025-12-31'
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Verificar argumentos da chamada
            args, kwargs = mock_send.call_args
            assert args[0] == 'user@example.com'
            assert 'Garantia Ativada' in args[1]  # subject
            assert 'João Silva' in args[2]  # body
            assert 'Garantia Estendida' in args[2]  # body
            assert 'Honda Civic 2020' in args[2]  # body
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_send_warranty_expiry_notification(self, mock_get_config):
        """Testa envio de notificação de vencimento de garantia."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_config.BASE_URL = 'https://example.com'
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        with patch.object(service, 'send_email', return_value=True) as mock_send:
            result = service.send_warranty_expiry_notification(
                'user@example.com', 'João Silva', 'Garantia Estendida',
                'Honda Civic 2020', 30
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Verificar argumentos da chamada
            args, kwargs = mock_send.call_args
            assert args[0] == 'user@example.com'
            assert '30 dias' in args[1]  # subject
            assert 'João Silva' in args[2]  # body
            assert 'Garantia Estendida' in args[2]  # body
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_send_admin_notification_with_user_info(self, mock_get_config):
        """Testa envio de notificação para admin com informações do usuário."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_config.ADMIN_EMAIL = 'admin@example.com'
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        user_info = {
            'nome': 'João Silva',
            'email': 'joao@example.com'
        }
        
        with patch.object(service, 'send_email', return_value=True) as mock_send:
            result = service.send_admin_notification(
                'Test Subject', 'Test Message', user_info
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Verificar argumentos da chamada
            args, kwargs = mock_send.call_args
            assert args[0] == 'admin@example.com'
            assert args[1] == 'Test Subject'
            assert 'Test Message' in args[2]
            assert 'João Silva' in args[2]
    
    @patch('app.email_service.get_config')
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    def test_send_admin_notification_no_admin_email(self, mock_get_config):
        """Testa envio de notificação para admin sem email configurado."""
        from app.email_service import EmailService
        
        mock_config = Mock()
        mock_config.EMAIL_FROM = 'test@example.com'
        mock_config.ADMIN_EMAIL = None
        mock_get_config.return_value = mock_config
        
        service = EmailService()
        
        result = service.send_admin_notification('Test Subject', 'Test Message')
        
        assert result is False

class TestConvenienceFunctions:
    """Testes para funções de conveniência."""
    
    @patch('app.email_service.EmailService')
    def test_send_welcome_email_function(self, mock_email_service_class):
        """Testa função de conveniência send_welcome_email."""
        from app.email_service import send_welcome_email
        
        mock_service = Mock()
        mock_service.send_welcome_email.return_value = True
        mock_email_service_class.return_value = mock_service
        
        result = send_welcome_email('user@example.com', 'João Silva')
        
        assert result is True
        mock_email_service_class.assert_called_once()
        mock_service.send_welcome_email.assert_called_once_with(
            'user@example.com', 'João Silva'
        )
    
    @patch('app.email_service.EmailService')
    def test_send_confirmation_email_function(self, mock_email_service_class):
        """Testa função de conveniência send_confirmation_email."""
        from app.email_service import send_confirmation_email
        
        mock_service = Mock()
        mock_service.send_confirmation_email.return_value = True
        mock_email_service_class.return_value = mock_service
        
        result = send_confirmation_email('user@example.com', 'João Silva', 'token123')
        
        assert result is True
        mock_service.send_confirmation_email.assert_called_once_with(
            'user@example.com', 'João Silva', 'token123'
        )

class TestVieutilFunction:
    """Testes para a função send_email_with_vieutil."""
    
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_email_with_vieutil_success(self, mock_vieutil):
        """Testa send_email_with_vieutil com sucesso."""
        from app.email_service import send_email_with_vieutil
        
        mock_vieutil.return_value = True
        
        result = send_email_with_vieutil(
            to='user@example.com',
            subject='Test Subject',
            text='Test Body'
        )
        
        assert result is True
        mock_vieutil.assert_called_once()
    
    @patch('app.email_service.VIEUTIL_AVAILABLE', False)
    def test_send_email_with_vieutil_unavailable(self):
        """Testa send_email_with_vieutil quando vieutil não está disponível."""
        from app.email_service import send_email_with_vieutil
        
        result = send_email_with_vieutil(
            to='user@example.com',
            subject='Test Subject',
            text='Test Body'
        )
        
        assert result is False
    
    @patch('app.email_service.VIEUTIL_AVAILABLE', True)
    @patch('app.email_service.vieutil_send_email')
    def test_send_email_with_vieutil_exception(self, mock_vieutil):
        """Testa send_email_with_vieutil com exceção."""
        from app.email_service import send_email_with_vieutil
        
        mock_vieutil.side_effect = Exception('Test error')
        
        result = send_email_with_vieutil(
            to='user@example.com',
            subject='Test Subject',
            text='Test Body'
        )
        
        assert result is False

class TestEmailServiceUtilities:
    """Testes para utilitários e funcionalidades auxiliares."""
    
    def test_datetime_import_and_usage(self):
        """Testa importação e uso do datetime."""
        from datetime import datetime
        
        now = datetime.now()
        formatted = now.strftime('%d/%m/%Y %H:%M:%S')
        
        assert isinstance(now, datetime)
        assert '/' in formatted
        assert ':' in formatted
    
    def test_typing_imports(self):
        """Testa importações de typing."""
        from typing import Optional, List, Dict
        
        # Testar uso básico dos tipos
        optional_str: Optional[str] = None
        list_str: List[str] = ['a', 'b', 'c']
        dict_str: Dict[str, str] = {'key': 'value'}
        
        assert optional_str is None
        assert len(list_str) == 3
        assert dict_str['key'] == 'value'
    
    def test_pathlib_import(self):
        """Testa importação do pathlib."""
        from pathlib import Path
        
        current_file = Path(__file__)
        assert isinstance(current_file, Path)
        assert current_file.exists()
    
    def test_email_template_formatting(self):
        """Testa formatação de templates de email."""
        template = """Olá {nome},
        
Sua garantia {produto} foi ativada!
        
Veículo: {veiculo}
Vencimento: {vencimento}
        
Atenciosamente,
Equipe Viemar"""
        
        data = {
            'nome': 'João Silva',
            'produto': 'Garantia Estendida',
            'veiculo': 'Honda Civic 2020',
            'vencimento': '2025-12-31'
        }
        
        formatted = template.format(**data)
        
        assert 'João Silva' in formatted
        assert 'Garantia Estendida' in formatted
        assert 'Honda Civic 2020' in formatted
        assert '2025-12-31' in formatted
        assert 'Equipe Viemar' in formatted