#!/usr/bin/env python3
"""
Tarefas assíncronas para a aplicação Viemar Garantia 70k
"""

import asyncio
import threading
from typing import Callable, Any
from app.logger import get_logger

logger = get_logger(__name__)

def run_async_task(func: Callable, *args, **kwargs) -> None:
    """
    Executa uma função de forma assíncrona em uma thread separada
    
    Args:
        func: Função a ser executada
        *args: Argumentos posicionais para a função
        **kwargs: Argumentos nomeados para a função
    """
    def task_wrapper():
        try:
            result = func(*args, **kwargs)
            logger.info(f"Tarefa assíncrona concluída: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Erro na tarefa assíncrona {func.__name__}: {e}")
            return False
    
    # Executar em thread separada para não bloquear a interface
    thread = threading.Thread(target=task_wrapper, daemon=True)
    thread.start()
    logger.info(f"Tarefa assíncrona iniciada: {func.__name__}")

def send_email_async(email_func: Callable, *args, **kwargs) -> None:
    """
    Envia email de forma assíncrona
    
    Args:
        email_func: Função de envio de email
        *args: Argumentos posicionais para a função de email
        **kwargs: Argumentos nomeados para a função de email
    """
    run_async_task(email_func, *args, **kwargs)

def send_confirmation_email_async(
    user_email: str, 
    user_name: str, 
    confirmation_token: str
) -> None:
    """
    Envia email de confirmação de forma assíncrona
    
    Args:
        user_email: Email do usuário
        user_name: Nome do usuário
        confirmation_token: Token de confirmação
    """
    from app.email_service import send_confirmation_email
    
    def send_email():
        try:
            result = send_confirmation_email(
                user_email=user_email,
                user_name=user_name,
                confirmation_token=confirmation_token
            )
            if result:
                logger.info(f"Email de confirmação enviado com sucesso para: {user_email}")
            else:
                logger.warning(f"Falha ao enviar email de confirmação para: {user_email}")
            return result
        except Exception as e:
            logger.error(f"Erro ao enviar email de confirmação para {user_email}: {e}")
            return False
    
    run_async_task(send_email)

def send_warranty_activation_email_async(
    user_email: str,
    user_name: str,
    produto_nome: str,
    veiculo_info: str,
    data_vencimento: str
) -> None:
    """
    Envia email de ativação de garantia de forma assíncrona
    
    Args:
        user_email: Email do usuário
        user_name: Nome do usuário
        produto_nome: Nome do produto
        veiculo_info: Informações do veículo
        data_vencimento: Data de vencimento da garantia
    """
    from app.email_service import send_warranty_activation_email
    
    def send_email():
        try:
            result = send_warranty_activation_email(
                user_email=user_email,
                user_name=user_name,
                produto_nome=produto_nome,
                veiculo_info=veiculo_info,
                data_vencimento=data_vencimento
            )
            if result:
                logger.info(f"Email de garantia ativada enviado para {user_email}")
            else:
                logger.error(f"Falha ao enviar email de garantia ativada para {user_email}")
            return result
        except Exception as e:
            logger.error(f"Erro ao enviar email de garantia ativada: {e}")
            return False
    
    run_async_task(send_email)