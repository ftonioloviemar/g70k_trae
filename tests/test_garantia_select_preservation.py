#!/usr/bin/env python3
"""
Teste específico para verificar se os selects de produto e veículo preservam os valores selecionados
"""

import requests
import logging
from datetime import datetime, timedelta
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_select_preservation():
    """Testa especificamente se os selects preservam os valores selecionados"""
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    try:
        # 1. Fazer login
        logger.info("1. Fazendo login...")
        login_response = session.post(f"{base_url}/login", data={
            "email": "sergio@reis.com",
            "senha": "123456"
        }, allow_redirects=False)
        
        if login_response.status_code != 302:
            logger.error(f"Erro no login: {login_response.status_code}")
            return False
            
        logger.info("Login realizado com sucesso")
        
        # 2. Acessar página de nova garantia para ver as opções disponíveis
        logger.info("2. Verificando opções disponíveis...")
        nova_garantia_response = session.get(f"{base_url}/cliente/garantias/nova")
        
        if nova_garantia_response.status_code != 200:
            logger.error(f"Erro ao acessar nova garantia: {nova_garantia_response.status_code}")
            return False
        
        html_inicial = nova_garantia_response.text
        
        # Extrair IDs de produtos e veículos disponíveis
        produto_pattern = r'<option value="(\d+)">([^<]+)</option>'
        veiculo_pattern = r'<option value="(\d+)">([^<]+)</option>'
        
        produtos_match = re.findall(produto_pattern, html_inicial)
        veiculos_match = re.findall(veiculo_pattern, html_inicial)
        
        if not produtos_match or not veiculos_match:
            logger.error("Não foi possível encontrar produtos ou veículos disponíveis")
            return False
        
        # Usar o primeiro produto e veículo encontrados
        produto_id = produtos_match[0][0]
        produto_nome = produtos_match[0][1]
        veiculo_id = veiculos_match[0][0]
        veiculo_nome = veiculos_match[0][1]
        
        logger.info(f"Produto selecionado: ID {produto_id} - {produto_nome}")
        logger.info(f"Veículo selecionado: ID {veiculo_id} - {veiculo_nome}")
        
        # 3. Submeter formulário com data de instalação inválida
        logger.info("3. Submetendo formulário com data inválida...")
        
        data_invalida = (datetime.now() - timedelta(days=35)).strftime('%Y-%m-%d')
        
        form_data = {
            "produto_id": produto_id,
            "veiculo_id": veiculo_id,
            "lote_fabricacao": "LOTE12345",
            "data_instalacao": data_invalida,
            "nota_fiscal": "NF123456",
            "nome_estabelecimento": "Oficina Teste",
            "quilometragem": "50000",
            "observacoes": "Teste de preservação"
        }
        
        garantia_response = session.post(
            f"{base_url}/cliente/garantias/nova", 
            data=form_data,
            allow_redirects=False
        )
        
        if garantia_response.status_code != 200:
            logger.error(f"Erro inesperado: {garantia_response.status_code}")
            return False
        
        html_com_erro = garantia_response.text
        
        # 4. Verificar se os selects têm as opções corretas marcadas como selected
        logger.info("4. Verificando preservação dos selects...")
        
        # Procurar por option com selected para produto
        produto_selected_pattern = f'<option[^>]*value="{produto_id}"[^>]*selected[^>]*>'
        produto_preservado = bool(re.search(produto_selected_pattern, html_com_erro, re.IGNORECASE))
        
        # Procurar por option com selected para veículo
        veiculo_selected_pattern = f'<option[^>]*value="{veiculo_id}"[^>]*selected[^>]*>'
        veiculo_preservado = bool(re.search(veiculo_selected_pattern, html_com_erro, re.IGNORECASE))
        
        # Verificar outros campos também
        outros_campos = {
            'lote_fabricacao': 'LOTE12345',
            'nota_fiscal': 'NF123456',
            'nome_estabelecimento': 'Oficina Teste',
            'quilometragem': '50000'
        }
        
        campos_preservados = 0
        for campo, valor in outros_campos.items():
            if f'value="{valor}"' in html_com_erro:
                logger.info(f"✓ Campo {campo} preservado")
                campos_preservados += 1
            else:
                logger.warning(f"✗ Campo {campo} NÃO preservado")
        
        # Verificar se a mensagem de erro está presente
        erro_presente = 'Data de instalação não pode ser superior a 30 dias' in html_com_erro
        
        # Resultados
        logger.info(f"\n=== RESULTADOS ===")
        logger.info(f"Produto preservado: {'✓' if produto_preservado else '✗'}")
        logger.info(f"Veículo preservado: {'✓' if veiculo_preservado else '✗'}")
        logger.info(f"Outros campos preservados: {campos_preservados}/4")
        logger.info(f"Mensagem de erro presente: {'✓' if erro_presente else '✗'}")
        
        # Teste passa se produto e veículo estão preservados e pelo menos 3 outros campos
        sucesso = produto_preservado and veiculo_preservado and campos_preservados >= 3 and erro_presente
        
        if sucesso:
            logger.info("\n🎉 TESTE PASSOU: Selects preservam corretamente os valores!")
        else:
            logger.error("\n❌ TESTE FALHOU: Selects não preservam os valores corretamente")
            
            # Debug: mostrar parte do HTML para análise
            logger.debug("\n=== DEBUG HTML (primeiros 2000 caracteres) ===")
            logger.debug(html_com_erro[:2000])
        
        return sucesso
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Teste Específico de Preservação de Selects ===")
    
    success = test_select_preservation()
    
    if success:
        logger.info("\n✅ CORREÇÃO FUNCIONANDO!")
        logger.info("Os selects de produto e veículo agora preservam os valores selecionados.")
    else:
        logger.error("\n❌ CORREÇÃO PRECISA DE AJUSTES!")
        logger.error("Os selects ainda não estão preservando corretamente os valores.")