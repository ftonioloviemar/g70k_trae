#!/usr/bin/env python3
"""Script para testar login manual via requests"""

import requests
from urllib.parse import urlparse, parse_qs

def test_login_nao_confirmado():
    """Testa login com usuário não confirmado"""
    base_url = 'http://localhost:8000'
    
    # Dados do usuário não confirmado
    email = 'naoconfirmado@teste.com'
    senha = '123456'
    
    print(f"Testando login com usuário não confirmado:")
    print(f"Email: {email}")
    print(f"Senha: {senha}")
    print()
    
    # Fazer requisição POST para login
    response = requests.post(
        f'{base_url}/login',
        data={'email': email, 'senha': senha},
        allow_redirects=False  # Não seguir redirecionamentos automaticamente
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        print(f"Redirecionamento para: {location}")
        
        # Analisar a URL de redirecionamento
        parsed_url = urlparse(location)
        query_params = parse_qs(parsed_url.query)
        
        print(f"Parâmetros da query: {query_params}")
        
        if 'erro' in query_params:
            erro = query_params['erro'][0]
            print(f"Tipo de erro: {erro}")
            
            if erro == 'email_nao_confirmado':
                print("✅ SUCESSO: Erro de email não confirmado detectado corretamente!")
                return True
            else:
                print(f"❌ FALHA: Erro inesperado: {erro}")
                return False
        else:
            print("❌ FALHA: Nenhum erro encontrado na URL de redirecionamento")
            return False
    else:
        print(f"❌ FALHA: Status code inesperado: {response.status_code}")
        print(f"Conteúdo da resposta: {response.text[:500]}")
        return False

def test_login_credenciais_invalidas():
    """Testa login com credenciais inválidas"""
    base_url = 'http://localhost:8000'
    
    print("\n" + "="*50)
    print("Testando login com credenciais inválidas:")
    
    # Fazer requisição POST com senha errada
    response = requests.post(
        f'{base_url}/login',
        data={'email': 'naoconfirmado@teste.com', 'senha': 'senha_errada'},
        allow_redirects=False
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        parsed_url = urlparse(location)
        query_params = parse_qs(parsed_url.query)
        
        if 'erro' in query_params:
            erro = query_params['erro'][0]
            print(f"Tipo de erro: {erro}")
            
            if erro == 'credenciais_invalidas':
                print("✅ SUCESSO: Erro de credenciais inválidas detectado corretamente!")
                return True
            else:
                print(f"❌ FALHA: Erro inesperado: {erro}")
                return False

def main():
    print("Testando funcionalidade de login...")
    print("="*50)
    
    try:
        # Testar usuário não confirmado
        resultado1 = test_login_nao_confirmado()
        
        # Testar credenciais inválidas
        resultado2 = test_login_credenciais_invalidas()
        
        print("\n" + "="*50)
        print("RESUMO DOS TESTES:")
        print(f"Email não confirmado: {'✅ PASSOU' if resultado1 else '❌ FALHOU'}")
        print(f"Credenciais inválidas: {'✅ PASSOU' if resultado2 else '❌ FALHOU'}")
        
        if resultado1 and resultado2:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor. Verifique se está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

if __name__ == '__main__':
    main()