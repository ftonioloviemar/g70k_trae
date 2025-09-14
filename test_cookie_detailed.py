#!/usr/bin/env python3
"""
Teste detalhado de cookies - verificar Set-Cookie header
"""

import requests
import logging
from urllib.parse import urlparse

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Debug detalhado de cookies"""
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Fazer login SEM seguir redirecionamentos
        logger.info("=== FAZENDO LOGIN (SEM REDIRECIONAMENTO) ===")
        login_data = {
            'email': 'sergio@reis.com',
            'senha': '123456'
        }
        
        # Usar requests simples (não session) para ver exatamente o que acontece
        login_response = requests.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        logger.info(f"Status do login: {login_response.status_code}")
        logger.info(f"Headers completos: {dict(login_response.headers)}")
        
        # Verificar especificamente o Set-Cookie
        set_cookie_headers = login_response.headers.get_list('Set-Cookie') if hasattr(login_response.headers, 'get_list') else []
        if not set_cookie_headers:
            set_cookie_header = login_response.headers.get('Set-Cookie')
            if set_cookie_header:
                set_cookie_headers = [set_cookie_header]
        
        logger.info(f"Set-Cookie headers: {set_cookie_headers}")
        
        # Verificar se há cookies na resposta
        if login_response.cookies:
            logger.info("Cookies na resposta:")
            for cookie in login_response.cookies:
                logger.info(f"  {cookie.name}={cookie.value}")
                logger.info(f"    domain={cookie.domain}, path={cookie.path}")
                logger.info(f"    secure={cookie.secure}, httponly={cookie.has_nonstandard_attr('HttpOnly')}")
        else:
            logger.error("❌ NENHUM COOKIE NA RESPOSTA!")
        
        # 2. Tentar com sessão manual
        logger.info("=== TESTANDO COM SESSÃO MANUAL ===")
        
        session = requests.Session()
        
        # Fazer login com sessão
        login_response2 = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        logger.info(f"Status do login com sessão: {login_response2.status_code}")
        
        # Verificar cookies na sessão
        logger.info(f"Cookies na sessão: {dict(session.cookies)}")
        
        if session.cookies:
            logger.info("Detalhes dos cookies na sessão:")
            for cookie in session.cookies:
                logger.info(f"  {cookie.name}={cookie.value}")
                logger.info(f"    domain={cookie.domain}, path={cookie.path}")
        else:
            logger.error("❌ NENHUM COOKIE NA SESSÃO!")
        
        # 3. Verificar se o problema é com o domínio
        logger.info("=== VERIFICANDO DOMÍNIO ===")
        parsed_url = urlparse(base_url)
        logger.info(f"Host da URL: {parsed_url.hostname}")
        logger.info(f"Porta da URL: {parsed_url.port}")
        
        # 4. Testar com diferentes configurações de cookie
        logger.info("=== TESTANDO CONFIGURAÇÕES DE COOKIE ===")
        
        # Simular o que deveria acontecer
        test_response = requests.Response()
        test_response.status_code = 302
        test_response.headers['Location'] = '/cliente'
        
        # Verificar se conseguimos definir cookie manualmente
        session2 = requests.Session()
        session2.cookies.set('viemar_session', 'test_value', domain='127.0.0.1', path='/')
        
        logger.info(f"Cookie manual definido: {dict(session2.cookies)}")
        
        # Testar acesso com cookie manual
        test_access = session2.get(f"{base_url}/cliente/veiculos", allow_redirects=False)
        logger.info(f"Status com cookie manual: {test_access.status_code}")
        
        if test_access.status_code == 302:
            redirect = test_access.headers.get('Location', '')
            if '/login' in redirect:
                logger.error(f"❌ Cookie manual não funcionou: {redirect}")
            else:
                logger.info(f"✅ Cookie manual funcionou: {redirect}")
        elif test_access.status_code == 200:
            logger.info("✅ Cookie manual permitiu acesso")
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()