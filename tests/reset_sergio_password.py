#!/usr/bin/env python3
"""
Script para redefinir a senha do usuário sergio@reis.com
"""

import sqlite3
import bcrypt
from pathlib import Path

def reset_sergio_password():
    """Redefine a senha do usuário sergio@reis.com para '123456'"""
    
    # Caminho do banco de dados
    db_path = Path("data/viemar_garantia.db")
    if not db_path.exists():
        db_path = Path("viemar_garantia.db")
    
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se o usuário existe
        cursor.execute("SELECT id, email FROM usuarios WHERE email = ?", ("sergio@reis.com",))
        user = cursor.fetchone()
        
        if not user:
            print("❌ Usuário sergio@reis.com não encontrado")
            return False
        
        user_id, email = user
        print(f"✅ Usuário encontrado: {email} (ID: {user_id})")
        
        # Gerar nova senha hash
        nova_senha = "123456"
        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
        
        # Atualizar a senha no banco
        cursor.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
            (senha_hash.decode('utf-8'), user_id)
        )
        
        conn.commit()
        
        print(f"✅ Senha redefinida com sucesso para: {nova_senha}")
        print(f"📧 Email: {email}")
        print(f"🔑 Nova senha: {nova_senha}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao redefinir senha: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Redefinindo senha do usuário sergio@reis.com...")
    success = reset_sergio_password()
    
    if success:
        print("\n🎉 Processo concluído com sucesso!")
        print("Agora você pode fazer login com:")
        print("  Email: sergio@reis.com")
        print("  Senha: 123456")
    else:
        print("\n❌ Falha ao redefinir a senha")