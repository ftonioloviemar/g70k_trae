#!/usr/bin/env python3
"""
Script para testar o login do usuário sergio@reis.com
"""

import requests
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sergio_login():
    """Testa o login do usuário sergio@reis.com"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # 1. Acessar página de login
        logger.info("1. Acessando página de login...")
        login_page = session.get(f"{base_url}/login")
        logger.info(f"Status da página de login: {login_page.status_code}")
        
        if login_page.status_code != 200:
            logger.error("❌ Falha ao acessar página de login")
            return False
        
        # 2. Fazer login
        logger.info("2. Fazendo login...")
        login_data = {
            "email": "sergio@reis.com",
            "senha": "123456"
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        logger.info(f"Status do login: {login_response.status_code}")
        
        # Salvar resposta para debug
        Path("tmp").mkdir(exist_ok=True)
        with open("tmp/sergio_login_response.html", "w", encoding="utf-8") as f:
            f.write(login_response.text)
        logger.info("Resposta do login salva em tmp/sergio_login_response.html")
        
        # Verificar se o login foi bem-sucedido
        if login_response.status_code == 302:  # Redirecionamento após login
            logger.info("✅ Login realizado com sucesso (redirecionamento)")
        elif login_response.status_code == 200:
            # Verificar se há mensagem de erro na página
            if "erro" in login_response.text.lower() or "incorret" in login_response.text.lower():
                logger.error("❌ Login falhou - credenciais incorretas")
                return False
            else:
                logger.info("✅ Login realizado com sucesso")
        else:
            logger.error(f"❌ Login falhou - status {login_response.status_code}")
            return False
        
        # 3. Acessar página de veículos
        logger.info("3. Acessando página de veículos...")
        veiculos_response = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da página de veículos: {veiculos_response.status_code}")
        
        # Salvar resposta para debug
        with open("tmp/sergio_veiculos_response.html", "w", encoding="utf-8") as f:
            f.write(veiculos_response.text)
        logger.info("Resposta da página de veículos salva em tmp/sergio_veiculos_response.html")
        
        if veiculos_response.status_code == 200:
            if "sergio@reis.com" in veiculos_response.text:
                logger.info("✅ Usuário logado e acessando página de veículos")
                return True
            else:
                logger.error("❌ Usuário não está logado na página de veículos")
                return False
        else:
            logger.error(f"❌ Falha ao acessar página de veículos - status {veiculos_response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste de login: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Testando login do usuário sergio@reis.com...")
    success = test_sergio_login()
    
    if success:
        print("\n🎉 TESTE PASSOU: Login funcionando corretamente!")
        print("Credenciais válidas:")
        print("  Email: sergio@reis.com")
        print("  Senha: 123456")
    else:
        print("\n❌ TESTE FALHOU: Problema no login")
        print("Verifique os arquivos em tmp/ para mais detalhes")