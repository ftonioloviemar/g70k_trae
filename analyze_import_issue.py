#!/usr/bin/env python3
"""
Script para analisar o problema de importação do usuário ftoniolo
Compara dados do XML com dados do banco e identifica conflitos
"""

import xml.etree.ElementTree as ET
import sqlite3
import os
from datetime import datetime

def analyze_ftoniolo_import_issue():
    """Analisa o problema de importação do ftoniolo"""
    
    xml_file = r"c:\python\g70k_trae\docs\context\caspio_viemar\Tables_2025-Sep-08_1152.xml"
    db_path = r"c:\python\g70k_trae\data\viemar_garantia.db"
    
    print("🔍 ANÁLISE DO PROBLEMA DE IMPORTAÇÃO - FTONIOLO")
    print("=" * 60)
    
    # 1. Dados do XML
    print("\n📄 1. DADOS NO XML:")
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
            if caspio_id == '5':  # Sabemos que ftoniolo tem ID 5
                ftoniolo_xml = {
                    'caspio_id': caspio_id,
                    'nome': row.find('NOME').text if row.find('NOME') is not None else None,
                    'email': row.find('EMAIL').text if row.find('EMAIL') is not None else None,
                    'cpf_cnpj': row.find('CPF_CNPJ').text if row.find('CPF_CNPJ') is not None else None,
                    'telefone': row.find('TELEFONE').text if row.find('TELEFONE') is not None else None,
                    'data_nascimento': row.find('DATA_NASCIMENTO').text if row.find('DATA_NASCIMENTO') is not None else None,
                    'data_cadastro': row.find('DATA_CADASTRO').text if row.find('DATA_CADASTRO') is not None else None,
                    'senha': row.find('SENHA').text if row.find('SENHA') is not None else None,
                    'email_confirmado': row.find('EMAIL_CONFIRMADO').text if row.find('EMAIL_CONFIRMADO') is not None else None
                }
                break
        
        if ftoniolo_xml:
            print("  ✅ Encontrado no XML:")
            for key, value in ftoniolo_xml.items():
                print(f"    {key}: {value}")
        else:
            print("  ❌ NÃO encontrado no XML")
            
    except Exception as e:
        print(f"  ❌ Erro ao ler XML: {e}")
        ftoniolo_xml = None
    
    # 2. Dados do Banco
    print("\n💾 2. DADOS NO BANCO:")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar por email
        cursor.execute("SELECT * FROM usuarios WHERE email = 'ftoniolo@premiumcar.com.br'")
        result = cursor.fetchone()
        
        if result:
            # Obter nomes das colunas
            cursor.execute("PRAGMA table_info(usuarios)")
            columns = [col[1] for col in cursor.fetchall()]
            
            ftoniolo_db = dict(zip(columns, result))
            
            print("  ✅ Encontrado no banco:")
            for key, value in ftoniolo_db.items():
                print(f"    {key}: {value}")
        else:
            print("  ❌ NÃO encontrado no banco")
            ftoniolo_db = None
        
        conn.close()
        
    except Exception as e:
        print(f"  ❌ Erro ao ler banco: {e}")
        ftoniolo_db = None
    
    # 3. Análise comparativa
    print("\n🔍 3. ANÁLISE COMPARATIVA:")
    
    if ftoniolo_xml and ftoniolo_db:
        print("  📊 Comparação de dados:")
        
        # Comparar campos principais
        comparisons = [
            ('Email', ftoniolo_xml['email'], ftoniolo_db['email']),
            ('Nome', ftoniolo_xml['nome'], ftoniolo_db['nome']),
            ('Caspio ID', ftoniolo_xml['caspio_id'], ftoniolo_db['caspio_id']),
            ('CPF/CNPJ', ftoniolo_xml['cpf_cnpj'], ftoniolo_db['cpf_cnpj']),
            ('Data Nascimento', ftoniolo_xml['data_nascimento'], ftoniolo_db['data_nascimento']),
        ]
        
        conflicts = []
        for field, xml_val, db_val in comparisons:
            if str(xml_val) != str(db_val):
                conflicts.append(field)
                print(f"    ⚠️  {field}:")
                print(f"       XML: {xml_val}")
                print(f"       DB:  {db_val}")
            else:
                print(f"    ✅ {field}: {xml_val}")
        
        if conflicts:
            print(f"\n  ⚠️  CONFLITOS ENCONTRADOS: {', '.join(conflicts)}")
        else:
            print("\n  ✅ Todos os campos principais coincidem")
    
    # 4. Verificar processo de importação
    print("\n🔧 4. ANÁLISE DO PROCESSO DE IMPORTAÇÃO:")
    
    if ftoniolo_db and ftoniolo_db['caspio_id'] is None:
        print("  ⚠️  PROBLEMA IDENTIFICADO:")
        print("     - Usuário existe no banco mas SEM caspio_id")
        print("     - Isso indica que foi criado manualmente ou por outro processo")
        print("     - A importação do Caspio pula usuários existentes (mesmo email)")
        
        print("\n  📋 POSSÍVEIS CAUSAS:")
        print("     1. Usuário foi criado manualmente antes da importação")
        print("     2. Importação anterior falhou parcialmente")
        print("     3. Processo de verificação de duplicatas está impedindo a atualização")
        
        print("\n  🔧 SOLUÇÕES POSSÍVEIS:")
        print("     1. Atualizar o registro existente com o caspio_id")
        print("     2. Remover o registro e reimportar")
        print("     3. Modificar o processo de importação para atualizar registros existentes")
    
    # 5. Verificar outros usuários com mesmo problema
    print("\n📊 5. VERIFICAÇÃO DE OUTROS CASOS SIMILARES:")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Usuários sem caspio_id
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE caspio_id IS NULL")
        sem_caspio_id = cursor.fetchone()[0]
        
        # Total de usuários
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]
        
        print(f"  📊 Usuários sem caspio_id: {sem_caspio_id}/{total_usuarios}")
        
        if sem_caspio_id > 0:
            print("  📋 Primeiros 5 usuários sem caspio_id:")
            cursor.execute("SELECT id, nome, email, data_cadastro FROM usuarios WHERE caspio_id IS NULL LIMIT 5")
            results = cursor.fetchall()
            for result in results:
                print(f"    ID: {result[0]}, Nome: {result[1]}, Email: {result[2]}, Data: {result[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"  ❌ Erro ao verificar outros casos: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSÃO: Usuário ftoniolo existe no XML mas não foi importado")
    print("   devido a conflito com registro existente sem caspio_id")

if __name__ == "__main__":
    analyze_ftoniolo_import_issue()