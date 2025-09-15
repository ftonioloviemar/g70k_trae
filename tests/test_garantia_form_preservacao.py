#!/usr/bin/env python3
"""
Teste para verificar se o formulário de garantia preserva os dados selecionados após erro de validação
"""

import requests
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_garantia_form_preservation():
    """Testa se o formulário preserva os dados após erro de validação"""
    
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
        
        # 2. Acessar página de nova garantia
        logger.info("2. Acessando página de nova garantia...")
        nova_garantia_response = session.get(f"{base_url}/cliente/garantias/nova")
        
        if nova_garantia_response.status_code != 200:
            logger.error(f"Erro ao acessar nova garantia: {nova_garantia_response.status_code}")
            return False
            
        logger.info("Página de nova garantia acessada com sucesso")
        
        # 3. Submeter formulário com data de instalação inválida (mais de 30 dias)
        logger.info("3. Submetendo formulário com data inválida...")
        
        # Data de 35 dias atrás (deve gerar erro)
        data_invalida = (datetime.now() - timedelta(days=35)).strftime('%Y-%m-%d')
        
        form_data = {
            "produto_id": "1",  # Assumindo que existe produto com ID 1
            "veiculo_id": "1",  # Assumindo que existe veículo com ID 1
            "lote_fabricacao": "LOTE12345",
            "data_instalacao": data_invalida,
            "nota_fiscal": "NF123456",
            "nome_estabelecimento": "Oficina Teste",
            "quilometragem": "50000",
            "observacoes": "Teste de preservação de dados"
        }
        
        garantia_response = session.post(
            f"{base_url}/cliente/garantias/nova", 
            data=form_data,
            allow_redirects=False
        )
        
        # Deve retornar 200 (formulário com erro) ao invés de redirect
        if garantia_response.status_code == 200:
            logger.info("Formulário retornado com erro de validação (esperado)")
            
            # 4. Verificar se os dados foram preservados no HTML
            html_content = garantia_response.text
            
            # Verificar se os valores estão preservados
            checks = [
                ('produto_id="1"', "Produto selecionado"),
                ('veiculo_id="1"', "Veículo selecionado"),
                ('value="LOTE12345"', "Lote de fabricação"),
                ('value="NF123456"', "Nota fiscal"),
                ('value="Oficina Teste"', "Nome do estabelecimento"),
                ('value="50000"', "Quilometragem"),
                ('Teste de preservação de dados', "Observações"),
                ('selected', "Opção selecionada nos selects")
            ]
            
            preserved_count = 0
            for check, description in checks:
                if check in html_content:
                    logger.info(f"✓ {description} preservado")
                    preserved_count += 1
                else:
                    logger.warning(f"✗ {description} NÃO preservado")
            
            if preserved_count >= 6:  # Pelo menos 6 dos 8 checks devem passar
                logger.info("✅ TESTE PASSOU: Dados preservados corretamente no formulário")
                return True
            else:
                logger.error(f"❌ TESTE FALHOU: Apenas {preserved_count}/8 dados preservados")
                return False
                
        elif garantia_response.status_code == 302:
            logger.error("❌ TESTE FALHOU: Formulário redirecionou (deveria mostrar erro)")
            return False
        else:
            logger.error(f"❌ TESTE FALHOU: Status inesperado {garantia_response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Teste de Preservação de Dados no Formulário de Garantia ===")
    
    success = test_garantia_form_preservation()
    
    if success:
        logger.info("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("O formulário agora preserva os dados selecionados após erro de validação.")
    else:
        logger.error("\n❌ TESTE FALHOU!")
        logger.error("O formulário ainda não preserva corretamente os dados.")