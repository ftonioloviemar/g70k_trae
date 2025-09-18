"""
Teste real do seletor de tamanho de página
Verifica se a funcionalidade está funcionando corretamente
"""
import pytest
from playwright.sync_api import Page, expect
import time
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config

@pytest.fixture(scope="session")
def base_url():
    """URL base da aplicação"""
    return "http://localhost:8000"  # Porta correta onde o servidor está rodando

def test_page_selector_functionality(page: Page, base_url: str):
    """
    Testa se o seletor de tamanho de página funciona corretamente
    """
    # Navegar para a página de login
    page.goto(f"{base_url}/login")
    
    # Fazer login como admin
    page.fill('input[name="email"]', 'admin@viemar.com.br')
    page.fill('input[name="senha"]', 'admin123')
    page.click('button[type="submit"]')
    
    # Aguardar redirecionamento
    page.wait_for_url("**/admin")
    
    # Navegar para a página de garantias
    page.click('a[href="/admin/garantias"]')
    page.wait_for_url("**/admin/garantias")
    
    # Aguardar a página carregar completamente
    page.wait_for_selector('select[name="page_size"]')
    
    # Verificar se o seletor existe
    page_selector = page.locator('select[name="page_size"]')
    expect(page_selector).to_be_visible()
    
    # Obter URL atual
    current_url = page.url
    print(f"URL atual: {current_url}")
    
    # Verificar se há registros na página
    registros = page.locator('tbody tr')
    initial_count = registros.count()
    print(f"Número inicial de registros: {initial_count}")
    
    # Testar mudança para 10 registros por página
    page.select_option('select[name="page_size"]', '10')
    
    # Aguardar um pouco para a página processar
    time.sleep(2)
    
    # Verificar se a URL mudou
    new_url = page.url
    print(f"Nova URL: {new_url}")
    
    # Verificar se page_size=10 está na URL
    assert "page_size=10" in new_url, f"page_size=10 não encontrado na URL: {new_url}"
    
    # Verificar se o número de registros mudou (se houver mais de 10 registros)
    new_registros = page.locator('tbody tr')
    new_count = new_registros.count()
    print(f"Número de registros após mudança: {new_count}")
    
    # Se havia mais de 10 registros inicialmente, agora deve ter no máximo 10
    if initial_count > 10:
        assert new_count <= 10, f"Esperado máximo 10 registros, mas encontrou {new_count}"
    
    # Testar mudança para 25 registros por página
    page.select_option('select[name="page_size"]', '25')
    time.sleep(2)
    
    # Verificar se a URL mudou para page_size=25
    final_url = page.url
    print(f"URL final: {final_url}")
    assert "page_size=25" in final_url, f"page_size=25 não encontrado na URL: {final_url}"
    
    # Verificar se o seletor mantém o valor correto
    selected_value = page.locator('select[name="page_size"]').input_value()
    assert selected_value == "25", f"Valor selecionado deveria ser 25, mas é {selected_value}"
    
    print("✅ Teste do seletor de página passou com sucesso!")

def test_page_selector_javascript_function(page: Page, base_url: str):
    """
    Testa se a função JavaScript changePage está funcionando
    """
    # Navegar para a página de login
    page.goto(f"{base_url}/login")
    
    # Fazer login como admin
    page.fill('input[name="email"]', 'admin@viemar.com.br')
    page.fill('input[name="senha"]', 'admin123')
    page.click('button[type="submit"]')
    
    # Aguardar redirecionamento
    page.wait_for_url("**/admin")
    
    # Navegar para a página de garantias
    page.click('a[href="/admin/garantias"]')
    page.wait_for_url("**/admin/garantias")
    
    # Aguardar a página carregar
    page.wait_for_selector('select[name="page_size"]')
    
    # Verificar se a função changePage existe
    change_page_exists = page.evaluate("""
        typeof changePage === 'function'
    """)
    
    assert change_page_exists, "Função changePage não existe no JavaScript"
    
    # Testar a função diretamente
    page.evaluate("""
        changePage(1, 50);
    """)
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Verificar se a URL mudou
    current_url = page.url
    assert "page_size=50" in current_url, f"Função changePage não atualizou a URL corretamente: {current_url}"
    assert "page=1" in current_url, f"Função changePage não definiu page=1 na URL: {current_url}"
    
    print("✅ Teste da função JavaScript changePage passou com sucesso!")

if __name__ == "__main__":
    # Executar os testes diretamente
    pytest.main([__file__, "-v", "-s"])