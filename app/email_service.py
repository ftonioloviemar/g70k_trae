#!/usr/bin/env python3
"""
Serviço de envio de emails para o sistema de garantia Viemar
"""

from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from app.config import Config
from app.date_utils import format_datetime_br
from app.logger import get_logger

# Importar vieutil para envio de emails em produção
try:
    from vieutil import send_email as vieutil_send_email
    VIEUTIL_AVAILABLE = True
except ImportError:
    VIEUTIL_AVAILABLE = False
    vieutil_send_email = None

logger = get_logger(__name__)

# Configuração será instanciada quando necessário
config = None

def get_config():
    """Obtém instância da configuração, criando se necessário"""
    global config
    if config is None:
        config = Config()
    return config

class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self):
        """Inicializa o serviço de email"""
        config = get_config()
        
        # vieutil.send_email não requer autenticação SMTP (usa relay autorizado)
        self.email_from = config.EMAIL_FROM
        
        # vieutil disponível (único método suportado)
        self.vieutil_available = VIEUTIL_AVAILABLE
        
        if self.vieutil_available:
            logger.info("EmailService inicializado com vieutil.send_email (relay autorizado)")
        else:
            logger.error("EmailService não pode ser inicializado - vieutil.send_email não disponível")
        

    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Envia email usando vieutil.send_email (relay autorizado - não requer autenticação SMTP)"""
        
        if not self.vieutil_available or not vieutil_send_email:
            logger.error("vieutil.send_email não está disponível")
            return False
            
        try:
            logger.info(f"Enviando email via vieutil para: {to_email}")
            
            # Usar apenas texto puro
            # vieutil.send_email não requer autenticação - usa relay autorizado
            result = vieutil_send_email(
                to=to_email,
                subject=subject,
                text=body,
                send_from="garantia70mil@viemar.com.br",
            )
            
            logger.info(f"Email enviado via vieutil com sucesso para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email via vieutil para {to_email}: {e}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Envia email de boas-vindas"""
        subject = "Bem-vindo ao Sistema de Garantia Viemar"
        
        body = f"""
Olá {user_name},

Seja bem-vindo ao Sistema de Garantia Viemar!

Seu cadastro foi realizado com sucesso. Agora você pode:
- Cadastrar seus veículos
- Ativar garantias dos produtos Viemar
- Acompanhar o status das suas garantias

Para acessar o sistema, visite: {get_config().BASE_URL}

Atenciosamente,
Equipe Viemar
"""
        
        return self.send_email(user_email, subject, body)
    
    def send_confirmation_email(self, user_email: str, user_name: str, confirmation_token: str) -> bool:
        """Envia email de confirmação de cadastro"""
        subject = "Confirme seu email - Sistema de Garantia Viemar"
        
        confirmation_url = f"{get_config().BASE_URL}/confirmar-email?token={confirmation_token}"
        
        body = f"""
Olá {user_name},

Obrigado por se cadastrar no Sistema de Garantia Viemar!

Para ativar sua conta, clique no link abaixo:
{confirmation_url}

Se você não se cadastrou em nosso sistema, ignore este email.

Este link expira em 24 horas.

Atenciosamente,
Equipe Viemar
"""
        
        return self.send_email(user_email, subject, body)
    
    def send_warranty_activation_email(
        self, 
        user_email: str, 
        user_name: str, 
        produto_nome: str,
        veiculo_info: str,
        data_vencimento: str
    ) -> bool:
        """Envia email de confirmação de ativação de garantia"""
        subject = f"Garantia Ativada - {produto_nome}"
        
        body = f"""
Olá {user_name},

Sua garantia foi ativada com sucesso!

Detalhes da Garantia:
- Produto: {produto_nome}
- Veículo: {veiculo_info}
- Data de Vencimento: {data_vencimento}

Guarde este email como comprovante da ativação da sua garantia.

Para consultar suas garantias, acesse: {get_config().BASE_URL}/garantias

Atenciosamente,
Equipe Viemar
"""
        
        return self.send_email(user_email, subject, body)
    
    def send_warranty_expiry_notification(
        self, 
        user_email: str, 
        user_name: str, 
        produto_nome: str,
        veiculo_info: str,
        days_until_expiry: int
    ) -> bool:
        """Envia notificação de vencimento próximo da garantia"""
        subject = f"Garantia vencendo em {days_until_expiry} dias - {produto_nome}"
        
        body = f"""
Olá {user_name},

Sua garantia está próxima do vencimento!

Detalhes:
- Produto: {produto_nome}
- Veículo: {veiculo_info}
- Vence em: {days_until_expiry} dias

Caso precise utilizar a garantia, entre em contato conosco o quanto antes.

Para mais informações, acesse: {get_config().BASE_URL}/garantias

Atenciosamente,
Equipe Viemar
"""
        
        return self.send_email(user_email, subject, body)
    
    def send_admin_notification(
        self, 
        subject: str, 
        message: str, 
        user_info: Optional[dict] = None
    ) -> bool:
        """Envia notificação para administradores"""
        admin_email = get_config().ADMIN_EMAIL
        if not admin_email:
            logger.warning("Email de administrador não configurado")
            return False
        
        body = f"""
Notificação do Sistema de Garantia Viemar

{message}
"""
        
        if user_info:
            body += f"""

Informações do Usuário:
- Nome: {user_info.get('nome', 'N/A')}
- Email: {user_info.get('email', 'N/A')}
- Data: {format_datetime_br(datetime.now())}
"""
        
        return self.send_email(admin_email, subject, body)

