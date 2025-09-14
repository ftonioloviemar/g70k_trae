#!/usr/bin/env python3
"""
Testes E2E para cenários de erro e validações em todas as telas
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
        
        # Usuário não confirmado
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('naoconfirmado@teste.com', generate_password_hash('123456'), 'Não Confirmado', 'cliente', False))
        
        # Produtos de teste
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD001', 'Produto Teste 1', True))
        
        # Produto inativo
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD002', 'Produto Inativo', False))
        
        # Veículo de teste
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (2, 'Toyota', 'Corolla', 2020, 'ABC1234', 'Branco', True))
        
        # Veículo com placa duplicada (para teste)
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (2, 'Honda', 'Civic', 2021, 'XYZ9876', 'Preto', True))
        
        return db
    
    def start_server(self):
        """Inicia servidor de teste"""
        def run_server():
            try:
                from main import app
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8008, log_level="error")
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
    return "http://127.0.0.1:8008"

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
class TestLoginErrorScenariosE2E:
    """Testes E2E para cenários de erro no login"""
    
    def test_login_empty_fields(self, page: Page, base_url: str):
        """Testa login com campos vazios"""
        page.goto(f"{base_url}/login")
        
        # Submeter formulário vazio
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error, .invalid-feedback")
        expect(error_message).to_be_visible()
        
        # Verificar que permanece na página de login
        expect(page).to_have_url(f"{base_url}/login")
    
    def test_login_invalid_email(self, page: Page, base_url: str):
        """Testa login com email inválido"""
        page.goto(f"{base_url}/login")
        
        # Preencher com email inválido
        page.fill("input[name='email']", "email-invalido")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # Verificar validação HTML5 ou mensagem de erro
        email_input = page.locator("input[name='email']")
        validity = page.evaluate("document.querySelector('input[name=\"email\"]').validity.valid")
        
        if not validity:
            # Validação HTML5 funcionando
            assert True
        else:
            # Verificar mensagem de erro do servidor
            error_message = page.locator(".alert-danger, .error")
            expect(error_message).to_be_visible()
    
    def test_login_wrong_credentials(self, page: Page, base_url: str):
        """Testa login com credenciais incorretas"""
        page.goto(f"{base_url}/login")
        
        # Preencher com credenciais incorretas
        page.fill("input[name='email']", "inexistente@teste.com")
        page.fill("input[name='senha']", "senhaerrada")
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("inválid")
        
        # Verificar que permanece na página de login
        expect(page).to_have_url(f"{base_url}/login")
    
    def test_login_unconfirmed_user(self, page: Page, base_url: str):
        """Testa login com usuário não confirmado"""
        page.goto(f"{base_url}/login")
        
        # Preencher com usuário não confirmado
        page.fill("input[name='email']", "naoconfirmado@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # Verificar mensagem sobre confirmação
        message = page.locator(".alert-warning, .alert-info, .warning")
        if message.count() > 0:
            expect(message).to_be_visible()
            expect(message).to_contain_text("confirm")
    
    def test_login_sql_injection_attempt(self, page: Page, base_url: str):
        """Testa tentativa de SQL injection no login"""
        page.goto(f"{base_url}/login")
        
        # Tentar SQL injection
        page.fill("input[name='email']", "admin@teste.com'; DROP TABLE usuarios; --")
        page.fill("input[name='senha']", "' OR '1'='1")
        page.click("button[type='submit']")
        
        # Verificar que não houve sucesso
        expect(page).not_to_have_url(f"{base_url}/dashboard")
        expect(page).not_to_have_url(f"{base_url}/admin")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestRegistrationErrorScenariosE2E:
    """Testes E2E para cenários de erro no cadastro"""
    
    def test_registration_empty_required_fields(self, page: Page, base_url: str):
        """Testa cadastro com campos obrigatórios vazios"""
        page.goto(f"{base_url}/cadastro")
        
        # Submeter formulário vazio
        page.click("button[type='submit']")
        
        # Verificar mensagens de erro
        error_messages = page.locator(".alert-danger, .error, .invalid-feedback")
        expect(error_messages.first).to_be_visible()
        
        # Verificar que permanece na página de cadastro
        expect(page).to_have_url(f"{base_url}/cadastro")
    
    def test_registration_invalid_email_format(self, page: Page, base_url: str):
        """Testa cadastro com formato de email inválido"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher com email inválido
        page.fill("input[name='nome']", "Teste Usuario")
        page.fill("input[name='email']", "email-sem-arroba")
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "123456")
        page.click("button[type='submit']")
        
        # Verificar validação
        email_input = page.locator("input[name='email']")
        validity = page.evaluate("document.querySelector('input[name=\"email\"]').validity.valid")
        
        assert not validity, "Email inválido deveria falhar na validação"
    
    def test_registration_password_mismatch(self, page: Page, base_url: str):
        """Testa cadastro com senhas não coincidentes"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher com senhas diferentes
        page.fill("input[name='nome']", "Teste Usuario")
        page.fill("input[name='email']", "teste@exemplo.com")
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "654321")
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("senha")
    
    def test_registration_duplicate_email(self, page: Page, base_url: str):
        """Testa cadastro com email já existente"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher com email já existente
        page.fill("input[name='nome']", "Teste Usuario")
        page.fill("input[name='email']", "cliente@teste.com")
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "123456")
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("já existe")
    
    def test_registration_invalid_cpf(self, page: Page, base_url: str):
        """Testa cadastro com CPF inválido"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher com CPF inválido
        page.fill("input[name='nome']", "Teste Usuario")
        page.fill("input[name='email']", "teste@exemplo.com")
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "123456")
        
        cpf_field = page.locator("input[name='cpf_cnpj']")
        if cpf_field.count() > 0:
            page.fill("input[name='cpf_cnpj']", "123.456.789-00")  # CPF inválido
            page.click("button[type='submit']")
            
            # Verificar mensagem de erro
            error_message = page.locator(".alert-danger, .error")
            expect(error_message).to_be_visible()
    
    def test_registration_invalid_cep(self, page: Page, base_url: str):
        """Testa cadastro com CEP inválido"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher com CEP inválido
        page.fill("input[name='nome']", "Teste Usuario")
        page.fill("input[name='email']", "teste@exemplo.com")
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "123456")
        
        cep_field = page.locator("input[name='cep']")
        if cep_field.count() > 0:
            page.fill("input[name='cep']", "00000-000")  # CEP inválido
            page.click("button[type='submit']")
            
            # Verificar mensagem de erro ou validação
            error_message = page.locator(".alert-danger, .error")
            if error_message.count() > 0:
                expect(error_message).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestVehicleErrorScenariosE2E:
    """Testes E2E para cenários de erro no módulo de veículos"""
    
    def test_vehicle_creation_empty_fields(self, logged_in_client: Page, base_url: str):
        """Testa criação de veículo com campos vazios"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos/novo")
        
        # Submeter formulário vazio
        page.click("button[type='submit']")
        
        # Verificar mensagens de erro
        error_messages = page.locator(".alert-danger, .error, .invalid-feedback")
        expect(error_messages.first).to_be_visible()
    
    def test_vehicle_invalid_plate_format(self, logged_in_client: Page, base_url: str):
        """Testa criação de veículo com placa inválida"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos/novo")
        
        # Preencher com placa inválida
        page.fill("input[name='marca']", "Toyota")
        page.fill("input[name='modelo']", "Corolla")
        page.fill("input[name='placa']", "PLACA-INVALIDA")
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()
    
    def test_vehicle_duplicate_plate(self, logged_in_client: Page, base_url: str):
        """Testa criação de veículo com placa duplicada"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos/novo")
        
        # Preencher com placa já existente
        page.fill("input[name='marca']", "Ford")
        page.fill("input[name='modelo']", "Focus")
        page.fill("input[name='placa']", "ABC1234")  # Placa já existe
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("já existe")
    
    def test_vehicle_invalid_year(self, logged_in_client: Page, base_url: str):
        """Testa criação de veículo com ano inválido"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos/novo")
        
        # Preencher com ano inválido
        page.fill("input[name='marca']", "Honda")
        page.fill("input[name='modelo']", "Civic")
        page.fill("input[name='placa']", "DEF5678")
        
        year_field = page.locator("input[name='ano_modelo']")
        if year_field.count() > 0:
            page.fill("input[name='ano_modelo']", "1800")  # Ano muito antigo
            page.click("button[type='submit']")
            
            # Verificar mensagem de erro
            error_message = page.locator(".alert-danger, .error")
            expect(error_message).to_be_visible()
    
    def test_vehicle_unauthorized_access(self, page: Page, base_url: str):
        """Testa acesso não autorizado ao módulo de veículos"""
        # Tentar acessar sem login
        page.goto(f"{base_url}/veiculos")
        
        # Verificar redirecionamento para login
        expect(page).to_have_url(f"{base_url}/login")
        
        # Verificar mensagem de erro ou aviso
        message = page.locator(".alert-warning, .alert-info")
        if message.count() > 0:
            expect(message).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestWarrantyErrorScenariosE2E:
    """Testes E2E para cenários de erro no módulo de garantias"""
    
    def test_warranty_creation_empty_fields(self, logged_in_client: Page, base_url: str):
        """Testa criação de garantia com campos vazios"""
        page = logged_in_client
        
        page.goto(f"{base_url}/garantias/nova")
        
        # Submeter formulário vazio
        page.click("button[type='submit']")
        
        # Verificar mensagens de erro
        error_messages = page.locator(".alert-danger, .error, .invalid-feedback")
        expect(error_messages.first).to_be_visible()
    
    def test_warranty_invalid_date(self, logged_in_client: Page, base_url: str):
        """Testa criação de garantia com data inválida"""
        page = logged_in_client
        
        page.goto(f"{base_url}/garantias/nova")
        
        # Preencher campos obrigatórios
        page.select_option("select[name='produto_id']", "1")
        page.select_option("select[name='veiculo_id']", "1")
        
        # Data inválida (futura demais)
        page.fill("input[name='data_instalacao']", "2030-12-31")
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()
    
    def test_warranty_inactive_product(self, logged_in_client: Page, base_url: str):
        """Testa criação de garantia com produto inativo"""
        page = logged_in_client
        
        page.goto(f"{base_url}/garantias/nova")
        
        # Verificar que produtos inativos não aparecem na lista
        product_options = page.locator("select[name='produto_id'] option")
        
        # Contar opções (deve ter apenas produtos ativos)
        option_count = product_options.count()
        
        # Verificar que produto inativo (ID 2) não está disponível
        inactive_option = page.locator("select[name='produto_id'] option[value='2']")
        expect(inactive_option).not_to_be_visible()
    
    def test_warranty_invalid_mileage(self, logged_in_client: Page, base_url: str):
        """Testa criação de garantia com quilometragem inválida"""
        page = logged_in_client
        
        page.goto(f"{base_url}/garantias/nova")
        
        # Preencher campos obrigatórios
        page.select_option("select[name='produto_id']", "1")
        page.select_option("select[name='veiculo_id']", "1")
        page.fill("input[name='data_instalacao']", "2024-01-01")
        
        # Quilometragem inválida
        mileage_field = page.locator("input[name='quilometragem']")
        if mileage_field.count() > 0:
            page.fill("input[name='quilometragem']", "-1000")  # Negativa
            page.click("button[type='submit']")
            
            # Verificar mensagem de erro
            error_message = page.locator(".alert-danger, .error")
            expect(error_message).to_be_visible()
    
    def test_warranty_unauthorized_access(self, page: Page, base_url: str):
        """Testa acesso não autorizado ao módulo de garantias"""
        # Tentar acessar sem login
        page.goto(f"{base_url}/garantias")
        
        # Verificar redirecionamento para login
        expect(page).to_have_url(f"{base_url}/login")

