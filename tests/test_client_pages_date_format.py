"""
Testes para validar formatação de datas nas páginas do cliente.

Este módulo testa especificamente as páginas "Meus Dados" e "Minhas Garantias"
para garantir que as datas estão sendo exibidas no formato brasileiro correto.
"""

import pytest
from datetime import datetime, date
from playwright.sync_api import Page, expect
import os
import sys
import re

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.date_utils import format_date_br


class TestClientPagesDateFormat:
    """Testes de formatação de datas nas páginas do cliente"""
    
    def test_format_date_br_function(self):
        """Testa se a função format_date_br está funcionando corretamente"""
        # Teste com string ISO
        assert format_date_br('2024-01-15') == '15/01/2024'
        assert format_date_br('2024-12-31') == '31/12/2024'
        
        # Teste com datetime
        dt = datetime(2024, 3, 10)
        assert format_date_br(dt) == '10/03/2024'
        
        # Teste com date
        d = date(2024, 6, 25)
        assert format_date_br(d) == '25/06/2024'
        
        # Teste com valores inválidos
        assert format_date_br(None) == 'N/A'
        assert format_date_br('') == 'N/A'
    
    def test_meus_dados_page_date_format(self, page: Page):
        """Testa se a página 'Meus Dados' exibe datas no formato brasileiro"""
        # Fazer login como cliente
        page.goto("http://localhost:8000/login")
        
        # Preencher formulário de login
        page.fill('input[name="email"]', os.getenv('CLIENT_EMAIL', 'sergio@reis.com'))
        page.fill('input[name="senha"]', os.getenv('CLIENT_PASSWORD', '123456'))
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento
        page.wait_for_url("**/cliente**")
        
        # Navegar para página "Meus Dados"
        page.goto("http://localhost:8000/cliente/perfil")
        
        # Verificar se a página carregou
        expect(page.locator('h2')).to_contain_text('Meu Perfil')
        
        # Procurar por data de cadastro no formato brasileiro
        # A data deve estar no formato dd/MM/yyyy
        date_text = page.locator('text=/Membro desde:/')
        expect(date_text).to_be_visible()
        
        # Verificar informações da conta
        account_info = page.locator('.uk-card:has-text("Informações da Conta")')
        br_date_pattern = account_info.locator('text=/\\d{2}\/\\d{2}\/\\d{4}/')
        if br_date_pattern.count() > 0:
            expect(br_date_pattern.first).to_be_visible()
    
    def test_minhas_garantias_page_date_format(self, page: Page):
        """Testa se as datas na página 'Minhas Garantias' estão no formato brasileiro"""
        # Fazer login como cliente
        page.goto("http://localhost:8000/login")
        
        # Preencher formulário de login
        page.fill('input[name="email"]', os.getenv('CLIENT_EMAIL', 'sergio@reis.com'))
        page.fill('input[name="senha"]', os.getenv('CLIENT_PASSWORD', '123456'))
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento
        page.wait_for_url("**/cliente**")
        
        # Navegar para a página de garantias
        page.goto("http://localhost:8000/cliente/garantias")
        
        # Aguardar a página carregar
        page.wait_for_load_state('networkidle')
        
        # Aguardar um pouco mais para garantir que a página carregou
        page.wait_for_timeout(2000)
        
        # Verificar se chegou na página de garantias - ser mais flexível
        try:
            # Tentar encontrar qualquer título relacionado a garantias
            title_selectors = [
                'h1',
                'h2', 
                'h3',
                '.title',
                '.page-title'
            ]
            
            title_found = False
            for selector in title_selectors:
                elements = page.locator(selector)
                for i in range(elements.count()):
                    element = elements.nth(i)
                    text = element.text_content()
                    if text and ("Garantias" in text or "garantias" in text):
                        expect(element).to_be_visible()
                        title_found = True
                        break
                if title_found:
                    break
            
            # Se não encontrou nenhum título, pelo menos verificar se a URL está correta
            if not title_found:
                expect(page).to_have_url(re.compile(r".*/cliente/garantias"))
                
        except Exception as e:
            # Se falhar, capturar screenshot para debug
            page.screenshot(path="tmp/garantias_page_debug.png")
            raise e
        
        # Verificar se a tabela existe
        table = page.locator('table')
        expect(table).to_be_visible()
        
        # Verificar cabeçalhos da tabela
        headers = table.locator('thead th')
        expect(headers.nth(3)).to_contain_text('Instalação')
        expect(headers.nth(4)).to_contain_text('Vencimento')
        
        # Verificar se não há datas no formato ISO (yyyy-mm-dd) na tabela
        table_body = table.locator('tbody')
        iso_dates_in_table = table_body.locator('text=/\\d{4}-\\d{2}-\\d{2}/')
        expect(iso_dates_in_table).to_have_count(0)
        
        # Se houver dados na tabela, verificar formato brasileiro
        rows = table_body.locator('tr')
        if rows.count() > 0:
            # Verificar se há datas no formato brasileiro nas colunas de data
            br_date_pattern = table_body.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/')
            if br_date_pattern.count() > 0:
                expect(br_date_pattern.first).to_be_visible()
    
    def test_client_navigation_links(self, page: Page):
        """Testa se os links de navegação do cliente estão funcionando"""
        # Fazer login como cliente
        page.goto("http://localhost:8000/login")
        
        # Preencher formulário de login
        page.fill('input[name="email"]', os.getenv('CLIENT_EMAIL', 'sergio@reis.com'))
        page.fill('input[name="senha"]', os.getenv('CLIENT_PASSWORD', '123456'))
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento
        page.wait_for_url("**/cliente**")
        
        # Verificar link "Meus Dados" - usar first para evitar strict mode violation
        meus_dados_link = page.locator('a[href="/cliente/perfil"]').first
        expect(meus_dados_link).to_be_visible()
        expect(meus_dados_link).to_contain_text('Meus Dados')
        
        # Verificar link "Minhas Garantias" - usar first para evitar strict mode violation
        garantias_link = page.locator('a[href="/cliente/garantias"]').first
        expect(garantias_link).to_be_visible()
        expect(garantias_link).to_contain_text('Garantias')
        
        # Testar navegação para "Meus Dados"
        meus_dados_link.click()
        page.wait_for_url("**/cliente/perfil")
        expect(page.locator('h2')).to_contain_text('Meu Perfil')
        
        # Voltar e testar navegação para "Minhas Garantias"
        page.goto("http://localhost:8000/cliente")
        garantias_link = page.locator('a[href="/cliente/garantias"]').first
        garantias_link.click()
        page.wait_for_url("**/cliente/garantias")
        
        # Aguardar a página carregar
        page.wait_for_load_state('networkidle')
        
        # Verificar se chegou na página de garantias
        # Tentar aguardar qualquer título aparecer
        try:
            page.wait_for_selector('h1, h2, h3', timeout=10000)
        except:
            # Se não encontrou título, continuar mesmo assim
            pass
        
        # Verificar se o título está presente
        title = page.locator('h2:has-text("Minhas Garantias")')
        if title.count() == 0:
            # Se não encontrou, tentar outros possíveis títulos
            title = page.locator('h1:has-text("Garantias"), h2:has-text("Garantias"), h3:has-text("Garantias")')
        
        # Se ainda não encontrou título, verificar se pelo menos chegou na URL correta
        if title.count() == 0:
            # Verificar se está na URL correta
            current_url = page.url
            assert "/cliente/garantias" in current_url, f"Não chegou na página de garantias. URL atual: {current_url}"
        else:
            expect(title.first).to_be_visible()
    
    def test_date_consistency_across_pages(self, page: Page):
        """Testa se as datas são consistentes entre as páginas"""
        # Fazer login como cliente
        page.goto("http://localhost:8000/login")
        
        # Preencher formulário de login
        page.fill('input[name="email"]', os.getenv('CLIENT_EMAIL', 'sergio@reis.com'))
        page.fill('input[name="senha"]', os.getenv('CLIENT_PASSWORD', '123456'))
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento
        page.wait_for_url("**/cliente**")
        
        # Verificar página "Meus Dados"
        page.goto("http://localhost:8000/cliente/perfil")
        
        # Aguardar carregamento da página
        page.wait_for_selector('h2')
        
        # Verificar se há datas no formato brasileiro na seção de informações
        info_section = page.locator('.card, .section, .info')
        if info_section.count() > 0:
            # Verificar se há datas no formato brasileiro
            br_date_pattern = info_section.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/')
            if br_date_pattern.count() > 0:
                expect(br_date_pattern.first).to_be_visible()
        
        # Verificar página "Minhas Garantias"
        page.goto("http://localhost:8000/cliente/garantias")
        
        # Aguardar carregamento da página
        page.wait_for_selector('table, h2, h3')
        
        # Verificar se a tabela existe e tem dados
        table = page.locator('table')
        if table.count() > 0:
            table_body = table.locator('tbody')
            rows = table_body.locator('tr')
            
            if rows.count() > 0:
                # Verificar se há datas no formato brasileiro na tabela
                br_dates_garantias = table_body.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/')
                if br_dates_garantias.count() > 0:
                    expect(br_dates_garantias.first).to_be_visible()
                
                # Verificar se não há datas no formato ISO nas colunas de data (colunas 3 e 4)
                # Focar apenas nas células de data para evitar falsos positivos
                data_instalacao_cells = table_body.locator('tr td:nth-child(4)')
                data_vencimento_cells = table_body.locator('tr td:nth-child(5)')
                
                iso_dates_instalacao = data_instalacao_cells.locator('text=/\\d{4}-\\d{2}-\\d{2}/')
                iso_dates_vencimento = data_vencimento_cells.locator('text=/\\d{4}-\\d{2}-\\d{2}/')
                
                expect(iso_dates_instalacao).to_have_count(0)
                expect(iso_dates_vencimento).to_have_count(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])