def send_email_with_vieutil(
    to: str,
    subject: str,
    text: str,
    files: List[str] = None,
    attachments: List[Dict] = None,
    port: int = None,
    server: str = None,
    username: str = None,
    password: str = None,
    use_tls: bool = None
) -> bool:
    """
    Compose and send email with provided info and attachments using vieutil.
    
    Note: vieutil.send_email does not require SMTP authentication as it uses
    a pre-authorized relay server. The server, port, username, password and
    use_tls parameters are ignored when using vieutil.
    
    Args:
        to (str): recipient email address
        subject (str): email subject
        text (str): email body text
        files (list[str]): list of file paths to be attached to email
        attachments (list[dict]): alternative attachment format (not used with vieutil)
        port (int): ignored - vieutil uses pre-configured relay
        server (str): ignored - vieutil uses pre-configured relay
        username (str): ignored - vieutil uses pre-authorized relay
        password (str): ignored - vieutil uses pre-authorized relay
        use_tls (bool): ignored - vieutil uses pre-configured security
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        send_from = "littleeagle.com.br"
        send_from_str = f"from_name <{send_from}>"
        
        # Send email using vieutil (no authentication required - uses pre-authorized relay)
        if VIEUTIL_AVAILABLE:
            return vieutil_send_email(
                send_from_str,
                to,
                subject,
                text,
                files or []
            )
        else:
            logger.error("vieutil não está disponível")
            return False
        
    except Exception as e:
        logger.error(f"Erro ao enviar email com vieutil: {e}")
        return False

# Instância global do serviço de email
def send_welcome_email(user_email: str, user_name: str) -> bool:
    """Função de conveniência para enviar email de boas-vindas"""
    email_service = EmailService()
    return email_service.send_welcome_email(user_email, user_name)

def send_confirmation_email(user_email: str, user_name: str, confirmation_token: str) -> bool:
    """Função de conveniência para enviar email de confirmação"""
    email_service = EmailService()
    return email_service.send_confirmation_email(user_email, user_name, confirmation_token)

def send_warranty_activation_email(
    user_email: str, 
    user_name: str, 
    produto_nome: str,
    veiculo_info: str,
    data_vencimento: str
) -> bool:
    """Função de conveniência para enviar email de ativação de garantia"""
    email_service = EmailService()
    return email_service.send_warranty_activation_email(
        user_email, user_name, produto_nome, veiculo_info, data_vencimento
    )

def send_warranty_expiry_notification(
    user_email: str, 
    user_name: str, 
    produto_nome: str,
    veiculo_info: str,
    days_until_expiry: int
) -> bool:
    """Função de conveniência para enviar notificação de vencimento"""
    email_service = EmailService()
    return email_service.send_warranty_expiry_notification(
        user_email, user_name, produto_nome, veiculo_info, days_until_expiry
    )

def send_admin_notification(
    subject: str, 
    message: str, 
    user_info: Optional[dict] = None
) -> bool:
    """Função de conveniência para enviar notificação para administradores"""
    email_service = EmailService()
    return email_service.send_admin_notification(subject, message, user_info)