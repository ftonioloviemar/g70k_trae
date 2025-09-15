#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de login com credenciais corretas
"""

import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_login_correto():
    """Testa login com credenciais corretas sergio@reis.com / 123456"""
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    try:
        logger.info("🔐 TESTANDO LOGIN COM CREDENCIAIS CORRETAS\n")
        
        # 1. Verificar se o servidor está rodando
        logger.info("1. Verificando servidor...")
        try:
            response = session.get(base_url, timeout=5)
            logger.info(f"Status do servidor: {response.status_code}")
            if response.status_code == 200:
                logger.info("✅ Servidor está rodando")
            else:
                logger.error(f"❌ Servidor retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro ao conectar com servidor: {e}")
            return False
        
        # 2. Acessar página de login
        logger.info("\n2. Acessando página de login...")
        login_page = session.get(f"{base_url}/login")
        logger.info(f"Status da página de login: {login_page.status_code}")
        
        if login_page.status_code != 200:
            logger.error(f"❌ Erro ao acessar página de login: {login_page.status_code}")
            return False
        
        # 3. Fazer login com credenciais corretas
        logger.info("\n3. Fazendo login com sergio@reis.com / 123456...")
        
        login_data = {
            'email': 'sergio@reis.com',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        logger.info(f"Status do login: {login_response.status_code}")
        logger.info(f"Headers de resposta: {dict(login_response.headers)}")
        
        # Verificar se foi redirecionado (sucesso no login)
        if login_response.status_code in [302, 303]:
            redirect_location = login_response.headers.get('location', '')
            logger.info(f"✅ Login bem-sucedido! Redirecionado para: {redirect_location}")
            
            # Verificar se não foi redirecionado para página de erro
            if 'erro=credenciais_invalidas' in redirect_location:
                logger.error("❌ Login falhou - credenciais inválidas")
                return False
            elif '/cliente' in redirect_location or '/admin' in redirect_location:
                logger.info("✅ Login confirmado - redirecionado para área logada")
            else:
                logger.warning(f"⚠️ Redirecionamento inesperado: {redirect_location}")
                
        else:
            logger.error(f"❌ Erro no login: {login_response.status_code}")
            if login_response.text:
                logger.error(f"Conteúdo da resposta: {login_response.text[:500]}")
            return False
        
        # 4. Verificar se consegue acessar área logada
        logger.info("\n4. Testando acesso à área do cliente...")
        
        # Seguir o redirecionamento
        if login_response.status_code in [302, 303]:
            redirect_url = login_response.headers.get('location', '')
            if redirect_url.startswith('/'):
                redirect_url = base_url + redirect_url
            
            cliente_response = session.get(redirect_url)
            logger.info(f"Status da área do cliente: {cliente_response.status_code}")
            
            if cliente_response.status_code == 200:
                logger.info("✅ Acesso à área do cliente bem-sucedido")
                
                # Verificar se não foi redirecionado de volta para login
                if '/login' in cliente_response.url:
                    logger.error("❌ Foi redirecionado de volta para login - sessão não criada")
                    return False
                else:
                    logger.info("✅ Sessão criada com sucesso")
                    return True
            else:
                logger.error(f"❌ Erro ao acessar área do cliente: {cliente_response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro geral no teste: {e}")
        return False

if __name__ == "__main__":
    logger.info(f"Iniciando teste de login correto - {datetime.now()}")
    sucesso = test_login_correto()
    
    if sucesso:
        logger.info("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("✅ Login com sergio@reis.com / 123456 funcionou corretamente")
    else:
        logger.error("\n❌ TESTE FALHOU!")
        logger.error("❌ Problema no login com sergio@reis.com / 123456")
    
    logger.info(f"Teste finalizado - {datetime.now()}")