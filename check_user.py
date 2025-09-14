#!/usr/bin/env python3
"""
Verificar dados do usuário no banco
"""

from fastlite import Database
import bcrypt
import os

def main():
    """Verificar usuário sergio@reis.com"""
    
    # Conectar ao banco de dados
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'viemar_garantia.db')
    db = Database(db_path)
    
    # Buscar usuário
    result = db.execute(
        "SELECT email, senha_hash, nome, tipo_usuario, confirmado FROM usuarios WHERE email = ?",
        ('sergio@reis.com',)
    ).fetchone()
    
    if result:
        email, senha_hash, nome, tipo_usuario, confirmado = result
        print(f"Usuário encontrado:")
        print(f"  Email: {email}")
        print(f"  Nome: {nome}")
        print(f"  Tipo: {tipo_usuario}")
        print(f"  Confirmado: {confirmado}")
        print(f"  Hash da senha: {senha_hash[:50]}...")
        
        # Testar senhas comuns
        senhas_teste = ['123456', 'senha123', 'admin', 'sergio123', 'sergio', 'reis', 'password', '12345678', 'teste123']
        
        for senha in senhas_teste:
            try:
                if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                    print(f"✅ Senha correta: {senha}")
                    break
                else:
                    print(f"❌ Senha incorreta: {senha}")
            except Exception as e:
                print(f"❌ Erro ao testar senha '{senha}': {e}")
    else:
        print("❌ Usuário sergio@reis.com não encontrado")
        
        # Listar todos os usuários
        print("\nUsuários disponíveis:")
        usuarios = db.execute("SELECT email, nome, tipo_usuario FROM usuarios").fetchall()
        for usuario in usuarios:
            print(f"  {usuario[0]} - {usuario[1]} ({usuario[2]})")

if __name__ == "__main__":
    main()