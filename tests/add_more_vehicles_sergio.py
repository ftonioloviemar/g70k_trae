#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar mais veículos para o usuário sergio@reis.com
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

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
        
        user = cursor.fetchone()
        
        if not user:
            print("❌ Usuário sergio@reis.com não encontrado!")
            return
        
        user_id, email, nome = user
        print(f"✅ Usuário encontrado: ID {user_id}, Nome: {nome}")
        
        # Verificar veículos atuais
        cursor.execute("""
            SELECT COUNT(*) FROM veiculos WHERE usuario_id = ?
        """, (user_id,))
        
        current_count = cursor.fetchone()[0]
        print(f"📊 Veículos atuais: {current_count}")
        
        # Lista de veículos para adicionar
        vehicles_to_add = [
            {
                'marca': 'Honda',
                'modelo': 'Civic',
                'ano_modelo': '2019',
                'placa': 'DEF5678',
                'chassi': '19XFC2F59KE000001',
                'cor': 'Azul'
            },
            {
                'marca': 'Volkswagen',
                'modelo': 'Jetta',
                'ano_modelo': '2021',
                'placa': 'GHI9012',
                'chassi': '3VWD17AJ5MM000002',
                'cor': 'Branco'
            },
            {
                'marca': 'Ford',
                'modelo': 'Focus',
                'ano_modelo': '2018',
                'placa': 'JKL3456',
                'chassi': '1FADP3K20JL000003',
                'cor': 'Vermelho'
            },
            {
                'marca': 'Chevrolet',
                'modelo': 'Cruze',
                'ano_modelo': '2022',
                'placa': 'MNO7890',
                'chassi': '1G1BE5SM4N7000004',
                'cor': 'Preto'
            }
        ]
        
        print(f"\n🚗 Adicionando {len(vehicles_to_add)} veículos para {nome}...")
        
        current_time = datetime.now().isoformat()
        
        for i, vehicle in enumerate(vehicles_to_add, 1):
            # Verificar se a placa já existe
            cursor.execute("""
                SELECT id FROM veiculos WHERE placa = ?
            """, (vehicle['placa'],))
            
            existing = cursor.fetchone()
            
            if existing:
                print(f"   ⚠️ Veículo {i}: Placa {vehicle['placa']} já existe (ID: {existing[0]})")
                continue
            
            # Inserir veículo
            cursor.execute("""
                INSERT INTO veiculos (
                    usuario_id, marca, modelo, ano_modelo, placa, chassi, cor,
                    data_cadastro, data_atualizacao, ativo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                vehicle['marca'],
                vehicle['modelo'],
                vehicle['ano_modelo'],
                vehicle['placa'],
                vehicle['chassi'],
                vehicle['cor'],
                current_time,
                current_time,
                1
            ))
            
            vehicle_id = cursor.lastrowid
            print(f"   ✅ Veículo {i}: {vehicle['marca']} {vehicle['modelo']} {vehicle['ano_modelo']} (ID: {vehicle_id}, Placa: {vehicle['placa']})")
        
        # Confirmar alterações
        conn.commit()
        
        # Verificar total final
        cursor.execute("""
            SELECT COUNT(*) FROM veiculos WHERE usuario_id = ?
        """, (user_id,))
        
        final_count = cursor.fetchone()[0]
        print(f"\n📊 Total de veículos após adição: {final_count}")
        
        # Listar todos os veículos do usuário
        print(f"\n🚗 Todos os veículos de {nome}:")
        
        cursor.execute("""
            SELECT id, marca, modelo, ano_modelo, placa, cor
            FROM veiculos 
            WHERE usuario_id = ?
            ORDER BY id
        """, (user_id,))
        
        all_vehicles = cursor.fetchall()
        
        for vehicle in all_vehicles:
            v_id, marca, modelo, ano, placa, cor = vehicle
            print(f"   - ID: {v_id}, {marca} {modelo} {ano}, Placa: {placa}, Cor: {cor}")
        
        conn.close()
        print(f"\n✅ Processo concluído! {nome} agora tem {final_count} veículo(s).")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar veículos: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()