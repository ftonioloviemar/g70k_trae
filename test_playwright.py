"""Testes com Playwright para a aplicação de garantias."""

import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import subprocess
import time
import os
import signal
from typing import Generator


class TestServer:
    """Classe para gerenciar o servidor de teste."""
    
    def __init__(self):
        self.process = None
        self.base_url = "http://localhost:8000"
    
    def start(self):
        """Inicia o servidor de teste."""
        # Mata qualquer processo existente na porta 5001
        try:
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                         capture_output=True, check=False)
        except:
            pass
        
        # Inicia o servidor
        self.process = subprocess.Popen(
            ["uv", "run", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # Aguarda o servidor iniciar
        time.sleep(3)
        
        # Verifica se o processo ainda está rodando
        if self.process.poll() is not None:
            stdout, stderr = self.process.communicate()
            raise Exception(f"Servidor falhou ao iniciar: {stderr.decode()}")
    
    def stop(self):
        """Para o servidor de teste."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except:
                pass


@pytest.fixture(scope="session")
def test_server() -> Generator[TestServer, None, None]:
    """Fixture para o servidor de teste."""
    server = TestServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """Fixture para o browser Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Fixture para o contexto do browser."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Fixture para a página."""
    page = context.new_page()
    yield page
    page.close()


class TestLogin:
    """Testes de login."""
    
    def test_login_page_loads(self, page: Page, test_server: TestServer):
        """Testa se a página de login carrega corretamente."""
        page.goto(test_server.base_url)
        
        # Verifica se a página de login carregou
        assert page.title() == "Sistema de Garantias Viemar"
        assert page.locator("h1").inner_text() == "Login"
        
        # Verifica se os campos estão presentes
        assert page.locator("input[name='email']").is_visible()
        assert page.locator("input[name='senha']").is_visible()
        assert page.locator("button[type='submit']").is_visible()
    
    def test_login_success(self, page: Page, test_server: TestServer):
        """Testa login com credenciais válidas."""
        page.goto(test_server.base_url)
        
        # Preenche o formulário de login
        page.fill("input[name='email']", "joao@teste.com")
        page.fill("input[name='senha']", "123456")
        
        # Clica no botão de login
        page.click("button[type='submit']")
        
        # Verifica se foi redirecionado para o dashboard
        page.wait_for_url(f"{test_server.base_url}/cliente/dashboard")
        assert "Dashboard" in page.content()
    
    def test_login_invalid_credentials(self, page: Page, test_server: TestServer):
        """Testa login com credenciais inválidas."""
        page.goto(test_server.base_url)
        
        # Preenche o formulário com credenciais inválidas
        page.fill("input[name='email']", "invalido@teste.com")
        page.fill("input[name='senha']", "senhaerrada")
        
        # Clica no botão de login
        page.click("button[type='submit']")
        
        # Verifica se permanece na página de login com mensagem de erro
        assert page.url == f"{test_server.base_url}/"
        assert "Email ou senha inválidos" in page.content()


class TestDashboard:
    """Testes do dashboard."""
    
    def login(self, page: Page, test_server: TestServer):
        """Faz login para acessar o dashboard."""
        page.goto(test_server.base_url)
        page.fill("input[name='email']", "joao@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        page.wait_for_url(f"{test_server.base_url}/cliente/dashboard")
    
    def test_dashboard_loads(self, page: Page, test_server: TestServer):
        """Testa se o dashboard carrega corretamente."""
        self.login(page, test_server)
        
        # Verifica se o dashboard carregou
        assert "Dashboard" in page.content()
        assert "Bem-vindo" in page.content()
        
        # Verifica se os links de navegação estão presentes
        assert page.locator("a[href='/cliente/garantias']").is_visible()
        assert page.locator("a[href='/cliente/dados']").is_visible()
    
    def test_navigation_to_garantias(self, page: Page, test_server: TestServer):
        """Testa navegação para a página de garantias."""
        self.login(page, test_server)
        
        # Clica no link de garantias
        page.click("a[href='/cliente/garantias']")
        
        # Verifica se foi redirecionado para a página de garantias
        page.wait_for_url(f"{test_server.base_url}/cliente/garantias")
        assert "Minhas Garantias" in page.content()
    
    def test_navigation_to_dados(self, page: Page, test_server: TestServer):
        """Testa navegação para a página de dados."""
        self.login(page, test_server)
        
        # Clica no link de dados
        page.click("a[href='/cliente/dados']")
        
        # Verifica se foi redirecionado para a página de dados
        page.wait_for_url(f"{test_server.base_url}/cliente/dados")
        assert "Meus Dados" in page.content()


class TestGarantias:
    """Testes da funcionalidade de garantias."""
    
    def login(self, page: Page, test_server: TestServer):
        """Faz login para acessar as garantias."""
        page.goto(test_server.base_url)
        page.fill("input[name='email']", "joao@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        page.wait_for_url(f"{test_server.base_url}/cliente/dashboard")
    
    def test_garantias_list_loads(self, page: Page, test_server: TestServer):
        """Testa se a lista de garantias carrega."""
        self.login(page, test_server)
        
        # Navega para garantias
        page.goto(f"{test_server.base_url}/cliente/garantias")
        
        # Verifica se a página carregou
        assert "Minhas Garantias" in page.content()
        
        # Verifica se há garantias listadas
        garantias = page.locator(".garantia-card, .card, [data-testid='garantia']")
        assert garantias.count() > 0
    
    def test_garantia_details_view(self, page: Page, test_server: TestServer):
        """Testa visualização dos detalhes de uma garantia."""
        self.login(page, test_server)
        
        # Navega para uma garantia específica
        page.goto(f"{test_server.base_url}/cliente/garantias/1")
        
        # Verifica se a página de detalhes carregou
        assert "Detalhes da Garantia" in page.content()
        
        # Verifica se informações da garantia estão presentes
        assert "Produto:" in page.content() or "Modelo:" in page.content()
        assert "Data de Compra:" in page.content() or "Compra:" in page.content()
    
    def test_garantia_access_control(self, page: Page, test_server: TestServer):
        """Testa controle de acesso às garantias."""
        self.login(page, test_server)
        
        # Tenta acessar uma garantia que não pertence ao usuário
        page.goto(f"{test_server.base_url}/cliente/garantias/999")
        
        # Verifica se foi redirecionado ou mostra erro
        assert (page.url == f"{test_server.base_url}/cliente/garantias" or 
                "não encontrada" in page.content().lower() or
                "acesso negado" in page.content().lower())


class TestResponsiveness:
    """Testes de responsividade para dispositivos móveis."""
    
    def login_mobile(self, page: Page, test_server: TestServer):
        """Faz login em dispositivo móvel."""
        page.goto(test_server.base_url)
        page.fill("input[name='email']", "joao@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        page.wait_for_url(f"{test_server.base_url}/cliente/dashboard")
    
    def test_mobile_login(self, browser: Browser, test_server: TestServer):
        """Testa login em dispositivo móvel."""
        # Simula dispositivo móvel
        context = browser.new_context(
            viewport={'width': 375, 'height': 667},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        )
        page = context.new_page()
        
        try:
            page.goto(test_server.base_url)
            
            # Verifica se a página é responsiva
            assert page.locator("input[name='email']").is_visible()
            assert page.locator("input[name='senha']").is_visible()
            
            # Faz login
            page.fill("input[name='email']", "joao@teste.com")
            page.fill("input[name='senha']", "123456")
            page.click("button[type='submit']")
            
            # Verifica se o login funcionou
            page.wait_for_url(f"{test_server.base_url}/cliente/dashboard")
            assert "Dashboard" in page.content()
        
        finally:
            page.close()
            context.close()
    
    def test_mobile_navigation(self, browser: Browser, test_server: TestServer):
        """Testa navegação em dispositivo móvel."""
        # Simula dispositivo móvel
        context = browser.new_context(
            viewport={'width': 375, 'height': 667},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        )
        page = context.new_page()
        
        try:
            self.login_mobile(page, test_server)
            
            # Testa navegação para garantias
            page.click("a[href='/cliente/garantias']")
            page.wait_for_url(f"{test_server.base_url}/cliente/garantias")
            assert "Minhas Garantias" in page.content()
            
            # Testa navegação para dados
            page.click("a[href='/cliente/dados']")
            page.wait_for_url(f"{test_server.base_url}/cliente/dados")
            assert "Meus Dados" in page.content()
        
        finally:
            page.close()
            context.close()


if __name__ == "__main__":
    # Executa os testes
    pytest.main(["-v", __file__])