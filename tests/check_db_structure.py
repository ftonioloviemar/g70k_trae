#!/usr/bin/env python3
"""
Script para verificar a estrutura do banco de dados
"""

import sqlite3
from pathlib import Path

def check_database_structure():
    """Verifica a estrutura do banco de dados"""
    
    # Caminho do banco de dados
    db_path = Path("data/viemar_garantia.db")
    if not db_path.exists():
        db_path = Path("viemar_garantia.db")
    
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 Tabelas encontradas:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Mostrar estrutura da tabela
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"    Colunas:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"      {col_name} ({col_type})")
            print()
        
        # Procurar por usuários
        print("🔍 Procurando por usuários com 'sergio':")
        for table in tables:
            table_name = table[0]
            try:
                # Tentar encontrar colunas que possam conter email
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                email_columns = [col[1] for col in columns if 'email' in col[1].lower()]
                
                if email_columns:
                    for email_col in email_columns:
                        cursor.execute(f"SELECT * FROM {table_name} WHERE {email_col} LIKE '%sergio%';")
                        users = cursor.fetchall()
                        
                        if users:
                            print(f"  Tabela {table_name}, coluna {email_col}:")
                            for user in users:
                                print(f"    {user}")
            except Exception as e:
                continue
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Verificando estrutura do banco de dados...")
    check_database_structure()