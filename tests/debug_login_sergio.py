#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug do login do usuário sergio@reis.com
"""

import sqlite3
import bcrypt
import requests

def debug_login():
    """Debug do login do sergio@reis.com"""
    print("🔍 DEBUG LOGIN SERGIO@REIS.COM")
    print("=" * 40)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('viemar_garantia.db')
        cursor = conn.cursor()
        
        # Buscar usuário
        cursor.execute("""
            SELECT id, nome, email, senha_hash, tipo_usuario, confirmado
            FROM usuarios 
            WHERE email = ?
        """, ('sergio@reis.com',))
        
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"✅ Usuário encontrado:")
            print(f"   - ID: {usuario[0]}")
            print(f"   - Nome: {usuario[1]}")
            print(f"   - Email: {usuario[2]}")
            print(f"   - Senha hash: {usuario[3][:20]}...")
            print(f"   - Tipo: {usuario[4]}")
            print(f"   - Confirmado: {usuario[5]}")
            
            # Testar hash da senha
            senha_teste = '123456'
            try:
                if bcrypt.checkpw(senha_teste.encode('utf-8'), usuario[3].encode('utf-8')):
                    print(f"✅ Senha '{senha_teste}' confere com o hash")
                else:
                    print(f"❌ Senha '{senha_teste}' NÃO confere com o hash")
                    
                    # Tentar outras senhas comuns
                    senhas_teste = ['abc123', 'sergio123', '123', 'password']
                    for senha in senhas_teste:
                        if bcrypt.checkpw(senha.encode('utf-8'), usuario[3].encode('utf-8')):
                            print(f"✅ Senha correta encontrada: '{senha}'")
                            break
                    else:
                        print("❌ Nenhuma senha comum funcionou")
                        
            except Exception as e:
                print(f"❌ Erro ao verificar senha: {e}")
                
        else:
            print("❌ Usuário não encontrado")
            
        conn.close()
        
        # Testar login via HTTP
        print("\n🌐 TESTANDO LOGIN VIA HTTP")
        print("-" * 30)
        
        session = requests.Session()
        
        # Primeiro, pegar a página de login para ver se há CSRF ou algo assim
        login_page = session.get('http://localhost:8000/login')
        print(f"Página de login: {login_page.status_code}")
        
        # Tentar login
        login_data = {
            'email': 'sergio@reis.com',
            'password': '123456'
        }
        
        login_response = session.post('http://localhost:8000/login', data=login_data, allow_redirects=False)
        print(f"Resposta login: {login_response.status_code}")
        print(f"Headers: {dict(login_response.headers)}")
        
        if login_response.status_code == 302:
            location = login_response.headers.get('location', '')
            print(f"Redirecionamento para: {location}")
            
            if 'cliente' in location:
                print("✅ Login bem-sucedido")
            elif 'erro=credenciais_invalidas' in location:
                print("❌ Credenciais inválidas")
            else:
                print(f"⚠️  Redirecionamento inesperado: {location}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    debug_login()