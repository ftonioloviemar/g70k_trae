#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar todos os veículos que deveriam estar associados ao usuário sergio@reis.com
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
        
        print("🔍 Verificando usuário sergio@reis.com...")
        
        # Verificar usuário
        cursor.execute("""
            SELECT id, email, nome 
            FROM usuarios 
            WHERE email = 'sergio@reis.com'
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("❌ Usuário sergio@reis.com não encontrado!")
            return
        
        print(f"✅ Encontrados {len(users)} usuário(s) com email sergio@reis.com:")
        for user in users:
            user_id, email, nome = user
            print(f"   - ID: {user_id}, Nome: {nome}")
        
        # Para cada usuário, verificar veículos
        for user in users:
            user_id = user[0]
            print(f"\n🚗 Verificando veículos para usuário ID {user_id}:")
            
            cursor.execute("""
                SELECT id, marca, modelo, ano_modelo, placa, chassi, usuario_id
                FROM veiculos 
                WHERE usuario_id = ?
                ORDER BY id
            """, (user_id,))
            
            vehicles = cursor.fetchall()
            
            if vehicles:
                print(f"   ✅ Encontrados {len(vehicles)} veículo(s):")
                for vehicle in vehicles:
                    v_id, marca, modelo, ano, placa, chassi, u_id = vehicle
                    print(f"      - ID: {v_id}, {marca} {modelo} {ano}, Placa: {placa}, Chassi: {chassi[:10]}...")
            else:
                print(f"   ❌ Nenhum veículo encontrado para usuário ID {user_id}")
        
        # Verificar se existem veículos com referências incorretas
        print("\n🔍 Verificando veículos órfãos ou com problemas de referência...")
        
        cursor.execute("""
            SELECT v.id, v.marca, v.modelo, v.ano_modelo, v.placa, v.usuario_id, u.email
            FROM veiculos v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE u.email IS NULL OR u.email LIKE '%sergio%'
        """)
        
        orphan_vehicles = cursor.fetchall()
        
        if orphan_vehicles:
            print(f"   ⚠️ Encontrados {len(orphan_vehicles)} veículo(s) com problemas:")
            for vehicle in orphan_vehicles:
                v_id, marca, modelo, ano, placa, u_id, email = vehicle
                if email is None:
                    print(f"      - ID: {v_id}, {marca} {modelo} {ano}, Placa: {placa} - ÓRFÃO (usuario_id: {u_id})")
                else:
                    print(f"      - ID: {v_id}, {marca} {modelo} {ano}, Placa: {placa} - Email: {email}")
        else:
            print("   ✅ Nenhum veículo órfão encontrado")
        
        # Verificar total de veículos no sistema
        print("\n📊 Estatísticas gerais:")
        
        cursor.execute("SELECT COUNT(*) FROM veiculos")
        total_vehicles = cursor.fetchone()[0]
        print(f"   - Total de veículos no sistema: {total_vehicles}")
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_users = cursor.fetchone()[0]
        print(f"   - Total de usuários no sistema: {total_users}")
        
        # Verificar se há dados de importação ou migração
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '%import%' OR name LIKE '%temp%' OR name LIKE '%backup%'
        """)
        
        temp_tables = cursor.fetchall()
        if temp_tables:
            print(f"\n🔍 Tabelas temporárias/importação encontradas:")
            for table in temp_tables:
                print(f"   - {table[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco de dados: {e}")
        return

if __name__ == "__main__":
    main()