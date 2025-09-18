"""
Teste para verificar o funcionamento do checkbox de email confirmado na edição de usuários.
"""
import pytest
from playwright.sync_api import Page, expect
import time


class TestToggleEmailConfirmado:
    """Testes para o componente Toggle de email confirmado"""
    
    def test_toggle_email_confirmado_funcionamento(self, page: Page):
        """Testa se o toggle de email confirmado funciona corretamente"""
        
        # Navegar para a página de login
        page.goto("http://localhost:8000/login")
        
        # Fazer login como admin
        page.fill('input[name="email"]', "ftoniolo@viemar.com.br")
        page.fill('input[name="senha"]', "123456")
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento
        page.wait_for_url("**/admin")
        
        # Navegar para usuários
        page.click('a[href="/admin/usuarios"]')
        page.wait_for_load_state("networkidle")
        
        # Encontrar um usuário para editar (primeiro da lista)
        edit_links = page.locator('a[href*="/admin/usuarios/"][href*="/editar"]')
        if edit_links.count() > 0:
            edit_links.first.click()
        else:
            pytest.skip("Nenhum usuário encontrado para testar")
        
        # Aguardar página de edição carregar
        page.wait_for_load_state("networkidle")
        
        # Verificar se o toggle existe (ainda é um input checkbox, mas com classes CSS do DaisyUI)
        toggle = page.locator('input[name="confirmado"]')
        expect(toggle).to_be_visible()
        
        # Verificar se é do tipo checkbox (Toggle do DaisyUI usa input type=checkbox)
        expect(toggle).to_have_attribute("type", "checkbox")
        
        # Verificar se tem as classes CSS do Toggle do DaisyUI
        # O elemento tem múltiplas classes: "uk-input toggle toggle-primary"
        # Usar contains para verificar se as classes estão presentes
        toggle_classes = toggle.get_attribute("class")
        assert "toggle" in toggle_classes, f"Classe 'toggle' não encontrada. Classes atuais: {toggle_classes}"
        assert "toggle-primary" in toggle_classes, f"Classe 'toggle-primary' não encontrada. Classes atuais: {toggle_classes}"
        
        # Testar mudança de estado do toggle
        initial_state = toggle.is_checked()
        print(f"Estado inicial do toggle: {initial_state}")
        
        # Clicar no toggle para alterar estado
        toggle.click()
        time.sleep(0.5)  # Aguardar um pouco
        
        # Verificar se o estado mudou
        new_state = toggle.is_checked()
        print(f"Novo estado do toggle: {new_state}")
        assert new_state != initial_state, "Toggle não mudou de estado ao clicar"
        
        # Salvar alterações
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento ou mensagem de sucesso
        page.wait_for_load_state("networkidle")
        
        # Verificar se foi redirecionado para lista de usuários ou se há mensagem de sucesso
        current_url = page.url
        print(f"URL após salvar: {current_url}")
        
        # Se foi redirecionado para lista, voltar para edição para verificar se salvou
        if "/admin/usuarios" in current_url and "/editar" not in current_url:
            # Voltar para edição do mesmo usuário
            edit_links = page.locator('a[href*="/admin/usuarios/"][href*="/editar"]')
            if edit_links.count() > 0:
                edit_links.first.click()
                page.wait_for_load_state("networkidle")
                
                # Verificar se o estado foi salvo
                toggle_after_save = page.locator('input[name="confirmado"]')
                saved_state = toggle_after_save.is_checked()
                print(f"Estado após salvar: {saved_state}")
                
                assert saved_state == new_state, "Estado do toggle não foi salvo corretamente"
        
        print("Teste do toggle concluído com sucesso!")
    
    def test_toggle_label_associacao(self, page: Page):
        """Testa se o label está corretamente associado ao toggle"""
        
        # Navegar para a página de login
        page.goto("http://localhost:8000/login")
        
        # Fazer login como admin
        page.fill('input[name="email"]', "ftoniolo@viemar.com.br")
        page.fill('input[name="senha"]', "123456")
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento para admin (não dashboard)
        page.wait_for_url("**/admin", timeout=30000)
        
        # Navegar para usuários
        page.goto("http://localhost:8000/admin/usuarios")
        page.wait_for_load_state("networkidle")
        
        # Encontrar um usuário para editar
        edit_links = page.locator('a[href*="/admin/usuarios/"][href*="/editar"]')
        if edit_links.count() > 0:
            edit_links.first.click()
        else:
            pytest.skip("Nenhum usuário encontrado para testar")
        
        # Aguardar página de edição carregar
        page.wait_for_load_state("networkidle")
        
        # Verificar se o label existe e está associado ao checkbox
        # Procurar por label que contém o texto "Email confirmado"
        label = page.locator('label:has-text("Email confirmado")')
        expect(label).to_be_visible()
        
        # Verificar se o label tem o atributo for_ correto (FastHTML usa for_ ao invés de for)
        # Vamos apenas verificar se o label funciona clicando nele
        
        # Testar se clicar no label também altera o toggle
        toggle = page.locator('input[name="confirmado"]')
        initial_state = toggle.is_checked()
        
        # Clicar no label
        label.click()
        time.sleep(0.5)
        
        # Verificar se o estado mudou
        new_state = toggle.is_checked()
        assert new_state != initial_state, "Clicar no label não alterou o estado do toggle"
        
        print("Teste de associação label-toggle concluído com sucesso!")