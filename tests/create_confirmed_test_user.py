#!/usr/bin/env python3
"""
Cria um usuário de teste confirmado para os testes
"""

import sqlite3
from models.usuario import Usuario
from datetime import datetime
import bcrypt

def create_confirmed_test_user():
    """Cria usuário de teste confirmado"""
    
    # Conectar ao banco
    conn = sqlite3.connect('data/viemar_garantia.db')
    cursor = conn.cursor()
    
    email = "teste@viemar.com"
    senha = "123456"
    
    try:
        # Verificar se usuário já existe
        cursor.execute("SELECT id, confirmado FROM usuarios WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            user_id, confirmado = existing
            if not confirmado:
                # Confirmar usuário existente
                cursor.execute("UPDATE usuarios SET confirmado = 1 WHERE email = ?", (email,))
                conn.commit()
                print(f"✅ Usuário {email} confirmado com sucesso!")
            else:
                print(f"✅ Usuário {email} já está confirmado!")
            
            # Atualizar senha para garantir que seja 123456
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (senha_hash, email))
            conn.commit()
            print(f"✅ Senha atualizada para: {senha}")
            
        else:
            # Criar novo usuário
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO usuarios (
                    email, senha_hash, nome, tipo_usuario, confirmado,
                    cpf_cnpj, telefone, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email,
                senha_hash,
                "Usuario Teste",
                "cliente",
                1,  # confirmado = True
                "123.456.789-00",
                "(11) 99999-9999",
                datetime.now().isoformat()
            ))
            
            conn.commit()
            user_id = cursor.lastrowid
            print(f"✅ Usuário criado com sucesso!")
            print(f"   ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Senha: {senha}")
            print(f"   Confirmado: Sim")
        
        # Testar login
        cursor.execute("SELECT senha_hash FROM usuarios WHERE email = ?", (email,))
        stored_hash = cursor.fetchone()[0]
        
        if bcrypt.checkpw(senha.encode('utf-8'), stored_hash.encode('utf-8')):
            print(f"✅ Teste de senha bem-sucedido!")
        else:
            print(f"❌ Erro no teste de senha!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_confirmed_test_user()