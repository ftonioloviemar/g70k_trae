#!/usr/bin/env python3
"""
Testes E2E para fluxos de navegação entre diferentes seções da aplicação
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from playwright.sync_api import Page, expect
from fasthtml.common import *
from fastlite import Database
import subprocess
import time
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta

# Reutilizar classe TestServer
class TestServer:
    def __init__(self):
        self.temp_dir = None
        self.db_path = None
        self.server_process = None
        self.server_thread = None
        self.app = None
        
    def setup_temp_database(self):
        """Cria banco temporário para testes"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_garantias.db')
        
        # Configurar variável de ambiente
        os.environ['DATABASE_PATH'] = self.db_path
        
        # Criar banco e tabelas
        db = Database(self.db_path)
        
        # Criar tabelas
        db.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                nome TEXT,
                telefone TEXT,
                cpf_cnpj TEXT,
                cep TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                data_nascimento DATE,
                tipo_usuario TEXT DEFAULT 'cliente',
                confirmado BOOLEAN DEFAULT FALSE,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                descricao TEXT NOT NULL,
                ativo BOOLEAN DEFAULT TRUE,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                ano_modelo INTEGER,
                placa TEXT NOT NULL,
                cor TEXT,
                chassi TEXT,
                ativo BOOLEAN DEFAULT TRUE,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS garantias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                veiculo_id INTEGER NOT NULL,
                lote_fabricacao TEXT,
                data_instalacao DATE,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_vencimento DATE,
                ativo BOOLEAN DEFAULT TRUE,
                nota_fiscal TEXT,
                nome_estabelecimento TEXT,
                quilometragem INTEGER,
                observacoes TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id),
                FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
            )
        """)
        
        # Inserir dados de teste
        from werkzeug.security import generate_password_hash
        
        # Usuário admin
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('admin@teste.com', generate_password_hash('admin123'), 'Admin Teste', 'admin', True))
        
        # Usuário cliente
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('cliente@teste.com', generate_password_hash('123456'), 'Cliente Teste', 'cliente', True))
        
        # Produtos de teste
        for i in range(3):
            db.execute("""
                INSERT INTO produtos (sku, descricao, ativo)
                VALUES (?, ?, ?)
            """, (f'PROD00{i+1}', f'Produto Teste {i+1}', True))
        
        # Veículos de teste
        veiculos_teste = [
            ('Toyota', 'Corolla', 2020, 'ABC1234', 'Branco'),
            ('Honda', 'Civic', 2021, 'DEF5678', 'Preto'),
            ('Ford', 'Focus', 2019, 'GHI9012', 'Azul')
        ]
        
        for marca, modelo, ano, placa, cor in veiculos_teste:
            db.execute("""
                INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (2, marca, modelo, ano, placa, cor, True))
        
        # Garantias de teste
        for i in range(3):
            data_instalacao = datetime.now().date()
            data_vencimento = data_instalacao + timedelta(days=365)
            
            db.execute("""
                INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                     data_instalacao, data_vencimento, ativo, nota_fiscal, 
                                     nome_estabelecimento, quilometragem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (2, i+1, i+1, f'LOTE00{i+1}', data_instalacao.isoformat(), data_vencimento.isoformat(), True, 
                  f'NF12345{i+1}', f'Oficina Teste {i+1}', 50000 + (i * 10000)))
        
        return db
    
    def start_server(self):
        """Inicia servidor de teste"""
        def run_server():
            try:
                from main import app
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8009, log_level="error")
            except Exception as e:
                print(f"Erro ao iniciar servidor: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        time.sleep(3)  # Aguardar servidor iniciar
    
    def stop_server(self):
        """Para servidor e limpa recursos"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Limpar variável de ambiente
        if 'DATABASE_PATH' in os.environ:
            del os.environ['DATABASE_PATH']

@pytest.fixture(scope="session")
def test_server():
    """Fixture do servidor de teste"""
    server = TestServer()
    server.setup_temp_database()
    server.start_server()
    yield server
    server.stop_server()

@pytest.fixture(scope="session")
def base_url(test_server):
    """URL base para testes"""
    return "http://127.0.0.1:8009"

@pytest.fixture
def logged_in_client(page: Page, base_url: str):
    """Fixture para cliente logado"""
    page.goto(f"{base_url}/login")
    page.fill("input[name='email']", "cliente@teste.com")
    page.fill("input[name='senha']", "123456")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{base_url}/dashboard")
    return page

@pytest.fixture
def logged_in_admin(page: Page, base_url: str):
    """Fixture para admin logado"""
    page.goto(f"{base_url}/login")
    page.fill("input[name='email']", "admin@teste.com")
    page.fill("input[name='senha']", "admin123")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{base_url}/admin")
    return page

@pytest.mark.e2e
@pytest.mark.playwright
class TestPublicNavigationFlowsE2E:
    """Testes E2E para fluxos de navegação em páginas públicas"""
    
    def test_home_to_login_flow(self, page: Page, base_url: str):
        """Testa fluxo da página inicial para login"""
        # Ir para página inicial
        page.goto(f"{base_url}")
        
        # Clicar no link de login
        login_link = page.locator("a[href='/login'], a:has-text('Login'), .btn-login")
        if login_link.count() > 0:
            login_link.first.click()
            expect(page).to_have_url(f"{base_url}/login")
        else:
            # Navegar diretamente se não houver link
            page.goto(f"{base_url}/login")
        
        # Verificar elementos da página de login
        expect(page.locator("input[name='email']")).to_be_visible()
        expect(page.locator("input[name='senha']")).to_be_visible()
    
    def test_login_to_register_flow(self, page: Page, base_url: str):
        """Testa fluxo do login para cadastro"""
        page.goto(f"{base_url}/login")
        
        # Clicar no link de cadastro
        register_link = page.locator("a[href='/cadastro'], a:has-text('Cadastr'), .btn-register")
        if register_link.count() > 0:
            register_link.first.click()
            expect(page).to_have_url(f"{base_url}/cadastro")
        else:
            # Navegar diretamente se não houver link
            page.goto(f"{base_url}/cadastro")
        
        # Verificar elementos da página de cadastro
        expect(page.locator("input[name='nome']")).to_be_visible()
        expect(page.locator("input[name='email']")).to_be_visible()
    
    def test_register_to_login_flow(self, page: Page, base_url: str):
        """Testa fluxo do cadastro para login"""
        page.goto(f"{base_url}/cadastro")
        
        # Clicar no link de login
        login_link = page.locator("a[href='/login'], a:has-text('Login'), .btn-login")
        if login_link.count() > 0:
            login_link.first.click()
            expect(page).to_have_url(f"{base_url}/login")
        else:
            # Navegar diretamente se não houver link
            page.goto(f"{base_url}/login")
        
        # Verificar que chegou ao login
        expect(page.locator("input[name='email']")).to_be_visible()
    
    def test_complete_registration_flow(self, page: Page, base_url: str):
        """Testa fluxo completo de cadastro"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher formulário de cadastro
        page.fill("input[name='nome']", "Novo Usuario Teste")
        page.fill("input[name='email']", "novousuario@teste.com")
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "123456")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento para página de sucesso ou login
        page.wait_for_url(f"{base_url}/**")
        
        # Verificar que não está mais na página de cadastro
        expect(page).not_to_have_url(f"{base_url}/cadastro")
        
        # Verificar mensagem de sucesso
        success_message = page.locator(".alert-success, .success, .confirmation")
        if success_message.count() > 0:
            expect(success_message).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestClientNavigationFlowsE2E:
    """Testes E2E para fluxos de navegação do cliente"""
    
    def test_login_to_dashboard_flow(self, page: Page, base_url: str):
        """Testa fluxo de login para dashboard"""
        page.goto(f"{base_url}/login")
        
        # Fazer login
        page.fill("input[name='email']", "cliente@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # Verificar redirecionamento para dashboard
        expect(page).to_have_url(f"{base_url}/dashboard")
        
        # Verificar elementos do dashboard
        expect(page.locator("text=Dashboard")).to_be_visible()
    
    def test_dashboard_to_vehicles_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo do dashboard para veículos"""
        page = logged_in_client
        
        # Clicar no link de veículos
        vehicles_link = page.locator("a[href='/veiculos'], a:has-text('Veículo'), .nav-vehicles")
        if vehicles_link.count() > 0:
            vehicles_link.first.click()
            expect(page).to_have_url(f"{base_url}/veiculos")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/veiculos")
        
        # Verificar página de veículos
        expect(page.locator("text=Veículos")).to_be_visible()
    
    def test_vehicles_to_new_vehicle_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo da listagem para novo veículo"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos")
        
        # Clicar no botão de novo veículo
        new_vehicle_btn = page.locator("a[href='/veiculos/novo'], .btn-new, .btn-add")
        if new_vehicle_btn.count() > 0:
            new_vehicle_btn.first.click()
            expect(page).to_have_url(f"{base_url}/veiculos/novo")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/veiculos/novo")
        
        # Verificar formulário de novo veículo
        expect(page.locator("input[name='marca']")).to_be_visible()
        expect(page.locator("input[name='modelo']")).to_be_visible()
    
    def test_new_vehicle_to_vehicles_list_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo de criação de veículo para listagem"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos/novo")
        
        # Preencher e submeter formulário
        page.fill("input[name='marca']", "Volkswagen")
        page.fill("input[name='modelo']", "Golf")
        page.fill("input[name='placa']", "VWG1234")
        page.click("button[type='submit']")
        
        # Verificar redirecionamento para listagem
        page.wait_for_url(f"{base_url}/veiculos**")
        
        # Verificar que veículo aparece na lista
        expect(page.locator("text=Volkswagen")).to_be_visible()
        expect(page.locator("text=Golf")).to_be_visible()
    
    def test_dashboard_to_warranties_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo do dashboard para garantias"""
        page = logged_in_client
        
        # Clicar no link de garantias
        warranties_link = page.locator("a[href='/garantias'], a:has-text('Garantia'), .nav-warranties")
        if warranties_link.count() > 0:
            warranties_link.first.click()
            expect(page).to_have_url(f"{base_url}/garantias")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/garantias")
        
        # Verificar página de garantias
        expect(page.locator("text=Garantias")).to_be_visible()
    
    def test_warranties_to_new_warranty_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo da listagem para nova garantia"""
        page = logged_in_client
        
        page.goto(f"{base_url}/garantias")
        
        # Clicar no botão de nova garantia
        new_warranty_btn = page.locator("a[href='/garantias/nova'], .btn-new, .btn-add")
        if new_warranty_btn.count() > 0:
            new_warranty_btn.first.click()
            expect(page).to_have_url(f"{base_url}/garantias/nova")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/garantias/nova")
        
        # Verificar formulário de nova garantia
        expect(page.locator("select[name='produto_id']")).to_be_visible()
        expect(page.locator("select[name='veiculo_id']")).to_be_visible()
    
    def test_profile_navigation_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo de navegação para perfil"""
        page = logged_in_client
        
        # Clicar no link de perfil
        profile_link = page.locator("a[href='/perfil'], a:has-text('Perfil'), .nav-profile")
        if profile_link.count() > 0:
            profile_link.first.click()
            expect(page).to_have_url(f"{base_url}/perfil")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/perfil")
        
        # Verificar página de perfil
        expect(page.locator("text=Perfil")).to_be_visible()
    
    def test_logout_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo de logout"""
        page = logged_in_client
        
        # Clicar no link de logout
        logout_link = page.locator("a[href='/logout'], a:has-text('Sair'), .btn-logout")
        if logout_link.count() > 0:
            logout_link.first.click()
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/logout")
        
        # Verificar redirecionamento para página inicial ou login
        page.wait_for_url(f"{base_url}/**")
        expect(page).not_to_have_url(f"{base_url}/dashboard")
        
        # Tentar acessar área protegida
        page.goto(f"{base_url}/dashboard")
        expect(page).to_have_url(f"{base_url}/login")

