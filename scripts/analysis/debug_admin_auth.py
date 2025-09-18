#!/usr/bin/env python3
"""
Script para debugar a autenticação do usuário admin
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Carregar variáveis de ambiente
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from fastlite import Database
from app.config import Config
from app.auth import AuthManager
import bcrypt

def debug_admin_auth():
    """Debug da autenticação do admin"""
    
    print("=== DEBUG AUTENTICAÇÃO ADMIN ===")
    
    # Conectar ao banco
    config = Config()
    db = Database(config.DATABASE_PATH)
    auth_manager = AuthManager(db)
    
    # Verificar se o usuário admin existe
    print("\n1. Verificando usuário admin no banco...")
    result = db.execute(
        "SELECT id, email, senha_hash, nome, tipo_usuario, confirmado FROM usuarios WHERE email = ?",
        ('admin@viemar.com.br',)
    ).fetchone()
    
    if not result:
        print("❌ Usuário admin não encontrado!")
        return
    
    usuario_id, email, senha_hash, nome, tipo_usuario, confirmado = result
    print(f"✅ Usuário encontrado:")
    print(f"   ID: {usuario_id}")
    print(f"   Email: {email}")
    print(f"   Nome: {nome}")
    print(f"   Tipo: {tipo_usuario}")
    print(f"   Confirmado: {confirmado}")
    print(f"   Hash da senha: {senha_hash[:50]}...")
    
    # Testar validação da senha
    print("\n2. Testando validação da senha...")
    senha_teste = "admin123"
    
    try:
        # Verificar se o hash está no formato correto
        if not senha_hash.startswith('$2b$'):
            print(f"❌ Hash da senha não está no formato bcrypt: {senha_hash[:20]}...")
            
            # Tentar gerar novo hash
            print("   Gerando novo hash bcrypt...")
            novo_hash = bcrypt.hashpw(senha_teste.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            print(f"   Novo hash: {novo_hash[:50]}...")
            
            # Atualizar no banco
            db.execute(
                "UPDATE usuarios SET senha_hash = ? WHERE email = ?",
                (novo_hash, 'admin@viemar.com.br')
            )
            print("   ✅ Hash atualizado no banco")
            senha_hash = novo_hash
        
        # Testar validação
        senha_valida = bcrypt.checkpw(senha_teste.encode('utf-8'), senha_hash.encode('utf-8'))
        print(f"   Senha '{senha_teste}' válida: {senha_valida}")
        
        if senha_valida:
            print("   ✅ Validação de senha OK")
        else:
            print("   ❌ Validação de senha falhou")
            
    except Exception as e:
        print(f"   ❌ Erro na validação: {e}")
    
    # Testar método autenticar_usuario
    print("\n3. Testando método autenticar_usuario...")
    try:
        resultado = auth_manager.autenticar_usuario('admin@viemar.com.br', senha_teste)
        
        if resultado is None:
            print("   ❌ Autenticação retornou None (credenciais inválidas)")
        elif isinstance(resultado, dict) and resultado.get('erro'):
            print(f"   ❌ Autenticação retornou erro: {resultado['erro']}")
        else:
            print("   ✅ Autenticação bem-sucedida!")
            print(f"   Dados retornados: {resultado}")
            
    except Exception as e:
        print(f"   ❌ Erro na autenticação: {e}")
    
    # Testar criação de sessão
    print("\n4. Testando criação de sessão...")
    try:
        if resultado and not resultado.get('erro'):
            session_id = auth_manager.criar_sessao(
                resultado['id'],
                resultado['email'],
                resultado['tipo_usuario']
            )
            print(f"   ✅ Sessão criada: {session_id[:16]}...")
            
            # Testar obtenção da sessão
            session_data = auth_manager.obter_sessao(session_id)
            if session_data:
                print("   ✅ Sessão obtida com sucesso")
                print(f"   Dados da sessão: {session_data}")
            else:
                print("   ❌ Falha ao obter sessão")
        else:
            print("   ⏭️  Pulando teste de sessão (autenticação falhou)")
            
    except Exception as e:
        print(f"   ❌ Erro na criação de sessão: {e}")
    
    print("\n=== FIM DO DEBUG ===")

if __name__ == "__main__":
    debug_admin_auth()