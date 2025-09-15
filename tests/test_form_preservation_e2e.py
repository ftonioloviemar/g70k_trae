#!/usr/bin/env python3
"""
Testes E2E para preservação de dados em formulários após erros de validação
"""

import pytest
from playwright.sync_api import Page, expect
from tests.conftest import TestClient


class TestFormPreservationE2E:
    """Testes E2E para preservação de dados em formulários"""
    
    def test_cadastro_form_preserves_data_on_validation_error(self, page: Page, test_client: TestClient):
        """Testa se o formulário de cadastro preserva dados quando há erro de validação"""
        # Navegar para a página de cadastro
        page.goto(f"{test_client.base_url}/cadastro")
        
        # Preencher o formulário com dados válidos, exceto senhas que não conferem
        page.fill('input[name="nome"]', 'João Silva')
        page.fill('input[name="email"]', 'joao@teste.com')
        page.fill('input[name="confirmar_email"]', 'joao@teste.com')
        page.fill('input[name="cep"]', '12345-678')
        page.fill('input[name="endereco"]', 'Rua das Flores, 123')
        page.fill('input[name="bairro"]', 'Centro')
        page.fill('input[name="cidade"]', 'São Paulo')
        page.select_option('select[name="uf"]', 'SP')
        page.fill('input[name="telefone"]', '(11) 99999-9999')
        page.fill('input[name="cpf_cnpj"]', '123.456.789-00')
        page.fill('input[name="data_nascimento"]', '1990-01-01')
        page.fill('input[name="senha"]', '123456')
        page.fill('input[name="confirmar_senha"]', '654321')  # Senha diferente para gerar erro
        
        # Submeter o formulário
        page.click('button[type="submit"]')
        
        # Aguardar a página recarregar com erros
        page.wait_for_load_state('networkidle')
        
        # Verificar se há mensagem de erro
        expect(page.locator('text=Corrija os erros abaixo')).to_be_visible()
        
        # Verificar se os dados foram preservados
        expect(page.locator('input[name="nome"]')).to_have_value('João Silva')
        expect(page.locator('input[name="email"]')).to_have_value('joao@teste.com')
        expect(page.locator('input[name="confirmar_email"]')).to_have_value('joao@teste.com')
        expect(page.locator('input[name="cep"]')).to_have_value('12345-678')
        expect(page.locator('input[name="endereco"]')).to_have_value('Rua das Flores, 123')
        expect(page.locator('input[name="bairro"]')).to_have_value('Centro')
        expect(page.locator('input[name="cidade"]')).to_have_value('São Paulo')
        expect(page.locator('select[name="uf"]')).to_have_value('SP')
        expect(page.locator('input[name="telefone"]')).to_have_value('(11) 99999-9999')
        expect(page.locator('input[name="cpf_cnpj"]')).to_have_value('123.456.789-00')
        expect(page.locator('input[name="data_nascimento"]')).to_have_value('1990-01-01')
        
        # As senhas devem estar vazias por segurança
        expect(page.locator('input[name="senha"]')).to_have_value('')
        expect(page.locator('input[name="confirmar_senha"]')).to_have_value('')
    
    def test_login_form_preserves_email_on_error(self, page: Page, test_client: TestClient):
        """Testa se o formulário de login preserva o email quando há erro de autenticação"""
        # Navegar para a página de login
        page.goto(f"{test_client.base_url}/login")
        
        # Preencher com email válido e senha inválida
        page.fill('input[name="email"]', 'usuario@teste.com')
        page.fill('input[name="senha"]', 'senha_errada')
        
        # Submeter o formulário
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento e carregamento
        page.wait_for_load_state('networkidle')
        
        # Verificar se há mensagem de erro
        expect(page.locator('text=Email ou senha incorretos')).to_be_visible()
        
        # Verificar se o email foi preservado
        expect(page.locator('input[name="email"]')).to_have_value('usuario@teste.com')
        
        # A senha deve estar vazia por segurança
        expect(page.locator('input[name="senha"]')).to_have_value('')
    
    def test_cadastro_form_multiple_errors_preserve_data(self, page: Page, test_client: TestClient):
        """Testa preservação de dados com múltiplos erros de validação"""
        # Navegar para a página de cadastro
        page.goto(f"{test_client.base_url}/cadastro")
        
        # Preencher apenas alguns campos (deixar campos obrigatórios vazios)
        page.fill('input[name="nome"]', 'Maria Santos')
        page.fill('input[name="email"]', 'email_invalido')  # Email inválido
        page.fill('input[name="confirmar_email"]', 'outro_email@teste.com')  # Email diferente
        page.fill('input[name="cidade"]', 'Rio de Janeiro')
        page.select_option('select[name="uf"]', 'RJ')
        page.fill('input[name="senha"]', '123')  # Senha muito curta
        
        # Submeter o formulário
        page.click('button[type="submit"]')
        
        # Aguardar a página recarregar com erros
        page.wait_for_load_state('networkidle')
        
        # Verificar se há mensagem de erro
        expect(page.locator('text=Corrija os erros abaixo')).to_be_visible()
        
        # Verificar se os dados preenchidos foram preservados
        expect(page.locator('input[name="nome"]')).to_have_value('Maria Santos')
        expect(page.locator('input[name="email"]')).to_have_value('email_invalido')
        expect(page.locator('input[name="confirmar_email"]')).to_have_value('outro_email@teste.com')
        expect(page.locator('input[name="cidade"]')).to_have_value('Rio de Janeiro')
        expect(page.locator('select[name="uf"]')).to_have_value('RJ')
        
        # Campos não preenchidos devem continuar vazios
        expect(page.locator('input[name="cep"]')).to_have_value('')
        expect(page.locator('input[name="endereco"]')).to_have_value('')
        expect(page.locator('input[name="bairro"]')).to_have_value('')
        
        # Senhas devem estar vazias por segurança
        expect(page.locator('input[name="senha"]')).to_have_value('')
        expect(page.locator('input[name="confirmar_senha"]')).to_have_value('')
    
    def test_successful_form_submission_clears_data(self, page: Page, test_client: TestClient):
        """Testa que após submissão bem-sucedida, o usuário é redirecionado (não fica no formulário)"""
        # Navegar para a página de cadastro
        page.goto(f"{test_client.base_url}/cadastro")
        
        # Preencher o formulário com dados válidos
        unique_email = f'usuario_teste_{page.evaluate("Date.now()")}@teste.com'
        
        page.fill('input[name="nome"]', 'Usuário Teste')
        page.fill('input[name="email"]', unique_email)
        page.fill('input[name="confirmar_email"]', unique_email)
        page.fill('input[name="senha"]', '123456')
        page.fill('input[name="confirmar_senha"]', '123456')
        
        # Submeter o formulário
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento
        page.wait_for_load_state('networkidle')
        
        # Verificar se foi redirecionado para página de sucesso ou confirmação
        # (não deve estar mais na página de cadastro)
        current_url = page.url
        assert '/cadastro' not in current_url, f"Usuário ainda está na página de cadastro: {current_url}"