#!/usr/bin/env python3
"""
Teste específico para debug de cookies
"""

import requests
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Debug específico de cookies"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Fazer login e capturar cookies
        logger.info("=== FAZENDO LOGIN ===")
        login_data = {
            'email': 'sergio@reis.com',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        logger.info(f"Status do login: {login_response.status_code}")
        logger.info(f"Headers de resposta: {dict(login_response.headers)}")
        
        # Verificar cookies definidos pelo servidor
        if 'Set-Cookie' in login_response.headers:
            logger.info(f"Set-Cookie header: {login_response.headers['Set-Cookie']}")
        
        # Verificar cookies na sessão
        logger.info(f"Cookies na sessão após login: {dict(session.cookies)}")
        
        # Listar todos os cookies com detalhes
        for cookie in session.cookies:
            logger.info(f"Cookie: {cookie.name}={cookie.value}, domain={cookie.domain}, path={cookie.path}")
        
        if login_response.status_code == 302:
            redirect_url = login_response.headers.get('Location', '')
            logger.info(f"Redirecionamento para: {redirect_url}")
            
            # Seguir redirecionamento mantendo cookies
            if redirect_url:
                final_url = f"{base_url}{redirect_url}" if redirect_url.startswith('/') else redirect_url
                dashboard_response = session.get(final_url)
                logger.info(f"Status do dashboard: {dashboard_response.status_code}")
                logger.info(f"Cookies após dashboard: {dict(session.cookies)}")
        
        # 2. Testar acesso direto à página de veículos
        logger.info("=== TESTANDO ACESSO DIRETO A VEÍCULOS ===")
        
        # Mostrar cookies que serão enviados
        logger.info(f"Cookies que serão enviados: {dict(session.cookies)}")
        
        veiculos_response = session.get(f"{base_url}/cliente/veiculos", allow_redirects=False)
        logger.info(f"Status da página de veículos: {veiculos_response.status_code}")
        logger.info(f"Headers de resposta: {dict(veiculos_response.headers)}")
        
        if veiculos_response.status_code == 302:
            redirect = veiculos_response.headers.get('Location', '')
            logger.error(f"❌ Redirecionado para: {redirect}")
        elif veiculos_response.status_code == 200:
            logger.info("✅ Acesso à página de veículos OK")
        
        # 3. Testar POST para cadastro
        logger.info("=== TESTANDO POST PARA CADASTRO ===")
        
        # Mostrar cookies antes do POST
        logger.info(f"Cookies antes do POST: {dict(session.cookies)}")
        
        veiculo_data = {
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano_modelo': '2023',
            'placa': 'DBG1234',
            'cor': 'Branco',
            'chassi': '9BWHE21JX24060123'
        }
        
        cadastro_response = session.post(
            f"{base_url}/cliente/veiculos", 
            data=veiculo_data,
            allow_redirects=False
        )
        
        logger.info(f"Status do cadastro: {cadastro_response.status_code}")
        logger.info(f"Headers de resposta: {dict(cadastro_response.headers)}")
        
        if cadastro_response.status_code == 302:
            redirect_url = cadastro_response.headers.get('Location', '')
            if '/login' in redirect_url:
                logger.error(f"❌ Perdeu sessão no POST: {redirect_url}")
            else:
                logger.info(f"✅ POST redirecionou corretamente: {redirect_url}")
        else:
            logger.error(f"❌ POST retornou status inesperado: {cadastro_response.status_code}")
        
        # 4. Verificar se os cookies ainda existem após o POST
        logger.info(f"Cookies após POST: {dict(session.cookies)}")
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()