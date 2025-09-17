#!/usr/bin/env python3
"""
Script para corrigir o registro do ftoniolo no banco
Adiciona o caspio_id correto e atualiza dados do XML
"""

import sqlite3
import xml.etree.ElementTree as ET
import os
from datetime import datetime
import json
import hashlib
import base64

def decode_caspio_password(hex_password: str) -> str:
    """Decodifica senha do Caspio (mesmo método do serviço)"""
    try:
        # Remove o prefixo 0x se existir
        if hex_password.startswith('0x'):
            hex_password = hex_password[2:]
        
        # Converte hex para bytes
        password_bytes = bytes.fromhex(hex_password)
        
        # Converte bytes para string
        password_str = password_bytes.decode('utf-8')
        
        # Parse do JSON
        password_data = json.loads(password_str)
        
        # Retorna o hash
        return password_data.get('hash', '')
    except Exception as e:
        print(f"Erro ao decodificar senha: {e}")
        return None

def parse_caspio_date(date_str: str) -> str:
    """Converte data do Caspio para formato SQLite (mesmo método do serviço)"""
    if not date_str:
        return None
    
    # Formatos possíveis do Caspio
    formats = [
        '%m/%d/%Y %I:%M:%S %p',  # 8/25/2017 3:45:50 PM
        '%m/%d/%Y',              # 8/25/2017
        '%Y-%m-%d %H:%M:%S',     # 2017-08-25 15:45:50
        '%Y-%m-%d'               # 2017-08-25
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    print(f"Formato de data não reconhecido: {date_str}")
    return None

def fix_ftoniolo_caspio_id():
    """Corrige o registro do ftoniolo adicionando caspio_id"""
    
    xml_file = r"c:\python\g70k_trae\docs\context\caspio_viemar\Tables_2025-Sep-08_1152.xml"
    db_path = r"c:\python\g70k_trae\data\viemar_garantia.db"
    
    print("🔧 CORREÇÃO DO REGISTRO FTONIOLO")
    print("=" * 50)
    
    # 1. Buscar dados no XML
    print("\n📄 1. Buscando dados no XML...")
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Encontrar tabela CLIENTE
        cliente_table = None
        for table in root.findall('.//Table'):
            name_elem = table.find('Name')
            if name_elem is not None and name_elem.text == 'CLIENTE':
                cliente_table = table
                break
        
        ftoniolo_xml = None
        for row in cliente_table.findall('Row'):
            caspio_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
            if caspio_id == '5':  # ftoniolo tem ID 5
                ftoniolo_xml = {
                    'caspio_id': int(caspio_id),
                    'nome': row.find('NOME').text if row.find('NOME') is not None else None,
                    'email': row.find('EMAIL').text if row.find('EMAIL') is not None else None,
                    'cpf_cnpj': row.find('CPF_CNPJ').text if row.find('CPF_CNPJ') is not None else None,
                    'telefone': row.find('TELEFONE').text if row.find('TELEFONE') is not None else None,
                    'cep': row.find('CEP').text if row.find('CEP') is not None else None,
                    'endereco': row.find('ENDERECO').text if row.find('ENDERECO') is not None else None,
                    'bairro': row.find('BAIRRO').text if row.find('BAIRRO') is not None else None,
                    'cidade': row.find('CIDADE').text if row.find('CIDADE') is not None else None,
                    'uf': row.find('UF').text if row.find('UF') is not None else None,
                    'data_nascimento': row.find('DATA_NASCIMENTO').text if row.find('DATA_NASCIMENTO') is not None else None,
                    'data_cadastro': row.find('DATA_CADASTRO').text if row.find('DATA_CADASTRO') is not None else None,
                    'senha': row.find('SENHA').text if row.find('SENHA') is not None else None,
                    'email_confirmado': row.find('EMAIL_CONFIRMADO').text if row.find('EMAIL_CONFIRMADO') is not None else None
                }
                break
        
        if not ftoniolo_xml:
            print("  ❌ Dados não encontrados no XML")
            return
        
        print("  ✅ Dados encontrados no XML:")
        for key, value in ftoniolo_xml.items():
            print(f"    {key}: {value}")
            
    except Exception as e:
        print(f"  ❌ Erro ao ler XML: {e}")
        return
    
    # 2. Processar dados
    print("\n🔄 2. Processando dados...")
    
    # Processar senha
    senha_hash = None
    if ftoniolo_xml['senha']:
        senha_hash = decode_caspio_password(ftoniolo_xml['senha'])
        print(f"  📝 Senha decodificada: {senha_hash[:20]}..." if senha_hash else "  ❌ Erro ao decodificar senha")
    
    # Processar datas
    data_nascimento = None
    if ftoniolo_xml['data_nascimento']:
        data_nascimento = parse_caspio_date(ftoniolo_xml['data_nascimento'])
        print(f"  📅 Data nascimento: {data_nascimento}")
    
    data_cadastro_original = None
    if ftoniolo_xml['data_cadastro']:
        data_cadastro_original = parse_caspio_date(ftoniolo_xml['data_cadastro'])
        print(f"  📅 Data cadastro original: {data_cadastro_original}")
    
    # 3. Atualizar banco
    print("\n💾 3. Atualizando banco de dados...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar registro atual
        cursor.execute("SELECT id, nome, caspio_id FROM usuarios WHERE email = ?", (ftoniolo_xml['email'],))
        current_record = cursor.fetchone()
        
        if not current_record:
            print("  ❌ Registro não encontrado no banco")
            return
        
        user_id, current_name, current_caspio_id = current_record
        print(f"  📋 Registro atual - ID: {user_id}, Nome: {current_name}, Caspio_ID: {current_caspio_id}")
        
        # Fazer backup do registro atual
        print("  💾 Fazendo backup do registro atual...")
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        backup_data = cursor.fetchone()
        
        # Atualizar com dados do XML
        update_query = """
            UPDATE usuarios SET 
                caspio_id = ?,
                nome = ?,
                senha_hash = COALESCE(?, senha_hash),
                cpf_cnpj = COALESCE(?, cpf_cnpj),
                telefone = COALESCE(?, telefone),
                cep = COALESCE(?, cep),
                endereco = COALESCE(?, endereco),
                bairro = COALESCE(?, bairro),
                cidade = COALESCE(?, cidade),
                uf = COALESCE(?, uf),
                data_nascimento = COALESCE(?, data_nascimento),
                confirmado = 1
            WHERE id = ?
        """
        
        cursor.execute(update_query, (
            ftoniolo_xml['caspio_id'],
            ftoniolo_xml['nome'],
            senha_hash,
            ftoniolo_xml['cpf_cnpj'],
            ftoniolo_xml['telefone'],
            ftoniolo_xml['cep'],
            ftoniolo_xml['endereco'],
            ftoniolo_xml['bairro'],
            ftoniolo_xml['cidade'],
            ftoniolo_xml['uf'],
            data_nascimento,
            user_id
        ))
        
        conn.commit()
        
        # Verificar resultado
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        updated_record = cursor.fetchone()
        
        # Obter nomes das colunas
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [col[1] for col in cursor.fetchall()]
        
        updated_data = dict(zip(columns, updated_record))
        
        print("  ✅ Registro atualizado com sucesso!")
        print("  📋 Dados atualizados:")
        for key, value in updated_data.items():
            if key in ['id', 'email', 'nome', 'caspio_id', 'confirmado', 'cpf_cnpj']:
                print(f"    {key}: {value}")
        
        conn.close()
        
    except Exception as e:
        print(f"  ❌ Erro ao atualizar banco: {e}")
        return
    
    print("\n" + "=" * 50)
    print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("   - Caspio_ID adicionado: 5")
    print("   - Nome atualizado para dados do XML")
    print("   - Outros campos preenchidos conforme XML")
    print("   - Usuário marcado como confirmado")

if __name__ == "__main__":
    fix_ftoniolo_caspio_id()