#!/usr/bin/env python3
"""
Testes E2E para dashboard e navegação
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

# Reutilizar classe TestServer do arquivo anterior
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
        
        # Usuário cliente
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('cliente@teste.com', generate_password_hash('123456'), 'Cliente Teste', 'cliente', True))
        
        # Usuário admin
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('admin@teste.com', generate_password_hash('admin123'), 'Admin Teste', 'admin', True))
        
        # Produtos de teste
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD001', 'Produto Teste 1', True))
        
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD002', 'Produto Teste 2', True))
        
        # Veículos de teste
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (1, 'Toyota', 'Corolla', 2020, 'ABC1234', 'Branco', True))
        
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (1, 'Honda', 'Civic', 2019, 'XYZ5678', 'Preto', True))
        
        # Garantias de teste
        data_instalacao = datetime.now().date()
        data_vencimento = data_instalacao + timedelta(days=365)
        
        db.execute("""
            INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                 data_instalacao, data_vencimento, ativo, nota_fiscal, 
                                 nome_estabelecimento, quilometragem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, 1, 1, 'LOTE001', data_instalacao.isoformat(), data_vencimento.isoformat(), True, 
              'NF123456', 'Oficina Teste', 50000))
        
        db.execute("""
            INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                 data_instalacao, data_vencimento, ativo, nota_fiscal, 
                                 nome_estabelecimento, quilometragem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, 2, 2, 'LOTE002', data_instalacao.isoformat(), data_vencimento.isoformat(), True, 
              'NF789012', 'Oficina Teste 2', 30000))
        
        return db
    
    def start_server(self):
        """Inicia servidor de teste"""
        def run_server():
            try:
                from main import app
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")
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
    return "http://127.0.0.1:8002"

@pytest.fixture
def logged_in_client(page: Page, base_url: str):
    """Fixture para cliente logado"""
    page.goto(f"{base_url}/login")
    page.fill("input[name='email']", "cliente@teste.com")
    page.fill("input[name='senha']", "123456")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{base_url}/cliente")
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
class TestDashboardE2E:
    """Testes E2E para dashboard"""
    
    def test_client_dashboard_elements(self, logged_in_client: Page, base_url: str):
        """Testa elementos do dashboard do cliente"""
        page = logged_in_client
        
        # Verificar título
        expect(page).to_have_title("Dashboard - Sistema de Garantias")
        
        # Verificar elementos principais
        expect(page.locator("text=Dashboard do Cliente")).to_be_visible()
        expect(page.locator("text=Bem-vindo")).to_be_visible()
        
        # Verificar cards de estatísticas
        expect(page.locator(".card")).to_have_count_greater_than(0)
        
        # Verificar navegação
        expect(page.locator("a[href='/cliente/veiculos']")).to_be_visible()
        expect(page.locator("a[href='/cliente/garantias']")).to_be_visible()
        expect(page.locator("a[href='/cliente/perfil']")).to_be_visible()
    
    def test_client_dashboard_statistics(self, logged_in_client: Page, base_url: str):
        """Testa estatísticas no dashboard do cliente"""
        page = logged_in_client
        
        # Verificar estatísticas de veículos
        expect(page.locator("text=Veículos Cadastrados")).to_be_visible()
        expect(page.locator("text=2")).to_be_visible()  # 2 veículos de teste
        
        # Verificar estatísticas de garantias
        expect(page.locator("text=Garantias Ativas")).to_be_visible()
        expect(page.locator("text=2")).to_be_visible()  # 2 garantias de teste
    
    def test_admin_dashboard_elements(self, logged_in_admin: Page, base_url: str):
        """Testa elementos do dashboard administrativo"""
        page = logged_in_admin
        
        # Verificar título
        expect(page).to_have_title("Dashboard Administrativo - Sistema de Garantias")
        
        # Verificar elementos principais
        expect(page.locator("text=Dashboard Administrativo")).to_be_visible()
        
        # Verificar navegação administrativa
        expect(page.locator("a[href='/admin/usuarios']")).to_be_visible()
        expect(page.locator("a[href='/admin/produtos']")).to_be_visible()
        expect(page.locator("a[href='/admin/garantias']")).to_be_visible()
        expect(page.locator("a[href='/admin/relatorios']")).to_be_visible()
    
    def test_navigation_menu(self, logged_in_client: Page, base_url: str):
        """Testa menu de navegação"""
        page = logged_in_client
        
        # Verificar menu principal
        expect(page.locator(".navbar")).to_be_visible()
        expect(page.locator("a[href='/cliente']")).to_be_visible()
        expect(page.locator("a[href='/logout']")).to_be_visible()
        
        # Testar navegação para veículos
        page.click("a[href='/cliente/veiculos']")
        expect(page).to_have_url(f"{base_url}/cliente/veiculos")
        expect(page.locator("text=Meus Veículos")).to_be_visible()
        
        # Voltar ao dashboard
        page.click("a[href='/cliente']")
        expect(page).to_have_url(f"{base_url}/cliente")
    
    def test_responsive_dashboard(self, logged_in_client: Page, base_url: str):
        """Testa responsividade do dashboard"""
        page = logged_in_client
        
        # Testar em diferentes tamanhos de tela
        # Mobile
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator(".navbar")).to_be_visible()
        expect(page.locator(".card")).to_be_visible()
        
        # Tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator(".navbar")).to_be_visible()
        expect(page.locator(".card")).to_be_visible()
        
        # Desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        expect(page.locator(".navbar")).to_be_visible()
        expect(page.locator(".card")).to_be_visible()
    
    def test_breadcrumb_navigation(self, logged_in_client: Page, base_url: str):
        """Testa navegação por breadcrumbs"""
        page = logged_in_client
        
        # Navegar para veículos
        page.click("a[href='/cliente/veiculos']")
        
        # Verificar breadcrumb
        expect(page.locator(".breadcrumb")).to_be_visible()
        expect(page.locator("text=Dashboard")).to_be_visible()
        expect(page.locator("text=Veículos")).to_be_visible()
    
    def test_quick_actions(self, logged_in_client: Page, base_url: str):
        """Testa ações rápidas no dashboard"""
        page = logged_in_client
        
        # Verificar botões de ação rápida
        expect(page.locator("text=Cadastrar Veículo")).to_be_visible()
        expect(page.locator("text=Ativar Garantia")).to_be_visible()
        
        # Testar ação rápida - cadastrar veículo
        page.click("text=Cadastrar Veículo")
        expect(page).to_have_url(f"{base_url}/cliente/veiculos/novo")
    
    def test_recent_activities(self, logged_in_client: Page, base_url: str):
        """Testa seção de atividades recentes"""
        page = logged_in_client
        
        # Verificar seção de atividades recentes
        expect(page.locator("text=Últimas Garantias")).to_be_visible()
        
        # Verificar se mostra garantias recentes
        expect(page.locator(".table")).to_be_visible()
        expect(page.locator("text=PROD001")).to_be_visible()
        expect(page.locator("text=PROD002")).to_be_visible()
    
    def test_profile_access(self, logged_in_client: Page, base_url: str):
        """Testa acesso ao perfil do usuário"""
        page = logged_in_client
        
        # Clicar no perfil
        page.click("a[href='/cliente/perfil']")
        
        # Verificar página de perfil
        expect(page).to_have_url(f"{base_url}/cliente/perfil")
        expect(page.locator("text=Meu Perfil")).to_be_visible()
        expect(page.locator("input[name='nome']")).to_be_visible()
        expect(page.locator("input[name='email']")).to_be_visible()
    
    def test_search_functionality(self, logged_in_client: Page, base_url: str):
        """Testa funcionalidade de busca (se disponível)"""
        page = logged_in_client
        
        # Verificar se existe campo de busca
        search_input = page.locator("input[type='search'], input[placeholder*='buscar'], input[placeholder*='Buscar']")
        
        if search_input.count() > 0:
            # Testar busca
            search_input.fill("Toyota")
            page.keyboard.press("Enter")
            
            # Verificar resultados
            expect(page.locator("text=Toyota")).to_be_visible()
    
    def test_notifications_area(self, logged_in_client: Page, base_url: str):
        """Testa área de notificações (se disponível)"""
        page = logged_in_client
        
        # Verificar se existe área de notificações
        notifications = page.locator(".alert, .notification, .toast")
        
        if notifications.count() > 0:
            expect(notifications.first).to_be_visible()
    
    def test_help_documentation_access(self, logged_in_client: Page, base_url: str):
        """Testa acesso à documentação/ajuda"""
        page = logged_in_client
        
        # Verificar links de ajuda
        help_links = page.locator("a[href*='ajuda'], a[href*='help'], a[href*='suporte']")
        
        if help_links.count() > 0:
            expect(help_links.first).to_be_visible()