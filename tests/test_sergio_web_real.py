#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste real da interface web para sergio@reis.com usando requests
"""

import requests
import sys
from urllib.parse import urljoin

def test_sergio_web_real():
    """Testa o login e visualização de veículos na interface web real"""
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    try:
        print("=== Teste Real da Interface Web - sergio@reis.com ===")
        
        # 1. Verificar se o servidor está rodando
        print("\n1. Verificando servidor...")
        try:
            response = session.get(base_url)
            if response.status_code == 200:
                print("✅ Servidor está rodando")
            else:
                print(f"❌ Servidor retornou status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar ao servidor. Certifique-se de que está rodando em http://localhost:8000")
            return False
        
        # 2. Fazer login
        print("\n2. Fazendo login...")
        login_data = {
            "email": "sergio@reis.com",
            "senha": "123456"
        }
        
        response = session.post(urljoin(base_url, "/login"), data=login_data)
        
        if response.status_code == 200:
            # Verificar se foi redirecionado para a página do cliente
            if "/cliente" in response.url or "cliente" in response.text.lower():
                print("✅ Login realizado com sucesso")
            else:
                print("❌ Login falhou - não foi redirecionado para área do cliente")
                print(f"URL atual: {response.url}")
                return False
        else:
            print(f"❌ Erro no login - Status: {response.status_code}")
            return False
        
        # 3. Acessar página de veículos
        print("\n3. Acessando página de veículos...")
        response = session.get(urljoin(base_url, "/cliente/veiculos"))
        
        if response.status_code == 200:
            print("✅ Página de veículos acessada com sucesso")
            
            # Verificar se os veículos aparecem na página
            content = response.text.lower()
            if "toyota" in content and "corolla" in content and "abc1234" in content:
                print("✅ Veículo Toyota Corolla ABC1234 encontrado na página!")
                return True
            else:
                print("❌ Veículo não encontrado na página")
                print("Conteúdo da página (primeiros 500 caracteres):")
                print(response.text[:500])
                return False
        else:
            print(f"❌ Erro ao acessar página de veículos - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando teste real da interface web para sergio@reis.com...")
    print("IMPORTANTE: Certifique-se de que o servidor está rodando em http://localhost:8000")
    
    sucesso = test_sergio_web_real()
    
    if sucesso:
        print("\n🎉 Teste da interface web passou! Os veículos do sergio@reis.com aparecem corretamente!")
    else:
        print("\n❌ Teste da interface web falhou.")
        sys.exit(1)