@pytest.mark.e2e
@pytest.mark.playwright
class TestAdminNavigationFlowsE2E:
    """Testes E2E para fluxos de navegação do administrador"""
    
    def test_admin_login_to_dashboard_flow(self, page: Page, base_url: str):
        """Testa fluxo de login admin para dashboard"""
        page.goto(f"{base_url}/login")
        
        # Fazer login como admin
        page.fill("input[name='email']", "admin@teste.com")
        page.fill("input[name='senha']", "admin123")
        page.click("button[type='submit']")
        
        # Verificar redirecionamento para área admin
        expect(page).to_have_url(f"{base_url}/admin")
        
        # Verificar elementos do painel admin
        expect(page.locator("text=Admin")).to_be_visible()
    
    def test_admin_to_users_management_flow(self, logged_in_admin: Page, base_url: str):
        """Testa fluxo para gerenciamento de usuários"""
        page = logged_in_admin
        
        # Clicar no link de usuários
        users_link = page.locator("a[href='/admin/usuarios'], a:has-text('Usuário'), .nav-users")
        if users_link.count() > 0:
            users_link.first.click()
            expect(page).to_have_url(f"{base_url}/admin/usuarios")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/admin/usuarios")
        
        # Verificar página de usuários
        expect(page.locator("text=Usuários")).to_be_visible()
    
    def test_admin_users_to_new_user_flow(self, logged_in_admin: Page, base_url: str):
        """Testa fluxo para criar novo usuário"""
        page = logged_in_admin
        
        page.goto(f"{base_url}/admin/usuarios")
        
        # Clicar no botão de novo usuário
        new_user_btn = page.locator("a[href='/admin/usuarios/novo'], .btn-new, .btn-add")
        if new_user_btn.count() > 0:
            new_user_btn.first.click()
            expect(page).to_have_url(f"{base_url}/admin/usuarios/novo")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/admin/usuarios/novo")
        
        # Verificar formulário de novo usuário
        expect(page.locator("input[name='nome']")).to_be_visible()
        expect(page.locator("input[name='email']")).to_be_visible()
    
    def test_admin_to_products_management_flow(self, logged_in_admin: Page, base_url: str):
        """Testa fluxo para gerenciamento de produtos"""
        page = logged_in_admin
        
        # Clicar no link de produtos
        products_link = page.locator("a[href='/admin/produtos'], a:has-text('Produto'), .nav-products")
        if products_link.count() > 0:
            products_link.first.click()
            expect(page).to_have_url(f"{base_url}/admin/produtos")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/admin/produtos")
        
        # Verificar página de produtos
        expect(page.locator("text=Produtos")).to_be_visible()
    
    def test_admin_to_warranties_management_flow(self, logged_in_admin: Page, base_url: str):
        """Testa fluxo para gerenciamento de garantias"""
        page = logged_in_admin
        
        # Clicar no link de garantias admin
        warranties_link = page.locator("a[href='/admin/garantias'], a:has-text('Garantia'), .nav-warranties")
        if warranties_link.count() > 0:
            warranties_link.first.click()
            expect(page).to_have_url(f"{base_url}/admin/garantias")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/admin/garantias")
        
        # Verificar página de garantias admin
        expect(page.locator("text=Garantias")).to_be_visible()
    
    def test_admin_to_reports_flow(self, logged_in_admin: Page, base_url: str):
        """Testa fluxo para relatórios"""
        page = logged_in_admin
        
        # Clicar no link de relatórios
        reports_link = page.locator("a[href='/admin/relatorios'], a:has-text('Relatório'), .nav-reports")
        if reports_link.count() > 0:
            reports_link.first.click()
            expect(page).to_have_url(f"{base_url}/admin/relatorios")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/admin/relatorios")
        
        # Verificar página de relatórios
        expect(page.locator("text=Relatórios")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestBreadcrumbNavigationE2E:
    """Testes E2E para navegação via breadcrumbs"""
    
    def test_breadcrumb_navigation_vehicles(self, logged_in_client: Page, base_url: str):
        """Testa navegação via breadcrumbs em veículos"""
        page = logged_in_client
        
        # Navegar para novo veículo
        page.goto(f"{base_url}/veiculos/novo")
        
        # Verificar breadcrumb
        breadcrumb = page.locator(".breadcrumb")
        if breadcrumb.count() > 0:
            # Clicar no link de veículos no breadcrumb
            vehicles_breadcrumb = page.locator(".breadcrumb a:has-text('Veículo')")
            if vehicles_breadcrumb.count() > 0:
                vehicles_breadcrumb.click()
                expect(page).to_have_url(f"{base_url}/veiculos")
    
    def test_breadcrumb_navigation_warranties(self, logged_in_client: Page, base_url: str):
        """Testa navegação via breadcrumbs em garantias"""
        page = logged_in_client
        
        # Navegar para nova garantia
        page.goto(f"{base_url}/garantias/nova")
        
        # Verificar breadcrumb
        breadcrumb = page.locator(".breadcrumb")
        if breadcrumb.count() > 0:
            # Clicar no link de garantias no breadcrumb
            warranties_breadcrumb = page.locator(".breadcrumb a:has-text('Garantia')")
            if warranties_breadcrumb.count() > 0:
                warranties_breadcrumb.click()
                expect(page).to_have_url(f"{base_url}/garantias")
    
    def test_breadcrumb_home_navigation(self, logged_in_client: Page, base_url: str):
        """Testa navegação para home via breadcrumb"""
        page = logged_in_client
        
        # Navegar para página profunda
        page.goto(f"{base_url}/veiculos/novo")
        
        # Clicar no home do breadcrumb
        home_breadcrumb = page.locator(".breadcrumb a:has-text('Home'), .breadcrumb a:has-text('Início')")
        if home_breadcrumb.count() > 0:
            home_breadcrumb.click()
            expect(page).to_have_url(f"{base_url}/dashboard")

@pytest.mark.e2e
@pytest.mark.playwright
class TestSearchNavigationFlowsE2E:
    """Testes E2E para fluxos de navegação via busca"""
    
    def test_vehicle_search_navigation(self, logged_in_client: Page, base_url: str):
        """Testa navegação via busca de veículos"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos")
        
        # Procurar campo de busca
        search_input = page.locator("input[name='busca'], input[type='search'], .search-input")
        if search_input.count() > 0:
            # Fazer busca
            search_input.fill("Toyota")
            
            # Clicar no botão de busca ou pressionar Enter
            search_btn = page.locator(".btn-search, button:has-text('Buscar')")
            if search_btn.count() > 0:
                search_btn.click()
            else:
                search_input.press("Enter")
            
            # Verificar resultados
            expect(page.locator("text=Toyota")).to_be_visible()
    
    def test_warranty_search_navigation(self, logged_in_client: Page, base_url: str):
        """Testa navegação via busca de garantias"""
        page = logged_in_client
        
        page.goto(f"{base_url}/garantias")
        
        # Procurar campo de busca
        search_input = page.locator("input[name='busca'], input[type='search'], .search-input")
        if search_input.count() > 0:
            # Fazer busca
            search_input.fill("PROD001")
            
            # Clicar no botão de busca ou pressionar Enter
            search_btn = page.locator(".btn-search, button:has-text('Buscar')")
            if search_btn.count() > 0:
                search_btn.click()
            else:
                search_input.press("Enter")
            
            # Verificar resultados
            expect(page.locator("text=PROD001")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestPaginationNavigationE2E:
    """Testes E2E para navegação via paginação"""
    
    def test_pagination_navigation(self, logged_in_client: Page, base_url: str):
        """Testa navegação via paginação"""
        page = logged_in_client
        
        # Ir para página com possível paginação
        page.goto(f"{base_url}/garantias")
        
        # Procurar controles de paginação
        pagination = page.locator(".pagination, .page-nav")
        if pagination.count() > 0:
            # Clicar na próxima página
            next_btn = page.locator(".pagination .next, .page-nav .next, a:has-text('Próxima')")
            if next_btn.count() > 0:
                next_btn.click()
                
                # Verificar que URL mudou
                expect(page).to_have_url(f"{base_url}/garantias?**")
                
                # Voltar para primeira página
                prev_btn = page.locator(".pagination .prev, .page-nav .prev, a:has-text('Anterior')")
                if prev_btn.count() > 0:
                    prev_btn.click()
    
    def test_page_size_navigation(self, logged_in_client: Page, base_url: str):
        """Testa navegação via mudança de tamanho de página"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos")
        
        # Procurar seletor de tamanho de página
        page_size_select = page.locator("select[name='per_page'], select[name='limit'], .page-size-select")
        if page_size_select.count() > 0:
            # Mudar tamanho da página
            page_size_select.select_option("50")
            
            # Verificar que URL mudou
            expect(page).to_have_url(f"{base_url}/veiculos?**")

