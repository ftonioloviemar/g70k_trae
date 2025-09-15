#!/usr/bin/env python3
"""
Aplicação FastHTML para Sistema de Garantia Viemar
"""

import logging
import os
from pathlib import Path
from fasthtml.common import *
from monsterui.all import *
from fastlite import Database

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Arquivo .env carregado: {env_path}")
    else:
        print(f"Arquivo .env não encontrado: {env_path}")
except ImportError:
    print("python-dotenv não instalado, usando apenas variáveis de ambiente do sistema")

from app.config import Config
from app.logger import setup_logging, get_logger
from app.database import init_database
from app.auth import setup_auth, init_auth
from app.routes import setup_routes
from app.routes_veiculos import setup_veiculo_routes
from app.routes_garantias import setup_garantia_routes
from app.routes_admin import setup_admin_routes

# Configurar logging
setup_logging()
logger = get_logger(__name__)

def create_app():
    """Cria e configura a aplicação FastHTML"""
    
    # Instanciar configuração
    config = Config()
    
    # Configurar aplicação com MonsterUI
    app, rt = fast_app(
        debug=config.DEBUG,
        live=config.LIVE_RELOAD,
        hdrs=Theme.blue.headers() + [
            Link(rel="stylesheet", href="/static/style.css")
        ]
    )
    
    # Configurar banco de dados
    db = Database(config.DATABASE_PATH)
    init_database(db)
    
    # Configurar autenticação
    init_auth(db)
    setup_auth(app)
    
    # Configurar todas as rotas
    setup_routes(app, db)
    setup_veiculo_routes(app, db)
    setup_garantia_routes(app, db)
    setup_admin_routes(app, db)
    
    logger.info("Aplicação FastHTML configurada com sucesso")
    return app, config

# Criar instância da aplicação para o Uvicorn
app, _ = create_app()

def main():
    """Função principal"""
    logger.info("Iniciando aplicação Viemar Garantia")
    
    app, config = create_app()
    
    # Iniciar servidor
    serve(
        host=config.HOST,
        port=config.PORT,
        reload=config.LIVE_RELOAD
    )

if __name__ == "__main__":
    main()
