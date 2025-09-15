#!/usr/bin/env python3
"""
Script para testar o cadastro de veículo com usuário sergio@reis.com
"""

import requests
import logging
import random
from pathlib import Path
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sergio_veiculo_cadastro():
    """Testa o cadastro de veículo com usuário sergio@reis.com"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # 1. Fazer login
        logger.info("1. Fazendo login...")
        login_data = {
            "email": "sergio@reis.com",
            "senha": "123456"
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        logger.info(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            logger.error("❌ Falha no login")
            return False
        
        logger.info("✅ Login realizado com sucesso")
        
        # 2. Verificar veículos antes do cadastro
        logger.info("2. Verificando veículos ANTES do cadastro...")
        lista_antes = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da lista antes: {lista_antes.status_code}")
        
        # Contar veículos antes
        soup_antes = BeautifulSoup(lista_antes.text, 'html.parser')
        veiculos_antes = soup_antes.find_all(string=lambda text: text and 'SRG' in text if text else False)
        logger.info(f"Veículos encontrados ANTES: {len(veiculos_antes)}")
        
        # 3. Cadastrar novo veículo
        logger.info("3. Cadastrando novo veículo...")
        
        # Gerar placa única
        placa_numero = random.randint(1000, 9999)
        placa_unica = f"SRG-{placa_numero}"
        chassi_numero = random.randint(100000000000000, 999999999999999)
        chassi_unico = f"SRG{chassi_numero}"
        
        veiculo_data = {
            "marca": "Honda",
            "modelo": "Civic",
            "ano_modelo": "2023",
            "placa": placa_unica,
            "cor": "Prata",
            "chassi": chassi_unico
        }
        
        logger.info(f"Dados do veículo: {veiculo_data}")
        
        cadastro_response = session.post(f"{base_url}/cliente/veiculos/novo", data=veiculo_data)
        logger.info(f"Status do cadastro: {cadastro_response.status_code}")
        
        # Salvar resposta para debug
        Path("tmp").mkdir(exist_ok=True)
        with open("tmp/sergio_cadastro_response.html", "w", encoding="utf-8") as f:
            f.write(cadastro_response.text)
        logger.info("Resposta do cadastro salva em tmp/sergio_cadastro_response.html")
        
        # Verificar se o cadastro foi bem-sucedido
        if cadastro_response.status_code == 302:  # Redirecionamento após cadastro
            logger.info("✅ Cadastro realizado com sucesso (redirecionamento)")
        elif cadastro_response.status_code == 200:
            # Verificar se retornou para a lista de veículos ou se há erro
            if "Meus Veículos" in cadastro_response.text and "table" in cadastro_response.text:
                logger.info("✅ Cadastro realizado com sucesso (retornou lista de veículos)")
            elif "Veículo cadastrado com sucesso" in cadastro_response.text:
                logger.info("✅ Cadastro realizado com sucesso (mensagem de sucesso)")
            else:
                # Verificar se há erros na página
                soup = BeautifulSoup(cadastro_response.text, 'html.parser')
                error_elements = soup.find_all(class_=["alert-danger", "text-danger", "error", "invalid-feedback"])
                
                if error_elements:
                    error_texts = [elem.get_text().strip() for elem in error_elements]
                    # Filtrar textos que não são erros reais
                    real_errors = [text for text in error_texts if text and text not in ["Sair", "Desativar", "Editar"]]
                    
                    if real_errors:
                        logger.error(f"❌ Erro no formulário de cadastro: {real_errors}")
                        return False
                    else:
                        logger.info("✅ Cadastro realizado com sucesso")
                else:
                    logger.info("✅ Cadastro realizado com sucesso")
        else:
            logger.error(f"❌ Falha no cadastro - status {cadastro_response.status_code}")
            return False
        
        # 4. Verificar veículos após o cadastro
        logger.info("4. Verificando lista APÓS o cadastro...")
        lista_depois = session.get(f"{base_url}/cliente/veiculos")
        logger.info(f"Status da lista: {lista_depois.status_code}")
        
        # Salvar lista para debug
        with open("tmp/sergio_lista_veiculos_debug.html", "w", encoding="utf-8") as f:
            f.write(lista_depois.text)
        logger.info("HTML da lista salvo em tmp/sergio_lista_veiculos_debug.html")
        
        # Verificar se a placa aparece na lista
        if placa_unica in lista_depois.text:
            logger.info(f"✅ Placa {placa_unica} encontrada na lista")
        else:
            logger.error(f"❌ Placa {placa_unica} NÃO encontrada na lista")
            return False
        
        # Contar veículos depois
        soup_depois = BeautifulSoup(lista_depois.text, 'html.parser')
        veiculos_depois = soup_depois.find_all(string=lambda text: text and 'SRG' in text if text else False)
        logger.info(f"Total de veículos DEPOIS: {len(veiculos_depois)}")
        
        logger.info("✅ SUCESSO: Veículo cadastrado e aparece na lista!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste de cadastro: {e}")
        return False

if __name__ == "__main__":
    print("🚗 Testando cadastro de veículo com sergio@reis.com...")
    success = test_sergio_veiculo_cadastro()
    
    if success:
        print("\n🎉 TESTE PASSOU: Cadastro de veículo funcionando corretamente!")
    else:
        print("\n❌ TESTE FALHOU: Problema no cadastro de veículo")
        print("Verifique os arquivos em tmp/ para mais detalhes")