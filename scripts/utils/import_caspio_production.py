#!/usr/bin/env python3
"""
Script de Produção para Importação de Dados do Caspio

Este script importa dados do sistema Caspio antigo para o novo sistema G70K.
Importa usuários, veículos e garantias mantendo a integridade dos dados.

Uso:
    uv run scripts/utils/import_caspio_production.py

Requisitos:
    - Arquivos XML do Caspio na pasta docs/context/caspio_viemar/
    - Banco de dados SQLite configurado
    - Backup do banco atual (recomendado)

Autor: Sistema G70K
Data: 2025-09-17
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app.services.caspio_import_service import CaspioImportService
from app.logger import get_logger

logger = get_logger(__name__)

def fazer_backup_banco():
    """Faz backup do banco de dados atual antes da importação."""
    try:
        from shutil import copy2
        
        db_path = root_dir / "data" / "viemar_garantia.db"
        if db_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = root_dir / "data" / f"viemar_garantia_backup_{timestamp}.db"
            copy2(db_path, backup_path)
            logger.info(f"Backup criado: {backup_path}")
            print(f"✅ Backup do banco criado: {backup_path.name}")
            return True
        else:
            logger.warning("Banco de dados não encontrado para backup")
            print("⚠️ Banco de dados não encontrado para backup")
            return False
    except Exception as e:
        logger.error(f"Erro ao fazer backup: {e}")
        print(f"❌ Erro ao fazer backup: {e}")
        return False

def verificar_arquivos_caspio():
    """Verifica se os arquivos XML do Caspio existem."""
    caspio_dir = root_dir / "docs" / "context" / "caspio_viemar"
    
    arquivos_necessarios = [
        "USUARIO.xml",
        "VEICULO.xml", 
        "PRODUTO_APLICADO.xml"
    ]
    
    arquivos_encontrados = []
    arquivos_faltando = []
    
    for arquivo in arquivos_necessarios:
        arquivo_path = caspio_dir / arquivo
        if arquivo_path.exists():
            arquivos_encontrados.append(arquivo)
            logger.info(f"Arquivo encontrado: {arquivo}")
        else:
            arquivos_faltando.append(arquivo)
            logger.warning(f"Arquivo não encontrado: {arquivo}")
    
    print(f"\n📁 Verificação de arquivos:")
    print(f"✅ Encontrados: {len(arquivos_encontrados)} arquivos")
    for arquivo in arquivos_encontrados:
        print(f"   - {arquivo}")
    
    if arquivos_faltando:
        print(f"❌ Faltando: {len(arquivos_faltando)} arquivos")
        for arquivo in arquivos_faltando:
            print(f"   - {arquivo}")
        return False
    
    return True

def main():
    """Função principal do script de importação."""
    print("🚀 Iniciando Importação de Dados do Caspio")
    print("=" * 50)
    
    # Verificar arquivos necessários
    print("\n1️⃣ Verificando arquivos do Caspio...")
    if not verificar_arquivos_caspio():
        print("\n❌ Arquivos necessários não encontrados!")
        print("Certifique-se de que os arquivos XML estão em docs/context/caspio_viemar/")
        return False
    
    # Fazer backup do banco
    print("\n2️⃣ Fazendo backup do banco de dados...")
    if not fazer_backup_banco():
        resposta = input("\n⚠️ Não foi possível fazer backup. Continuar mesmo assim? (s/N): ")
        if resposta.lower() != 's':
            print("Importação cancelada pelo usuário.")
            return False
    
    # Confirmar importação
    print("\n3️⃣ Confirmação de importação")
    print("Esta operação irá importar dados do Caspio para o sistema atual.")
    print("Dados duplicados serão ignorados automaticamente.")
    resposta = input("\nDeseja continuar com a importação? (s/N): ")
    
    if resposta.lower() != 's':
        print("Importação cancelada pelo usuário.")
        return False
    
    # Executar importação
    print("\n4️⃣ Executando importação...")
    print("-" * 30)
    
    try:
        # Inicializar serviço de importação
        caspio_dir = root_dir / "docs" / "context" / "caspio_viemar"
        service = CaspioImportService(str(caspio_dir))
        
        # Executar importação completa
        stats = service.import_all()
        
        # Exibir resultados
        print("\n" + "=" * 50)
        print("🎉 IMPORTAÇÃO CONCLUÍDA!")
        print("=" * 50)
        
        print(f"\n📈 Estatísticas finais:")
        print(f"- Usuários: {stats['users_imported']} importados, {stats['users_skipped']} ignorados")
        print(f"- Veículos: {stats['vehicles_imported']} importados, {stats['vehicles_skipped']} ignorados")
        print(f"- Garantias: {stats['warranties_imported']} importadas, {stats['warranties_skipped']} ignoradas")
        
        if stats['errors']:
            print(f"\n⚠️ Erros encontrados ({len(stats['errors'])}):")
            for i, erro in enumerate(stats['errors'][:10], 1):
                print(f"  {i}. {erro}")
            if len(stats['errors']) > 10:
                print(f"  ... e mais {len(stats['errors']) - 10} erros")
        
        # Log final
        logger.info("Importação de produção concluída com sucesso")
        logger.info(f"Stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante importação: {e}")
        print(f"\n❌ Erro durante importação: {e}")
        return False

if __name__ == "__main__":
    try:
        sucesso = main()
        if sucesso:
            print("\n✅ Script executado com sucesso!")
            sys.exit(0)
        else:
            print("\n❌ Script finalizado com erros.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Importação interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)