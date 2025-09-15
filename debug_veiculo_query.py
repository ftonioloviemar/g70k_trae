#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar a consulta de veículos na interface web
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
        
        print("🔍 Debugando consulta de veículos para sergio@reis.com...")
        
        # Obter ID do usuário
        cursor.execute("""
            SELECT id FROM usuarios WHERE email = 'sergio@reis.com'
        """)
        
        user_result = cursor.fetchone()
        if not user_result:
            print("❌ Usuário não encontrado!")
            return
        
        user_id = user_result[0]
        print(f"✅ Usuário ID: {user_id}")
        
        # Executar a mesma consulta que está na rota
        print("\n🔍 Executando consulta da rota (ORDER BY data_cadastro DESC):")
        cursor.execute("""
            SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
            FROM veiculos 
            WHERE usuario_id = ? 
            ORDER BY data_cadastro DESC
        """, (user_id,))
        
        veiculos_rota = cursor.fetchall()
        
        print(f"   Resultados: {len(veiculos_rota)} veículo(s)")
        for i, v in enumerate(veiculos_rota, 1):
            v_id, marca, modelo, ano, placa, cor, chassi, data_cadastro, ativo = v
            print(f"   {i}. ID: {v_id}, {marca} {modelo} {ano}, Placa: {placa}, Ativo: {ativo}, Data: {data_cadastro}")
        
        # Executar consulta simples para comparar
        print("\n🔍 Executando consulta simples (ORDER BY id):")
        cursor.execute("""
            SELECT id, marca, modelo, ano_modelo, placa, cor, ativo
            FROM veiculos 
            WHERE usuario_id = ? 
            ORDER BY id
        """, (user_id,))
        
        veiculos_simples = cursor.fetchall()
        
        print(f"   Resultados: {len(veiculos_simples)} veículo(s)")
        for i, v in enumerate(veiculos_simples, 1):
            v_id, marca, modelo, ano, placa, cor, ativo = v
            print(f"   {i}. ID: {v_id}, {marca} {modelo} {ano}, Placa: {placa}, Ativo: {ativo}")
        
        # Verificar se há problemas com campos NULL ou vazios
        print("\n🔍 Verificando campos NULL ou problemáticos:")
        cursor.execute("""
            SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo,
                   CASE WHEN marca IS NULL THEN 'marca_null' ELSE 'marca_ok' END as marca_status,
                   CASE WHEN modelo IS NULL THEN 'modelo_null' ELSE 'modelo_ok' END as modelo_status,
                   CASE WHEN placa IS NULL THEN 'placa_null' ELSE 'placa_ok' END as placa_status,
                   CASE WHEN data_cadastro IS NULL THEN 'data_null' ELSE 'data_ok' END as data_status
            FROM veiculos 
            WHERE usuario_id = ?
        """, (user_id,))
        
        veiculos_debug = cursor.fetchall()
        
        for v in veiculos_debug:
            v_id = v[0]
            status_info = f"Marca: {v[9]}, Modelo: {v[10]}, Placa: {v[11]}, Data: {v[12]}"
            print(f"   ID {v_id}: {status_info}")
        
        # Verificar se há filtros de ativo
        print("\n🔍 Verificando apenas veículos ativos:")
        cursor.execute("""
            SELECT id, marca, modelo, ano_modelo, placa, ativo
            FROM veiculos 
            WHERE usuario_id = ? AND ativo = 1
            ORDER BY data_cadastro DESC
        """, (user_id,))
        
        veiculos_ativos = cursor.fetchall()
        
        print(f"   Veículos ativos: {len(veiculos_ativos)}")
        for v in veiculos_ativos:
            print(f"   - ID: {v[0]}, {v[1]} {v[2]} {v[3]}, Placa: {v[4]}")
        
        # Verificar se há problemas de encoding
        print("\n🔍 Verificando encoding de caracteres especiais:")
        cursor.execute("""
            SELECT id, marca, modelo, placa, 
                   LENGTH(marca) as marca_len,
                   LENGTH(modelo) as modelo_len,
                   LENGTH(placa) as placa_len
            FROM veiculos 
            WHERE usuario_id = ?
        """, (user_id,))
        
        veiculos_encoding = cursor.fetchall()
        
        for v in veiculos_encoding:
            v_id, marca, modelo, placa, marca_len, modelo_len, placa_len = v
            print(f"   ID {v_id}: Marca='{marca}'({marca_len}), Modelo='{modelo}'({modelo_len}), Placa='{placa}'({placa_len})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao debugar consulta: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()