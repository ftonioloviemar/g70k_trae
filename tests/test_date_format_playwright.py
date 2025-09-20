"""
Testes Playwright para validar a formatação de datas na interface de administração.
"""
import pytest
import re
from playwright.sync_api import Page, expect
from datetime import datetime
from fastlite import Database
from app.config import Config
from models.usuario import Usuario


@pytest.fixture
def admin_user():
    """Cria um usuário administrador para os testes."""
    config = Config()
    db = Database(config.DATABASE_PATH)
    
    # Limpa usuário admin se existir
    db.execute("DELETE FROM usuarios WHERE email = ?", ("admin@test.com",))
    
    # Cria usuário admin
    senha_hash = Usuario.criar_hash_senha("admin123")
    data_cadastro_admin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute("""
        INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("admin@test.com", senha_hash, "Admin User", "administrador", True, data_cadastro_admin))
    
    yield
    
    # Cleanup
    db.execute("DELETE FROM usuarios WHERE email = ?", ("admin@test.com",))


@pytest.fixture
def test_users():
    """Cria usuários de teste com diferentes datas de cadastro."""
    config = Config()
    db = Database(config.DATABASE_PATH)
    
    # Limpa usuários de teste se existirem
    db.execute("DELETE FROM usuarios WHERE email LIKE '%@testdate.com'")
    
    # Cria usuários com diferentes formatos de data
    test_data = [
        ("user1@testdate.com", "User One", "2025-09-20 15:30:45"),
        ("user2@testdate.com", "User Two", "2025-09-19 10:15:30"),
        ("user3@testdate.com", "User Three", "2025-09-18 08:45:15"),
    ]
    
    for email, nome, data_cadastro in test_data:
        senha_hash = Usuario.criar_hash_senha("test123")
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (email, senha_hash, nome, "cliente", True, data_cadastro))
    
    yield
    
    # Cleanup
    db.execute("DELETE FROM usuarios WHERE email LIKE '%@testdate.com'")


def test_admin_login_and_date_format(page: Page, admin_user, test_users):
    """Testa o login do admin e verifica a formatação das datas na página de usuários."""
    
    # Navega para a página de login
    page.goto("http://localhost:8000/login")
    
    # Faz login como admin
    page.fill('input[name="email"]', "admin@test.com")
    page.fill('input[name="senha"]', "admin123")
    page.click('button[type="submit"]')
    
    # Verifica se foi redirecionado para o dashboard
    expect(page).to_have_url(re.compile(r".*/admin.*"))
    
    # Navega para a página de usuários
    page.goto("http://localhost:8000/admin/usuarios")
    
    # Aguarda a página carregar
    page.wait_for_selector("table", timeout=10000)
    
    # Verifica se a página de usuários carregou
    expect(page.locator("h2")).to_contain_text("Gerenciar Usuários")
    
    # Verifica se existe uma tabela
    table = page.locator("table")
    expect(table).to_be_visible()
    
    # Verifica se existem linhas na tabela (além do cabeçalho)
    rows = page.locator("table tbody tr")
    expect(rows.first).to_be_visible()
    
    # Verifica a formatação das datas na coluna "Cadastro"
    # Procura por células que contêm datas no formato brasileiro
    date_pattern = r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}"
    
    # Pega todas as células da coluna de cadastro (assumindo que é a 6ª coluna, índice 5)
    cadastro_cells = page.locator("table tbody tr td:nth-child(6)")
    
    # Verifica se pelo menos uma célula tem o formato correto
    cell_count = cadastro_cells.count()
    assert cell_count > 0, "Nenhuma célula de data encontrada"
    
    valid_dates_found = 0
    for i in range(cell_count):
        cell_text = cadastro_cells.nth(i).text_content()
        if cell_text and cell_text != "N/A":
            # Verifica se a data está no formato brasileiro
            if re.match(date_pattern, cell_text):
                valid_dates_found += 1
                print(f"Data válida encontrada: {cell_text}")
            else:
                print(f"Data inválida encontrada: {cell_text}")
    
    assert valid_dates_found > 0, "Nenhuma data no formato brasileiro (dd/MM/yyyy HH:mm:ss) foi encontrada"


def test_date_format_validation_detailed(page: Page, admin_user, test_users):
    """Teste mais detalhado da formatação de datas."""
    
    # Login como admin
    page.goto("http://localhost:8000/login")
    page.fill('input[name="email"]', "admin@test.com")
    page.fill('input[name="senha"]', "admin123")
    page.click('button[type="submit"]')
    
    # Navega para usuários
    page.goto("http://localhost:8000/admin/usuarios")
    page.wait_for_selector("table tbody tr", timeout=10000)
    
    # Pega todas as linhas da tabela
    rows = page.locator("table tbody tr")
    row_count = rows.count()
    
    print(f"Encontradas {row_count} linhas na tabela")
    
    # Verifica cada linha
    for i in range(row_count):
        row = rows.nth(i)
        
        # Pega o email (2ª coluna) para identificar a linha
        email_cell = row.locator("td:nth-child(2)")
        email = email_cell.text_content()
        
        # Pega a data de cadastro (6ª coluna)
        date_cell = row.locator("td:nth-child(6)")
        date_text = date_cell.text_content()
        
        print(f"Linha {i+1}: Email={email}, Data={date_text}")
        
        # Se não for N/A, deve estar no formato brasileiro
        if date_text and date_text != "N/A":
            # Verifica o padrão dd/MM/yyyy HH:mm:ss
            date_pattern = r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$"
            assert re.match(date_pattern, date_text), f"Data '{date_text}' não está no formato brasileiro correto (dd/MM/yyyy HH:mm:ss)"
            
            # Verifica se não está no formato ISO
            iso_pattern = r"\d{4}-\d{2}-\d{2}"
            assert not re.search(iso_pattern, date_text), f"Data '{date_text}' ainda está no formato ISO"


def test_no_iso_dates_in_interface(page: Page, admin_user, test_users):
    """Verifica que não há datas no formato ISO na interface."""
    
    # Login como admin
    page.goto("http://localhost:8000/login")
    page.fill('input[name="email"]', "admin@test.com")
    page.fill('input[name="senha"]', "admin123")
    page.click('button[type="submit"]')
    
    # Navega para usuários
    page.goto("http://localhost:8000/admin/usuarios")
    page.wait_for_selector("table", timeout=10000)
    
    # Pega todo o conteúdo da tabela
    table_content = page.locator("table").text_content()
    
    # Verifica que não há datas no formato ISO (yyyy-mm-dd)
    iso_pattern = r"\d{4}-\d{2}-\d{2}"
    iso_matches = re.findall(iso_pattern, table_content)
    
    assert len(iso_matches) == 0, f"Encontradas datas no formato ISO na interface: {iso_matches}"
    
    print("✅ Nenhuma data no formato ISO encontrada na interface")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])