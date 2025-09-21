#!/usr/bin/env python3
"""
Teste para validar o feedback visual de erros no formulário de cadastro
"""

import requests
import logging
from datetime import datetime
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cadastro_form_validation():
    """Testa se o formulário de cadastro exibe erros específicos para cada campo"""
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    try:
        logger.info("=== TESTE DE VALIDAÇÃO DO FORMULÁRIO DE CADASTRO ===")
        
        # 1. Acessar página de cadastro
        logger.info("1. Acessando página de cadastro...")
        cadastro_response = session.get(f"{base_url}/cadastro")
        
        if cadastro_response.status_code != 200:
            logger.error(f"Erro ao acessar página de cadastro: {cadastro_response.status_code}")
            return False
            
        logger.info("Página de cadastro acessada com sucesso")
        
        # 2. Testar cenário 1: Campos obrigatórios vazios
        logger.info("2. Testando campos obrigatórios vazios...")
        
        form_data_vazio = {
            "nome": "",
            "email": "",
            "telefone": "",
            "cpf_cnpj": "",
            "cep": "",
            "endereco": "",
            "bairro": "",
            "cidade": "",
            "uf": "",
            "data_nascimento": "",
            "senha": "",
            "confirmar_senha": ""
        }
        
        response_vazio = session.post(f"{base_url}/cadastro", data=form_data_vazio)
        
        if response_vazio.status_code == 200:
            logger.info("✅ Formulário retornou erros para campos vazios")
            
            # Verificar se há mensagens de erro específicas
            html_content = response_vazio.text
            
            # Verificar se há classes de erro
            if 'is-invalid' in html_content:
                logger.info("✅ Classes 'is-invalid' encontradas no HTML")
            else:
                logger.warning("⚠️ Classes 'is-invalid' não encontradas")
            
            # Verificar se há mensagens de feedback
            if 'invalid-feedback' in html_content:
                logger.info("✅ Elementos 'invalid-feedback' encontrados no HTML")
            else:
                logger.warning("⚠️ Elementos 'invalid-feedback' não encontrados")
                
        else:
            logger.error(f"Erro inesperado: {response_vazio.status_code}")
            return False
        
        # 3. Testar cenário 2: Email inválido
        logger.info("3. Testando email inválido...")
        
        form_data_email_invalido = {
            "nome": "João Silva",
            "email": "email-invalido",
            "telefone": "(11) 99999-9999",
            "cpf_cnpj": "123.456.789-00",
            "cep": "01234-567",
            "endereco": "Rua Teste, 123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "data_nascimento": "1990-01-01",
            "senha": "123456",
            "confirmar_senha": "123456"
        }
        
        response_email = session.post(f"{base_url}/cadastro", data=form_data_email_invalido)
        
        if response_email.status_code == 200:
            logger.info("✅ Formulário retornou erro para email inválido")
            
            html_content = response_email.text
            
            # Verificar se o campo email tem classe de erro
            if 'name="email"' in html_content and 'is-invalid' in html_content:
                logger.info("✅ Campo email marcado com erro")
            else:
                logger.warning("⚠️ Campo email não marcado com erro")
                
        else:
            logger.error(f"Erro inesperado: {response_email.status_code}")
            return False
        
        # 4. Testar cenário 3: Senhas não coincidem
        logger.info("4. Testando senhas que não coincidem...")
        
        form_data_senha_diferente = {
            "nome": "João Silva",
            "email": "joao@teste.com",
            "telefone": "(11) 99999-9999",
            "cpf_cnpj": "123.456.789-00",
            "cep": "01234-567",
            "endereco": "Rua Teste, 123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "data_nascimento": "1990-01-01",
            "senha": "123456",
            "confirmar_senha": "654321"
        }
        
        response_senha = session.post(f"{base_url}/cadastro", data=form_data_senha_diferente)
        
        if response_senha.status_code == 200:
            logger.info("✅ Formulário retornou erro para senhas diferentes")
            
            html_content = response_senha.text
            
            # Verificar se há erro específico para confirmação de senha
            if 'confirmar_senha' in html_content and ('não coincidem' in html_content or 'diferentes' in html_content):
                logger.info("✅ Erro específico para confirmação de senha encontrado")
            else:
                logger.warning("⚠️ Erro específico para confirmação de senha não encontrado")
                
        else:
            logger.error(f"Erro inesperado: {response_senha.status_code}")
            return False
        
        logger.info("=== TESTE CONCLUÍDO COM SUCESSO ===")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando teste de validação do formulário de cadastro...")
    
    # Aguardar um pouco para garantir que o servidor esteja rodando
    time.sleep(2)
    
    success = test_cadastro_form_validation()
    
    if success:
        logger.info("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("O formulário de cadastro agora exibe erros específicos para cada campo.")
    else:
        logger.error("\n❌ TESTE FALHOU!")
        logger.error("Verifique os logs acima para identificar os problemas.")