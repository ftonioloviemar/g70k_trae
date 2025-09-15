#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar todos os usuários sergio@reis.com no banco
"""

import sqlite3

def check_sergio_users():
    """Verifica todos os usuários sergio@reis.com"""
    
    db_path = "viemar_garantia.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Verificando usuários sergio@reis.com ===")
        
        # Buscar todos os usuários com email sergio@reis.com
        cursor.execute(
            "SELECT id, email, nome, tipo_usuario FROM usuarios WHERE email = ?",
            ("sergio@reis.com",)
        )
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("❌ Nenhum usuário sergio@reis.com encontrado!")
            return
            
        print(f"✅ {len(usuarios)} usuário(s) encontrado(s):")
        for usuario in usuarios:
            user_id, email, nome, tipo = usuario
            print(f"   - ID: {user_id}, Nome: {nome}, Tipo: {tipo}")
            
            # Verificar veículos para cada usuário
            cursor.execute(
                "SELECT id, marca, modelo, placa FROM veiculos WHERE usuario_id = ?",
                (user_id,)
            )
            veiculos = cursor.fetchall()
            
            if veiculos:
                print(f"     Veículos ({len(veiculos)}):")
                for veiculo in veiculos:
                    v_id, marca, modelo, placa = veiculo
                    print(f"       - {marca} {modelo} - {placa} (ID: {v_id})")
            else:
                print("     Nenhum veículo encontrado")
        
        # Verificar se há veículos órfãos
        print("\n=== Verificando veículos órfãos ===")
        cursor.execute(
            "SELECT v.id, v.marca, v.modelo, v.placa, v.usuario_id FROM veiculos v LEFT JOIN usuarios u ON v.usuario_id = u.id WHERE u.id IS NULL"
        )
        orfaos = cursor.fetchall()
        
        if orfaos:
            print(f"❌ {len(orfaos)} veículo(s) órfão(s) encontrado(s):")
            for orfao in orfaos:
                v_id, marca, modelo, placa, user_id = orfao
                print(f"   - {marca} {modelo} - {placa} (ID: {v_id}, usuario_id: {user_id})")
        else:
            print("✅ Nenhum veículo órfão encontrado")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_sergio_users()