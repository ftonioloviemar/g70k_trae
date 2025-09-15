#!/usr/bin/env python3
"""
Verificar autenticação do usuário sergio@reis.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastlite import Database
from pathlib import Path
import bcrypt

def main():
    """Verificar usuário sergio@reis.com"""
    
    # Caminho direto para o banco
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / 'data' / 'viemar_garantia.db'
    
    print(f"🔍 Verificando banco em: {db_path}")
    print(f"📁 Arquivo existe: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Arquivo de banco não encontrado!")
        return
    
    db = Database(db_path)
    
    # Buscar usuário
    result = db.execute(
        "SELECT id, email, senha_hash, nome, tipo_usuario, confirmado FROM usuarios WHERE email = ?",
        ('sergio@reis.com',)
    ).fetchone()
    
    if result:
        user_id, email, senha_hash, nome, tipo_usuario, confirmado = result
        print(f"✅ Usuário encontrado:")
        print(f"  ID: {user_id}")
        print(f"  Email: {email}")
        print(f"  Nome: {nome}")
        print(f"  Tipo: {tipo_usuario}")
        print(f"  Confirmado: {confirmado}")
        print(f"  Hash da senha: {senha_hash[:50]}...")
        
        # Testar senha
        senha_teste = "123456"
        print(f"\n🔐 Testando senha '{senha_teste}':")
        
        # Verificar com bcrypt diretamente
        try:
            senha_correta = bcrypt.checkpw(senha_teste.encode('utf-8'), senha_hash.encode('utf-8'))
            print(f"  Bcrypt direto: {'✅ Válida' if senha_correta else '❌ Inválida'}")
        except Exception as e:
            print(f"  Erro bcrypt: {e}")
            
    else:
        print("❌ Usuário não encontrado")
        
        # Listar todos os usuários
        print("\n📋 Todos os usuários:")
        usuarios = db.execute("SELECT id, email, nome FROM usuarios").fetchall()
        for user in usuarios:
            print(f"  {user[0]}: {user[1]} - {user[2]}")

if __name__ == "__main__":
    main()