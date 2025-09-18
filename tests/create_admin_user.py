#!/usr/bin/env python3
"""
Script para criar usuário admin no banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastlite import Database
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user():
    """Cria usuário admin no banco de dados"""
    
    # Conectar ao banco
    db_path = "data/viemar_garantia.db"
    db = Database(db_path)
    
    # Verificar se admin já existe
    existing_admin = db.execute(
        "SELECT id FROM usuarios WHERE email = ?",
        ("admin@viemar.com.br",)
    ).fetchone()
    
    if existing_admin:
        print("✅ Usuário admin já existe")
        return
    
    # Criar usuário admin
    password_hash = generate_password_hash("admin123")
    
    db.execute("""
        INSERT INTO usuarios (
            nome, email, senha_hash, tipo_usuario, 
            confirmado, data_cadastro
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "Administrador",
        "admin@viemar.com.br", 
        password_hash,
        "administrador",
        1,  # email confirmado
        datetime.now().isoformat()
    ))
    
    print("✅ Usuário admin criado com sucesso!")
    print("📧 Email: admin@viemar.com.br")
    print("🔑 Senha: admin123")

if __name__ == "__main__":
    create_admin_user()