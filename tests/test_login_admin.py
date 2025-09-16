#!/usr/bin/env python3
"""
Teste de login administrativo
"""

import requests

def test_admin_login():
    """Testa diferentes credenciais de admin"""
    
    # Testar diferentes credenciais de admin
    credenciais = [
        {'email': 'ftoniolo@viemar.com.br', 'senha': 'admin123'},
        {'email': 'admin@viemar.com.br', 'senha': 'admin123'},
        {'email': 'admin@teste.com', 'senha': '123456'},
        {'email': 'ftoniolo@viemar.com.br', 'senha': '123456'}
    ]
    
    for i, cred in enumerate(credenciais, 1):
        print(f'=== TESTE {i}: {cred["email"]} ===')
        try:
            response = requests.post('http://localhost:8000/login', data=cred, allow_redirects=False)
            print(f'Status: {response.status_code}')
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f'Redirect: {location}')
                if '/admin' in location:
                    print('✓ Login admin bem-sucedido!')
                    return cred  # Retorna as credenciais que funcionaram
                elif 'erro=' in location:
                    print('✗ Erro no login (credenciais inválidas)')
            elif response.status_code == 200:
                print('✗ Login retornou 200 (possível erro no form)')
                print(f'URL final: {response.url}')
        except Exception as e:
            print(f'✗ Erro: {e}')
        print()
    
    return None

if __name__ == '__main__':
    credenciais_validas = test_admin_login()
    if credenciais_validas:
        print(f'\n✓ Credenciais válidas encontradas: {credenciais_validas["email"]}')
    else:
        print('\n✗ Nenhuma credencial válida encontrada')