#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se os veículos do sergio@reis.com aparecem na interface web
"""

import sqlite3
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.auth import AuthManager
from fastlite import Database

def test_sergio_veiculos_web():
    """Testa se os veículos do sergio@reis.com aparecem na interface web"""
    
    db_path = "viemar_garantia.db"
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Teste de Veículos Web do sergio@reis.com ===")
        
        # 1. Verificar usuário
        print("\n1. Verificando usuário...")
        cursor.execute(
            "SELECT id, email, nome, tipo_usuario FROM usuarios WHERE email = ?",
            ("sergio@reis.com",)
        )
        usuario = cursor.fetchone()
        
        if not usuario:
            print("❌ Usuário não encontrado!")
            return False
            
        user_id, email, nome, tipo_usuario = usuario
        print(f"✅ Usuário encontrado: {nome} (ID: {user_id})")
        
        # 2. Verificar veículos no banco
        print("\n2. Verificando veículos no banco...")
        cursor.execute(
            "SELECT id, marca, modelo, ano_modelo, placa, usuario_id FROM veiculos WHERE usuario_id = ?",
            (user_id,)
        )
        veiculos = cursor.fetchall()
        
        if not veiculos:
            print("❌ Nenhum veículo encontrado no banco!")
            return False
            
        print(f"✅ {len(veiculos)} veículo(s) encontrado(s):")
        for veiculo in veiculos:
            v_id, marca, modelo, ano_modelo, placa, v_user_id = veiculo
            print(f"   - {marca} {modelo} {ano_modelo} - {placa} (ID: {v_id}, User: {v_user_id})")
        
        # 3. Criar sessão de autenticação
        print("\n3. Criando sessão de autenticação...")
        db = Database(db_path)
        auth_manager = AuthManager(db)
        
        session_id = auth_manager.criar_sessao(user_id, email, tipo_usuario)
        print(f"✅ Sessão criada: {session_id}")
        
        # 4. Simular a consulta da rota de veículos
        print("\n4. Simulando consulta da rota de veículos...")
        
        # Simular request.state.usuario
        class MockRequest:
            def __init__(self, usuario_data):
                self.state = type('State', (), {'usuario': usuario_data})()
        
        # Dados do usuário da sessão
        session_data = auth_manager.obter_sessao(session_id)
        if not session_data:
            print("❌ Sessão inválida!")
            return False
            
        mock_request = MockRequest(session_data)
        
        # Simular a lógica da rota listar_veiculos
        usuario_logado = mock_request.state.usuario
        usuario_id_sessao = usuario_logado.get('usuario_id')
        tipo_usuario_sessao = usuario_logado.get('tipo_usuario')
        
        print(f"   Usuario da sessão: ID={usuario_id_sessao}, Tipo={tipo_usuario_sessao}")
        
        # Verificar se é cliente
        if tipo_usuario_sessao != 'cliente':
            print("❌ Usuário não é cliente!")
            return False
            
        # Consultar veículos como na rota
        cursor.execute(
            "SELECT id, marca, modelo, ano_modelo, placa, chassi FROM veiculos WHERE usuario_id = ? ORDER BY marca, modelo",
            (usuario_id_sessao,)
        )
        veiculos_rota = cursor.fetchall()
        
        if not veiculos_rota:
            print("❌ Nenhum veículo retornado pela consulta da rota!")
            print(f"   Consultando com usuario_id: {usuario_id_sessao}")
            
            # Debug: verificar se há problema com o usuario_id
            cursor.execute("SELECT DISTINCT usuario_id FROM veiculos")
            todos_usuarios = cursor.fetchall()
            print(f"   Todos os usuario_id na tabela veiculos: {[u[0] for u in todos_usuarios]}")
            
            return False
            
        print(f"✅ {len(veiculos_rota)} veículo(s) retornado(s) pela rota:")
        for veiculo in veiculos_rota:
            v_id, marca, modelo, ano_modelo, placa, chassi = veiculo
            print(f"   - {marca} {modelo} {ano_modelo} - {placa} (ID: {v_id})")
        
        # 5. Verificar se os dados coincidem
        print("\n5. Verificando consistência...")
        if len(veiculos) == len(veiculos_rota):
            print("✅ Número de veículos coincide entre banco e rota!")
            return True
        else:
            print(f"❌ Inconsistência: {len(veiculos)} no banco vs {len(veiculos_rota)} na rota")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Iniciando teste de veículos web do sergio@reis.com...")
    
    sucesso = test_sergio_veiculos_web()
    
    if sucesso:
        print("\n🎉 Veículos do sergio@reis.com aparecem corretamente na interface web!")
    else:
        print("\n❌ Problema com os veículos do sergio@reis.com na interface web.")
        sys.exit(1)