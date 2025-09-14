#!/usr/bin/env python3
"""
Script para testar o cadastro de veículos via web
"""

import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Testa o cadastro de veículos via web"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Testar se o servidor está rodando
        logger.info("Testando conexão com o servidor...")
        response = session.get(base_url)
        logger.info(f"Status da página inicial: {response.status_code}")
        
        if response.status_code != 200:
            logger.error("Servidor não está respondendo corretamente")
            return
        
        # 2. Fazer login
        logger.info("Fazendo login...")
        login_data = {
            'email': 'sergio@reis.com',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        logger.info(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302, 303]:
            logger.error(f"Erro no login: {login_response.text[:500]}")
            return
        
        # 3. Acessar página de veículos
        logger.info("Acessando página de veículos...")
        veiculos_response = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da página de veículos: {veiculos_response.status_code}")
        
        if veiculos_response.status_code != 200:
            logger.error(f"Erro ao acessar veículos: {veiculos_response.text[:500]}")
            return
        
        # Verificar se há veículos na página
        if "Nenhum veículo cadastrado" in veiculos_response.text:
            logger.info("Nenhum veículo encontrado na listagem")
        else:
            logger.info("Veículos encontrados na listagem")
            # Procurar por placas na página
            import re
            placas = re.findall(r'[A-Z]{3}[0-9][A-Z0-9][0-9]{2}', veiculos_response.text)
            if placas:
                logger.info(f"Placas encontradas: {placas}")
        
        # 4. Acessar formulário de novo veículo
        logger.info("Acessando formulário de novo veículo...")
        novo_response = session.get(f"{base_url}/cliente/veiculos/novo")
        logger.info(f"Status do formulário: {novo_response.status_code}")
        
        if novo_response.status_code != 200:
            logger.error(f"Erro ao acessar formulário: {novo_response.text[:500]}")
            return
        
        # 5. Cadastrar novo veículo
        logger.info("Cadastrando novo veículo...")
        timestamp = datetime.now().strftime('%H%M%S')
        veiculo_data = {
            'marca': 'Honda',
            'modelo': 'Civic',
            'ano_modelo': '2021',
            'placa': f'WEB{timestamp[1:4]}',
            'cor': 'Prata',
            'chassi': '9BWHE21JX24060831'
        }
        
        cadastro_response = session.post(f"{base_url}/cliente/veiculos", data=veiculo_data)
        logger.info(f"Status do cadastro: {cadastro_response.status_code}")
        
        if cadastro_response.status_code in [302, 303]:
            logger.info("Redirecionamento após cadastro (provável sucesso)")
            redirect_url = cadastro_response.headers.get('Location', '')
            logger.info(f"URL de redirecionamento: {redirect_url}")
        elif cadastro_response.status_code == 200:
            # Verificar se há erros na página
            if "erro" in cadastro_response.text.lower() or "error" in cadastro_response.text.lower():
                logger.error("Possível erro no cadastro")
                # Procurar por mensagens de erro específicas
                import re
                errors = re.findall(r'class="[^"]*alert[^"]*danger[^"]*"[^>]*>([^<]+)', cadastro_response.text)
                if errors:
                    logger.error(f"Erros encontrados: {errors}")
            else:
                logger.info("Cadastro pode ter sido bem-sucedido")
        else:
            logger.error(f"Erro no cadastro: {cadastro_response.text[:500]}")
            return
        
        # 6. Verificar se o veículo aparece na lista
        logger.info("Verificando se o veículo aparece na lista...")
        lista_response = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da verificação: {lista_response.status_code}")
        
        if veiculo_data['placa'] in lista_response.text:
            logger.info(f"✅ Veículo {veiculo_data['placa']} encontrado na lista!")
        else:
            logger.error(f"❌ Veículo {veiculo_data['placa']} NÃO encontrado na lista!")
            
            # Verificar se há outros veículos
            if "Nenhum veículo cadastrado" in lista_response.text:
                logger.error("A lista está vazia")
            else:
                logger.info("Há outros veículos na lista, mas não o recém-cadastrado")
                # Procurar por placas na página
                import re
                placas = re.findall(r'[A-Z]{3}[0-9A-Z]{3}', lista_response.text)
                if placas:
                    logger.info(f"Outras placas encontradas: {placas}")
        
        # 7. Fazer logout
        logger.info("Fazendo logout...")
        session.get(f"{base_url}/logout")
        
    except requests.exceptions.ConnectionError:
        logger.error("Não foi possível conectar ao servidor. Verifique se está rodando em http://127.0.0.1:8000")
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()