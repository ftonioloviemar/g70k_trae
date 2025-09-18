#!/usr/bin/env python3
"""
Script para debugar o problema de sessão e cookies
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
from bs4 import BeautifulSoup

def debug_session_cookies():
    """Debug do sistema de sessão e cookies"""
    
    print("=== DEBUG SESSÃO E COOKIES ===\n")
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_data = {
        'email': 'ftoniolo@viemar.com.br',
        'senha': '123456'
    }
    
    try:
        login_response = session.post('http://localhost:8000/login', data=login_data, allow_redirects=False)
        print(f"   Status: {login_response.status_code}")
        print(f"   Headers: {dict(login_response.headers)}")
        print(f"   Cookies após login: {dict(session.cookies)}")
        
        if login_response.status_code == 302:
            location = login_response.headers.get('Location', '')
            print(f"   Redirecionamento: {location}")
            
            # 2. Seguir redirecionamento
            print("\n2. Seguindo redirecionamento...")
            redirect_response = session.get(f'http://localhost:8000{location}', allow_redirects=False)
            print(f"   Status: {redirect_response.status_code}")
            print(f"   Cookies após redirect: {dict(session.cookies)}")
            
            if redirect_response.status_code == 200:
                print("   ✅ Acesso ao admin bem-sucedido!")
                
                # 3. Tentar acessar página de usuários
                print("\n3. Tentando acessar página de usuários...")
                usuarios_response = session.get('http://localhost:8000/admin/usuarios', allow_redirects=False)
                print(f"   Status: {usuarios_response.status_code}")
                print(f"   Cookies: {dict(session.cookies)}")
                
                if usuarios_response.status_code == 200:
                    print("   ✅ Acesso à página de usuários bem-sucedido!")
                    
                    # Verificar se tem paginação
                    soup = BeautifulSoup(usuarios_response.text, 'html.parser')
                    
                    # Procurar por elementos de paginação
                    pagination_container = soup.find(class_='pagination-container')
                    if pagination_container:
                        print("   ✅ Container de paginação encontrado!")
                        print(f"   HTML da paginação: {pagination_container}")
                    else:
                        print("   ❌ Container de paginação NÃO encontrado")
                        
                        # Procurar por outros indicadores de paginação
                        mostrando = soup.find(string=lambda text: text and 'Mostrando' in text)
                        if mostrando:
                            print(f"   ✅ Texto 'Mostrando' encontrado: {mostrando}")
                        else:
                            print("   ❌ Texto 'Mostrando' NÃO encontrado")
                        
                        # Procurar por botões de página
                        page_buttons = soup.find_all('a', class_='page-link')
                        if page_buttons:
                            print(f"   ✅ Botões de página encontrados: {len(page_buttons)}")
                        else:
                            print("   ❌ Botões de página NÃO encontrados")
                    
                    # Salvar HTML para análise
                    with open('tmp/debug_usuarios_page.html', 'w', encoding='utf-8') as f:
                        f.write(usuarios_response.text)
                    print("   📄 HTML salvo em tmp/debug_usuarios_page.html")
                    
                elif usuarios_response.status_code == 302:
                    location = usuarios_response.headers.get('Location', '')
                    print(f"   ❌ Redirecionado para: {location}")
                else:
                    print(f"   ❌ Erro: {usuarios_response.status_code}")
                    
            elif redirect_response.status_code == 302:
                location = redirect_response.headers.get('Location', '')
                print(f"   ❌ Redirecionado novamente para: {location}")
            else:
                print(f"   ❌ Erro no redirect: {redirect_response.status_code}")
                
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            print(f"   Conteúdo: {login_response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_session_cookies()