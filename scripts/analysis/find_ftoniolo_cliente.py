#!/usr/bin/env python3
"""Script para encontrar ftoniolo especificamente na tabela CLIENTE"""

import xml.etree.ElementTree as ET
import os

def find_ftoniolo_in_cliente():
    """Encontra ftoniolo na tabela CLIENTE"""
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
        
        # Verificar estrutura do primeiro registro
        first_row = cliente_table.find('Row')
        if first_row:
            print('\nCampos disponíveis na tabela CLIENTE:')
            for field in first_row.findall('Field'):
                field_name = field.get('name')
                print(f'  - {field_name}')
        
        # Procurar por ftoniolo
        print('\nProcurando por ftoniolo...')
        found_count = 0
        
        for i, row in enumerate(cliente_table.findall('Row')):
            # Criar dicionário com todos os campos
            record = {}
            for field in row.findall('Field'):
                field_name = field.get('name')
                field_value = field.text if field.text else ''
                record[field_name] = field_value
            
            # Verificar se tem ftoniolo em qualquer campo
            has_ftoniolo = False
            for field_name, field_value in record.items():
                if 'ftoniolo' in field_value.lower():
                    has_ftoniolo = True
                    break
            
            if has_ftoniolo:
                found_count += 1
                print(f'\n=== REGISTRO {i+1} COM FTONIOLO ===')
                for field_name, field_value in record.items():
                    if field_value:  # Só mostra campos não vazios
                        print(f'{field_name}: {field_value}')
                
                # Verificar campos críticos para importação
                email = record.get('EMAIL', '')
                nome = record.get('NOME', '')
                caspio_id = record.get('ID_CLIENTE', '')
                
                print(f'\n=== ANÁLISE PARA IMPORTAÇÃO ===')
                print(f'ID_CLIENTE: {caspio_id}')
                print(f'EMAIL: {email}')
                print(f'NOME: {nome}')
                print(f'EMAIL válido: {bool(email and "@" in email)}')
                print(f'NOME presente: {bool(nome)}')
                print(f'ID_CLIENTE presente: {bool(caspio_id)}')
        
        if found_count == 0:
            print('Nenhum registro com "ftoniolo" encontrado na tabela CLIENTE!')
            
            # Vamos verificar alguns registros aleatórios para debug
            print('\nVerificando alguns registros para debug...')
            rows = cliente_table.findall('Row')
            for i in [0, 100, 500, 1000, 1500, 2000]:
                if i < len(rows):
                    row = rows[i]
                    record = {}
                    for field in row.findall('Field'):
                        field_name = field.get('name')
                        field_value = field.text if field.text else ''
                        record[field_name] = field_value
                    
                    email = record.get('EMAIL', '')
                    nome = record.get('NOME', '')
                    print(f'Registro {i+1}: EMAIL={email}, NOME={nome}')
        
    except Exception as e:
        print(f'Erro ao analisar XML: {e}')

if __name__ == '__main__':
    find_ftoniolo_in_cliente()