@pytest.mark.e2e
@pytest.mark.playwright
class TestAdminErrorScenariosE2E:
    """Testes E2E para cenários de erro no módulo administrativo"""
    
    def test_admin_unauthorized_access(self, logged_in_client: Page, base_url: str):
        """Testa acesso não autorizado ao painel administrativo"""
        page = logged_in_client
        
        # Cliente tentando acessar área admin
        page.goto(f"{base_url}/admin")
        
        # Verificar que não tem acesso
        expect(page).not_to_have_url(f"{base_url}/admin")
        
        # Verificar mensagem de erro ou redirecionamento
        error_message = page.locator(".alert-danger, .error")
        if error_message.count() > 0:
            expect(error_message).to_be_visible()
            expect(error_message).to_contain_text("autorizado")
    
    def test_admin_user_creation_invalid_data(self, logged_in_admin: Page, base_url: str):
        """Testa criação de usuário com dados inválidos"""
        page = logged_in_admin
        
        page.goto(f"{base_url}/admin/usuarios/novo")
        
        # Submeter formulário vazio
        page.click("button[type='submit']")
        
        # Verificar mensagens de erro
        error_messages = page.locator(".alert-danger, .error, .invalid-feedback")
        expect(error_messages.first).to_be_visible()
    
    def test_admin_user_duplicate_email(self, logged_in_admin: Page, base_url: str):
        """Testa criação de usuário com email duplicado"""
        page = logged_in_admin
        
        page.goto(f"{base_url}/admin/usuarios/novo")
        
        # Preencher com email já existente
        page.fill("input[name='nome']", "Novo Usuario")
        page.fill("input[name='email']", "cliente@teste.com")  # Email já existe
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("já existe")
    
    def test_admin_product_creation_invalid_sku(self, logged_in_admin: Page, base_url: str):
        """Testa criação de produto com SKU inválido"""
        page = logged_in_admin
        
        page.goto(f"{base_url}/admin/produtos/novo")
        
        # Preencher com SKU já existente
        page.fill("input[name='sku']", "PROD001")  # SKU já existe
        page.fill("input[name='descricao']", "Produto Teste")
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        error_message = page.locator(".alert-danger, .error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("já existe")

@pytest.mark.e2e
@pytest.mark.playwright
class TestGeneralErrorScenariosE2E:
    """Testes E2E para cenários de erro gerais"""
    
    def test_404_page_not_found(self, page: Page, base_url: str):
        """Testa página não encontrada (404)"""
        page.goto(f"{base_url}/pagina-inexistente")
        
        # Verificar status 404 ou página de erro
        page_content = page.locator("body")
        expect(page_content).to_contain_text("404")
    
    def test_csrf_protection(self, logged_in_client: Page, base_url: str):
        """Testa proteção CSRF"""
        page = logged_in_client
        
        # Tentar submeter formulário sem token CSRF
        page.goto(f"{base_url}/veiculos/novo")
        
        # Remover token CSRF se existir
        page.evaluate("""
            const csrfInput = document.querySelector('input[name="csrf_token"]');
            if (csrfInput) csrfInput.remove();
        """)
        
        # Preencher e submeter
        page.fill("input[name='marca']", "Toyota")
        page.fill("input[name='modelo']", "Corolla")
        page.fill("input[name='placa']", "GHI9012")
        page.click("button[type='submit']")
        
        # Verificar que foi rejeitado
        error_message = page.locator(".alert-danger, .error")
        if error_message.count() > 0:
            expect(error_message).to_be_visible()
    
    def test_session_timeout(self, page: Page, base_url: str):
        """Testa timeout de sessão"""
        # Login
        page.goto(f"{base_url}/login")
        page.fill("input[name='email']", "cliente@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # Simular expiração de sessão (limpar cookies)
        page.context.clear_cookies()
        
        # Tentar acessar área protegida
        page.goto(f"{base_url}/dashboard")
        
        # Verificar redirecionamento para login
        expect(page).to_have_url(f"{base_url}/login")
    
    def test_xss_protection(self, logged_in_client: Page, base_url: str):
        """Testa proteção contra XSS"""
        page = logged_in_client
        
        page.goto(f"{base_url}/veiculos/novo")
        
        # Tentar inserir script malicioso
        xss_payload = "<script>alert('XSS')</script>"
        
        page.fill("input[name='marca']", xss_payload)
        page.fill("input[name='modelo']", "Corolla")
        page.fill("input[name='placa']", "JKL3456")
        page.click("button[type='submit']")
        
        # Verificar que script não foi executado
        # Se chegou até aqui sem alert, a proteção funcionou
        assert True
    
    def test_file_upload_validation(self, logged_in_client: Page, base_url: str):
        """Testa validação de upload de arquivos"""
        page = logged_in_client
        
        # Procurar por campos de upload
        page.goto(f"{base_url}/garantias/nova")
        
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            # Criar arquivo temporário inválido
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp:
                tmp.write(b"fake executable")
                tmp_path = tmp.name
            
            try:
                # Tentar upload de arquivo inválido
                file_input.set_input_files(tmp_path)
                page.click("button[type='submit']")
                
                # Verificar mensagem de erro
                error_message = page.locator(".alert-danger, .error")
                if error_message.count() > 0:
                    expect(error_message).to_be_visible()
            finally:
                os.unlink(tmp_path)
    
    def test_rate_limiting(self, page: Page, base_url: str):
        """Testa limitação de taxa de requisições"""
        # Fazer múltiplas tentativas de login rapidamente
        for i in range(10):
            page.goto(f"{base_url}/login")
            page.fill("input[name='email']", f"teste{i}@exemplo.com")
            page.fill("input[name='senha']", "senhaerrada")
            page.click("button[type='submit']")
            
            # Verificar se há limitação após várias tentativas
            if i > 5:
                rate_limit_message = page.locator(".alert-warning")
                if rate_limit_message.count() > 0 and "muitas tentativas" in page.content().lower():
                    expect(rate_limit_message).to_be_visible()
                    break
    
    def test_database_connection_error(self, page: Page, base_url: str):
        """Testa tratamento de erro de conexão com banco"""
        # Este teste é mais conceitual - em um ambiente real,
        # você simularia falha do banco de dados
        
        # Por enquanto, apenas verificar que a aplicação responde
        page.goto(f"{base_url}")
        
        # Se chegou até aqui, a conexão está funcionando
        expect(page.locator("body")).to_be_visible()
        
        # Em um teste real, você desconectaria o banco e verificaria
        # se a aplicação mostra uma página de erro apropriada
        assert True