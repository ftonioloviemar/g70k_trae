#!/usr/bin/env python3
"""
Script para testar a importação de dados do Caspio.
Testa a importação de usuários, veículos e garantias.
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(str(Path(__file__).parent))

from app.services.caspio_import_service import CaspioImportService
import logging

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """
    Executa o teste de importação do Caspio.
    """
    print("🚀 Iniciando teste de importação do Caspio...")
    
    # Caminho do arquivo XML do Caspio
    xml_path = "docs/context/caspio_viemar/Tables_2025-Sep-08_1152.xml"
    
    if not Path(xml_path).exists():
        print(f"❌ Erro: Arquivo XML não encontrado em {xml_path}")
        return
    
    try:
        # Cria o serviço de importação
        db_path = "data/viemar_garantia.db"
        import_service = CaspioImportService(db_path, xml_path)
        
        print("\n📊 Estatísticas iniciais:")
        print(f"- Usuários: {import_service.stats.users_imported} importados, {import_service.stats.users_skipped} ignorados")
        print(f"- Veículos: {import_service.stats.vehicles_imported} importados, {import_service.stats.vehicles_skipped} ignorados")
        print(f"- Garantias: {import_service.stats.warranties_imported} importadas, {import_service.stats.warranties_skipped} ignoradas")
        
        # Testa importação de usuários
        print("\n👥 Importando usuários...")
        users_imported = import_service.import_users()
        print(f"✅ {users_imported} usuários importados com sucesso")
        
        # Testa importação de veículos
        print("\n🚗 Importando veículos...")
        vehicles_imported = import_service.import_vehicles()
        print(f"✅ {vehicles_imported} veículos importados com sucesso")
        
        # Testa importação de garantias
        print("\n🛡️ Importando garantias...")
        warranties_imported = import_service.import_warranties()
        print(f"✅ {warranties_imported} garantias importadas com sucesso")
        
        # Exibe estatísticas finais
        print("\n📈 Estatísticas finais:")
        stats = import_service.get_import_stats()
        print(f"- Usuários: {stats['users_imported']} importados, {stats['users_skipped']} ignorados")
        print(f"- Veículos: {stats['vehicles_imported']} importados, {stats['vehicles_skipped']} ignorados")
        print(f"- Garantias: {stats['warranties_imported']} importadas, {stats['warranties_skipped']} ignoradas")
        
        if stats['errors']:
            print(f"\n⚠️ Erros encontrados ({len(stats['errors'])}):")
            for i, error in enumerate(stats['errors'][:5], 1):
                print(f"  {i}. {error}")
            if len(stats['errors']) > 5:
                print(f"  ... e mais {len(stats['errors']) - 5} erros")
        
        print("\n🎉 Importação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a importação: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)