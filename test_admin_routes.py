#!/usr/bin/env python3
"""
Teste das rotas administrativas de edição e reset de senha
"""

import requests
import sys

def test_admin_routes():
    """Testa as rotas administrativas"""
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Primeiro fazer login como administrador
    print('=== FAZENDO LOGIN COMO ADMIN ===')
    try:
        login_data = {
            'email': 'ftoniolo@viemar.com.br',
            'senha': '123456'
        }
        
        login_response = session.post('http://localhost:8000/login', data=login_data, allow_redirects=False)
        print(f'Login Status Code: {login_response.status_code}')
        
        if login_response.status_code == 302:
            location = login_response.headers.get('Location', '')
            print(f'Redirect para: {location}')
            if '/admin' in location:
                print('✓ Login admin bem-sucedido!')
                # Seguir o redirecionamento para manter a sessão
                session.get(f'http://localhost:8000{location}')
            else:
                print(f'✗ Erro no login - redirecionado para: {location}')
                return
        else:
            print(f'✗ Erro no login: {login_response.status_code}')
            return
            
    except Exception as e:
        print(f'✗ Erro ao fazer login: {e}')
        return
    
    # Testar POST de edição de usuário
    print('\n=== TESTANDO POST EDIÇÃO DE USUÁRIO ===')
    try:
        # Dados para editar o usuário
        data = {
            'nome': 'Usuário Teste Editado',
            'email': 'naoconfirmado@teste.com',
            'tipo_usuario': 'cliente',
            'cpf_cnpj': '12345678901',
            'telefone': '11999999999',
            'cep': '01234567',
            'endereco': 'Rua Teste, 123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'uf': 'SP'
        }
        
        response = session.post('http://localhost:8000/admin/usuarios/12/editar', data=data)
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 302:  # Redirect esperado
            print('✓ Edição de usuário funcionando (redirect)')
            location = response.headers.get('Location', 'N/A')
            print(f'Location: {location}')
        else:
            print(f'✗ Erro na edição: {response.status_code}')
            print(f'Conteúdo: {response.text[:300]}...')
            
    except Exception as e:
        print(f'✗ Erro ao testar edição POST: {e}')

    # Testar POST de reset de senha
    print('\n=== TESTANDO POST RESET DE SENHA ===')
    try:
        data = {
            'nova_senha': 'novasenha123',
            'confirmar_senha': 'novasenha123'
        }
        
        response = session.post('http://localhost:8000/admin/usuarios/12/reset-senha', data=data)
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 302:  # Redirect esperado
            print('✓ Reset de senha funcionando (redirect)')
            location = response.headers.get('Location', 'N/A')
            print(f'Location: {location}')
        else:
            print(f'✗ Erro no reset: {response.status_code}')
            print(f'Conteúdo: {response.text[:300]}...')
            
    except Exception as e:
        print(f'✗ Erro ao testar reset POST: {e}')

if __name__ == '__main__':
    test_admin_routes()