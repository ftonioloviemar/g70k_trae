#!/usr/bin/env python3
"""Script para debugar os campos do XML que parecem estar vazios"""

import xml.etree.ElementTree as ET
import os

def debug_xml_fields():
    """Debug dos campos do XML"""
    xml_path = r'c:\python\g70k_trae\docs\context\caspio_viemar\Tables_2025-Sep-08_1152.xml'
    
    if not os.path.exists(xml_path):
        print('Arquivo XML não encontrado!')
        return
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Encontrar a tabela CLIENTE
        cliente_table = None
        for table in root.findall('.//Table'):
            name_elem = table.find('Name')
            if name_elem is not None and name_elem.text == 'CLIENTE':
                cliente_table = table
                break
        
        if not cliente_table:
            print('Tabela CLIENTE não encontrada!')
            return
        
        print(f'Tabela CLIENTE encontrada com {len(cliente_table.findall("Row"))} registros')
        
        # Analisar o primeiro registro em detalhes
        first_row = cliente_table.find('Row')
        if first_row:
            print('\n=== ANÁLISE DETALHADA DO PRIMEIRO REGISTRO ===')
            print(f'Número de campos (Field): {len(first_row.findall("Field"))}')
            
            for i, field in enumerate(first_row.findall('Field')):
                field_name = field.get('name')
                field_text = field.text
                field_attribs = field.attrib
                
                print(f'\nCampo {i+1}:')
                print(f'  Nome: {field_name}')
                print(f'  Texto: {repr(field_text)}')
                print(f'  Atributos: {field_attribs}')
                
                # Verificar se tem elementos filhos
                children = list(field)
                if children:
                    print(f'  Elementos filhos: {len(children)}')
                    for child in children:
                        print(f'    - {child.tag}: {repr(child.text)}')
        
        # Verificar se os dados estão em uma estrutura diferente
        print('\n=== VERIFICANDO ESTRUTURA ALTERNATIVA ===')
        
        # Talvez os dados estejam diretamente como elementos filhos do Row
        if first_row:
            print('Elementos filhos diretos do Row:')
            for child in first_row:
                if child.tag != 'Field':
                    print(f'  {child.tag}: {repr(child.text)}')
        
        # Verificar se há dados em algum lugar
        print('\n=== PROCURANDO DADOS EM QUALQUER LUGAR ===')
        
        # Procurar por qualquer elemento que contenha "ftoniolo"
        def search_element(element, path=""):
            if element.text and 'ftoniolo' in element.text.lower():
                print(f'Encontrado "ftoniolo" em {path}/{element.tag}: {element.text}')
            
            for child in element:
                search_element(child, f"{path}/{element.tag}")
        
        search_element(root)
        
        # Verificar se o XML está corrompido ou em formato diferente
        print('\n=== VERIFICANDO FORMATO DO XML ===')
        
        # Ler as primeiras linhas do arquivo como texto
        with open(xml_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            print('Primeiras 10 linhas do arquivo:')
            for i, line in enumerate(lines, 1):
                print(f'{i:2d}: {line.rstrip()}')
        
    except Exception as e:
        print(f'Erro ao analisar XML: {e}')

if __name__ == '__main__':
    debug_xml_fields()