from api_brasil import APIBrasilClient, VehiclesApi, CNPJApi, CPFApi, CEPGeoLocationAPI
from api_brasil.features.vehicles import Endpoints
import json

def test_api_brasil_complete():
    """
    Teste completo da API Brasil com diferentes endpoints.
    
    Para usar este teste:
    1. Acesse https://apibrasil.com.br
    2. Crie uma conta e obtenha seu bearer_token
    3. Obtenha seu device_token na área de credenciais
    4. Substitua os valores abaixo pelos seus tokens reais
    """
    
    # IMPORTANTE: Substitua pelos seus tokens reais
    bearer_token = "your_bearer_token_here"  # Token da API Brasil
    device_token = "your_device_token_here"  # Device token
    
    try:
        # Instancie o client da APIBrasil
        api_brasil_client = APIBrasilClient(bearer_token=bearer_token)
        
        print("🚗 Testando API de Veículos")
        print("=" * 50)
        test_vehicles_api(api_brasil_client, device_token)
        
        print("\n🏢 Testando API de CNPJ")
        print("=" * 50)
        test_cnpj_api(api_brasil_client, device_token)
        
        print("\n👤 Testando API de CPF")
        print("=" * 50)
        test_cpf_api(api_brasil_client, device_token)
        
        print("\n📍 Testando API de CEP")
        print("=" * 50)
        test_cep_api(api_brasil_client, device_token)
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        print("\nVerifique se:")
        print("1. O pacote api-brasil está instalado: uv add api-brasil")
        print("2. Seus tokens estão corretos")
        print("3. Você tem créditos na API Brasil")

def test_vehicles_api(client, device_token):
    """Testa a API de consulta de veículos."""
    try:
        vehicles_api = VehiclesApi(api_brasil_client=client, device_token=device_token)
        vehicles_api.set_plate(plate="ABC-1234")
        
        print("Consultando dados do veículo...")
        response, status_code = vehicles_api.consulta(vechiles_api_endpoint=Endpoints.dados)
        
        print(f"Status: {status_code}")
        if isinstance(response, str):
            try:
                response_data = json.loads(response)
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
            except:
                print(response)
        else:
            print(json.dumps(response, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Erro na API de Veículos: {str(e)}")

def test_cnpj_api(client, device_token):
    """Testa a API de consulta de CNPJ."""
    try:
        cnpj_api = CNPJApi(api_brasil_client=client, device_token=device_token)
        cnpj_api.set_cnpj(cnpj="11.222.333/0001-81")  # CNPJ de exemplo
        
        print("Consultando dados do CNPJ...")
        response, status_code = cnpj_api.consulta()
        
        print(f"Status: {status_code}")
        if isinstance(response, str):
            try:
                response_data = json.loads(response)
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
            except:
                print(response)
        else:
            print(json.dumps(response, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Erro na API de CNPJ: {str(e)}")

def test_cpf_api(client, device_token):
    """Testa a API de consulta de CPF."""
    try:
        cpf_api = CPFApi(api_brasil_client=client, device_token=device_token)
        cpf_api.set_cpf(cpf="123.456.789-09")  # CPF de exemplo
        
        print("Consultando dados do CPF...")
        response, status_code = cpf_api.consulta()
        
        print(f"Status: {status_code}")
        if isinstance(response, str):
            try:
                response_data = json.loads(response)
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
            except:
                print(response)
        else:
            print(json.dumps(response, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Erro na API de CPF: {str(e)}")

def test_cep_api(client, device_token):
    """Testa a API de consulta de CEP."""
    try:
        cep_api = CEPGeoLocationAPI(api_brasil_client=client, device_token=device_token)
        cep_api.set_cep(cep="01310-100")  # CEP da Av. Paulista, SP
        
        print("Consultando dados do CEP...")
        response, status_code = cep_api.consulta()
        
        print(f"Status: {status_code}")
        if isinstance(response, str):
            try:
                response_data = json.loads(response)
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
            except:
                print(response)
        else:
            print(json.dumps(response, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Erro na API de CEP: {str(e)}")

if __name__ == "__main__":
    test_api_brasil_complete()