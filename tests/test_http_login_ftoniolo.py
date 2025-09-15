#!/usr/bin/env python3
"""
Teste HTTP real para login do usuário ftoniolo@viemar.com.br
"""

import requests
import sys

def test_login_ftoniolo():
    """Testar login HTTP do usuário ftoniolo@viemar.com.br"""
    
    base_url = "http://localhost:8000"
    
    print(f"🌐 Testando login HTTP em {base_url}")
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Acessar página de login
        print(f"\n1️⃣ Acessando página de login...")
        response = session.get(f"{base_url}/login")
        print(f"  Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar página de login: {response.status_code}")
            return False
            
        print(f"✅ Página de login acessada")
        
        # 2. Enviar dados de login
        print(f"\n2️⃣ Enviando dados de login...")
        login_data = {
            "email": "ftoniolo@viemar.com.br",
            "senha": "123456"
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            redirect_location = response.headers.get('location', '')
            print(f"  Redirecionamento para: {redirect_location}")
            
            if redirect_location == '/admin':
                print(f"✅ Login bem-sucedido! Redirecionado para: {redirect_location}")
            else:
                print(f"❌ Redirecionamento inesperado: {redirect_location}")
                return False
        else:
            print(f"❌ Login falhou. Status: {response.status_code}")
            if 'erro=' in response.text:
                print(f"  Erro detectado na resposta")
            return False
        
        # 3. Testar acesso à área administrativa
        print(f"\n3️⃣ Testando acesso à área administrativa...")
        response = session.get(f"{base_url}/admin")
        print(f"  Status área admin: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Acesso à área administrativa bem-sucedido!")
            if "Administrador" in response.text or "admin" in response.text.lower():
                print(f"✅ Conteúdo administrativo encontrado!")
        else:
            print(f"❌ Erro ao acessar área administrativa: {response.status_code}")
            return False
        
        # 4. Verificar cookies
        print(f"\n4️⃣ Verificando cookies...")
        cookies = session.cookies.get_dict()
        print(f"  Cookies: {cookies}")
        
        if 'viemar_session' in cookies:
            print(f"✅ Cookie de sessão encontrado")
        else:
            print(f"❌ Cookie de sessão não encontrado")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Erro de conexão. Verifique se o servidor está rodando em {base_url}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_login_ftoniolo()
    if success:
        print(f"\n🎉 Teste de login do ftoniolo@viemar.com.br passou!")
        sys.exit(0)
    else:
        print(f"\n💥 Teste de login do ftoniolo@viemar.com.br falhou!")
        sys.exit(1)