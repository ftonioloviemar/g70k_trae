#!/usr/bin/env python3
"""
Teste detalhado para verificar o cadastro de veículos via interface web
"""

import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_veiculo_cadastro_completo():
    """Teste completo do cadastro de veículo via interface web"""
    
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    # Gerar dados únicos
    timestamp = int(datetime.now().timestamp())
    placa_unica = f"TST{timestamp % 10000:04d}"  # TST + 4 dígitos
    chassi_unico = f"9BWHE21JX24{timestamp % 1000000:06d}"
    
    logger.info(f"=== TESTE COMPLETO DE CADASTRO DE VEÍCULO ===")
    logger.info(f"Placa: {placa_unica}, Chassi: {chassi_unico}")
    
    try:
        # 1. Fazer login
        logger.info("1. Fazendo login...")
        login_data = {
            "email": "teste@viemar.com",
            "senha": "123456"
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        logger.info(f"Status do login: {login_response.status_code}")
        logger.info(f"Headers do login: {dict(login_response.headers)}")
        
        if login_response.status_code == 302:
            logger.info("✅ Login realizado com sucesso (redirecionamento)")
        elif login_response.status_code == 200:
            # Verificar se já está logado (dashboard aparece)
            if "Olá," in login_response.text and "teste@viemar.com" in login_response.text:
                logger.info("✅ Usuário já estava logado")
            else:
                logger.error("❌ Falha no login - página de login retornada")
                
                # Salvar resposta para debug
                with open('tmp/login_error_response.html', 'w', encoding='utf-8') as f:
                    f.write(login_response.text)
                logger.info("Resposta do login salva em tmp/login_error_response.html")
                
                # Verificar se há mensagens de erro
                soup = BeautifulSoup(login_response.text, 'html.parser')
                erros = soup.find_all(class_=re.compile(r'(alert|error|danger)'))
                if erros:
                    logger.error("Erros encontrados na página de login:")
                    for erro in erros:
                        logger.error(f"  - {erro.get_text().strip()}")
                
                return False
        else:
            logger.error(f"❌ Status inesperado do login: {login_response.status_code}")
            return False
            
        logger.info("✅ Login realizado com sucesso")
        
        # 2. Acessar página de veículos ANTES do cadastro
        logger.info("2. Verificando lista ANTES do cadastro...")
        veiculos_response = session.get(f"{base_url}/cliente/veiculos")
        
        if veiculos_response.status_code == 200:
            soup_antes = BeautifulSoup(veiculos_response.text, 'html.parser')
            veiculos_antes = soup_antes.find_all(text=re.compile(r'TST\d{4}'))
            logger.info(f"Veículos encontrados ANTES: {len(veiculos_antes)}")
            
            # Verificar se a placa já existe
            if placa_unica in veiculos_response.text:
                logger.warning(f"⚠️ Placa {placa_unica} já existe! Gerando nova...")
                timestamp = int(datetime.now().timestamp()) + 1
                placa_unica = f"TST{timestamp % 10000:04d}"
                chassi_unico = f"9BWHE21JX24{timestamp % 1000000:06d}"
                logger.info(f"Nova placa: {placa_unica}")
        
        # 3. Cadastrar novo veículo
        logger.info("3. Cadastrando novo veículo...")
        veiculo_data = {
            'marca': 'Volkswagen',
            'modelo': 'Golf',
            'ano_modelo': '2022',
            'placa': placa_unica,
            'cor': 'Azul',
            'chassi': chassi_unico
        }
        
        cadastro_response = session.post(f"{base_url}/cliente/veiculos", data=veiculo_data)
        logger.info(f"Status do cadastro: {cadastro_response.status_code}")
        logger.info(f"Headers: {dict(cadastro_response.headers)}")
        
        # Salvar resposta do cadastro para debug
        with open('tmp/cadastro_response.html', 'w', encoding='utf-8') as f:
            f.write(cadastro_response.text)
        logger.info("Resposta do cadastro salva em tmp/cadastro_response.html")
        
        # Verificar se há erros no cadastro (procurar por alertas de erro específicos)
        soup_cadastro = BeautifulSoup(cadastro_response.text, 'html.parser')
        erros_cadastro = soup_cadastro.find_all(class_=re.compile(r'alert-danger|error|invalid-feedback'))
        if erros_cadastro:
            logger.error("❌ Erros encontrados no cadastro:")
            for erro in erros_cadastro:
                texto_erro = erro.get_text().strip()
                # Ignorar botões e elementos que não são erros
                if texto_erro not in ['Sair', 'Desativar', 'Editar', 'Cancelar']:
                    logger.error(f"  - {texto_erro}")
            # Se todos os "erros" foram ignorados, não há erro real
            erros_reais = [e for e in erros_cadastro if e.get_text().strip() not in ['Sair', 'Desativar', 'Editar', 'Cancelar']]
            if erros_reais:
                return False
        
        # Verificar se foi redirecionado com sucesso (status 302) ou se retornou o formulário (status 200)
        if cadastro_response.status_code == 302:
            location = cadastro_response.headers.get('location', '')
            logger.info(f"Redirecionamento: {location}")
            
            if 'sucesso=cadastrado' in location:
                logger.info("✅ Cadastro realizado com sucesso")
            else:
                logger.warning(f"⚠️ Redirecionamento inesperado: {location}")
        elif cadastro_response.status_code == 200:
            # Verificar se é uma página de sucesso (lista de veículos) ou erro (formulário)
            if "Meus Veículos" in cadastro_response.text and "table" in cadastro_response.text:
                logger.info("✅ Cadastro realizado com sucesso (retornou lista de veículos)")
            elif "Veículo cadastrado com sucesso" in cadastro_response.text:
                logger.info("✅ Cadastro realizado com sucesso")
            else:
                logger.error("❌ Cadastro retornou formulário - possível erro")
                return False
        else:
            logger.error(f"❌ Status inesperado do cadastro: {cadastro_response.status_code}")
            return False
        
        # 4. Verificar lista APÓS o cadastro
        logger.info("4. Verificando lista APÓS o cadastro...")
        
        # Aguardar um pouco para garantir que o banco foi atualizado
        import time
        time.sleep(0.5)
        
        veiculos_response_depois = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da lista: {veiculos_response_depois.status_code}")
        
        if veiculos_response_depois.status_code == 200:
            soup_depois = BeautifulSoup(veiculos_response_depois.text, 'html.parser')
            
            # Salvar HTML para debug
            with open('tmp/lista_veiculos_debug.html', 'w', encoding='utf-8') as f:
                f.write(veiculos_response_depois.text)
            logger.info("HTML da lista salvo em tmp/lista_veiculos_debug.html")
            
            # Procurar pela placa de várias formas
            placa_encontrada = False
            
            # Busca 1: Texto simples
            if placa_unica in veiculos_response_depois.text:
                logger.info(f"✅ Placa {placa_unica} encontrada no texto da página")
                placa_encontrada = True
            
            # Busca 2: Com hífen
            placa_formatada = f"{placa_unica[:3]}-{placa_unica[3:]}"
            if placa_formatada in veiculos_response_depois.text:
                logger.info(f"✅ Placa formatada {placa_formatada} encontrada")
                placa_encontrada = True
            
            # Busca 3: Em elementos específicos
            elementos_placa = soup_depois.find_all(text=re.compile(placa_unica))
            if elementos_placa:
                logger.info(f"✅ Placa encontrada em {len(elementos_placa)} elementos")
                placa_encontrada = True
            
            # Busca 4: Contar total de veículos
            veiculos_depois = soup_depois.find_all(text=re.compile(r'TST\d{4}'))
            logger.info(f"Total de veículos DEPOIS: {len(veiculos_depois)}")
            
            if not placa_encontrada:
                logger.error(f"❌ Placa {placa_unica} NÃO encontrada na lista!")
                
                # Debug adicional
                logger.info("=== DEBUG: Primeiros 500 caracteres da resposta ===")
                logger.info(veiculos_response_depois.text[:500])
                
                # Verificar se há mensagem de "nenhum veículo"
                if "nenhum veículo" in veiculos_response_depois.text.lower():
                    logger.error("❌ Página mostra 'nenhum veículo cadastrado'")
                
                return False
            else:
                logger.info("✅ SUCESSO: Veículo cadastrado e aparece na lista!")
                return True
        
        else:
            logger.error(f"❌ Erro ao acessar lista de veículos: {veiculos_response_depois.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {str(e)}")
        return False

if __name__ == "__main__":
    # Criar diretório tmp se não existir
    import os
    os.makedirs('tmp', exist_ok=True)
    
    sucesso = test_veiculo_cadastro_completo()
    
    if sucesso:
        print("\n🎉 TESTE PASSOU: Cadastro de veículo funcionando corretamente!")
    else:
        print("\n❌ TESTE FALHOU: Problema no cadastro ou exibição de veículos!")
        exit(1)