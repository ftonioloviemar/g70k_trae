#!/usr/bin/env python3
"""
Testes E2E expandidos para garantias - CRUD completo
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
        
        # Segundo cliente
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('cliente2@teste.com', generate_password_hash('123456'), 'Cliente Dois', 'cliente', True))
        
        # Produtos de teste
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD001', 'Produto Teste 1', True))
        
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD002', 'Produto Teste 2', True))
        
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD003', 'Produto Inativo', False))
        
        # Veículos de teste
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (2, 'Toyota', 'Corolla', 2020, 'ABC1234', 'Branco', True))
        
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (2, 'Honda', 'Civic', 2019, 'DEF5678', 'Preto', True))
        
        db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, cor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (3, 'Ford', 'Focus', 2021, 'GHI9012', 'Azul', True))
        
        # Garantias de teste
        data_instalacao = datetime.now().date()
        data_vencimento = data_instalacao + timedelta(days=365)
        data_vencimento_expirada = data_instalacao - timedelta(days=30)
        
        # Garantia ativa
        db.execute("""
            INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                 data_instalacao, data_vencimento, ativo, nota_fiscal, 
                                 nome_estabelecimento, quilometragem, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 1, 1, 'LOTE001', data_instalacao.isoformat(), data_vencimento.isoformat(), True, 
              'NF123456', 'Oficina Teste', 50000, 'Garantia em dia'))
        
        # Garantia expirada
        db.execute("""
            INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                 data_instalacao, data_vencimento, ativo, nota_fiscal, 
                                 nome_estabelecimento, quilometragem, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 2, 2, 'LOTE002', (data_instalacao - timedelta(days=400)).isoformat(), data_vencimento_expirada.isoformat(), True, 
              'NF789012', 'Oficina Dois', 75000, 'Garantia expirada'))
        
        # Garantia inativa
        db.execute("""
            INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                 data_instalacao, data_vencimento, ativo, nota_fiscal, 
                                 nome_estabelecimento, quilometragem, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 1, 1, 'LOTE003', data_instalacao.isoformat(), data_vencimento.isoformat(), False, 
              'NF345678', 'Oficina Três', 60000, 'Garantia cancelada'))
        
        return db
    
    def start_server(self):
        """Inicia servidor de teste"""
        def run_server():
            try:
                from main import app
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8006, log_level="error")
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
    return "http://127.0.0.1:8006"

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
class TestWarrantyListingE2E:
    """Testes E2E para listagem de garantias"""
    
    def test_warranty_list_display(self, logged_in_client: Page, base_url: str):
        """Testa exibição da lista de garantias"""
        page = logged_in_client
        
        # Navegar para garantias
        page.goto(f"{base_url}/garantias")
        
        # Verificar título
        expect(page).to_have_title("Minhas Garantias - Sistema de Garantias")
        expect(page.locator("text=Minhas Garantias")).to_be_visible()
        
        # Verificar botão de nova garantia
        expect(page.locator("a[href='/garantias/nova']")).to_be_visible()
        
        # Verificar tabela de garantias
        expect(page.locator(".table")).to_be_visible()
        expect(page.locator("text=PROD001")).to_be_visible()
        expect(page.locator("text=PROD002")).to_be_visible()
        expect(page.locator("text=Toyota Corolla")).to_be_visible()
        expect(page.locator("text=Honda Civic")).to_be_visible()
    
    def test_warranty_status_display(self, logged_in_client: Page, base_url: str):
        """Testa exibição de status das garantias"""
        page = logged_in_client
        
        # Navegar para garantias
        page.goto(f"{base_url}/garantias")
        
        # Verificar diferentes status
        expect(page.locator(".badge-success, .text-success")).to_be_visible()  # Ativa
        expect(page.locator(".badge-danger, .text-danger")).to_be_visible()    # Expirada
        expect(page.locator(".badge-secondary, .text-muted")).to_be_visible()  # Inativa
    
    def test_warranty_search_functionality(self, logged_in_client: Page, base_url: str):
        """Testa funcionalidade de busca"""
        page = logged_in_client
        
        # Navegar para garantias
        page.goto(f"{base_url}/garantias")
        
        # Buscar por produto
        search_input = page.locator("input[name='busca'], input[placeholder*='buscar']").first
        if search_input.count() > 0:
            search_input.fill("PROD001")
            page.keyboard.press("Enter")
            
            # Verificar resultado da busca
            expect(page.locator("text=PROD001")).to_be_visible()
    
    def test_warranty_filter_by_status(self, logged_in_client: Page, base_url: str):
        """Testa filtro por status"""
        page = logged_in_client
        
        # Navegar para garantias
        page.goto(f"{base_url}/garantias")
        
        # Filtrar por status ativo
        status_filter = page.locator("select[name='status']")
        if status_filter.count() > 0:
            status_filter.select_option("ativo")
            
            # Verificar que apenas garantias ativas são exibidas
            expect(page.locator(".badge-success, .text-success")).to_be_visible()
    
    def test_warranty_pagination(self, logged_in_client: Page, base_url: str):
        """Testa paginação das garantias"""
        page = logged_in_client
        
        # Navegar para garantias
        page.goto(f"{base_url}/garantias")
        
        # Verificar se há paginação
        pagination = page.locator(".pagination")
        if pagination.count() > 0:
            expect(pagination).to_be_visible()
            
            # Testar navegação entre páginas
            next_page = page.locator("a:has-text('Próxima'), a:has-text('>')")
            if next_page.count() > 0:
                next_page.click()
                expect(page).to_have_url(f"{base_url}/garantias?page=2")

