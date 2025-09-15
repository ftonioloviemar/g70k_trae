#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar um veículo de teste para sergio@reis.com
"""

import sqlite3
from datetime import datetime

def create_sergio_vehicle():
    """Cria um veículo de teste para sergio@reis.com"""
    
    db_path = "viemar_garantia.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Criando veículo para sergio@reis.com ===")
        
        # 1. Verificar se o usuário existe
        cursor.execute(
            "SELECT id, nome FROM usuarios WHERE email = ?",
            ("sergio@reis.com",)
        )
        usuario = cursor.fetchone()
        
        if not usuario:
            print("❌ Usuário sergio@reis.com não encontrado!")
            return False
            
        user_id, nome = usuario
        print(f"✅ Usuário encontrado: {nome} (ID: {user_id})")
        
        # 2. Verificar se já tem veículos
        cursor.execute(
            "SELECT COUNT(*) FROM veiculos WHERE usuario_id = ?",
            (user_id,)
        )
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Usuário já possui {count} veículo(s)")
            return True
            
        # 3. Criar veículo de teste
        print("\n📝 Criando veículo de teste...")
        
        agora = datetime.now().isoformat()
        
        cursor.execute(
            """
            INSERT INTO veiculos (
                usuario_id, marca, modelo, ano_modelo, placa, 
                data_cadastro, data_atualizacao, ativo, cor, chassi
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                "Toyota",
                "Corolla",
                "2020",
                "ABC1234",
                agora,
                agora,
                True,
                "Prata",
                "9BWZZZ377VT004251"
            )
        )
        
        veiculo_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Veículo criado com sucesso! ID: {veiculo_id}")
        print("   - Marca: Toyota")
        print("   - Modelo: Corolla")
        print("   - Ano: 2020")
        print("   - Placa: ABC1234")
        
        # 4. Verificar se foi criado corretamente
        cursor.execute(
            "SELECT id, marca, modelo, ano_modelo, placa FROM veiculos WHERE usuario_id = ?",
            (user_id,)
        )
        veiculos = cursor.fetchall()
        
        print(f"\n✅ Verificação: {len(veiculos)} veículo(s) encontrado(s) para o usuário")
        for veiculo in veiculos:
            v_id, marca, modelo, ano, placa = veiculo
            print(f"   - {marca} {modelo} {ano} - {placa} (ID: {v_id})")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Iniciando criação de veículo para sergio@reis.com...")
    
    sucesso = create_sergio_vehicle()
    
    if sucesso:
        print("\n🎉 Veículo criado com sucesso!")
    else:
        print("\n❌ Falha ao criar veículo.")