#!/usr/bin/env python3
"""
Teste para verificar se o usuário admin está sendo criado corretamente
"""

import tempfile
import os
from fastlite import Database
from app.database import init_database
import bcrypt

def test_admin_creation():
    """Testa se o usuário admin é criado corretamente"""
    
    # Criar banco temporário
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Inicializar banco
        db = Database(db_path)
        init_database(db)
        
        # Verificar se o usuário admin foi criado
        admin = db.execute(
            "SELECT id, email, senha_hash, tipo_usuario FROM usuarios WHERE email = ?",
            ('ftoniolo@viemar.com.br',)
        ).fetchone()
        
        if admin:
            print(f"✓ Admin encontrado: ID={admin[0]}, Email={admin[1]}, Tipo={admin[3]}")
            
            # Testar verificação de senha
            senha_correta = bcrypt.checkpw('abc123'.encode('utf-8'), admin[2].encode('utf-8'))
            print(f"✓ Senha 'abc123' está correta: {senha_correta}")
            
            if senha_correta:
                print("✓ Usuário admin criado e senha funcionando corretamente!")
            else:
                print("✗ ERRO: Senha não está funcionando!")
                print(f"Hash armazenado: {admin[2]}")
        else:
            print("✗ ERRO: Usuário admin não foi encontrado no banco!")
            
            # Listar todos os usuários
            usuarios = db.execute("SELECT id, email, tipo_usuario FROM usuarios").fetchall()
            print(f"Usuários no banco: {len(usuarios)}")
            for u in usuarios:
                print(f"  - ID={u[0]}, Email={u[1]}, Tipo={u[2]}")
        
        db.close()
        
    finally:
        # Limpar arquivo temporário
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == '__main__':
    test_admin_creation()