@pytest.mark.e2e
@pytest.mark.playwright
class TestWarrantyCreationE2E:
    """Testes E2E para criação de garantias"""
    
    def test_warranty_creation_form_display(self, logged_in_client: Page, base_url: str):
        """Testa exibição do formulário de criação"""
        page = logged_in_client
        
        # Navegar para nova garantia
        page.goto(f"{base_url}/garantias/nova")
        
        # Verificar título
        expect(page).to_have_title("Nova Garantia - Sistema de Garantias")
        expect(page.locator("text=Nova Garantia")).to_be_visible()
        
        # Verificar campos
        expect(page.locator("select[name='produto_id']")).to_be_visible()
        expect(page.locator("select[name='veiculo_id']")).to_be_visible()
        expect(page.locator("input[name='lote_fabricacao']")).to_be_visible()
        expect(page.locator("input[name='data_instalacao']")).to_be_visible()
        expect(page.locator("input[name='nota_fiscal']")).to_be_visible()
        expect(page.locator("input[name='nome_estabelecimento']")).to_be_visible()
        expect(page.locator("input[name='quilometragem']")).to_be_visible()
        expect(page.locator("textarea[name='observacoes']")).to_be_visible()
    
    def test_warranty_creation_success(self, logged_in_client: Page, base_url: str):
        """Testa criação bem-sucedida de garantia"""
        page = logged_in_client
        
        # Navegar para nova garantia
        page.goto(f"{base_url}/garantias/nova")
        
        # Preencher formulário
        page.select_option("select[name='produto_id']", "1")  # PROD001
        page.select_option("select[name='veiculo_id']", "1")   # Toyota Corolla
        page.fill("input[name='lote_fabricacao']", "LOTE004")
        page.fill("input[name='data_instalacao']", "2024-01-15")
        page.fill("input[name='nota_fiscal']", "NF999888")
        page.fill("input[name='nome_estabelecimento']", "Nova Oficina")
        page.fill("input[name='quilometragem']", "45000")
        page.fill("textarea[name='observacoes']", "Nova garantia de teste")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento e sucesso
        expect(page).to_have_url(f"{base_url}/garantias")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Garantia cadastrada com sucesso")).to_be_visible()
        
        # Verificar na lista
        expect(page.locator("text=LOTE004")).to_be_visible()
        expect(page.locator("text=Nova Oficina")).to_be_visible()
    
    def test_warranty_creation_validation(self, logged_in_client: Page, base_url: str):
        """Testa validações na criação de garantia"""
        page = logged_in_client
        
        # Navegar para nova garantia
        page.goto(f"{base_url}/garantias/nova")
        
        # Tentar submeter formulário vazio
        page.click("button[type='submit']")
        
        # Verificar mensagens de erro
        expect(page.locator(".alert-danger, .error")).to_be_visible()
        
        # Testar data de instalação futura
        page.select_option("select[name='produto_id']", "1")
        page.select_option("select[name='veiculo_id']", "1")
        page.fill("input[name='data_instalacao']", "2025-12-31")
        page.click("button[type='submit']")
        
        expect(page.locator("text=Data de instalação não pode ser futura")).to_be_visible()
    
    def test_warranty_creation_duplicate_lote(self, logged_in_client: Page, base_url: str):
        """Testa criação com lote duplicado"""
        page = logged_in_client
        
        # Navegar para nova garantia
        page.goto(f"{base_url}/garantias/nova")
        
        # Preencher com lote já existente
        page.select_option("select[name='produto_id']", "1")
        page.select_option("select[name='veiculo_id']", "1")
        page.fill("input[name='lote_fabricacao']", "LOTE001")  # Já existe
        page.fill("input[name='data_instalacao']", "2024-01-15")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar erro de lote duplicado
        expect(page.locator("text=Lote de fabricação já cadastrado")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestWarrantyDetailsE2E:
    """Testes E2E para visualização de detalhes da garantia"""
    
    def test_warranty_details_display(self, logged_in_client: Page, base_url: str):
        """Testa exibição dos detalhes da garantia"""
        page = logged_in_client
        
        # Navegar para lista
        page.goto(f"{base_url}/garantias")
        
        # Clicar em ver detalhes da primeira garantia
        page.click("a[href='/garantias/1']")
        
        # Verificar título
        expect(page).to_have_title("Detalhes da Garantia - Sistema de Garantias")
        expect(page.locator("text=Detalhes da Garantia")).to_be_visible()
        
        # Verificar informações da garantia
        expect(page.locator("text=LOTE001")).to_be_visible()
        expect(page.locator("text=PROD001")).to_be_visible()
        expect(page.locator("text=Toyota Corolla")).to_be_visible()
        expect(page.locator("text=NF123456")).to_be_visible()
        expect(page.locator("text=Oficina Teste")).to_be_visible()
        expect(page.locator("text=50000")).to_be_visible()  # Quilometragem
    
    def test_warranty_details_actions(self, logged_in_client: Page, base_url: str):
        """Testa ações disponíveis nos detalhes"""
        page = logged_in_client
        
        # Navegar para detalhes
        page.goto(f"{base_url}/garantias/1")
        
        # Verificar botões de ação
        expect(page.locator("a[href='/garantias/1/editar']")).to_be_visible()
        expect(page.locator("a[href='/garantias']")).to_be_visible()  # Voltar
        
        # Verificar botão de imprimir/exportar
        print_button = page.locator("button:has-text('Imprimir'), a:has-text('Exportar')")
        if print_button.count() > 0:
            expect(print_button.first).to_be_visible()
    
    def test_warranty_details_status_badge(self, logged_in_client: Page, base_url: str):
        """Testa exibição do status na página de detalhes"""
        page = logged_in_client
        
        # Navegar para garantia ativa
        page.goto(f"{base_url}/garantias/1")
        expect(page.locator(".badge-success, .text-success")).to_be_visible()
        
        # Navegar para garantia expirada
        page.goto(f"{base_url}/garantias/2")
        expect(page.locator(".badge-danger, .text-danger")).to_be_visible()
    
    def test_warranty_details_timeline(self, logged_in_client: Page, base_url: str):
        """Testa timeline/histórico da garantia"""
        page = logged_in_client
        
        # Navegar para detalhes
        page.goto(f"{base_url}/garantias/1")
        
        # Verificar se há seção de histórico
        timeline = page.locator(".timeline, .history")
        if timeline.count() > 0:
            expect(timeline).to_be_visible()
            expect(page.locator("text=Cadastrada em")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestWarrantyEditingE2E:
    """Testes E2E para edição de garantias"""
    
    def test_warranty_edit_form_display(self, logged_in_client: Page, base_url: str):
        """Testa exibição do formulário de edição"""
        page = logged_in_client
        
        # Navegar para edição
        page.goto(f"{base_url}/garantias/1/editar")
        
        # Verificar título
        expect(page).to_have_title("Editar Garantia - Sistema de Garantias")
        expect(page.locator("text=Editar Garantia")).to_be_visible()
        
        # Verificar campos preenchidos
        expect(page.locator("input[name='lote_fabricacao']")).to_have_value("LOTE001")
        expect(page.locator("input[name='nota_fiscal']")).to_have_value("NF123456")
        expect(page.locator("input[name='nome_estabelecimento']")).to_have_value("Oficina Teste")
        expect(page.locator("input[name='quilometragem']")).to_have_value("50000")
    
    def test_warranty_edit_success(self, logged_in_client: Page, base_url: str):
        """Testa edição bem-sucedida"""
        page = logged_in_client
        
        # Navegar para edição
        page.goto(f"{base_url}/garantias/1/editar")
        
        # Modificar dados
        page.fill("input[name='nome_estabelecimento']", "Oficina Modificada")
        page.fill("input[name='quilometragem']", "55000")
        page.fill("textarea[name='observacoes']", "Observação modificada")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento e sucesso
        expect(page).to_have_url(f"{base_url}/garantias/1")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Garantia atualizada com sucesso")).to_be_visible()
        
        # Verificar dados atualizados
        expect(page.locator("text=Oficina Modificada")).to_be_visible()
        expect(page.locator("text=55000")).to_be_visible()
    
    def test_warranty_edit_validation(self, logged_in_client: Page, base_url: str):
        """Testa validações na edição"""
        page = logged_in_client
        
        # Navegar para edição
        page.goto(f"{base_url}/garantias/1/editar")
        
        # Limpar campo obrigatório
        page.fill("input[name='lote_fabricacao']", "")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar erro
        expect(page.locator(".alert-danger, .error")).to_be_visible()
        expect(page.locator("text=Lote de fabricação é obrigatório")).to_be_visible()
    
    def test_warranty_edit_cancel(self, logged_in_client: Page, base_url: str):
        """Testa cancelamento da edição"""
        page = logged_in_client
        
        # Navegar para edição
        page.goto(f"{base_url}/garantias/1/editar")
        
        # Modificar dados
        page.fill("input[name='nome_estabelecimento']", "Teste Cancelar")
        
        # Cancelar
        page.click("a[href='/garantias/1']")
        
        # Verificar que voltou para detalhes sem salvar
        expect(page).to_have_url(f"{base_url}/garantias/1")
        expect(page.locator("text=Teste Cancelar")).not_to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestWarrantyDeletionE2E:
    """Testes E2E para exclusão/desativação de garantias"""
    
    def test_warranty_deactivation(self, logged_in_client: Page, base_url: str):
        """Testa desativação de garantia"""
        page = logged_in_client
        
        # Navegar para lista
        page.goto(f"{base_url}/garantias")
        
        # Clicar em desativar garantia ativa
        deactivate_button = page.locator("a[href='/garantias/1/desativar']")
        if deactivate_button.count() > 0:
            deactivate_button.click()
            
            # Confirmar desativação
            confirm_button = page.locator("button:has-text('Confirmar')")
            if confirm_button.count() > 0:
                confirm_button.click()
            
            # Verificar sucesso
            expect(page.locator(".alert-success")).to_be_visible()
            expect(page.locator("text=Garantia desativada")).to_be_visible()
    
    def test_warranty_reactivation(self, logged_in_client: Page, base_url: str):
        """Testa reativação de garantia"""
        page = logged_in_client
        
        # Navegar para lista
        page.goto(f"{base_url}/garantias")
        
        # Clicar em reativar garantia inativa
        reactivate_button = page.locator("a[href='/garantias/3/ativar']")
        if reactivate_button.count() > 0:
            reactivate_button.click()
            
            # Verificar sucesso
            expect(page.locator(".alert-success")).to_be_visible()
            expect(page.locator("text=Garantia reativada")).to_be_visible()
    
    def test_warranty_deletion_confirmation(self, logged_in_client: Page, base_url: str):
        """Testa confirmação de exclusão"""
        page = logged_in_client
        
        # Navegar para detalhes
        page.goto(f"{base_url}/garantias/3")
        
        # Clicar em excluir
        delete_button = page.locator("button:has-text('Excluir'), a:has-text('Excluir')")
        if delete_button.count() > 0:
            delete_button.click()
            
            # Verificar modal de confirmação
            expect(page.locator(".modal, .confirm-dialog")).to_be_visible()
            expect(page.locator("text=Tem certeza que deseja excluir")).to_be_visible()
            
            # Cancelar exclusão
            cancel_button = page.locator("button:has-text('Cancelar')")
            if cancel_button.count() > 0:
                cancel_button.click()
            
            # Verificar que ainda está na página
            expect(page).to_have_url(f"{base_url}/garantias/3")

@pytest.mark.e2e
@pytest.mark.playwright
class TestWarrantyResponsiveDesignE2E:
    """Testes E2E para design responsivo das garantias"""
    
    def test_warranty_list_mobile(self, logged_in_client: Page, base_url: str):
        """Testa lista de garantias em mobile"""
        page = logged_in_client
        
        # Configurar viewport mobile
        page.set_viewport_size({"width": 375, "height": 667})
        
        # Navegar para garantias
        page.goto(f"{base_url}/garantias")
        
        # Verificar que elementos são visíveis
        expect(page.locator("text=Minhas Garantias")).to_be_visible()
        expect(page.locator("a[href='/garantias/nova']")).to_be_visible()
        
        # Verificar se tabela se adapta ou vira cards
        table_or_cards = page.locator(".table, .card")
        expect(table_or_cards.first).to_be_visible()
    
    def test_warranty_form_tablet(self, logged_in_client: Page, base_url: str):
        """Testa formulário de garantia em tablet"""
        page = logged_in_client
        
        # Configurar viewport tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        
        # Navegar para nova garantia
        page.goto(f"{base_url}/garantias/nova")
        
        # Verificar que formulário é visível e usável
        expect(page.locator("text=Nova Garantia")).to_be_visible()
        expect(page.locator("select[name='produto_id']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()
    
    def test_warranty_details_responsive(self, logged_in_client: Page, base_url: str):
        """Testa detalhes da garantia em diferentes tamanhos"""
        page = logged_in_client
        
        # Navegar para detalhes
        page.goto(f"{base_url}/garantias/1")
        
        # Testar em diferentes tamanhos
        viewports = [
            {"width": 320, "height": 568},  # Mobile pequeno
            {"width": 768, "height": 1024}, # Tablet
            {"width": 1920, "height": 1080} # Desktop
        ]
        
        for viewport in viewports:
            page.set_viewport_size(viewport)
            expect(page.locator("text=Detalhes da Garantia")).to_be_visible()
            expect(page.locator("text=LOTE001")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestWarrantyBulkOperationsE2E:
    """Testes E2E para operações em lote"""
    
    def test_warranty_bulk_selection(self, logged_in_client: Page, base_url: str):
        """Testa seleção em lote de garantias"""
        page = logged_in_client
        
        # Navegar para lista
        page.goto(f"{base_url}/garantias")
        
        # Verificar checkboxes de seleção
        checkboxes = page.locator("input[type='checkbox'][name='selected[]']")
        if checkboxes.count() > 0:
            # Selecionar primeira garantia
            checkboxes.first.check()
            
            # Verificar que ações em lote aparecem
            bulk_actions = page.locator(".bulk-actions")
            if bulk_actions.count() > 0:
                expect(bulk_actions).to_be_visible()
    
    def test_warranty_bulk_export(self, logged_in_client: Page, base_url: str):
        """Testa exportação em lote"""
        page = logged_in_client
        
        # Navegar para lista
        page.goto(f"{base_url}/garantias")
        
        # Verificar botão de exportar todas
        export_button = page.locator("button:has-text('Exportar'), a:has-text('Exportar')")
        if export_button.count() > 0:
            expect(export_button.first).to_be_visible()
    
    def test_warranty_advanced_filters(self, logged_in_client: Page, base_url: str):
        """Testa filtros avançados"""
        page = logged_in_client
        
        # Navegar para lista
        page.goto(f"{base_url}/garantias")
        
        # Verificar filtros avançados
        advanced_filters = page.locator(".advanced-filters, .filter-panel")
        if advanced_filters.count() > 0:
            expect(advanced_filters).to_be_visible()
            
            # Testar filtro por data
            date_filter = page.locator("input[name='data_inicio']")
            if date_filter.count() > 0:
                date_filter.fill("2024-01-01")
                
                # Aplicar filtro
                apply_button = page.locator("button:has-text('Filtrar')")
                if apply_button.count() > 0:
                    apply_button.click()