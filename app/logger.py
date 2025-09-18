#!/usr/bin/env python3
"""
Sistema de logging com rotação diária para a aplicação Viemar
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Configura o sistema de logging com rotação diária"""
    
    # Criar diretório de logs se não existir
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato do log
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar handler para arquivo com rotação diária
    log_file = log_dir / 'viemar_garantia.log'
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=30,  # Manter 30 dias de logs
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    
    # Configurar handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.DEBUG)
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log inicial
    logger = logging.getLogger(__name__)
    logger.info("Sistema de logging configurado com sucesso")
    logger.info(f"Logs salvos em: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado para o módulo especificado"""
    return logging.getLogger(name)

# Instância padrão do logger para uso direto
logger = get_logger(__name__)