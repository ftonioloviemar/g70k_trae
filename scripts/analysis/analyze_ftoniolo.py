#!/usr/bin/env python3
"""Script para analisar o registro do ftoniolo no XML do Caspio"""

import xml.etree.ElementTree as ET
import os

def analyze_ftoniolo_record():
    """Analisa o registro do ftoniolo no XML do Caspio"""
    xml_path = r'c:\python\g70k_trae\docs\context\caspio_viemar\Tables_2025-Sep-08_1152.xml'
    
    if not os.path.exists(xml_path):
        print('Arquivo XML não encontrado!')
        return
    
    try:
        # Carregar e analisar o XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Encontrar a tabela CLIENTE
        cliente_table = None
        for table in root.findall('Table'):
            if table.get('name') == 'CLIENTE':
                cliente_table = table
                break
        
        if not cliente_table:
            print('Tabela CLIENTE não encontrada!')
            return
        
        print('Analisando registros do ftoniolo no XML do Caspio...')
        
        for i, row in enumerate(cliente_table.findall('Row')):
            record = {}
            for field in row.findall('Field'):
                field_name = field.get('name')
                field_value = field.text if field.text else ''
                record[field_name] = field_value
            
            # Verificar se é o registro do ftoniolo
            if 'ftoniolo' in record.get('EMAIL', '').lower():
                print(f'\n=== REGISTRO {i+1} - FTONIOLO ===')
                for key, value in record.items():
                    print(f'{key}: {repr(value)}')
                
                # Verificar campos críticos para importação
                print(f'\n=== ANÁLISE DOS CAMPOS CRÍTICOS ===')
                email = record.get('EMAIL', '')
                nome = record.get('NOME', '')
                email_confirmado = record.get('EMAIL_CONFIRMADO', '')
                senha = record.get('SENHA', '')
                data_cadastro = record.get('DATA_CADASTRO', '')
                
                print(f'EMAIL válido: {bool(email and "@" in email)}')
                print(f'NOME presente: {bool(nome)}')
                print(f'EMAIL_CONFIRMADO: {email_confirmado}')
                print(f'SENHA presente: {bool(senha)}')
                print(f'DATA_CADASTRO: {data_cadastro}')
                
                # Verificar possíveis problemas
                print(f'\n=== POSSÍVEIS PROBLEMAS ===')
                if not email or '@' not in email:
                    print('- EMAIL inválido ou ausente')
                if not nome:
                    print('- NOME ausente')
                if not senha:
                    print('- SENHA ausente')
                if email_confirmado == '0' or email_confirmado == 'false':
                    print('- EMAIL não confirmado')
                
                return record
        
        print('Registro do ftoniolo não encontrado!')
        return None
        
    except Exception as e:
        print(f'Erro ao analisar XML: {e}')
        return None

if __name__ == '__main__':
    analyze_ftoniolo_record()