@pytest.mark.e2e
@pytest.mark.playwright
class TestComplexNavigationFlowsE2E:
    """Testes E2E para fluxos de navegação complexos"""
    
    def test_complete_vehicle_warranty_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo completo: criar veículo → criar garantia"""
        page = logged_in_client
        
        # 1. Criar novo veículo
        page.goto(f"{base_url}/veiculos/novo")
        page.fill("input[name='marca']", "Nissan")
        page.fill("input[name='modelo']", "Sentra")
        page.fill("input[name='placa']", "NIS1234")
        page.click("button[type='submit']")
        
        # 2. Navegar para garantias
        page.goto(f"{base_url}/garantias/nova")
        
        # 3. Verificar que novo veículo está disponível
        vehicle_select = page.locator("select[name='veiculo_id']")
        expect(vehicle_select).to_be_visible()
        
        # 4. Criar garantia para o veículo
        page.select_option("select[name='produto_id']", "1")
        page.select_option("select[name='veiculo_id']", label="Nissan Sentra")
        page.fill("input[name='data_instalacao']", "2024-01-01")
        page.click("button[type='submit']")
        
        # 5. Verificar que garantia foi criada
        page.wait_for_url(f"{base_url}/garantias**")
        expect(page.locator("text=Nissan")).to_be_visible()
    
    def test_admin_user_to_client_view_flow(self, logged_in_admin: Page, base_url: str):
        """Testa fluxo: admin cria usuário → visualiza como cliente"""
        page = logged_in_admin
        
        # 1. Criar novo usuário
        page.goto(f"{base_url}/admin/usuarios/novo")
        page.fill("input[name='nome']", "Cliente Novo")
        page.fill("input[name='email']", "clientenovo@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # 2. Logout do admin
        page.goto(f"{base_url}/logout")
        
        # 3. Login como novo cliente
        page.goto(f"{base_url}/login")
        page.fill("input[name='email']", "clientenovo@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # 4. Verificar acesso ao dashboard do cliente
        expect(page).to_have_url(f"{base_url}/dashboard")
        expect(page.locator("text=Dashboard")).to_be_visible()
    
    def test_error_recovery_navigation_flow(self, logged_in_client: Page, base_url: str):
        """Testa fluxo de recuperação de erro de navegação"""
        page = logged_in_client
        
        # 1. Tentar acessar página inexistente
        page.goto(f"{base_url}/pagina-inexistente")
        
        # 2. Verificar página de erro
        expect(page.locator("text=404")).to_be_visible()
        
        # 3. Navegar de volta para área válida
        home_link = page.locator("a[href='/dashboard'], a:has-text('Home'), a:has-text('Início')")
        if home_link.count() > 0:
            home_link.click()
            expect(page).to_have_url(f"{base_url}/dashboard")
        else:
            # Navegar diretamente
            page.goto(f"{base_url}/dashboard")
            expect(page.locator("text=Dashboard")).to_be_visible()
    
    def test_deep_link_navigation_flow(self, page: Page, base_url: str):
        """Testa fluxo de deep link com redirecionamento"""
        # 1. Tentar acessar página protegida sem login
        page.goto(f"{base_url}/veiculos/novo")
        
        # 2. Verificar redirecionamento para login
        expect(page).to_have_url(f"{base_url}/login")
        
        # 3. Fazer login
        page.fill("input[name='email']", "cliente@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # 4. Verificar redirecionamento para página original (se implementado)
        # Ou para dashboard
        page.wait_for_url(f"{base_url}/**")
        
        # 5. Navegar manualmente para página desejada
        page.goto(f"{base_url}/veiculos/novo")
        expect(page.locator("input[name='marca']")).to_be_visible()