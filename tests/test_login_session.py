#!/usr/bin/env python3
"""
Teste simples de login e manutenção de sessão
"""

import requests
import logging
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Teste de login e sessão"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Acessar página de login primeiro
        logger.info("=== ACESSANDO PÁGINA DE LOGIN ===")
        login_page = session.get(f"{base_url}/login")
        logger.info(f"Status da página de login: {login_page.status_code}")
        
        # 2. Fazer login
        logger.info("=== FAZENDO LOGIN ===")
        login_data = {
            'email': 'sergio@reis.com',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        logger.info(f"Status do login: {login_response.status_code}")
        logger.info(f"Headers: {dict(login_response.headers)}")
        
        # Verificar cookies
        logger.info(f"Cookies após login: {dict(session.cookies)}")
        
        if login_response.status_code == 302:
            redirect_url = login_response.headers.get('Location', '')
            logger.info(f"Redirecionamento para: {redirect_url}")
            
            # Seguir redirecionamento
            if redirect_url:
                final_url = f"{base_url}{redirect_url}" if redirect_url.startswith('/') else redirect_url
                dashboard_response = session.get(final_url)
                logger.info(f"Status do dashboard: {dashboard_response.status_code}")
                
                if dashboard_response.status_code == 200:
                    logger.info("✅ Login realizado com sucesso!")
                else:
                    logger.error(f"❌ Erro ao acessar dashboard: {dashboard_response.status_code}")
                    return
        else:
            logger.error(f"❌ Login falhou com status: {login_response.status_code}")
            return
        
        # 3. Testar acesso à página de veículos
        logger.info("=== TESTANDO ACESSO A VEÍCULOS ===")
        veiculos_response = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da página de veículos: {veiculos_response.status_code}")
        
        if veiculos_response.status_code == 200:
            logger.info("✅ Acesso à página de veículos OK")
            
            # Contar veículos atuais
            soup = BeautifulSoup(veiculos_response.text, 'html.parser')
            tabela = soup.find('table')
            veiculos_count = 0
            if tabela:
                linhas = tabela.find_all('tr')[1:]  # Pular cabeçalho
                veiculos_count = len(linhas)
            logger.info(f"Veículos encontrados: {veiculos_count}")
            
        elif veiculos_response.status_code == 302:
            logger.error("❌ Redirecionado novamente - sessão perdida")
            redirect = veiculos_response.headers.get('Location', '')
            logger.error(f"Redirecionado para: {redirect}")
            return
        else:
            logger.error(f"❌ Erro ao acessar veículos: {veiculos_response.status_code}")
            return
        
        # 4. Testar acesso ao formulário de novo veículo
        logger.info("=== TESTANDO FORMULÁRIO DE NOVO VEÍCULO ===")
        novo_response = session.get(f"{base_url}/cliente/veiculos/novo")
        logger.info(f"Status do formulário: {novo_response.status_code}")
        
        if novo_response.status_code == 200:
            logger.info("✅ Acesso ao formulário OK")
        elif novo_response.status_code == 302:
            logger.error("❌ Redirecionado - sessão perdida no formulário")
            redirect = novo_response.headers.get('Location', '')
            logger.error(f"Redirecionado para: {redirect}")
            return
        else:
            logger.error(f"❌ Erro ao acessar formulário: {novo_response.status_code}")
            return
        
        # 5. Testar cadastro de veículo
        logger.info("=== TESTANDO CADASTRO DE VEÍCULO ===")
        veiculo_data = {
            'marca': 'Honda',
            'modelo': 'Civic',
            'ano_modelo': '2023',
            'placa': 'TST9999',
            'cor': 'Prata',
            'chassi': '9BWHE21JX24060999'
        }
        
        cadastro_response = session.post(
            f"{base_url}/cliente/veiculos", 
            data=veiculo_data,
            allow_redirects=False
        )
        
        logger.info(f"Status do cadastro: {cadastro_response.status_code}")
        logger.info(f"Headers: {dict(cadastro_response.headers)}")
        
        if cadastro_response.status_code == 302:
            redirect_url = cadastro_response.headers.get('Location', '')
            logger.info(f"✅ Cadastro redirecionou para: {redirect_url}")
            
            # Verificar se foi para a lista de veículos
            if '/cliente/veiculos' in redirect_url:
                logger.info("✅ Redirecionamento correto para lista de veículos")
                
                # Acessar a lista final
                lista_final = session.get(f"{base_url}/cliente/veiculos")
                if lista_final.status_code == 200:
                    # Verificar se o veículo aparece
                    if 'TST9999' in lista_final.text:
                        logger.info("✅ Veículo encontrado na lista!")
                    else:
                        logger.error("❌ Veículo NÃO encontrado na lista")
                        
                        # Debug: mostrar placas encontradas
                        import re
                        placas = re.findall(r'[A-Z]{3}[0-9A-Z]{4}', lista_final.text)
                        logger.info(f"Placas encontradas: {set(placas)}")
                else:
                    logger.error(f"❌ Erro ao acessar lista final: {lista_final.status_code}")
            else:
                logger.error(f"❌ Redirecionamento incorreto: {redirect_url}")
        else:
            logger.error(f"❌ Cadastro falhou com status: {cadastro_response.status_code}")
            
            # Analisar resposta de erro
            if cadastro_response.status_code == 200:
                soup = BeautifulSoup(cadastro_response.text, 'html.parser')
                alertas = soup.find_all('div', class_=lambda x: x and 'alert' in x)
                if alertas:
                    logger.error("Erros encontrados:")
                    for alerta in alertas:
                        logger.error(f"  - {alerta.get_text().strip()}")
        
    except requests.exceptions.ConnectionError:
        logger.error("Não foi possível conectar ao servidor")
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()