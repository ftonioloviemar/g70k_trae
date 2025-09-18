"""
Teste de debug para verificar o problema de login e checkbox de email confirmado.
"""
import pytest
from playwright.sync_api import Page, expect
import time


def test_debug_login_and_checkbox(page: Page):
    """Teste de debug para login e checkbox"""
    
    print("=== INICIANDO TESTE DE DEBUG ===")
    
    # Navegar para a página de login
    print("1. Navegando para página de login...")
    page.goto("http://localhost:8000/login")
    page.wait_for_load_state("networkidle")
    
    # Verificar se a página de login carregou
    print("2. Verificando se página de login carregou...")
    expect(page).to_have_url("http://localhost:8000/login")
    
    # Verificar se os campos existem
    print("3. Verificando campos de login...")
    email_field = page.locator('input[name="email"]')
    password_field = page.locator('input[name="senha"]')
    submit_button = page.locator('button[type="submit"]')
    
    expect(email_field).to_be_visible()
    expect(password_field).to_be_visible()
    expect(submit_button).to_be_visible()
    
    # Preencher campos
    print("4. Preenchendo campos...")
    email_field.fill("ftoniolo@viemar.com.br")
    password_field.fill("123456")
    
    # Aguardar um pouco
    time.sleep(1)
    
    # Fazer login
    print("5. Clicando em submit...")
    submit_button.click()
    
    # Aguardar redirecionamento com timeout maior
    print("6. Aguardando redirecionamento...")
    try:
        page.wait_for_url("**/dashboard", timeout=10000)
        print("✓ Redirecionamento para dashboard bem-sucedido!")
    except Exception as e:
        print(f"✗ Erro no redirecionamento: {e}")
        print(f"URL atual: {page.url}")
        
        # Verificar se há mensagens de erro na página
        error_messages = page.locator('.alert-danger, .error, [class*="error"]')
        if error_messages.count() > 0:
            print("Mensagens de erro encontradas:")
            for i in range(error_messages.count()):
                print(f"  - {error_messages.nth(i).text_content()}")
        
        # Capturar screenshot para debug
        page.screenshot(path="debug_login_error.png")
        
        # Tentar navegar diretamente para admin/usuarios
        print("7. Tentando navegar diretamente para admin/usuarios...")
        page.goto("http://localhost:8000/admin/usuarios")
        page.wait_for_load_state("networkidle")
    
    # Verificar URL atual
    current_url = page.url
    print(f"URL atual após login: {current_url}")
    
    # Se não estiver no dashboard, tentar navegar para usuários
    if "dashboard" not in current_url:
        print("8. Navegando para admin/usuarios...")
        page.goto("http://localhost:8000/admin/usuarios")
        page.wait_for_load_state("networkidle")
    else:
        # Navegar para usuários
        print("8. Clicando no link de usuários...")
        users_link = page.locator('a[href="/admin/usuarios"]')
        if users_link.count() > 0:
            users_link.click()
            page.wait_for_load_state("networkidle")
        else:
            print("Link de usuários não encontrado, navegando diretamente...")
            page.goto("http://localhost:8000/admin/usuarios")
            page.wait_for_load_state("networkidle")
    
    # Verificar se chegou na página de usuários
    print(f"9. URL após navegar para usuários: {page.url}")
    
    # Procurar links de edição
    print("10. Procurando links de edição...")
    edit_links = page.locator('a[href*="/admin/usuarios/"][href*="/editar"]')
    edit_count = edit_links.count()
    print(f"Encontrados {edit_count} links de edição")
    
    if edit_count > 0:
        print("11. Clicando no primeiro link de edição...")
        edit_links.first.click()
        page.wait_for_load_state("networkidle")
        
        print(f"12. URL da página de edição: {page.url}")
        
        # Procurar o checkbox
        print("13. Procurando checkbox de email confirmado...")
        checkbox = page.locator('input[name="confirmado"]')
        
        if checkbox.count() > 0:
            print("✓ Checkbox encontrado!")
            print(f"Tipo: {checkbox.get_attribute('type')}")
            print(f"Visível: {checkbox.is_visible()}")
            print(f"Estado inicial: {checkbox.is_checked()}")
            
            # Testar clique
            print("14. Testando clique no checkbox...")
            initial_state = checkbox.is_checked()
            checkbox.click()
            time.sleep(0.5)
            new_state = checkbox.is_checked()
            
            print(f"Estado após clique: {new_state}")
            print(f"Mudou de estado: {new_state != initial_state}")
            
            if new_state != initial_state:
                print("✓ Checkbox funciona corretamente!")
                
                # Testar salvamento
                print("15. Testando salvamento...")
                save_button = page.locator('button[type="submit"]')
                if save_button.count() > 0:
                    save_button.click()
                    page.wait_for_load_state("networkidle")
                    print(f"URL após salvar: {page.url}")
                    print("✓ Salvamento executado!")
                else:
                    print("✗ Botão de salvar não encontrado")
            else:
                print("✗ Checkbox não mudou de estado")
        else:
            print("✗ Checkbox não encontrado")
            
            # Listar todos os inputs da página para debug
            all_inputs = page.locator('input')
            input_count = all_inputs.count()
            print(f"Total de inputs na página: {input_count}")
            for i in range(min(input_count, 10)):  # Mostrar apenas os primeiros 10
                input_elem = all_inputs.nth(i)
                name = input_elem.get_attribute('name') or 'sem nome'
                input_type = input_elem.get_attribute('type') or 'sem tipo'
                print(f"  Input {i+1}: name='{name}', type='{input_type}'")
    else:
        print("✗ Nenhum link de edição encontrado")
        
        # Capturar screenshot da página de usuários
        page.screenshot(path="debug_usuarios_page.png")
    
    print("=== TESTE DE DEBUG CONCLUÍDO ===")