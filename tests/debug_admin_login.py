#!/usr/bin/env python3
"""
Script para debugar o login do admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastlite import Database
from werkzeug.security import check_password_hash

def debug_admin_login():
    """Debug do login do admin"""
    
    # Conectar ao banco
    db_path = "data/viemar_garantia.db"
    db = Database(db_path)
    
    # Buscar usuário admin
    admin = db.execute(
        "SELECT * FROM usuarios WHERE email = ?",
        ("admin@viemar.com.br",)
    ).fetchone()
    
    if not admin:
        print("❌ Usuário admin não encontrado")
        return
    
    # Converter tuple para dict usando os nomes das colunas
    colunas = [desc[0] for desc in db.execute("SELECT * FROM usuarios LIMIT 1").description]
    admin_dict = dict(zip(colunas, admin))
    
    print("✅ Usuário admin encontrado:")
    print(f"📧 Email: {admin_dict['email']}")
    print(f"👤 Nome: {admin_dict['nome']}")
    print(f"🔑 Tipo: {admin_dict['tipo_usuario']}")
    print(f"✅ Confirmado: {admin_dict['confirmado']}")
    print(f"🔐 Hash da senha: {admin_dict['senha_hash'][:50]}...")
    
    # Testar validação da senha
    senha_teste = "admin123"
    senha_valida = check_password_hash(admin_dict['senha_hash'], senha_teste)
    
    print(f"\n🧪 Teste de validação da senha '{senha_teste}': {'✅ VÁLIDA' if senha_valida else '❌ INVÁLIDA'}")
    
    # Verificar estrutura da tabela
    print("\n📋 Estrutura da tabela usuarios:")
    colunas = db.execute("PRAGMA table_info(usuarios)").fetchall()
    for coluna in colunas:
        print(f"  - {coluna['name']}: {coluna['type']}")

if __name__ == "__main__":
    debug_admin_login()