#!/usr/bin/env python3
"""
Teste específico para verificar a correção do erro de visualização de garantias
"""

import requests
import json
from datetime import datetime

def test_garantia_view():
    """Testa se a visualização de garantias está funcionando"""
    
    # URL da aplicação
    base_url = "http://localhost:8000"
    
    # Primeiro, fazer login
    login_data = {
        "email": "joao@teste.com",
        "senha": "123456"
    }
    
    session = requests.Session()
    
    try:
        # Fazer login
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Tentar acessar a página de garantias
            garantias_response = session.get(f"{base_url}/cliente/garantias")
            print(f"Garantias page status: {garantias_response.status_code}")
            
            if garantias_response.status_code == 200:
                # Tentar acessar uma garantia específica
                garantia_response = session.get(f"{base_url}/cliente/garantias/1")
                print(f"Garantia view status: {garantia_response.status_code}")
                
                if garantia_response.status_code == 200:
                    print("✅ Visualização de garantias funcionando corretamente!")
                    print("Conteúdo da página:")
                    # Mostrar apenas uma parte do conteúdo para verificar se não há erros
                    content = garantia_response.text
                    if "500 Server Error" in content:
                        print("❌ Ainda há erro 500 na página")
                        return False
                    elif "Detalhes da Garantia" in content:
                        print("✅ Página carregou com sucesso - encontrado 'Detalhes da Garantia'")
                        return True
                    else:
                        print("⚠️ Página carregou mas conteúdo inesperado")
                        print("Primeiros 500 caracteres do conteúdo:")
                        print(content[:500])
                        return False
                else:
                    print(f"❌ Erro ao acessar garantia específica: {garantia_response.status_code}")
                    return False
            else:
                print(f"❌ Erro ao acessar página de garantias: {garantias_response.status_code}")
                return False
        else:
            print(f"❌ Erro no login: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    print("Testando visualização de garantias...")
    success = test_garantia_view()
    if success:
        print("\n🎉 Teste concluído com sucesso!")
    else:
        print("\n💥 Teste falhou - ainda há problemas")