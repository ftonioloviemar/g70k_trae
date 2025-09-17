#!/usr/bin/env python3
"""Script para debugar a estrutura das tabelas no XML do Caspio"""

import xml.etree.ElementTree as ET
import os

def debug_xml_tables():
    """Debug da estrutura das tabelas no XML"""
    xml_path = r'c:\python\g70k_trae\docs\context\caspio_viemar\Tables_2025-Sep-08_1152.xml'
    
    if not os.path.exists(xml_path):
        print('Arquivo XML não encontrado!')
        return
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        print('=== ANÁLISE DAS TABELAS NO XML ===')
        
        tables = root.findall('.//Table')
        print(f'Total de tabelas encontradas: {len(tables)}')
        
        for i, table in enumerate(tables):
            print(f'\n--- TABELA {i+1} ---')
            print(f'Atributos da tabela: {table.attrib}')
            
            # Verificar se tem tag Name
            name_elem = table.find('Name')
            if name_elem is not None:
                print(f'Nome da tabela (tag Name): {name_elem.text}')
            else:
                print('Tag Name não encontrada')
            
            # Verificar se tem atributo name
            if 'name' in table.attrib:
                print(f'Nome da tabela (atributo name): {table.attrib["name"]}')
            
            # Mostrar primeiros elementos filhos
            print('Primeiros elementos filhos:')
            for j, child in enumerate(table[:5]):  # Primeiros 5 filhos
                print(f'  {j+1}. Tag: {child.tag}, Atributos: {child.attrib}')
                if child.text and child.text.strip():
                    print(f'     Texto: {child.text[:50]}...')
            
            # Se for uma tabela com registros Row, verificar os campos
            rows = table.findall('Row')
            if rows:
                print(f'Número de registros (Row): {len(rows)}')
                first_row = rows[0]
                fields = first_row.findall('Field')
                if fields:
                    print('Campos do primeiro registro:')
                    for field in fields[:10]:  # Primeiros 10 campos
                        field_name = field.get('name', 'SEM_NOME')
                        field_value = field.text if field.text else ''
                        print(f'  - {field_name}: {field_value[:30]}...')
                    
                    # Verificar se tem campo EMAIL com ftoniolo
                    for row in rows:
                        for field in row.findall('Field'):
                            if field.get('name') == 'EMAIL' and field.text and 'ftoniolo' in field.text.lower():
                                print(f'*** ENCONTRADO FTONIOLO na tabela {i+1}! ***')
                                print(f'    Email: {field.text}')
                                # Mostrar todos os campos deste registro
                                print('    Todos os campos do registro:')
                                for f in row.findall('Field'):
                                    fname = f.get('name', 'SEM_NOME')
                                    fvalue = f.text if f.text else ''
                                    print(f'      {fname}: {fvalue}')
                                return  # Para na primeira ocorrência
        
    except Exception as e:
        print(f'Erro ao analisar XML: {e}')

if __name__ == '__main__':
    debug_xml_tables()