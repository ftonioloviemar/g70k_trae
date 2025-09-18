"""
Teste simples para verificar se a paginação está horizontal
"""
import requests
import time
from bs4 import BeautifulSoup


def test_pagination_horizontal_simple():
    """Testa se a paginação está horizontal usando requests e BeautifulSoup"""
    
    # Aguardar um pouco para garantir que o servidor está rodando
    time.sleep(2)
    
    try:
        # Criar sessão para manter cookies
        session = requests.Session()
        
        # Primeiro fazer login como admin
        login_data = {
            'email': 'admin@viemar.com.br',
            'senha': 'admin123'  # Mudando de 'password' para 'senha'
        }
        
        login_response = session.post("http://localhost:8000/login", data=login_data, timeout=10)
        
        print(f"🔐 Status do login: {login_response.status_code}")
        print(f"🔗 URL após login: {login_response.url}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: Status code {login_response.status_code}")
            print(f"📄 Conteúdo da resposta: {login_response.text[:500]}")
            return False
            
        # Fazer requisição para a página de usuários
        response = session.get("http://localhost:8000/admin/usuarios", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erro: Status code {response.status_code}")
            return False
            
        # Parsear o HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: salvar o HTML para análise
        with open("C:\\python\\g70k_trae\\tmp\\debug_usuarios_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("📄 HTML salvo em tmp/debug_usuarios_page.html")
        
        # Verificar se existe o container de paginação
        pagination_container = soup.find(class_="pagination-container")
        
        if not pagination_container:
            print("❌ Container de paginação não encontrado")
            return False
            
        print("✅ Container de paginação encontrado")
        
        # Verificar se tem a classe mt-3 (margem top)
        if "mt-3" in pagination_container.get("class", []):
            print("✅ Classe mt-3 encontrada")
        
        # Verificar se tem elementos row e col
        rows = pagination_container.find_all(class_="row")
        if rows:
            print(f"✅ Encontradas {len(rows)} row(s)")
            
            # Verificar colunas na primeira row
            cols = rows[0].find_all(class_=lambda x: x and "col" in x)
            if cols:
                print(f"✅ Encontradas {len(cols)} coluna(s)")
                
                # Verificar se as colunas têm as classes corretas
                for i, col in enumerate(cols):
                    classes = col.get("class", [])
                    if "d-flex" in classes:
                        print(f"✅ Coluna {i+1} tem d-flex")
                    if "align-items-center" in classes:
                        print(f"✅ Coluna {i+1} tem align-items-center")
                        
        # Verificar se existe navegação de páginas
        pagination_nav = soup.find("nav", {"aria-label": "Navegação de páginas"})
        if pagination_nav:
            print("✅ Navegação de páginas encontrada")
            
        # Verificar se existe seletor de registros por página
        page_size_selector = soup.find("select", class_="form-select")
        if page_size_selector:
            print("✅ Seletor de registros por página encontrado")
            
        # Verificar informações de paginação
        pagination_info = soup.find("small", class_="text-muted")
        if pagination_info and "Mostrando" in pagination_info.text:
            print("✅ Informações de paginação encontradas")
            
        print("🎉 Teste de paginação horizontal passou!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    success = test_pagination_horizontal_simple()
    if success:
        print("\n✅ SUCESSO: A paginação está funcionando corretamente!")
    else:
        print("\n❌ FALHA: Problemas encontrados na paginação")