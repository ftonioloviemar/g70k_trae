#!/usr/bin/env python3
"""
Verificar usuário ftoniolo@viemar.com.br no banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Arquivo .env carregado: {env_path}")
    else:
        print(f"⚠️ Arquivo .env não encontrado: {env_path}")
except ImportError:
    print("⚠️ python-dotenv não instalado")

from app.config import Config
from fastlite import Database
import bcrypt

def main():
    """Verificar usuário ftoniolo@viemar.com.br"""
    
    try:
        print(f"🔍 Verificando usuário ftoniolo@viemar.com.br...")
        config = Config()
        
        print(f"📁 Caminho do banco: {config.DATABASE_PATH}")
        
        if os.path.exists(config.DATABASE_PATH):
            db = Database(config.DATABASE_PATH)
            
            # Verificar se usuário ftoniolo existe
            result = db.execute(
                "SELECT id, email, nome, senha_hash FROM usuarios WHERE email = ?",
                ('ftoniolo@viemar.com.br',)
            ).fetchone()
            
            if result:
                print(f"✅ Usuário ftoniolo@viemar.com.br encontrado!")
                print(f"  ID: {result[0]}")
                print(f"  Email: {result[1]}")
                print(f"  Nome: {result[2]}")
                
                # Testar senhas comuns
                senhas_teste = ['123456', 'admin123', 'viemar123', 'ftoniolo123']
                
                print(f"\n🔐 Testando senhas...")
                senha_hash = result[3]
                if isinstance(senha_hash, str):
                    senha_hash = senha_hash.encode('utf-8')
                    
                for senha in senhas_teste:
                    if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
                        print(f"✅ Senha correta encontrada: {senha}")
                        break
                else:
                    print(f"❌ Nenhuma das senhas testadas funcionou")
                    print(f"  Senhas testadas: {senhas_teste}")
                    
                    # Mostrar hash para debug
                    print(f"  Hash no banco: {result[3][:50]}...")
                    
            else:
                print(f"❌ Usuário ftoniolo@viemar.com.br NÃO encontrado!")
                
                # Listar todos os usuários
                print(f"\n📋 Usuários no banco:")
                usuarios = db.execute("SELECT id, email, nome FROM usuarios").fetchall()
                for user in usuarios:
                    print(f"  {user[0]}: {user[1]} - {user[2]}")
        else:
            print(f"❌ Arquivo de banco não existe!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()