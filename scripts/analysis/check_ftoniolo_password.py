#!/usr/bin/env python3
"""
Script para verificar a senha do usuário ftoniolo
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastlite import Database
import bcrypt

def check_ftoniolo_password():
    """Verifica a senha do usuário ftoniolo"""
    
    print("=== VERIFICANDO SENHA DO FTONIOLO ===\n")
    
    # Conectar ao banco
    db_path = "data/viemar_garantia.db"
    db = Database(db_path)
    
    # Buscar usuário ftoniolo
    user = db.execute(
        "SELECT * FROM usuarios WHERE email = ?",
        ("ftoniolo@viemar.com.br",)
    ).fetchone()
    
    if not user:
        print("❌ Usuário ftoniolo não encontrado")
        return
    
    # Converter para dict
    colunas = [desc[0] for desc in db.execute("SELECT * FROM usuarios LIMIT 1").description]
    user_dict = dict(zip(colunas, user))
    
    print("✅ Usuário ftoniolo encontrado:")
    print(f"📧 Email: {user_dict['email']}")
    print(f"👤 Nome: {user_dict['nome']}")
    print(f"🔑 Tipo: {user_dict['tipo_usuario']}")
    print(f"✅ Confirmado: {user_dict['confirmado']}")
    print(f"🔐 Hash da senha: {user_dict['senha_hash'][:50]}...")
    
    # Testar várias senhas possíveis
    senhas_teste = ['abc123', '123456', 'admin123', 'ftoniolo', 'viemar123']
    
    print(f"\n🧪 Testando senhas possíveis:")
    for senha in senhas_teste:
        try:
            # Testar com bcrypt
            senha_valida = bcrypt.checkpw(senha.encode('utf-8'), user_dict['senha_hash'].encode('utf-8'))
            print(f"   '{senha}': {'✅ VÁLIDA' if senha_valida else '❌ INVÁLIDA'}")
            
            if senha_valida:
                print(f"\n🎉 SENHA CORRETA ENCONTRADA: '{senha}'")
                return senha
                
        except Exception as e:
            print(f"   '{senha}': ❌ ERRO - {e}")
    
    print("\n❌ Nenhuma senha testada funcionou")
    
    # Verificar se o hash está no formato correto
    hash_senha = user_dict['senha_hash']
    if hash_senha.startswith('$2b$') or hash_senha.startswith('$2a$') or hash_senha.startswith('$2y$'):
        print("✅ Hash parece estar no formato bcrypt correto")
    else:
        print("❌ Hash não parece estar no formato bcrypt")
        print(f"   Formato atual: {hash_senha[:20]}...")

if __name__ == "__main__":
    check_ftoniolo_password()