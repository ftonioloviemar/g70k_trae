#!/usr/bin/env python3
"""
Teste para verificar se as correções de encoding do Firebird funcionaram
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import Config
from app.services.firebird_service import get_firebird_service
from fastlite import Database
import logging

# Configurar logging para ver detalhes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_firebird_encoding():
    """
    Testa se o problema de encoding foi resolvido
    """
    try:
        logger.info("Iniciando teste de encoding do Firebird...")
        
        # Configurar serviço
        config = Config()
        firebird_service = get_firebird_service(config)
        
        logger.info(f"Charset configurado: {config.FIREBIRD_CHARSET}")
        
        # Configurar encoding para Firebird
        firebird_config = {
            'host': config.FIREBIRD_HOST,
            'database': config.FIREBIRD_DATABASE,
            'user': config.FIREBIRD_USER,
            'password': config.FIREBIRD_PASSWORD,
            'charset': 'ISO8859_1'  # Encoding correto para Firebird
        }
        
        # Testar conexão
        logger.info("Testando conexão...")
        connection_ok = firebird_service.test_connection()
        logger.info(f"Conexão: {'OK' if connection_ok else 'FALHOU'}")
        
        if not connection_ok:
            logger.error("Conexão falhou, não é possível continuar o teste")
            return False
        
        # Testar busca de produtos
        logger.info("Testando busca de produtos...")
        produtos = firebird_service.get_produtos_erp()
        logger.info(f"Produtos encontrados: {len(produtos)}")
        
        # Mostrar alguns produtos para verificar encoding
        for i, produto in enumerate(produtos[:5]):
            logger.info(f"Produto {i+1}: SKU='{produto['sku']}', Descrição='{produto['descricao']}'")
            
            # Verificar se há caracteres especiais
            descricao = produto['descricao']
            has_special_chars = any(ord(c) > 127 for c in descricao)
            if has_special_chars:
                logger.info(f"  -> Contém caracteres especiais: {[c for c in descricao if ord(c) > 127]}")
        
        # Testar sincronização
        logger.info("Testando sincronização...")
        db = Database(config.DATABASE_PATH)
        stats = firebird_service.sync_produtos(db)
        logger.info(f"Estatísticas da sincronização: {stats}")
        
        if stats['erros'] == 0:
            logger.info("✅ Teste de encoding passou! Nenhum erro de encoding detectado.")
            return True
        else:
            logger.warning(f"⚠️ Sincronização teve {stats['erros']} erros")
            return False
            
    except UnicodeDecodeError as e:
        logger.error(f"❌ Erro de encoding ainda presente: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    success = test_firebird_encoding()
    if success:
        print("\n🎉 Correção de encoding funcionou!")
        sys.exit(0)
    else:
        print("\n💥 Ainda há problemas de encoding")
        sys.exit(1)