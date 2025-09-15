#!/usr/bin/env python3
"""
Teste HTTP real do login do sergio@reis.com
"""

import requests
import sys
import os

def main():
    """Teste HTTP real do login"""
    
    base_url = "http://localhost:8000"
    
    print(f"🌐 Testando login HTTP em {base_url}")
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # 1. Acessar página de login
    print(f"\n1️⃣ Acessando página de login...")
    try:
        response = session.get(f"{base_url}/login")
        print(f"  Status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Erro ao acessar página de login")
            return
        print(f"✅ Página de login acessada")
    except Exception as e:
        print(f"❌ Erro ao acessar página de login: {e}")
        return
    
    # 2. Fazer login
    print(f"\n2️⃣ Enviando dados de login...")
    login_data = {
        'email': 'sergio@reis.com',
        'senha': '123456'
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('location', '')
            print(f"  Redirecionamento para: {location}")
            
            if 'erro=credenciais_invalidas' in location:
                print(f"❌ Credenciais inválidas!")
            elif location in ['/cliente', '/admin']:
                print(f"✅ Login bem-sucedido! Redirecionado para: {location}")
                
                # 3. Verificar se consegue acessar área logada
                print(f"\n3️⃣ Testando acesso à área logada...")
                response = session.get(f"{base_url}{location}")
                print(f"  Status área logada: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ Acesso à área logada bem-sucedido!")
                    # Verificar se tem conteúdo esperado
                    if 'Sergio' in response.text or 'sergio@reis.com' in response.text:
                        print(f"✅ Conteúdo personalizado encontrado!")
                    else:
                        print(f"⚠️ Conteúdo personalizado não encontrado")
                else:
                    print(f"❌ Erro ao acessar área logada")
            else:
                print(f"⚠️ Redirecionamento inesperado: {location}")
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            print(f"  Conteúdo: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Erro durante login: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Verificar cookies
    print(f"\n4️⃣ Verificando cookies...")
    cookies = session.cookies
    print(f"  Cookies: {dict(cookies)}")
    
    if 'viemar_session' in cookies:
        print(f"✅ Cookie de sessão encontrado")
    else:
        print(f"❌ Cookie de sessão não encontrado")

if __name__ == "__main__":
    main()