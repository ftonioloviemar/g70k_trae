#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da página de veículos do sergio@reis.com
"""

import requests
import sys
from urllib.parse import urljoin

def debug_sergio_page():
    """Debug da página de veículos do sergio@reis.com"""
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    try:
        print("=== Debug da Página de Veículos - sergio@reis.com ===")
        
        # 1. Fazer login
        print("\n1. Fazendo login...")
        login_data = {
            "email": "sergio@reis.com",
            "senha": "123456"
        }
        
        response = session.post(urljoin(base_url, "/login"), data=login_data)
        print(f"Status do login: {response.status_code}")
        
        # 2. Acessar página de veículos
        print("\n2. Acessando página de veículos...")
        response = session.get(urljoin(base_url, "/cliente/veiculos"))
        print(f"Status da página: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print("\n3. Conteúdo completo da página:")
            print("=" * 80)
            print(content)
            print("=" * 80)
            
            # Procurar por indicadores de veículos
            print("\n4. Análise do conteúdo:")
            
            # Verificar se há mensagens de erro
            if "erro" in content.lower():
                print("❌ Possível erro encontrado na página")
            
            # Verificar se há indicação de lista vazia
            if "nenhum veículo" in content.lower() or "sem veículos" in content.lower():
                print("❌ Página indica que não há veículos")
            
            # Verificar se há tabela ou lista
            if "<table" in content.lower() or "<ul" in content.lower() or "<li" in content.lower():
                print("✅ Estrutura de lista/tabela encontrada")
            else:
                print("❌ Nenhuma estrutura de lista encontrada")
            
            # Verificar dados específicos
            if "toyota" in content.lower():
                print("✅ 'Toyota' encontrado na página")
            else:
                print("❌ 'Toyota' não encontrado na página")
                
            if "corolla" in content.lower():
                print("✅ 'Corolla' encontrado na página")
            else:
                print("❌ 'Corolla' não encontrado na página")
                
            if "abc1234" in content.lower():
                print("✅ 'ABC1234' encontrado na página")
            else:
                print("❌ 'ABC1234' não encontrado na página")
        
        else:
            print(f"❌ Erro ao acessar página: {response.status_code}")
            print(response.text[:1000])
            
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Iniciando debug da página de veículos do sergio@reis.com...")
    debug_sergio_page()