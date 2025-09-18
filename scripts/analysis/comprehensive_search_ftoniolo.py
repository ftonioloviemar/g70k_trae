#!/usr/bin/env python3
"""
Script para busca abrangente do usuário ftoniolo no XML do Caspio
Busca por diferentes variações e analisa a estrutura dos dados
"""

import xml.etree.ElementTree as ET
import os
import re
from typing import List, Dict, Any

def search_ftoniolo_comprehensive():
    """Busca abrangente por ftoniolo no XML"""
    
    xml_file = r"c:\python\g70k_trae\docs\context\caspio_viemar\Tables_2025-Sep-08_1152.xml"
    
    if not os.path.exists(xml_file):
        print(f"❌ Arquivo XML não encontrado: {xml_file}")
        return
    
    print(f"📁 Analisando arquivo: {xml_file}")
    print(f"📊 Tamanho do arquivo: {os.path.getsize(xml_file):,} bytes")
    
    try:
        # Parse do XML
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Encontrar tabela CLIENTE
        cliente_table = None
        for table in root.findall('.//Table'):
            name_elem = table.find('Name')
            if name_elem is not None and name_elem.text == 'CLIENTE':
                cliente_table = table
                break
        
        if cliente_table is None:
            print("❌ Tabela CLIENTE não encontrada")
            return
        
        rows = cliente_table.findall('Row')
        print(f"📋 Total de registros na tabela CLIENTE: {len(rows)}")
        
        # Padrões de busca para ftoniolo
        search_patterns = [
            'ftoniolo',
            'FTONIOLO', 
            'Ftoniolo',
            'ftoniolo@',
            'FTONIOLO@',
            'Ftoniolo@',
            'premiumcar',
            'PREMIUMCAR',
            'PremiumCar'
        ]
        
        print("\n🔍 Iniciando busca abrangente...")
        
        matches_found = []
        
        # Buscar em todos os registros
        for i, row in enumerate(rows):
            row_data = {}
            
            # Extrair todos os campos do registro
            for field in row:
                field_name = field.tag
                field_value = field.text if field.text else ""
                row_data[field_name] = field_value
                
                # Buscar por qualquer padrão
                for pattern in search_patterns:
                    if pattern.lower() in field_value.lower():
                        matches_found.append({
                            'registro': i + 1,
                            'campo': field_name,
                            'valor': field_value,
                            'padrao_encontrado': pattern,
                            'registro_completo': row_data
                        })
        
        # Exibir resultados
        if matches_found:
            print(f"\n✅ Encontrados {len(matches_found)} matches:")
            for match in matches_found:
                print(f"\n📍 Registro #{match['registro']}")
                print(f"   Campo: {match['campo']}")
                print(f"   Valor: '{match['valor']}'")
                print(f"   Padrão: {match['padrao_encontrado']}")
                print("   Registro completo:")
                for k, v in match['registro_completo'].items():
                    if v:  # Só mostrar campos não vazios
                        print(f"     {k}: {v}")
        else:
            print("\n❌ Nenhum match encontrado para os padrões de busca")
            
            # Vamos analisar alguns registros para entender a estrutura
            print("\n📊 Analisando estrutura dos primeiros 5 registros:")
            for i in range(min(5, len(rows))):
                row = rows[i]
                print(f"\n--- Registro {i+1} ---")
                for field in row:
                    field_name = field.tag
                    field_value = field.text if field.text else "[VAZIO]"
                    print(f"  {field_name}: {field_value}")
        
        # Buscar especificamente por emails que contenham @
        print("\n📧 Buscando registros com emails válidos:")
        email_count = 0
        for i, row in enumerate(rows):
            for field in row:
                if field.tag == 'EMAIL' and field.text and '@' in field.text:
                    email_count += 1
                    if email_count <= 10:  # Mostrar apenas os primeiros 10
                        print(f"  Registro {i+1}: {field.text}")
        
        print(f"\n📊 Total de registros com email válido: {email_count}")
        
        # Verificar se há registros com campos específicos preenchidos
        print("\n📋 Estatísticas dos campos:")
        field_stats = {}
        
        for row in rows:
            for field in row:
                field_name = field.tag
                if field_name not in field_stats:
                    field_stats[field_name] = {'total': 0, 'preenchidos': 0, 'vazios': 0}
                
                field_stats[field_name]['total'] += 1
                if field.text and field.text.strip():
                    field_stats[field_name]['preenchidos'] += 1
                else:
                    field_stats[field_name]['vazios'] += 1
        
        for field_name, stats in field_stats.items():
            pct_preenchido = (stats['preenchidos'] / stats['total']) * 100
            print(f"  {field_name}: {stats['preenchidos']}/{stats['total']} preenchidos ({pct_preenchido:.1f}%)")

    except ET.ParseError as e:
        print(f"❌ Erro ao fazer parse do XML: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    search_ftoniolo_comprehensive()