#!/usr/bin/env python3
"""
Redefinir senha do usuário ftoniolo@viemar.com.br
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
    """Redefinir senha do usuário ftoniolo@viemar.com.br"""
    
    try:
        print(f"🔐 Redefinindo senha do usuário ftoniolo@viemar.com.br...")
        config = Config()
        
        print(f"📁 Caminho do banco: {config.DATABASE_PATH}")
        
        if os.path.exists(config.DATABASE_PATH):
            db = Database(config.DATABASE_PATH)
            
            # Verificar se usuário existe
            result = db.execute(
                "SELECT id, email, nome FROM usuarios WHERE email = ?",
                ('ftoniolo@viemar.com.br',)
            ).fetchone()
            
            if result:
                print(f"✅ Usuário encontrado: {result[1]} - {result[2]}")
                
                # Gerar nova senha hash
                nova_senha = "123456"
                senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
                
                # Atualizar senha no banco
                db.execute(
                    "UPDATE usuarios SET senha_hash = ? WHERE email = ?",
                    (senha_hash.decode('utf-8'), 'ftoniolo@viemar.com.br')
                )
                
                print(f"✅ Senha redefinida para: {nova_senha}")
                
                # Verificar se a atualização funcionou
                result_updated = db.execute(
                    "SELECT senha_hash FROM usuarios WHERE email = ?",
                    ('ftoniolo@viemar.com.br',)
                ).fetchone()
                
                if result_updated:
                    stored_hash = result_updated[0]
                    if isinstance(stored_hash, str):
                        stored_hash = stored_hash.encode('utf-8')
                    
                    if bcrypt.checkpw(nova_senha.encode('utf-8'), stored_hash):
                        print(f"✅ Verificação: Nova senha funciona corretamente!")
                    else:
                        print(f"❌ Verificação: Nova senha não funciona!")
                        
            else:
                print(f"❌ Usuário ftoniolo@viemar.com.br não encontrado!")
        else:
            print(f"❌ Arquivo de banco não existe!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()