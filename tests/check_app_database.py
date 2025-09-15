#!/usr/bin/env python3
"""
Verificar qual banco de dados a aplicação está usando
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

def main():
    """Verificar configuração do banco da aplicação"""
    
    try:
        print(f"🔍 Verificando configuração da aplicação...")
        config = Config()
        
        print(f"📁 Caminho do banco configurado: {config.DATABASE_PATH}")
        print(f"📁 Arquivo existe: {os.path.exists(config.DATABASE_PATH)}")
        
        if os.path.exists(config.DATABASE_PATH):
            print(f"\n🔍 Verificando conteúdo do banco...")
            db = Database(config.DATABASE_PATH)
            
            # Verificar se usuário sergio existe
            result = db.execute(
                "SELECT id, email, nome FROM usuarios WHERE email = ?",
                ('sergio@reis.com',)
            ).fetchone()
            
            if result:
                print(f"✅ Usuário sergio@reis.com encontrado no banco da aplicação!")
                print(f"  ID: {result[0]}")
                print(f"  Email: {result[1]}")
                print(f"  Nome: {result[2]}")
            else:
                print(f"❌ Usuário sergio@reis.com NÃO encontrado no banco da aplicação!")
                
                # Listar todos os usuários
                print(f"\n📋 Usuários no banco da aplicação:")
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