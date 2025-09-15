#!/usr/bin/env python3
"""
Criar usuário de teste com senha conhecida
"""

from fastlite import Database
import bcrypt
import os

def main():
    """Criar usuário de teste"""
    
    # Conectar ao banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'viemar_garantia.db')
    db = Database(db_path)
    
    # Dados do usuário de teste
    email = 'teste@viemar.com'
    senha = '123456'
    nome = 'Usuario Teste'
    tipo_usuario = 'cliente'
    
    # Gerar hash da senha
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        # Verificar se usuário já existe
        existing = db.execute(
            "SELECT id FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()
        
        if existing:
            print(f"Usuário {email} já existe. Atualizando senha...")
            db.execute(
                "UPDATE usuarios SET senha_hash = ? WHERE email = ?",
                (senha_hash, email)
            )
        else:
            print(f"Criando usuário {email}...")
            db.execute(
                "INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado) VALUES (?, ?, ?, ?, ?)",
                (email, senha_hash, nome, tipo_usuario, True)
            )
        
        print(f"✅ Usuário criado/atualizado com sucesso!")
        print(f"Email: {email}")
        print(f"Senha: {senha}")
        
        # Testar a senha
        result = db.execute(
            "SELECT senha_hash FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()
        
        if result and bcrypt.checkpw(senha.encode('utf-8'), result[0].encode('utf-8')):
            print("✅ Senha testada com sucesso!")
        else:
            print("❌ Erro ao testar senha")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()