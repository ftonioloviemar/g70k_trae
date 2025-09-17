#!/usr/bin/env python3
"""
Script para analisar os dados do Caspio e preparar importação.

Este script analisa os arquivos XML do Caspio para entender a estrutura
dos dados de usuários, veículos e produtos/garantias.
"""

import xml.etree.ElementTree as ET
import json
import binascii
from pathlib import Path
from typing import Dict, List, Any

def decode_caspio_password(hex_password: str) -> Dict[str, str]:
    """
    Decodifica a senha do Caspio que está em formato hexadecimal.
    
    Args:
        hex_password: String hexadecimal da senha do Caspio
        
    Returns:
        Dict com informações da senha decodificada
    """
    try:
        # Remove o prefixo 0x se existir
        if hex_password.startswith('0x'):
            hex_password = hex_password[2:]
        
        # Converte de hex para bytes e depois para string
        decoded_bytes = binascii.unhexlify(hex_password)
        decoded_str = decoded_bytes.decode('utf-8')
        
        # Tenta fazer parse do JSON
        password_data = json.loads(decoded_str)
        return password_data
    except Exception as e:
        return {"error": str(e), "raw": hex_password}

def analyze_caspio_xml(xml_file_path: str) -> Dict[str, Any]:
    """
    Analisa um arquivo XML do Caspio e extrai informações das tabelas.
    
    Args:
        xml_file_path: Caminho para o arquivo XML
        
    Returns:
        Dict com informações das tabelas encontradas
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        tables_info = {}
        
        # Procura por todas as tabelas
        for table in root.findall('.//Table'):
            table_name_elem = table.find('Name')
            if table_name_elem is not None:
                table_name = table_name_elem.text
                
                # Analisa a estrutura da tabela
                rows = table.findall('Row')
                table_info = {
                    'name': table_name,
                    'row_count': len(rows),
                    'columns': set(),
                    'sample_data': []
                }
                
                # Analisa algumas linhas de exemplo
                for i, row in enumerate(rows[:3]):  # Pega apenas 3 exemplos
                    row_data = {}
                    for child in row:
                        column_name = child.tag
                        table_info['columns'].add(column_name)
                        
                        # Tratamento especial para senhas
                        if column_name == 'SENHA' and child.text:
                            password_info = decode_caspio_password(child.text)
                            row_data[column_name] = {
                                'raw': child.text[:50] + '...' if len(child.text) > 50 else child.text,
                                'decoded': password_info
                            }
                        else:
                            row_data[column_name] = child.text
                    
                    table_info['sample_data'].append(row_data)
                
                # Converte set para list para serialização JSON
                table_info['columns'] = list(table_info['columns'])
                tables_info[table_name] = table_info
        
        return tables_info
    
    except Exception as e:
        return {"error": str(e)}

def main():
    """
    Função principal para analisar os dados do Caspio.
    """
    caspio_dir = Path("docs/context/caspio_viemar")
    tables_xml = caspio_dir / "Tables_2025-Sep-08_1152.xml"
    
    if not tables_xml.exists():
        print(f"Arquivo não encontrado: {tables_xml}")
        return
    
    print("Analisando dados do Caspio...")
    print(f"Arquivo: {tables_xml}")
    print("=" * 50)
    
    # Analisa o arquivo XML
    tables_info = analyze_caspio_xml(str(tables_xml))
    
    if "error" in tables_info:
        print(f"Erro ao analisar XML: {tables_info['error']}")
        return
    
    # Exibe informações das tabelas
    for table_name, info in tables_info.items():
        print(f"\nTabela: {table_name}")
        print(f"Registros: {info['row_count']}")
        print(f"Colunas: {', '.join(info['columns'])}")
        
        if info['sample_data']:
            print("\nExemplo de dados:")
            for i, sample in enumerate(info['sample_data'][:1]):  # Mostra apenas 1 exemplo
                print(f"  Registro {i+1}:")
                for col, value in sample.items():
                    if isinstance(value, dict) and 'decoded' in value:
                        print(f"    {col}: {value['decoded']}")
                    else:
                        display_value = str(value)[:100] + '...' if value and len(str(value)) > 100 else value
                        print(f"    {col}: {display_value}")
    
    # Salva análise em arquivo JSON
    output_file = caspio_dir / "analysis_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tables_info, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nAnálise salva em: {output_file}")
    print("\nResumo das tabelas encontradas:")
    for table_name, info in tables_info.items():
        print(f"- {table_name}: {info['row_count']} registros")

if __name__ == "__main__":
    main()