from api_brasil import APIBrasilClient, VehiclesApi
from api_brasil.features.vehicles import Endpoints
import json

def test_api_brasil_vehicles():
    """
    Teste da API Brasil para consulta de dados de veículos.
    
    Para usar este teste:
    1. Acesse https://apibrasil.com.br
    2. Crie uma conta e obtenha seu bearer_token
    3. Obtenha seu device_token na área de credenciais
    4. Substitua os valores abaixo pelos seus tokens reais
    """
    
    # IMPORTANTE: Substitua pelos seus tokens reais
    bearer_token = "your_bearer_token_here"  # Token da API Brasil
    device_token = "your_device_token_here"  # Device token
    placa = "ABC-1234"  # Placa do veículo para consulta
    
    try:
        # Instancie o client da APIBrasil
        api_brasil_client = APIBrasilClient(bearer_token=bearer_token)
        
        # Usando a API de Veículos
        vehicles_api = VehiclesApi(api_brasil_client=api_brasil_client, device_token=device_token)
        vehicles_api.set_plate(plate=placa)
        
        print(f"Consultando dados do veículo com placa: {placa}")
        print("-" * 50)
        
        # Consulta os dados do veículo
        response, status_code = vehicles_api.consulta(vechiles_api_endpoint=Endpoints.dados)
        
        print(f"Status Code: {status_code}")
        print(f"Response:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        if status_code == 200:
            print("\n✅ Consulta realizada com sucesso!")
        elif status_code == 401:
            print("\n❌ Erro de autenticação. Verifique seus tokens.")
        else:
            print(f"\n⚠️ Resposta inesperada: {status_code}")
            
    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        print("\nVerifique se:")
        print("1. O pacote api-brasil está instalado: uv add api-brasil")
        print("2. Seus tokens estão corretos")
        print("3. Você tem créditos na API Brasil")

if __name__ == "__main__":
    test_api_brasil_vehicles()