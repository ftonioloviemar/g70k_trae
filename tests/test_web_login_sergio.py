#!/usr/bin/env python3
"""
Teste do login web do sergio@reis.com simulando exatamente a aplicação
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastlite import Database
from pathlib import Path
from app.auth import init_auth, get_auth_manager
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Teste completo do login web sergio@reis.com"""
    
    # Caminho direto para o banco (igual ao main.py)
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / 'data' / 'viemar_garantia.db'
    
    print(f"🔍 Simulando inicialização da aplicação...")
    print(f"📁 Banco de dados: {db_path}")
    print(f"📁 Arquivo existe: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Arquivo de banco não encontrado!")
        return
    
    # Simular exatamente o que acontece no main.py
    print(f"\n1️⃣ Inicializando banco de dados...")
    db = Database(db_path)
    
    print(f"\n2️⃣ Inicializando sistema de autenticação...")
    init_auth(db)
    
    print(f"\n3️⃣ Obtendo AuthManager...")
    try:
        auth_manager = get_auth_manager()
        print(f"✅ AuthManager obtido com sucesso")
    except Exception as e:
        print(f"❌ Erro ao obter AuthManager: {e}")
        return
    
    # Dados de teste
    email_teste = "sergio@reis.com"
    senha_teste = "123456"
    
    print(f"\n4️⃣ Simulando login web...")
    print(f"  Email: {email_teste}")
    print(f"  Senha: {senha_teste}")
    
    # Simular exatamente o que acontece na rota de login
    print(f"\n5️⃣ Processando dados do formulário...")
    email_form = email_teste.strip().lower()
    senha_form = senha_teste
    
    print(f"  Email processado: '{email_form}'")
    print(f"  Senha processada: '{senha_form}'")
    
    if not email_form or not senha_form:
        print("❌ Email ou senha vazios!")
        return
    
    print(f"\n6️⃣ Chamando autenticar_usuario...")
    try:
        usuario = auth_manager.autenticar_usuario(email_form, senha_form)
        
        if usuario:
            print(f"✅ Autenticação bem-sucedida!")
            print(f"  Dados do usuário: {usuario}")
            
            # Simular criação de sessão
            print(f"\n7️⃣ Criando sessão...")
            session_id = auth_manager.criar_sessao(
                usuario['id'],
                usuario['email'],
                usuario['tipo_usuario']
            )
            print(f"✅ Sessão criada: {session_id[:20]}...")
            
            # Determinar redirecionamento
            if usuario['tipo_usuario'] in ['admin', 'administrador']:
                redirect_url = '/admin'
            else:
                redirect_url = '/cliente'
            
            print(f"✅ Redirecionamento: {redirect_url}")
            print(f"\n🎉 LOGIN WEB SIMULADO COM SUCESSO!")
            
        else:
            print(f"❌ Autenticação falhou!")
            print(f"❌ Seria redirecionado para: /login?erro=credenciais_invalidas")
            
    except Exception as e:
        print(f"❌ Erro durante autenticação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()