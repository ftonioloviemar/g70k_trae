#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar se existem mais veículos para sergio@reis.com em outras tabelas ou estruturas
"""

import sqlite3
import sys
from pathlib import Path

def main():
    db_path = Path("viemar_garantia.db")
    
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Investigando estrutura completa do banco de dados...")
        
        # Listar todas as tabelas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Tabelas encontradas ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            
            # Contar registros em cada tabela
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"   - {table_name}: {count} registros")
            
            # Se a tabela contém 'veiculo' ou 'vehicle' no nome, investigar mais
            if 'veiculo' in table_name.lower() or 'vehicle' in table_name.lower():
                print(f"     🔍 Investigando tabela {table_name}:")
                
                # Mostrar estrutura da tabela
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"       Colunas: {[col[1] for col in columns]}")
                
                # Mostrar alguns registros
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                records = cursor.fetchall()
                if records:
                    print(f"       Primeiros registros:")
                    for i, record in enumerate(records, 1):
                        print(f"         {i}: {record}")
        
        print("\n🔍 Procurando por referências a 'sergio' em todas as tabelas...")
        
        # Procurar por 'sergio' em todas as tabelas
        for table in tables:
            table_name = table[0]
            
            try:
                # Obter colunas da tabela
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Procurar em colunas de texto
                text_columns = [col[1] for col in columns if col[2].upper() in ['TEXT', 'VARCHAR']]
                
                for column in text_columns:
                    cursor.execute(f"""
                        SELECT * FROM {table_name} 
                        WHERE LOWER({column}) LIKE '%sergio%'
                        LIMIT 10
                    """)
                    
                    results = cursor.fetchall()
                    if results:
                        print(f"\n   ✅ Encontrado 'sergio' em {table_name}.{column}:")
                        for result in results:
                            print(f"      {result}")
                            
            except Exception as e:
                # Ignorar erros de consulta em tabelas específicas
                pass
        
        print("\n🔍 Verificando se existem garantias para sergio@reis.com...")
        
        # Verificar tabela de garantias
        cursor.execute("""
            SELECT g.*, u.email 
            FROM garantias g
            JOIN usuarios u ON g.usuario_id = u.id
            WHERE u.email = 'sergio@reis.com'
        """)
        
        garantias = cursor.fetchall()
        if garantias:
            print(f"   ✅ Encontradas {len(garantias)} garantia(s) para sergio@reis.com:")
            for garantia in garantias:
                print(f"      {garantia}")
        else:
            print("   ❌ Nenhuma garantia encontrada para sergio@reis.com")
        
        print("\n🔍 Verificando histórico de veículos ou logs...")
        
        # Procurar por tabelas de log ou histórico
        log_tables = [t[0] for t in tables if 'log' in t[0].lower() or 'hist' in t[0].lower() or 'audit' in t[0].lower()]
        
        if log_tables:
            print(f"   📋 Tabelas de log/histórico encontradas: {log_tables}")
            for log_table in log_tables:
                try:
                    cursor.execute(f"SELECT * FROM {log_table} LIMIT 5")
                    records = cursor.fetchall()
                    if records:
                        print(f"      {log_table}: {len(records)} registros (mostrando 5)")
                        for record in records:
                            print(f"        {record}")
                except Exception as e:
                    print(f"      Erro ao consultar {log_table}: {e}")
        else:
            print("   ❌ Nenhuma tabela de log/histórico encontrada")
        
        print("\n🔍 Verificando se há dados em arquivos de backup ou importação...")
        
        # Verificar se existem arquivos relacionados
        import os
        current_dir = Path(".")
        
        backup_files = list(current_dir.glob("*.db*")) + list(current_dir.glob("*backup*")) + list(current_dir.glob("*import*"))
        
        if backup_files:
            print(f"   📁 Arquivos relacionados encontrados:")
            for file in backup_files:
                print(f"      - {file.name} ({file.stat().st_size} bytes)")
        else:
            print("   ❌ Nenhum arquivo de backup/importação encontrado")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao investigar banco de dados: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()