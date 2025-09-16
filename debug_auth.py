#!/usr/bin/env python3
"""Script para debugar a função de autenticação"""

from fastlite import Database
from app.auth import AuthManager

def debug_auth():
    """Debug da função de autenticação"""
    # Conectar ao banco
    db = Database('g70k.db')
    auth_manager = AuthManager(db)
    
    email = 'naoconfirmado@teste.com'
    senha = '123456'
    
    print(f"Debugando autenticação para:")
    print(f"Email: {email}")
    print(f"Senha: {senha}")
    print()
    
    # Verificar se o usuário existe no banco
    user_query = db.execute(
        'SELECT id, nome, email, senha_hash, tipo_usuario, confirmado FROM usuarios WHERE email = ?',
        (email,)
    ).fetchone()
    
    if user_query:
        print(f"Usuário encontrado no banco:")
        print(f"  ID: {user_query[0]}")
        print(f"  Nome: {user_query[1]}")
        print(f"  Email: {user_query[2]}")
        print(f"  Tipo: {user_query[4]}")
        print(f"  Confirmado: {user_query[5]} (tipo: {type(user_query[5])})")
        print()
        
        # Verificar se a senha está correta
        import bcrypt
        senha_hash = user_query[3]
        senha_correta = bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))
        print(f"Senha correta: {senha_correta}")
        print()
        
        # Testar a função de autenticação
        print("Testando auth_manager.autenticar_usuario():")
        resultado = auth_manager.autenticar_usuario(email, senha)
        print(f"Resultado: {resultado}")
        print(f"Tipo do resultado: {type(resultado)}")
        
        if isinstance(resultado, dict):
            print(f"Chaves do dicionário: {list(resultado.keys())}")
            if 'erro' in resultado:
                print(f"Erro encontrado: {resultado['erro']}")
        
    else:
        print("❌ Usuário não encontrado no banco!")
    
    db.close()

if __name__ == '__main__':
    debug_auth()