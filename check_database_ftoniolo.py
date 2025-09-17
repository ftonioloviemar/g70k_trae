#!/usr/bin/env python3
"""
Script para verificar se o usuário ftoniolo existe no banco SQLite
e comparar com os dados do XML
"""

import sqlite3
import os
from typing import Optional, Dict, Any

def check_ftoniolo_in_database():
    """Verifica se ftoniolo existe no banco de dados"""
    
    db_path = r"c:\python\g70k_trae\data\viemar_garantia.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    print(f"📁 Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela usuarios
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='usuarios'")
        table_structure = cursor.fetchone()
        
        if table_structure:
            print("📋 Estrutura da tabela usuarios:")
            print(table_structure[0])
        else:
            print("❌ Tabela 'usuarios' não encontrada")
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("📋 Tabelas disponíveis:")
            for table in tables:
                print(f"  - {table[0]}")
            return
        
        print("\n" + "="*60)
        
        # Buscar por ftoniolo de várias formas
        search_patterns = [
            ("Email exato", "SELECT * FROM usuarios WHERE email = 'ftoniolo@premiumcar.com.br'"),
            ("Email case-insensitive", "SELECT * FROM usuarios WHERE LOWER(email) LIKE '%ftoniolo%'"),
            ("Nome contém ftoniolo", "SELECT * FROM usuarios WHERE LOWER(nome) LIKE '%ftoniolo%'"),
            ("Nome contém fabio", "SELECT * FROM usuarios WHERE LOWER(nome) LIKE '%fabio%'"),
            ("Email contém premiumcar", "SELECT * FROM usuarios WHERE LOWER(email) LIKE '%premiumcar%'"),
            ("Caspio ID = 5", "SELECT * FROM usuarios WHERE caspio_id = 5")
        ]
        
        found_any = False
        
        for description, query in search_patterns:
            print(f"\n🔍 {description}:")
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results:
                found_any = True
                print(f"  ✅ Encontrados {len(results)} registro(s):")
                
                # Obter nomes das colunas
                cursor.execute("PRAGMA table_info(usuarios)")
                columns = [col[1] for col in cursor.fetchall()]
                
                for result in results:
                    print("  📄 Registro:")
                    for i, value in enumerate(result):
                        print(f"    {columns[i]}: {value}")
            else:
                print("  ❌ Nenhum resultado encontrado")
        
        if not found_any:
            print(f"\n❌ Usuário ftoniolo NÃO foi encontrado no banco de dados!")
            
            # Verificar quantos usuários existem no total
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            total_users = cursor.fetchone()[0]
            print(f"📊 Total de usuários no banco: {total_users}")
            
            # Mostrar alguns usuários de exemplo
            print("\n📋 Primeiros 5 usuários no banco:")
            cursor.execute("SELECT id, nome, email, caspio_id FROM usuarios LIMIT 5")
            results = cursor.fetchall()
            for result in results:
                print(f"  ID: {result[0]}, Nome: {result[1]}, Email: {result[2]}, Caspio_ID: {result[3]}")
            
            # Verificar se há usuários da premiumcar
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE LOWER(email) LIKE '%premiumcar%'")
            premiumcar_count = cursor.fetchone()[0]
            print(f"\n📊 Usuários com email @premiumcar: {premiumcar_count}")
            
            if premiumcar_count > 0:
                cursor.execute("SELECT nome, email, caspio_id FROM usuarios WHERE LOWER(email) LIKE '%premiumcar%'")
                premiumcar_users = cursor.fetchall()
                print("📋 Usuários da PremiumCar no banco:")
                for user in premiumcar_users:
                    print(f"  Nome: {user[0]}, Email: {user[1]}, Caspio_ID: {user[2]}")
        
        # Verificar logs de importação se existir tabela
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%log%'")
        log_tables = cursor.fetchall()
        
        if log_tables:
            print(f"\n📋 Tabelas de log encontradas: {[t[0] for t in log_tables]}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Erro no banco de dados: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    check_ftoniolo_in_database()