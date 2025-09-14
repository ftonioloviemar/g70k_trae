#!/usr/bin/env python3
"""
Serviço de envio de emails para o sistema de garantia Viemar
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from app.config import Config
from app.logger import get_logger

logger = get_logger(__name__)

class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_user = Config.EMAIL_USER
        self.email_password = Config.EMAIL_PASSWORD
        self.use_tls = Config.EMAIL_USE_TLS
        
    def _create_connection(self):
        """Cria conexão SMTP"""
        try:
            if self.use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            server.login(self.email_user, self.email_password)
            return server
        except Exception as e:
            logger.error(f"Erro ao conectar com servidor SMTP: {e}")
            raise
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Envia email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Adicionar corpo do email
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            if html_body:
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Adicionar anexos se houver
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {Path(file_path).name}'
                        )
                        msg.attach(part)
            
            # Enviar email
            with self._create_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {e}")
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

Para acessar o sistema, visite: {Config.BASE_URL}

Atenciosamente,
Equipe Viemar
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bem-vindo à Viemar</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c5aa0;">Bem-vindo ao Sistema de Garantia Viemar!</h2>
        
        <p>Olá <strong>{user_name}</strong>,</p>
        
        <p>Seu cadastro foi realizado com sucesso. Agora você pode:</p>
        
        <ul>
            <li>Cadastrar seus veículos</li>
            <li>Ativar garantias dos produtos Viemar</li>
            <li>Acompanhar o status das suas garantias</li>
        </ul>
        
        <p>
            <a href="{Config.BASE_URL}" 
               style="background-color: #2c5aa0; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Acessar Sistema
            </a>
        </p>
        
        <p>Atenciosamente,<br>
        <strong>Equipe Viemar</strong></p>
    </div>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body, html_body)
    
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

Para consultar suas garantias, acesse: {Config.BASE_URL}/garantias

Atenciosamente,
Equipe Viemar
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Garantia Ativada - Viemar</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #28a745;">Garantia Ativada com Sucesso!</h2>
        
        <p>Olá <strong>{user_name}</strong>,</p>
        
        <p>Sua garantia foi ativada com sucesso!</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #2c5aa0;">Detalhes da Garantia</h3>
            <p><strong>Produto:</strong> {produto_nome}</p>
            <p><strong>Veículo:</strong> {veiculo_info}</p>
            <p><strong>Data de Vencimento:</strong> {data_vencimento}</p>
        </div>
        
        <p style="background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
            <strong>Importante:</strong> Guarde este email como comprovante da ativação da sua garantia.
        </p>
        
        <p>
            <a href="{Config.BASE_URL}/garantias" 
               style="background-color: #28a745; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Ver Minhas Garantias
            </a>
        </p>
        
        <p>Atenciosamente,<br>
        <strong>Equipe Viemar</strong></p>
    </div>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body, html_body)
    
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

Para mais informações, acesse: {Config.BASE_URL}/garantias

Atenciosamente,
Equipe Viemar
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Garantia Vencendo - Viemar</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #dc3545;">Garantia Vencendo em {days_until_expiry} Dias</h2>
        
        <p>Olá <strong>{user_name}</strong>,</p>
        
        <p>Sua garantia está próxima do vencimento!</p>
        
        <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
            <h3 style="margin-top: 0; color: #721c24;">Detalhes da Garantia</h3>
            <p><strong>Produto:</strong> {produto_nome}</p>
            <p><strong>Veículo:</strong> {veiculo_info}</p>
            <p><strong>Vence em:</strong> {days_until_expiry} dias</p>
        </div>
        
        <p>Caso precise utilizar a garantia, entre em contato conosco o quanto antes.</p>
        
        <p>
            <a href="{Config.BASE_URL}/garantias" 
               style="background-color: #dc3545; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Ver Minhas Garantias
            </a>
        </p>
        
        <p>Atenciosamente,<br>
        <strong>Equipe Viemar</strong></p>
    </div>
</body>
</html>
"""
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_admin_notification(
        self, 
        subject: str, 
        message: str, 
        user_info: Optional[dict] = None
    ) -> bool:
        """Envia notificação para administradores"""
        admin_email = Config.ADMIN_EMAIL
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
- Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        return self.send_email(admin_email, subject, body)

# Instância global do serviço de email
email_service = EmailService()

def send_welcome_email(user_email: str, user_name: str) -> bool:
    """Função helper para enviar email de boas-vindas"""
    return email_service.send_welcome_email(user_email, user_name)

def send_warranty_activation_email(
    user_email: str, 
    user_name: str, 
    produto_nome: str,
    veiculo_info: str,
    data_vencimento: str
) -> bool:
    """Função helper para enviar email de ativação de garantia"""
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
    """Função helper para enviar notificação de vencimento"""
    return email_service.send_warranty_expiry_notification(
        user_email, user_name, produto_nome, veiculo_info, days_until_expiry
    )

def send_admin_notification(
    subject: str, 
    message: str, 
    user_info: Optional[dict] = None
) -> bool:
    """Função helper para enviar notificação para admin"""
    return email_service.send_admin_notification(subject, message, user_info)