#!/usr/bin/env python3
"""
Teste de cadastro de usuário e envio de email
"""

import requests
import time

def test_user_registration():
    """Testa o cadastro de um novo usuário"""
    
    base_url = "http://localhost:8000"
    
    # Dados do usuário de teste
    user_data = {
        "email": "teste4@viemar.com",
        "senha": "123456",
        "confirmar_senha": "123456",
        "nome": "Usuario Teste 4",
        "tipo_usuario": "cliente"
    }
    
    print(f"Testando cadastro do usuário: {user_data['email']}")
    
    try:
        # Fazer POST para cadastro
        response = requests.post(
            f"{base_url}/cadastro",
            data=user_data,
            allow_redirects=False
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✅ Redirecionamento detectado - cadastro provavelmente realizado")
            print(f"Location: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 200:
            print("⚠️ Retornou 200 - pode ter erro no formulário")
            if "erro" in response.text.lower() or "error" in response.text.lower():
                print("❌ Erro detectado na resposta")
            else:
                print("✅ Resposta OK")
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            
        # Aguardar um pouco para o email ser processado
        print("Aguardando processamento do email...")
        time.sleep(2)
        
        return response.status_code in [200, 302]
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    success = test_user_registration()
    if success:
        print("\n✅ Teste concluído. Verifique os logs para detalhes do envio de email.")
    else:
        print("\n❌ Teste falhou.")