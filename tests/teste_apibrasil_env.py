import os
from api_brasil import APIBrasilClient, VehiclesApi
from api_brasil.features.vehicles import Endpoints
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def test_api_brasil_with_env():
    """
    Teste da API Brasil usando variáveis de ambiente.
    
    Configure as seguintes variáveis no arquivo .env:
    API_BRASIL_BEARER_TOKEN=seu_bearer_token_aqui
    API_BRASIL_DEVICE_TOKEN=seu_device_token_aqui
    
    Ou configure as variáveis de ambiente do sistema.
    """
    
    # Obtém tokens das variáveis de ambiente
    bearer_token = os.getenv('API_BRASIL_BEARER_TOKEN')
    device_token = os.getenv('API_BRASIL_DEVICE_TOKEN')
    
    # Verifica se os tokens foram configurados
    if not bearer_token or not device_token:
        print("❌ Tokens não configurados!")
        print("\nConfigure as variáveis de ambiente:")
        print("API_BRASIL_BEARER_TOKEN=seu_bearer_token")
        print("API_BRASIL_DEVICE_TOKEN=seu_device_token")
        print("\nOu adicione no arquivo .env:")
        print("API_BRASIL_BEARER_TOKEN=seu_bearer_token")
        print("API_BRASIL_DEVICE_TOKEN=seu_device_token")
        return
    
    # Placa para teste (pode ser configurada via env também)
    placa = os.getenv('TEST_VEHICLE_PLATE', 'ABC-1234')
    
    try:
        print(f"🔑 Usando tokens das variáveis de ambiente")
        print(f"🚗 Testando com placa: {placa}")
        print("-" * 50)
        
        # Instancia o client da APIBrasil
        api_brasil_client = APIBrasilClient(bearer_token=bearer_token)
        
        # Usando a API de Veículos
        vehicles_api = VehiclesApi(api_brasil_client=api_brasil_client, device_token=device_token)
        vehicles_api.set_plate(plate=placa)
        
        # Consulta os dados do veículo
        response, status_code = vehicles_api.consulta(vechiles_api_endpoint=Endpoints.dados)
        
        print(f"Status Code: {status_code}")
        print(f"Response:")
        
        if isinstance(response, str):
            try:
                response_data = json.loads(response)
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(response)
        else:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Análise do resultado
        if status_code == 200:
            print("\n✅ Consulta realizada com sucesso!")
            if isinstance(response, str):
                try:
                    data = json.loads(response)
                    if not data.get('is_error', False):
                        print("📊 Dados do veículo obtidos com sucesso!")
                    else:
                        print("⚠️ API retornou erro nos dados")
                except:
                    pass
        elif status_code == 401:
            print("\n❌ Erro de autenticação. Verifique seus tokens.")
        elif status_code == 402:
            print("\n💳 Créditos insuficientes na conta API Brasil.")
        elif status_code == 404:
            print("\n🔍 Dados não encontrados para esta placa.")
        elif status_code == 429:
            print("\n⏰ Limite de requisições excedido. Aguarde um momento.")
        else:
            print(f"\n⚠️ Resposta inesperada: {status_code}")
            
    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        print("\nVerifique se:")
        print("1. O pacote api-brasil está instalado: uv add api-brasil")
        print("2. O pacote python-dotenv está instalado: uv add python-dotenv")
        print("3. Seus tokens estão corretos nas variáveis de ambiente")
        print("4. Você tem créditos na API Brasil")
        print("5. A placa está no formato correto (ABC-1234)")

def show_env_example():
    """Mostra exemplo de arquivo .env"""
    print("📝 Exemplo de arquivo .env:")
    print("-" * 30)
    print("# Tokens da API Brasil")
    print("API_BRASIL_BEARER_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
    print("API_BRASIL_DEVICE_TOKEN=seu_device_token_aqui")
    print("")
    print("# Placa para teste (opcional)")
    print("TEST_VEHICLE_PLATE=ABC-1234")
    print("-" * 30)
    print("\n💡 Dica: Nunca commite o arquivo .env no repositório!")
    print("Adicione .env no seu .gitignore")

if __name__ == "__main__":
    print("🇧🇷 Teste da API Brasil com Variáveis de Ambiente")
    print("=" * 60)
    
    # Verifica se deve mostrar exemplo do .env
    if '--show-env' in os.sys.argv:
        show_env_example()
    else:
        test_api_brasil_with_env()
        print("\n💡 Use --show-env para ver exemplo de configuração")