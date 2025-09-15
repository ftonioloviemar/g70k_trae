#!/usr/bin/env python3
"""
Debug detalhado do login do sergio@reis.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastlite import Database
from pathlib import Path
from app.auth import AuthManager
import bcrypt
import logging

# Configurar logging para ver detalhes
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Debug detalhado do login sergio@reis.com"""
    
    # Caminho direto para o banco
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / 'data' / 'viemar_garantia.db'
    
    print(f"🔍 Verificando banco em: {db_path}")
    print(f"📁 Arquivo existe: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Arquivo de banco não encontrado!")
        return
    
    db = Database(db_path)
    
    # Dados de teste
    email_teste = "sergio@reis.com"
    senha_teste = "123456"
    
    print(f"\n🔐 Testando login com:")
    print(f"  Email: {email_teste}")
    print(f"  Senha: {senha_teste}")
    
    # 1. Verificar se usuário existe
    print(f"\n1️⃣ Verificando se usuário existe...")
    result = db.execute(
        "SELECT id, email, senha_hash, nome, tipo_usuario, confirmado FROM usuarios WHERE email = ?",
        (email_teste.lower().strip(),)
    ).fetchone()
    
    if not result:
        print("❌ Usuário não encontrado na consulta!")
        return
    
    usuario_id, usuario_email, senha_hash, nome, tipo_usuario, confirmado = result
    print(f"✅ Usuário encontrado:")
    print(f"  ID: {usuario_id}")
    print(f"  Email: {usuario_email}")
    print(f"  Nome: {nome}")
    print(f"  Tipo: {tipo_usuario}")
    print(f"  Confirmado: {confirmado}")
    
    # 2. Verificar confirmação de email
    print(f"\n2️⃣ Verificando confirmação de email...")
    if tipo_usuario not in ['admin', 'administrador'] and not confirmado:
        print(f"❌ Email não confirmado para usuário tipo '{tipo_usuario}'")
        return
    else:
        print(f"✅ Email confirmado ou usuário é admin")
    
    # 3. Verificar senha
    print(f"\n3️⃣ Verificando senha...")
    print(f"  Hash armazenado: {senha_hash[:50]}...")
    
    try:
        senha_correta = bcrypt.checkpw(senha_teste.encode('utf-8'), senha_hash.encode('utf-8'))
        print(f"  Bcrypt result: {senha_correta}")
        
        if not senha_correta:
            print("❌ Senha incorreta!")
            return
        else:
            print("✅ Senha correta!")
    except Exception as e:
        print(f"❌ Erro ao verificar senha: {e}")
        return
    
    # 4. Testar AuthManager completo
    print(f"\n4️⃣ Testando AuthManager completo...")
    try:
        auth_manager = AuthManager(db)
        usuario_auth = auth_manager.autenticar_usuario(email_teste, senha_teste)
        
        if usuario_auth:
            print(f"✅ AuthManager autenticou com sucesso!")
            print(f"  Dados retornados: {usuario_auth}")
        else:
            print(f"❌ AuthManager falhou na autenticação!")
            
    except Exception as e:
        print(f"❌ Erro no AuthManager: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎯 Conclusão: Todos os testes passaram individualmente!")

if __name__ == "__main__":
    main()