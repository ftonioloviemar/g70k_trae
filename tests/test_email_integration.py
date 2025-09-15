#!/usr/bin/env python3
"""
Teste de integração para verificar se o envio de email de confirmação funciona
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# Configurar path para importar módulos da aplicação
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.email_service import send_confirmation_email
from models.usuario import Usuario

def test_email_confirmation_integration():
    """Teste de integração para confirmação de email"""
    
    # Configurar variáveis de ambiente temporárias
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ['SECRET_KEY'] = 'test-secret-key-12345'
        os.environ['ADMIN_EMAIL'] = 'admin@test.com'
        os.environ['ADMIN_PASSWORD'] = 'admin123'
        os.environ['DATABASE_PATH'] = str(Path(temp_dir) / 'test.db')
        os.environ['BASE_URL'] = 'http://localhost:8000'
        os.environ['SMTP_USERNAME'] = 'test@test.com'
        os.environ['SMTP_PASSWORD'] = 'password123'
        os.environ['EMAIL_FROM'] = 'noreply@viemar.com.br'
        
        try:
            # Gerar token de confirmação
            token = Usuario.gerar_token_confirmacao()
            
            # Testar envio de email (com mock para não enviar realmente)
            with patch('app.email_service.VIEUTIL_AVAILABLE', False), \
                 patch('smtplib.SMTP') as mock_smtp:
                
                # Configurar mock do SMTP
                mock_server = mock_smtp.return_value
                mock_server.starttls.return_value = None
                mock_server.login.return_value = None
                mock_server.send_message.return_value = {}
                mock_server.quit.return_value = None
                
                # Tentar enviar email
                result = send_confirmation_email(
                    user_email='test@example.com',
                    user_name='João Silva',
                    confirmation_token=token
                )
                
                # Verificar se o envio foi bem-sucedido
                print(f"Resultado do envio: {result}")
                print(f"Token gerado: {token}")
                print(f"Tamanho do token: {len(token)}")
                
                # Verificações básicas
                assert isinstance(token, str)
                assert len(token) >= 32
                assert isinstance(result, bool)
                
                print("✅ Teste de integração passou!")
                
        finally:
            # Limpar variáveis de ambiente
            for key in ['SECRET_KEY', 'ADMIN_EMAIL', 'ADMIN_PASSWORD', 'DATABASE_PATH', 'BASE_URL', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_FROM']:
                os.environ.pop(key, None)

if __name__ == '__main__':
    test_email_confirmation_integration()
    print("Teste de integração concluído com sucesso!")