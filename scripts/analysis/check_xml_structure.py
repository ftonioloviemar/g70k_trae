#!/usr/bin/env python3
"""Script para verificar a estrutura do XML do Caspio"""

import xml.etree.ElementTree as ET
import os

def check_xml_structure():
    """Verifica a estrutura do XML do Caspio"""
    xml_path = r'c:\python\g70k_trae\docs\context\caspio_viemar\Tables_2025-Sep-08_1152.xml'
    
    if not os.path.exists(xml_path):
        print('Arquivo XML não encontrado!')
        return
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        print('Estrutura do XML:')
        print(f'Root tag: {root.tag}')
        print(f'Root attributes: {root.attrib}')
        
        print('\nTags filhas do root:')
        for child in root:
            print(f'  Tag: {child.tag}, Attributes: {child.attrib}')
            if child.tag == 'Table':
                table_name = child.get('name')
                row_count = len(child.findall('Row'))
                print(f'    Nome da tabela: {table_name}')
                print(f'    Número de registros: {row_count}')
                
                # Se for a tabela CLIENTE, mostrar alguns campos
                if table_name == 'CLIENTE':
                    first_row = child.find('Row')
                    if first_row:
                        print('    Campos da tabela CLIENTE:')
                        for field in first_row.findall('Field'):
                            field_name = field.get('name')
                            print(f'      - {field_name}')
        
        # Procurar especificamente por ftoniolo
        print('\nProcurando por ftoniolo em todas as tabelas...')
        for table in root.findall('Table'):
            table_name = table.get('name')
            for i, row in enumerate(table.findall('Row')):
                for field in row.findall('Field'):
                    if field.text and 'ftoniolo' in field.text.lower():
                        print(f'Encontrado "ftoniolo" na tabela {table_name}, registro {i+1}, campo {field.get("name")}: {field.text}')
        
    except Exception as e:
        print(f'Erro ao analisar XML: {e}')

if __name__ == '__main__':
    check_xml_structure()