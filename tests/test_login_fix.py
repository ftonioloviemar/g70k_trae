#!/usr/bin/env python3
"""
Teste de login com usuário de teste
"""

import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Testar login com usuário de teste"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Fazer login com usuário de teste
        logger.info("=== FAZENDO LOGIN COM USUÁRIO DE TESTE ===")
        login_data = {
            'email': 'teste@viemar.com',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        logger.info(f"Status do login: {login_response.status_code}")
        logger.info(f"Headers: {dict(login_response.headers)}")
        
        # Verificar cookies
        logger.info(f"Cookies após login: {dict(session.cookies)}")
        
        if 'Set-Cookie' in login_response.headers:
            logger.info(f"Set-Cookie header: {login_response.headers['Set-Cookie']}")
        
        if login_response.status_code == 302:
            redirect_url = login_response.headers.get('Location', '')
            logger.info(f"Redirecionamento para: {redirect_url}")
            
            if session.cookies:
                logger.info("✅ Cookie definido com sucesso!")
                
                # 2. Testar acesso à página de veículos
                logger.info("=== TESTANDO ACESSO A VEÍCULOS ===")
                veiculos_response = session.get(f"{base_url}/cliente/veiculos", allow_redirects=False)
                logger.info(f"Status da página de veículos: {veiculos_response.status_code}")
                
                if veiculos_response.status_code == 200:
                    logger.info("✅ Acesso à página de veículos OK!")
                    
                    # 3. Testar cadastro de veículo
                    logger.info("=== TESTANDO CADASTRO DE VEÍCULO ===")
                    
                    # Gerar dados únicos para evitar conflitos
                    import random
                    import string
                    timestamp = str(int(datetime.now().timestamp()))[-4:]  # Últimos 4 dígitos do timestamp
                    placa_unica = f"TST{timestamp}"
                    chassi_unico = f"9BWHE21JX2406{timestamp.zfill(4)}"
                    
                    veiculo_data = {
                        'marca': 'Toyota',
                        'modelo': 'Corolla',
                        'ano_modelo': '2023',
                        'placa': placa_unica,  # Formato válido: ABC1234
                        'cor': 'Branco',
                        'chassi': chassi_unico
                    }
                    
                    logger.info(f"Testando com placa: {placa_unica} e chassi: {chassi_unico}")
                    
                    cadastro_response = session.post(
                        f"{base_url}/cliente/veiculos", 
                        data=veiculo_data,
                        allow_redirects=False
                    )
                    
                    logger.info(f"Status do cadastro: {cadastro_response.status_code}")
                    logger.info(f"Headers do cadastro: {dict(cadastro_response.headers)}")
                    
                    if cadastro_response.status_code == 200:
                        # Status 200 indica erro de validação - vamos ver o conteúdo
                        logger.error("❌ Status 200 indica erro de validação")
                        response_text = cadastro_response.text
                        
                        # Salvar resposta completa para análise
                        with open('tmp/cadastro_error_response.html', 'w', encoding='utf-8') as f:
                            f.write(response_text)
                        logger.info("Resposta salva em tmp/cadastro_error_response.html")
                        
                        # Procurar por mensagens de erro mais específicas
                        import re
                        
                        # Procurar por divs com classe de erro
                        error_divs = re.findall(r'<div[^>]*class="[^"]*(?:alert-danger|invalid-feedback|text-danger)[^"]*"[^>]*>([^<]+)</div>', response_text, re.IGNORECASE)
                        if error_divs:
                            logger.error("Erros encontrados:")
                            for error in error_divs:
                                logger.error(f"  - {error.strip()}")
                        
                        # Procurar por inputs com classe is-invalid
                        invalid_inputs = re.findall(r'<input[^>]*class="[^"]*is-invalid[^"]*"[^>]*name="([^"]+)"', response_text, re.IGNORECASE)
                        if invalid_inputs:
                            logger.error(f"Campos inválidos: {invalid_inputs}")
                        
                        # Verificar se há campos obrigatórios não preenchidos
                        if 'obrigatório' in response_text.lower():
                            logger.error("Há campos obrigatórios não preenchidos")
                            
                    elif cadastro_response.status_code == 302:
                        redirect = cadastro_response.headers.get('Location', '')
                        if '/login' in redirect:
                            logger.error(f"❌ Perdeu sessão no cadastro: {redirect}")
                        else:
                            logger.info(f"✅ Cadastro redirecionou corretamente: {redirect}")
                            
                            # 4. Verificar se o veículo aparece na lista
                            logger.info("=== VERIFICANDO LISTA DE VEÍCULOS ===")
                            lista_response = session.get(f"{base_url}/cliente/veiculos")
                            
                            # Verificar diferentes formatos da placa
                            placa_formatada = f"TST-{timestamp}"  # Formato com hífen
                            if placa_unica in lista_response.text or placa_formatada in lista_response.text:
                                logger.info("✅ Veículo aparece na lista!")
                            else:
                                logger.error("❌ Veículo não aparece na lista")
                                # Debug: mostrar placas encontradas
                                import re
                                placas = re.findall(r'[A-Z]{3}[0-9A-Z-]{4,5}', lista_response.text)
                                logger.info(f"Placas encontradas na página: {set(placas)}")
                                
                                # Verificar se há mensagem de sucesso
                                if 'sucesso=cadastrado' in lista_response.url or 'cadastrado' in lista_response.text.lower():
                                    logger.info("✅ Mensagem de sucesso encontrada")
                                else:
                                    logger.error("❌ Nenhuma mensagem de sucesso encontrada")
                    else:
                        logger.error(f"❌ Status inesperado no cadastro: {cadastro_response.status_code}")
                        
                elif veiculos_response.status_code == 302:
                    redirect = veiculos_response.headers.get('Location', '')
                    logger.error(f"❌ Redirecionado da página de veículos: {redirect}")
                else:
                    logger.error(f"❌ Status inesperado na página de veículos: {veiculos_response.status_code}")
            else:
                logger.error("❌ Nenhum cookie definido após login")
        else:
            logger.error(f"❌ Login falhou: {login_response.status_code}")
            
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()