#!/usr/bin/env python3
"""
Script para debug detalhado do cadastro de veículos
"""

import requests
import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Debug detalhado do cadastro de veículos"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Fazer login
        logger.info("=== FAZENDO LOGIN ===")
        login_data = {
            'email': 'sergio@reis.com',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        logger.info(f"Status do login: {login_response.status_code}")
        logger.debug(f"Headers de resposta: {dict(login_response.headers)}")
        
        if login_response.status_code != 200:
            logger.error(f"Erro no login: {login_response.text[:1000]}")
            return
        
        # 2. Verificar estado atual dos veículos
        logger.info("=== VERIFICANDO VEÍCULOS ATUAIS ===")
        veiculos_response = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da página de veículos: {veiculos_response.status_code}")
        
        # Contar veículos atuais
        soup = BeautifulSoup(veiculos_response.text, 'html.parser')
        tabela = soup.find('table')
        veiculos_atuais = 0
        if tabela:
            linhas = tabela.find_all('tr')[1:]  # Pular cabeçalho
            veiculos_atuais = len(linhas)
        
        logger.info(f"Veículos atuais na lista: {veiculos_atuais}")
        
        # 3. Acessar formulário de novo veículo
        logger.info("=== ACESSANDO FORMULÁRIO ===")
        novo_response = session.get(f"{base_url}/cliente/veiculos/novo")
        logger.info(f"Status do formulário: {novo_response.status_code}")
        
        if novo_response.status_code != 200:
            logger.error(f"Erro ao acessar formulário: {novo_response.text[:1000]}")
            return
        
        # 4. Preparar dados do veículo
        timestamp = datetime.now().strftime('%H%M%S')
        veiculo_data = {
            'marca': 'Volkswagen',
            'modelo': 'Golf',
            'ano_modelo': '2022',
            'placa': f'DBG{timestamp[1:4]}',
            'cor': 'Azul',
            'chassi': '9BWHE21JX24060832'
        }
        
        logger.info(f"=== CADASTRANDO VEÍCULO ===")
        logger.info(f"Dados do veículo: {veiculo_data}")
        
        # 5. Enviar dados do cadastro
        cadastro_response = session.post(
            f"{base_url}/cliente/veiculos", 
            data=veiculo_data,
            allow_redirects=False  # Não seguir redirecionamentos automaticamente
        )
        
        logger.info(f"Status do cadastro: {cadastro_response.status_code}")
        logger.info(f"Headers de resposta: {dict(cadastro_response.headers)}")
        
        # Verificar se houve redirecionamento
        if cadastro_response.status_code in [302, 303]:
            redirect_url = cadastro_response.headers.get('Location', '')
            logger.info(f"✅ Redirecionamento para: {redirect_url}")
            
            # Seguir o redirecionamento
            final_response = session.get(f"{base_url}{redirect_url}" if redirect_url.startswith('/') else redirect_url)
            logger.info(f"Status da página final: {final_response.status_code}")
            
        elif cadastro_response.status_code == 200:
            logger.warning("⚠️ Retornou 200 ao invés de redirecionamento - possível erro")
            
            # Analisar a resposta para encontrar erros
            soup = BeautifulSoup(cadastro_response.text, 'html.parser')
            
            # Procurar por alertas de erro
            alertas = soup.find_all('div', class_=lambda x: x and 'alert' in x)
            if alertas:
                logger.error("Alertas encontrados na página:")
                for alerta in alertas:
                    logger.error(f"  - {alerta.get_text().strip()}")
            
            # Procurar por mensagens de erro em campos
            campos_erro = soup.find_all('div', class_=lambda x: x and 'invalid-feedback' in x)
            if campos_erro:
                logger.error("Erros de validação encontrados:")
                for erro in campos_erro:
                    logger.error(f"  - {erro.get_text().strip()}")
            
            # Verificar se ainda está no formulário
            form = soup.find('form')
            if form:
                logger.error("Ainda está na página do formulário - cadastro falhou")
                
                # Verificar valores dos campos
                inputs = form.find_all(['input', 'select', 'textarea'])
                logger.debug("Valores dos campos no formulário:")
                for inp in inputs:
                    name = inp.get('name', 'sem_nome')
                    value = inp.get('value', '')
                    if name and name != 'csrf_token':
                        logger.debug(f"  {name}: {value}")
        else:
            logger.error(f"Status inesperado: {cadastro_response.status_code}")
            logger.error(f"Resposta: {cadastro_response.text[:1000]}")
        
        # 6. Verificar se o veículo aparece na lista
        logger.info("=== VERIFICANDO LISTA APÓS CADASTRO ===")
        lista_response = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da verificação: {lista_response.status_code}")
        
        # Contar veículos após cadastro
        soup = BeautifulSoup(lista_response.text, 'html.parser')
        tabela = soup.find('table')
        veiculos_depois = 0
        if tabela:
            linhas = tabela.find_all('tr')[1:]  # Pular cabeçalho
            veiculos_depois = len(linhas)
        
        logger.info(f"Veículos após cadastro: {veiculos_depois}")
        
        if veiculos_depois > veiculos_atuais:
            logger.info(f"✅ Número de veículos aumentou de {veiculos_atuais} para {veiculos_depois}")
        else:
            logger.error(f"❌ Número de veículos não aumentou (antes: {veiculos_atuais}, depois: {veiculos_depois})")
        
        # Procurar especificamente pela placa
        if veiculo_data['placa'] in lista_response.text:
            logger.info(f"✅ Veículo {veiculo_data['placa']} encontrado na lista!")
        else:
            logger.error(f"❌ Veículo {veiculo_data['placa']} NÃO encontrado na lista!")
            
            # Listar todas as placas encontradas
            import re
            placas = re.findall(r'[A-Z]{3}[0-9A-Z]{4}', lista_response.text)
            if placas:
                logger.info(f"Placas encontradas na página: {set(placas)}")
            else:
                logger.info("Nenhuma placa encontrada na página")
        
        # 7. Verificar mensagens de sucesso/erro
        soup = BeautifulSoup(lista_response.text, 'html.parser')
        alertas = soup.find_all('div', class_=lambda x: x and 'alert' in x)
        if alertas:
            logger.info("Mensagens na página de veículos:")
            for alerta in alertas:
                texto = alerta.get_text().strip()
                if texto:
                    logger.info(f"  - {texto}")
        
    except requests.exceptions.ConnectionError:
        logger.error("Não foi possível conectar ao servidor. Verifique se está rodando em http://127.0.0.1:8000")
    except Exception as e:
        logger.error(f"Erro durante o debug: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()