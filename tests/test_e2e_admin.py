#!/usr/bin/env python3
"""
Testes E2E para funcionalidades administrativas
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
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD001', 'Produto Teste 1', True))
        
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD002', 'Produto Teste 2', False))
        
        # Veículo de teste
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (2, 'Toyota', 'Corolla', 2020, 'ABC1234', 'Branco', True))
        
        # Garantia de teste
        data_instalacao = datetime.now().date()
        data_vencimento = data_instalacao + timedelta(days=365)
        
        db.execute("""
            INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                 data_instalacao, data_vencimento, ativo, nota_fiscal, 
                                 nome_estabelecimento, quilometragem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 1, 1, 'LOTE001', data_instalacao.isoformat(), data_vencimento.isoformat(), True, 
              'NF123456', 'Oficina Teste', 50000))
        
        return db
    
    def start_server(self):
        """Inicia servidor de teste"""
        def run_server():
            try:
                # Garantir que a variável de ambiente está definida antes de importar
                os.environ['DATABASE_PATH'] = self.db_path
                from main import create_app
                app, config = create_app()
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8004, log_level="error")
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
    return "http://127.0.0.1:8004"

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
class TestAdminUsersE2E:
    """Testes E2E para gerenciamento de usuários"""
    
    def test_admin_users_list(self, logged_in_admin: Page, base_url: str):
        """Testa listagem de usuários"""
        page = logged_in_admin
        
        # Navegar para usuários
        page.goto(f"{base_url}/admin/usuarios")
        
        # Verificar título
        expect(page).to_have_title("Gerenciar Usuários - Sistema de Garantias")
        expect(page.locator("text=Gerenciar Usuários")).to_be_visible()
        
        # Verificar botão de novo usuário
        expect(page.locator("a[href='/admin/usuarios/novo']")).to_be_visible()
        
        # Verificar tabela de usuários
        expect(page.locator(".table")).to_be_visible()
        expect(page.locator("text=Admin Teste")).to_be_visible()
        expect(page.locator("text=Cliente Teste")).to_be_visible()
        expect(page.locator("text=admin@teste.com")).to_be_visible()
        expect(page.locator("text=cliente@teste.com")).to_be_visible()
    
    def test_admin_create_user_form(self, logged_in_admin: Page, base_url: str):
        """Testa formulário de criação de usuário"""
        page = logged_in_admin
        
        # Navegar para formulário
        page.goto(f"{base_url}/admin/usuarios/novo")
        
        # Verificar título
        expect(page).to_have_title("Novo Usuário - Sistema de Garantias")
        expect(page.locator("text=Novo Usuário")).to_be_visible()
        
        # Verificar campos
        expect(page.locator("input[name='nome']")).to_be_visible()
        expect(page.locator("input[name='email']")).to_be_visible()
        expect(page.locator("input[name='senha']")).to_be_visible()
        expect(page.locator("select[name='tipo_usuario']")).to_be_visible()
        expect(page.locator("input[name='telefone']")).to_be_visible()
        expect(page.locator("input[name='cpf_cnpj']")).to_be_visible()
    
    def test_admin_create_user_success(self, logged_in_admin: Page, base_url: str):
        """Testa criação bem-sucedida de usuário"""
        page = logged_in_admin
        
        # Navegar para formulário
        page.goto(f"{base_url}/admin/usuarios/novo")
        
        # Preencher formulário
        page.fill("input[name='nome']", "Novo Admin")
        page.fill("input[name='email']", "novoadmin@teste.com")
        page.fill("input[name='senha']", "senha123")
        page.select_option("select[name='tipo_usuario']", "admin")
        page.fill("input[name='telefone']", "(11) 99999-9999")
        page.fill("input[name='cpf_cnpj']", "123.456.789-00")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento e sucesso
        expect(page).to_have_url(f"{base_url}/admin/usuarios")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Usuário criado com sucesso")).to_be_visible()
        
        # Verificar na lista
        expect(page.locator("text=Novo Admin")).to_be_visible()
        expect(page.locator("text=novoadmin@teste.com")).to_be_visible()
    
    def test_admin_edit_user(self, logged_in_admin: Page, base_url: str):
        """Testa edição de usuário"""
        page = logged_in_admin
        
        # Navegar para lista
        page.goto(f"{base_url}/admin/usuarios")
        
        # Clicar em editar usuário cliente
        page.click("a[href='/admin/usuarios/2/editar']")
        
        # Verificar formulário preenchido
        expect(page.locator("input[name='nome']")).to_have_value("Cliente Teste")
        expect(page.locator("input[name='email']")).to_have_value("cliente@teste.com")
        
        # Modificar dados
        page.fill("input[name='nome']", "Cliente Modificado")
        
        # Submeter
        page.click("button[type='submit']")
        
        # Verificar sucesso
        expect(page).to_have_url(f"{base_url}/admin/usuarios")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Cliente Modificado")).to_be_visible()
    
    def test_admin_view_user_details(self, logged_in_admin: Page, base_url: str):
        """Testa visualização de detalhes do usuário"""
        page = logged_in_admin
        
        # Navegar para lista
        page.goto(f"{base_url}/admin/usuarios")
        
        # Clicar em ver detalhes
        page.click("a[href='/admin/usuarios/2']")
        
        # Verificar página de detalhes
        expect(page.locator("text=Detalhes do Usuário")).to_be_visible()
        expect(page.locator("text=Cliente Teste")).to_be_visible()
        expect(page.locator("text=cliente@teste.com")).to_be_visible()
        expect(page.locator("text=cliente")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestAdminProductsE2E:
    """Testes E2E para gerenciamento de produtos"""
    
    def test_admin_products_list(self, logged_in_admin: Page, base_url: str):
        """Testa listagem de produtos"""
        page = logged_in_admin
        
        # Navegar para produtos
        page.goto(f"{base_url}/admin/produtos")
        
        # Verificar título
        expect(page).to_have_title("Gerenciar Produtos - Sistema de Garantias")
        expect(page.locator("text=Gerenciar Produtos")).to_be_visible()
        
        # Verificar botão de novo produto
        expect(page.locator("a[href='/admin/produtos/novo']")).to_be_visible()
        
        # Verificar tabela de produtos
        expect(page.locator(".table")).to_be_visible()
        expect(page.locator("text=PROD001")).to_be_visible()
        expect(page.locator("text=PROD002")).to_be_visible()
        expect(page.locator("text=Produto Teste 1")).to_be_visible()
    
    def test_admin_create_product_success(self, logged_in_admin: Page, base_url: str):
        """Testa criação bem-sucedida de produto"""
        page = logged_in_admin
        
        # Navegar para formulário
        page.goto(f"{base_url}/admin/produtos/novo")
        
        # Preencher formulário
        page.fill("input[name='sku']", "PROD003")
        page.fill("input[name='descricao']", "Produto Teste 3")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento e sucesso
        expect(page).to_have_url(f"{base_url}/admin/produtos")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Produto criado com sucesso")).to_be_visible()
        
        # Verificar na lista
        expect(page.locator("text=PROD003")).to_be_visible()
        expect(page.locator("text=Produto Teste 3")).to_be_visible()
    
    def test_admin_edit_product(self, logged_in_admin: Page, base_url: str):
        """Testa edição de produto"""
        page = logged_in_admin
        
        # Navegar para lista
        page.goto(f"{base_url}/admin/produtos")
        
        # Clicar em editar
        page.click("a[href='/admin/produtos/1/editar']")
        
        # Verificar formulário preenchido
        expect(page.locator("input[name='sku']")).to_have_value("PROD001")
        expect(page.locator("input[name='descricao']")).to_have_value("Produto Teste 1")
        
        # Modificar descrição
        page.fill("input[name='descricao']", "Produto Modificado")
        
        # Submeter
        page.click("button[type='submit']")
        
        # Verificar sucesso
        expect(page).to_have_url(f"{base_url}/admin/produtos")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Produto Modificado")).to_be_visible()
    
    def test_admin_toggle_product_status(self, logged_in_admin: Page, base_url: str):
        """Testa ativação/desativação de produto"""
        page = logged_in_admin
        
        # Navegar para lista
        page.goto(f"{base_url}/admin/produtos")
        
        # Verificar status inicial do PROD002 (inativo)
        expect(page.locator("text=Inativo")).to_be_visible()
        
        # Clicar em ativar
        page.click("a[href='/admin/produtos/2/toggle']")
        
        # Verificar mudança de status
        expect(page.locator("text=Ativo")).to_be_visible()
        
        # Desativar novamente
        page.click("a[href='/admin/produtos/2/toggle']")
        
        # Verificar volta ao status inativo
        expect(page.locator("text=Inativo")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestAdminWarrantiesE2E:
    """Testes E2E para gerenciamento de garantias pelo admin"""
    
    def test_admin_warranties_list(self, logged_in_admin: Page, base_url: str):
        """Testa listagem de garantias pelo admin"""
        page = logged_in_admin
        
        # Navegar para garantias
        page.goto(f"{base_url}/admin/garantias")
        
        # Verificar título
        expect(page).to_have_title("Gerenciar Garantias - Sistema de Garantias")
        expect(page.locator("text=Gerenciar Garantias")).to_be_visible()
        
        # Verificar tabela de garantias
        expect(page.locator(".table")).to_be_visible()
        expect(page.locator("text=PROD001")).to_be_visible()
        expect(page.locator("text=Cliente Teste")).to_be_visible()
        expect(page.locator("text=Toyota Corolla")).to_be_visible()
    
    def test_admin_warranty_details(self, logged_in_admin: Page, base_url: str):
        """Testa visualização de detalhes da garantia"""
        page = logged_in_admin
        
        # Navegar para lista
        page.goto(f"{base_url}/admin/garantias")
        
        # Clicar em ver detalhes
        page.click("a[href='/admin/garantias/1']")
        
        # Verificar página de detalhes
        expect(page.locator("text=Detalhes da Garantia")).to_be_visible()
        expect(page.locator("text=LOTE001")).to_be_visible()
        expect(page.locator("text=NF123456")).to_be_visible()
        expect(page.locator("text=Oficina Teste")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestAdminReportsE2E:
    """Testes E2E para relatórios administrativos"""
    
    def test_admin_reports_page(self, logged_in_admin: Page, base_url: str):
        """Testa página de relatórios"""
        page = logged_in_admin
        
        # Navegar para relatórios
        page.goto(f"{base_url}/admin/relatorios")
        
        # Verificar título
        expect(page).to_have_title("Relatórios - Sistema de Garantias")
        expect(page.locator("text=Relatórios")).to_be_visible()
        
        # Verificar opções de relatórios
        expect(page.locator("text=Usuários")).to_be_visible()
        expect(page.locator("text=Garantias")).to_be_visible()
        expect(page.locator("text=Produtos")).to_be_visible()
    
    def test_admin_reports_filters(self, logged_in_admin: Page, base_url: str):
        """Testa filtros de relatórios"""
        page = logged_in_admin
        
        # Navegar para relatórios
        page.goto(f"{base_url}/admin/relatorios")
        
        # Verificar se existem filtros de data
        date_inputs = page.locator("input[type='date']")
        if date_inputs.count() > 0:
            expect(date_inputs.first).to_be_visible()
        
        # Verificar filtros de tipo
        select_filters = page.locator("select")
        if select_filters.count() > 0:
            expect(select_filters.first).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestAdminNavigationE2E:
    """Testes E2E para navegação administrativa"""
    
    def test_admin_sidebar_navigation(self, logged_in_admin: Page, base_url: str):
        """Testa navegação pela sidebar administrativa"""
        page = logged_in_admin
        
        # Verificar links da sidebar
        expect(page.locator("a[href='/admin']")).to_be_visible()
        expect(page.locator("a[href='/admin/usuarios']")).to_be_visible()
        expect(page.locator("a[href='/admin/produtos']")).to_be_visible()
        expect(page.locator("a[href='/admin/garantias']")).to_be_visible()
        expect(page.locator("a[href='/admin/relatorios']")).to_be_visible()
        
        # Testar navegação
        page.click("a[href='/admin/usuarios']")
        expect(page).to_have_url(f"{base_url}/admin/usuarios")
        
        page.click("a[href='/admin/produtos']")
        expect(page).to_have_url(f"{base_url}/admin/produtos")
        
        page.click("a[href='/admin']")
        expect(page).to_have_url(f"{base_url}/admin")
    
    def test_admin_breadcrumbs(self, logged_in_admin: Page, base_url: str):
        """Testa breadcrumbs na área administrativa"""
        page = logged_in_admin
        
        # Navegar para usuários
        page.goto(f"{base_url}/admin/usuarios")
        
        # Verificar breadcrumb
        breadcrumb = page.locator(".breadcrumb")
        if breadcrumb.count() > 0:
            expect(breadcrumb).to_be_visible()
            expect(page.locator("text=Admin")).to_be_visible()
            expect(page.locator("text=Usuários")).to_be_visible()
    
    def test_admin_responsive_design(self, logged_in_admin: Page, base_url: str):
        """Testa design responsivo da área administrativa"""
        page = logged_in_admin
        
        # Testar em mobile
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator("text=Dashboard Administrativo")).to_be_visible()
        
        # Verificar se menu mobile funciona
        mobile_menu = page.locator(".navbar-toggler, .menu-toggle")
        if mobile_menu.count() > 0:
            mobile_menu.click()
            expect(page.locator("a[href='/admin/usuarios']")).to_be_visible()
        
        # Voltar ao desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        expect(page.locator("text=Dashboard Administrativo")).to_be_visible()
    
    def test_admin_logout_functionality(self, logged_in_admin: Page, base_url: str):
        """Testa logout da área administrativa"""
        page = logged_in_admin
        
        # Fazer logout
        page.click("a[href='/logout']")
        
        # Verificar redirecionamento
        expect(page).to_have_url(f"{base_url}/login")
        
        # Tentar acessar área admin sem login
        page.goto(f"{base_url}/admin")
        expect(page).to_have_url(f"{base_url}/login")