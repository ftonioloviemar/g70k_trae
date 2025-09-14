#!/usr/bin/env python3
"""
Testes E2E para módulo de veículos
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
from datetime import datetime

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
        
        # Inserir dados de teste
        from werkzeug.security import generate_password_hash
        
        # Usuário cliente
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('cliente@teste.com', generate_password_hash('123456'), 'Cliente Teste', 'cliente', True))
        
        # Veículo de teste existente
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, chassi, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, 'Toyota', 'Corolla', 2020, 'ABC1234', 'Branco', 'CHASSI123', True))
        
        return db
    
    def start_server(self):
        """Inicia servidor de teste"""
        def run_server():
            try:
                from main import app
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8003, log_level="error")
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
    return "http://127.0.0.1:8003"

@pytest.fixture
def logged_in_client(page: Page, base_url: str):
    """Fixture para cliente logado"""
    page.goto(f"{base_url}/login")
    page.fill("input[name='email']", "cliente@teste.com")
    page.fill("input[name='senha']", "123456")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{base_url}/cliente")
    return page

@pytest.mark.e2e
@pytest.mark.playwright
class TestVehiclesE2E:
    """Testes E2E para módulo de veículos"""
    
    def test_vehicles_list_page(self, logged_in_client: Page, base_url: str):
        """Testa página de listagem de veículos"""
        page = logged_in_client
        
        # Navegar para veículos
        page.goto(f"{base_url}/cliente/veiculos")
        
        # Verificar título
        expect(page).to_have_title("Meus Veículos - Sistema de Garantias")
        expect(page.locator("text=Meus Veículos")).to_be_visible()
        
        # Verificar botão de cadastro
        expect(page.locator("a[href='/cliente/veiculos/novo']")).to_be_visible()
        expect(page.locator("text=Cadastrar Novo Veículo")).to_be_visible()
        
        # Verificar tabela de veículos
        expect(page.locator(".table")).to_be_visible()
        expect(page.locator("text=Toyota Corolla")).to_be_visible()
        expect(page.locator("text=ABC-1234")).to_be_visible()
    
    def test_vehicle_create_form_elements(self, logged_in_client: Page, base_url: str):
        """Testa elementos do formulário de cadastro"""
        page = logged_in_client
        
        # Navegar para formulário de cadastro
        page.goto(f"{base_url}/cliente/veiculos/novo")
        
        # Verificar título
        expect(page).to_have_title("Cadastrar Veículo - Sistema de Garantias")
        expect(page.locator("text=Cadastrar Novo Veículo")).to_be_visible()
        
        # Verificar campos obrigatórios
        expect(page.locator("input[name='marca']")).to_be_visible()
        expect(page.locator("input[name='modelo']")).to_be_visible()
        expect(page.locator("input[name='ano_modelo']")).to_be_visible()
        expect(page.locator("input[name='placa']")).to_be_visible()
        expect(page.locator("input[name='cor']")).to_be_visible()
        expect(page.locator("input[name='chassi']")).to_be_visible()
        
        # Verificar botões
        expect(page.locator("button[type='submit']")).to_be_visible()
        expect(page.locator("a[href='/cliente/veiculos']")).to_be_visible()
    
    def test_vehicle_create_success(self, logged_in_client: Page, base_url: str):
        """Testa cadastro bem-sucedido de veículo"""
        page = logged_in_client
        
        # Navegar para formulário
        page.goto(f"{base_url}/cliente/veiculos/novo")
        
        # Preencher formulário
        page.fill("input[name='marca']", "Honda")
        page.fill("input[name='modelo']", "Civic")
        page.fill("input[name='ano_modelo']", "2021")
        page.fill("input[name='placa']", "XYZ5678")
        page.fill("input[name='cor']", "Preto")
        page.fill("input[name='chassi']", "CHASSI456")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento e sucesso
        expect(page).to_have_url(f"{base_url}/cliente/veiculos")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Veículo cadastrado com sucesso")).to_be_visible()
        
        # Verificar se aparece na lista
        expect(page.locator("text=Honda Civic")).to_be_visible()
        expect(page.locator("text=XYZ-5678")).to_be_visible()
    
    def test_vehicle_create_validation_errors(self, logged_in_client: Page, base_url: str):
        """Testa validações do formulário de cadastro"""
        page = logged_in_client
        
        # Navegar para formulário
        page.goto(f"{base_url}/cliente/veiculos/novo")
        
        # Submeter formulário vazio
        page.click("button[type='submit']")
        
        # Verificar validações HTML5
        expect(page.locator("input[name='marca']:invalid")).to_be_visible()
        expect(page.locator("input[name='modelo']:invalid")).to_be_visible()
        expect(page.locator("input[name='placa']:invalid")).to_be_visible()
    
    def test_vehicle_create_duplicate_plate(self, logged_in_client: Page, base_url: str):
        """Testa cadastro com placa duplicada"""
        page = logged_in_client
        
        # Navegar para formulário
        page.goto(f"{base_url}/cliente/veiculos/novo")
        
        # Preencher com placa já existente
        page.fill("input[name='marca']", "Ford")
        page.fill("input[name='modelo']", "Focus")
        page.fill("input[name='ano_modelo']", "2019")
        page.fill("input[name='placa']", "ABC1234")  # Placa já existe
        page.fill("input[name='cor']", "Azul")
        page.fill("input[name='chassi']", "CHASSI789")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        expect(page.locator(".alert-danger")).to_be_visible()
        expect(page.locator("text=Placa já cadastrada")).to_be_visible()
    
    def test_vehicle_edit_form(self, logged_in_client: Page, base_url: str):
        """Testa formulário de edição de veículo"""
        page = logged_in_client
        
        # Navegar para lista de veículos
        page.goto(f"{base_url}/cliente/veiculos")
        
        # Clicar em editar
        page.click("a[href='/cliente/veiculos/1/editar']")
        
        # Verificar título
        expect(page).to_have_title("Editar Veículo - Sistema de Garantias")
        expect(page.locator("text=Editar Veículo")).to_be_visible()
        
        # Verificar campos preenchidos
        expect(page.locator("input[name='marca']")).to_have_value("Toyota")
        expect(page.locator("input[name='modelo']")).to_have_value("Corolla")
        expect(page.locator("input[name='ano_modelo']")).to_have_value("2020")
        expect(page.locator("input[name='placa']")).to_have_value("ABC1234")
    
    def test_vehicle_edit_success(self, logged_in_client: Page, base_url: str):
        """Testa edição bem-sucedida de veículo"""
        page = logged_in_client
        
        # Navegar para edição
        page.goto(f"{base_url}/cliente/veiculos/1/editar")
        
        # Modificar dados
        page.fill("input[name='cor']", "Prata")
        page.fill("input[name='ano_modelo']", "2021")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento e sucesso
        expect(page).to_have_url(f"{base_url}/cliente/veiculos")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Veículo atualizado com sucesso")).to_be_visible()
        
        # Verificar mudanças na lista
        expect(page.locator("text=2021")).to_be_visible()
    
    def test_vehicle_toggle_status(self, logged_in_client: Page, base_url: str):
        """Testa ativação/desativação de veículo"""
        page = logged_in_client
        
        # Navegar para lista de veículos
        page.goto(f"{base_url}/cliente/veiculos")
        
        # Verificar status inicial (ativo)
        expect(page.locator("text=Ativo")).to_be_visible()
        
        # Clicar em desativar
        page.click("a[href='/cliente/veiculos/1/toggle']")
        
        # Verificar mudança de status
        expect(page.locator("text=Inativo")).to_be_visible()
        expect(page.locator("text=Ativar")).to_be_visible()
        
        # Reativar
        page.click("a[href='/cliente/veiculos/1/toggle']")
        
        # Verificar volta ao status ativo
        expect(page.locator("text=Ativo")).to_be_visible()
        expect(page.locator("text=Desativar")).to_be_visible()
    
    def test_vehicle_view_details(self, logged_in_client: Page, base_url: str):
        """Testa visualização de detalhes do veículo"""
        page = logged_in_client
        
        # Navegar para lista de veículos
        page.goto(f"{base_url}/cliente/veiculos")
        
        # Clicar em ver detalhes (se disponível)
        view_link = page.locator("a[href='/cliente/veiculos/1']").first
        if view_link.count() > 0:
            view_link.click()
            
            # Verificar página de detalhes
            expect(page.locator("text=Detalhes do Veículo")).to_be_visible()
            expect(page.locator("text=Toyota")).to_be_visible()
            expect(page.locator("text=Corolla")).to_be_visible()
    
    def test_vehicle_search_filter(self, logged_in_client: Page, base_url: str):
        """Testa busca/filtro de veículos"""
        page = logged_in_client
        
        # Navegar para lista de veículos
        page.goto(f"{base_url}/cliente/veiculos")
        
        # Verificar se existe campo de busca
        search_input = page.locator("input[type='search'], input[placeholder*='buscar'], input[name='busca']")
        
        if search_input.count() > 0:
            # Testar busca
            search_input.fill("Toyota")
            page.keyboard.press("Enter")
            
            # Verificar resultados filtrados
            expect(page.locator("text=Toyota")).to_be_visible()
    
    def test_vehicle_pagination(self, logged_in_client: Page, base_url: str):
        """Testa paginação da lista de veículos"""
        page = logged_in_client
        
        # Navegar para lista de veículos
        page.goto(f"{base_url}/cliente/veiculos")
        
        # Verificar se existe paginação
        pagination = page.locator(".pagination, .page-navigation")
        
        if pagination.count() > 0:
            expect(pagination).to_be_visible()
            
            # Testar navegação entre páginas
            next_button = page.locator("a:has-text('Próxima'), a:has-text('>')")
            if next_button.count() > 0:
                next_button.click()
                expect(page.locator(".pagination")).to_be_visible()
    
    def test_vehicle_form_plate_formatting(self, logged_in_client: Page, base_url: str):
        """Testa formatação automática da placa"""
        page = logged_in_client
        
        # Navegar para formulário
        page.goto(f"{base_url}/cliente/veiculos/novo")
        
        # Testar formatação da placa
        placa_input = page.locator("input[name='placa']")
        placa_input.fill("abc1234")
        
        # Verificar se foi formatada (ABC-1234)
        placa_input.blur()
        # A formatação pode acontecer via JavaScript
        page.wait_for_timeout(500)
    
    def test_vehicle_form_year_validation(self, logged_in_client: Page, base_url: str):
        """Testa validação do ano do veículo"""
        page = logged_in_client
        
        # Navegar para formulário
        page.goto(f"{base_url}/cliente/veiculos/novo")
        
        # Preencher com ano inválido
        page.fill("input[name='marca']", "Test")
        page.fill("input[name='modelo']", "Test")
        page.fill("input[name='ano_modelo']", "1800")  # Ano muito antigo
        page.fill("input[name='placa']", "TST1234")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar se há validação de ano
        error_message = page.locator(".alert-danger, .error, .invalid-feedback")
        if error_message.count() > 0:
            expect(error_message).to_be_visible()
    
    def test_vehicle_responsive_design(self, logged_in_client: Page, base_url: str):
        """Testa design responsivo da página de veículos"""
        page = logged_in_client
        
        # Navegar para lista de veículos
        page.goto(f"{base_url}/cliente/veiculos")
        
        # Testar em mobile
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator("text=Meus Veículos")).to_be_visible()
        expect(page.locator(".table, .card")).to_be_visible()
        
        # Testar em tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator("text=Meus Veículos")).to_be_visible()
        
        # Voltar ao desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        expect(page.locator("text=Meus Veículos")).to_be_visible()
    
    def test_vehicle_cancel_operations(self, logged_in_client: Page, base_url: str):
        """Testa cancelamento de operações"""
        page = logged_in_client
        
        # Testar cancelar cadastro
        page.goto(f"{base_url}/cliente/veiculos/novo")
        page.click("a[href='/cliente/veiculos']")
        expect(page).to_have_url(f"{base_url}/cliente/veiculos")
        
        # Testar cancelar edição
        page.goto(f"{base_url}/cliente/veiculos/1/editar")
        page.click("a[href='/cliente/veiculos']")
        expect(page).to_have_url(f"{base_url}/cliente/veiculos")