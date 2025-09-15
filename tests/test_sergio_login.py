#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para verificar o login do sergio@reis.com
"""

import sqlite3
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.auth import AuthManager
from models.usuario import Usuario
from app.database import Database

def test_sergio_login():
    """Testa o login do sergio@reis.com"""
    print("=== Teste de Login do sergio@reis.com ===")
    
    # Conectar ao banco
    db_path = "data/viemar_garantia.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar se o usuário existe
        print("\n1. Verificando usuário no banco...")
        cursor.execute(
            "SELECT id, email, nome, senha_hash, tipo_usuario FROM usuarios WHERE email = ?",
            ("sergio@reis.com",)
        )
        usuario = cursor.fetchone()
        
        if not usuario:
            print("❌ Usuário sergio@reis.com não encontrado!")
            return False
            
        user_id, email, nome, senha_hash, tipo_usuario = usuario
        print(f"✅ Usuário encontrado:")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Nome: {nome}")
        print(f"   Tipo: {tipo_usuario}")
        print(f"   Hash da senha: {senha_hash[:50] if senha_hash else 'VAZIO'}...")
        
        # 2. Testar hash da senha
        print("\n2. Testando hash da senha...")
        senha_teste = "123456"
        
        # Verificar se a senha está vazia ou None
        if not senha_hash or senha_hash.strip() == "":
            print("❌ Hash da senha está vazio! Corrigindo...")
            novo_hash = Usuario.criar_hash_senha(senha_teste)
            cursor.execute(
                "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
                (novo_hash, user_id)
            )
            conn.commit()
            print(f"✅ Senha atualizada com novo hash: {novo_hash[:50]}...")
            senha_hash = novo_hash
        
        # 3. Testar autenticação
        print("\n3. Testando autenticação...")
        
        # Inicializar Database e AuthManager
        from fastlite import Database
        db = Database(db_path)
        auth_manager = AuthManager(db)
        
        # Tentar autenticar
        try:
            resultado = auth_manager.autenticar_usuario(email, senha_teste)
            if resultado:
                print(f"✅ Autenticação bem-sucedida!")
                print(f"   Dados retornados: {resultado}")
                
                # 4. Criar sessão
                print("\n4. Criando sessão...")
                session_id = auth_manager.criar_sessao(user_id, email, tipo_usuario)
                print(f"✅ Sessão criada: {session_id}")
                
                # 5. Verificar sessão
                print("\n5. Verificando sessão...")
                session_data = auth_manager.obter_sessao(session_id)
                if session_data:
                    print(f"✅ Sessão válida:")
                    print(f"   usuario_id: {session_data.get('usuario_id')}")
                    print(f"   usuario_email: {session_data.get('usuario_email')}")
                    print(f"   tipo_usuario: {session_data.get('tipo_usuario')}")
                    return True
                else:
                    print("❌ Sessão não encontrada")
                    return False
            else:
                print("❌ Falha na autenticação")
                return False
                
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Iniciando teste do login do sergio@reis.com...")
    
    sucesso = test_sergio_login()
    
    if sucesso:
        print("\n🎉 Login do sergio@reis.com está funcionando!")
    else:
        print("\n❌ Problema no login do sergio@reis.com.")
        sys.exit(1)