#!/usr/bin/env python3
"""
Testes E2E para gestão de usuários (cadastro, edição, perfil)
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
        
        # Inserir dados de teste
        from werkzeug.security import generate_password_hash
        
        # Usuário admin
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('admin@teste.com', generate_password_hash('admin123'), 'Admin Teste', 'admin', True))
        
        # Usuário cliente
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado, telefone, cpf_cnpj, cep, endereco, cidade, estado, data_nascimento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('cliente@teste.com', generate_password_hash('123456'), 'Cliente Teste', 'cliente', True, 
              '(11) 99999-9999', '123.456.789-00', '01234-567', 'Rua Teste, 123', 'São Paulo', 'SP', '1990-01-01'))
        
        return db
    
    def start_server(self):
        """Inicia servidor de teste"""
        def run_server():
            try:
                from main import app
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8005, log_level="error")
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
    return "http://127.0.0.1:8005"

@pytest.fixture
def logged_in_client(page: Page, base_url: str):
    """Fixture para cliente logado"""
    page.goto(f"{base_url}/login")
    page.fill("input[name='email']", "cliente@teste.com")
    page.fill("input[name='senha']", "123456")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{base_url}/dashboard")
    return page

@pytest.mark.e2e
@pytest.mark.playwright
class TestUserRegistrationE2E:
    """Testes E2E para cadastro de usuários"""
    
    def test_user_registration_form_display(self, page: Page, base_url: str):
        """Testa exibição do formulário de cadastro"""
        page.goto(f"{base_url}/cadastro")
        
        # Verificar título
        expect(page).to_have_title("Cadastro - Sistema de Garantias")
        expect(page.locator("text=Cadastro de Cliente")).to_be_visible()
        
        # Verificar campos obrigatórios
        expect(page.locator("input[name='nome']")).to_be_visible()
        expect(page.locator("input[name='email']")).to_be_visible()
        expect(page.locator("input[name='senha']")).to_be_visible()
        expect(page.locator("input[name='confirmar_senha']")).to_be_visible()
        expect(page.locator("input[name='telefone']")).to_be_visible()
        expect(page.locator("input[name='cpf_cnpj']")).to_be_visible()
        expect(page.locator("input[name='cep']")).to_be_visible()
        expect(page.locator("input[name='data_nascimento']")).to_be_visible()
        
        # Verificar botão de submissão
        expect(page.locator("button[type='submit']")).to_be_visible()
        expect(page.locator("text=Cadastrar")).to_be_visible()
    
    def test_user_registration_success(self, page: Page, base_url: str):
        """Testa cadastro bem-sucedido"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher formulário
        page.fill("input[name='nome']", "Novo Cliente")
        page.fill("input[name='email']", "novocliente@teste.com")
        page.fill("input[name='senha']", "senha123")
        page.fill("input[name='confirmar_senha']", "senha123")
        page.fill("input[name='telefone']", "(11) 88888-8888")
        page.fill("input[name='cpf_cnpj']", "987.654.321-00")
        page.fill("input[name='cep']", "12345-678")
        page.fill("input[name='data_nascimento']", "1985-05-15")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento para página de sucesso
        expect(page).to_have_url(f"{base_url}/cadastro/sucesso")
        expect(page.locator("text=Cadastro realizado com sucesso")).to_be_visible()
        expect(page.locator("text=Novo Cliente")).to_be_visible()
    
    def test_user_registration_validation_errors(self, page: Page, base_url: str):
        """Testa validações do formulário de cadastro"""
        page.goto(f"{base_url}/cadastro")
        
        # Tentar submeter formulário vazio
        page.click("button[type='submit']")
        
        # Verificar mensagens de erro
        expect(page.locator(".alert-danger, .error")).to_be_visible()
        
        # Testar email inválido
        page.fill("input[name='email']", "email_invalido")
        page.click("button[type='submit']")
        expect(page.locator("text=Email inválido")).to_be_visible()
        
        # Testar senhas diferentes
        page.fill("input[name='senha']", "senha123")
        page.fill("input[name='confirmar_senha']", "senha456")
        page.click("button[type='submit']")
        expect(page.locator("text=Senhas não coincidem")).to_be_visible()
    
    def test_user_registration_duplicate_email(self, page: Page, base_url: str):
        """Testa cadastro com email duplicado"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher com email já existente
        page.fill("input[name='nome']", "Cliente Duplicado")
        page.fill("input[name='email']", "cliente@teste.com")  # Email já existe
        page.fill("input[name='senha']", "senha123")
        page.fill("input[name='confirmar_senha']", "senha123")
        page.fill("input[name='telefone']", "(11) 77777-7777")
        page.fill("input[name='cpf_cnpj']", "111.222.333-44")
        page.fill("input[name='cep']", "54321-876")
        page.fill("input[name='data_nascimento']", "1980-12-25")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar erro de email duplicado
        expect(page.locator("text=Email já cadastrado")).to_be_visible()
    
    def test_user_registration_cep_validation(self, page: Page, base_url: str):
        """Testa validação de CEP"""
        page.goto(f"{base_url}/cadastro")
        
        # Testar CEP inválido
        page.fill("input[name='cep']", "123")
        page.fill("input[name='nome']", "Teste CEP")
        page.click("button[type='submit']")
        
        # Verificar erro de CEP
        expect(page.locator("text=CEP inválido")).to_be_visible()
    
    def test_user_registration_cpf_validation(self, page: Page, base_url: str):
        """Testa validação de CPF/CNPJ"""
        page.goto(f"{base_url}/cadastro")
        
        # Testar CPF inválido
        page.fill("input[name='cpf_cnpj']", "123.456.789-10")  # CPF inválido
        page.fill("input[name='nome']", "Teste CPF")
        page.click("button[type='submit']")
        
        # Verificar erro de CPF
        expect(page.locator("text=CPF/CNPJ inválido")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestUserProfileE2E:
    """Testes E2E para perfil do usuário"""
    
    def test_user_profile_display(self, logged_in_client: Page, base_url: str):
        """Testa exibição do perfil do usuário"""
        page = logged_in_client
        
        # Navegar para perfil
        page.goto(f"{base_url}/perfil")
        
        # Verificar título
        expect(page).to_have_title("Meu Perfil - Sistema de Garantias")
        expect(page.locator("text=Meu Perfil")).to_be_visible()
        
        # Verificar dados do usuário
        expect(page.locator("text=Cliente Teste")).to_be_visible()
        expect(page.locator("text=cliente@teste.com")).to_be_visible()
        expect(page.locator("text=(11) 99999-9999")).to_be_visible()
        expect(page.locator("text=123.456.789-00")).to_be_visible()
        
        # Verificar botão de editar
        expect(page.locator("a[href='/perfil/editar']")).to_be_visible()
    
    def test_user_profile_edit_form(self, logged_in_client: Page, base_url: str):
        """Testa formulário de edição do perfil"""
        page = logged_in_client
        
        # Navegar para edição
        page.goto(f"{base_url}/perfil/editar")
        
        # Verificar título
        expect(page).to_have_title("Editar Perfil - Sistema de Garantias")
        expect(page.locator("text=Editar Perfil")).to_be_visible()
        
        # Verificar campos preenchidos
        expect(page.locator("input[name='nome']")).to_have_value("Cliente Teste")
        expect(page.locator("input[name='email']")).to_have_value("cliente@teste.com")
        expect(page.locator("input[name='telefone']")).to_have_value("(11) 99999-9999")
        expect(page.locator("input[name='cpf_cnpj']")).to_have_value("123.456.789-00")
        expect(page.locator("input[name='cep']")).to_have_value("01234-567")
        
        # Verificar botões
        expect(page.locator("button[type='submit']")).to_be_visible()
        expect(page.locator("a[href='/perfil']")).to_be_visible()  # Cancelar
    
    def test_user_profile_edit_success(self, logged_in_client: Page, base_url: str):
        """Testa edição bem-sucedida do perfil"""
        page = logged_in_client
        
        # Navegar para edição
        page.goto(f"{base_url}/perfil/editar")
        
        # Modificar dados
        page.fill("input[name='nome']", "Cliente Modificado")
        page.fill("input[name='telefone']", "(11) 88888-8888")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar redirecionamento e sucesso
        expect(page).to_have_url(f"{base_url}/perfil")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Perfil atualizado com sucesso")).to_be_visible()
        
        # Verificar dados atualizados
        expect(page.locator("text=Cliente Modificado")).to_be_visible()
        expect(page.locator("text=(11) 88888-8888")).to_be_visible()
    
    def test_user_profile_edit_validation(self, logged_in_client: Page, base_url: str):
        """Testa validações na edição do perfil"""
        page = logged_in_client
        
        # Navegar para edição
        page.goto(f"{base_url}/perfil/editar")
        
        # Limpar campo obrigatório
        page.fill("input[name='nome']", "")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar erro
        expect(page.locator(".alert-danger, .error")).to_be_visible()
        expect(page.locator("text=Nome é obrigatório")).to_be_visible()
    
    def test_user_change_password_form(self, logged_in_client: Page, base_url: str):
        """Testa formulário de alteração de senha"""
        page = logged_in_client
        
        # Navegar para alteração de senha
        page.goto(f"{base_url}/perfil/senha")
        
        # Verificar título
        expect(page).to_have_title("Alterar Senha - Sistema de Garantias")
        expect(page.locator("text=Alterar Senha")).to_be_visible()
        
        # Verificar campos
        expect(page.locator("input[name='senha_atual']")).to_be_visible()
        expect(page.locator("input[name='nova_senha']")).to_be_visible()
        expect(page.locator("input[name='confirmar_nova_senha']")).to_be_visible()
        
        # Verificar botões
        expect(page.locator("button[type='submit']")).to_be_visible()
        expect(page.locator("a[href='/perfil']")).to_be_visible()
    
    def test_user_change_password_success(self, logged_in_client: Page, base_url: str):
        """Testa alteração bem-sucedida de senha"""
        page = logged_in_client
        
        # Navegar para alteração de senha
        page.goto(f"{base_url}/perfil/senha")
        
        # Preencher formulário
        page.fill("input[name='senha_atual']", "123456")
        page.fill("input[name='nova_senha']", "novasenha123")
        page.fill("input[name='confirmar_nova_senha']", "novasenha123")
        
        # Submeter formulário
        page.click("button[type='submit']")
        
        # Verificar sucesso
        expect(page).to_have_url(f"{base_url}/perfil")
        expect(page.locator(".alert-success")).to_be_visible()
        expect(page.locator("text=Senha alterada com sucesso")).to_be_visible()
    
    def test_user_change_password_validation(self, logged_in_client: Page, base_url: str):
        """Testa validações na alteração de senha"""
        page = logged_in_client
        
        # Navegar para alteração de senha
        page.goto(f"{base_url}/perfil/senha")
        
        # Testar senha atual incorreta
        page.fill("input[name='senha_atual']", "senhaerrada")
        page.fill("input[name='nova_senha']", "novasenha123")
        page.fill("input[name='confirmar_nova_senha']", "novasenha123")
        page.click("button[type='submit']")
        
        expect(page.locator("text=Senha atual incorreta")).to_be_visible()
        
        # Testar confirmação de senha diferente
        page.fill("input[name='senha_atual']", "123456")
        page.fill("input[name='nova_senha']", "novasenha123")
        page.fill("input[name='confirmar_nova_senha']", "senhadiferente")
        page.click("button[type='submit']")
        
        expect(page.locator("text=Confirmação de senha não confere")).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestUserAccountManagementE2E:
    """Testes E2E para gerenciamento de conta"""
    
    def test_user_account_settings(self, logged_in_client: Page, base_url: str):
        """Testa página de configurações da conta"""
        page = logged_in_client
        
        # Navegar para configurações
        page.goto(f"{base_url}/conta/configuracoes")
        
        # Verificar título
        expect(page.locator("text=Configurações da Conta")).to_be_visible()
        
        # Verificar opções disponíveis
        expect(page.locator("text=Notificações")).to_be_visible()
        expect(page.locator("text=Privacidade")).to_be_visible()
        expect(page.locator("text=Preferências")).to_be_visible()
    
    def test_user_notification_preferences(self, logged_in_client: Page, base_url: str):
        """Testa preferências de notificação"""
        page = logged_in_client
        
        # Navegar para notificações
        page.goto(f"{base_url}/conta/notificacoes")
        
        # Verificar checkboxes de notificação
        email_notifications = page.locator("input[name='email_notifications']")
        sms_notifications = page.locator("input[name='sms_notifications']")
        
        if email_notifications.count() > 0:
            expect(email_notifications).to_be_visible()
        
        if sms_notifications.count() > 0:
            expect(sms_notifications).to_be_visible()
    
    def test_user_data_export(self, logged_in_client: Page, base_url: str):
        """Testa exportação de dados do usuário"""
        page = logged_in_client
        
        # Navegar para exportação de dados
        page.goto(f"{base_url}/conta/exportar-dados")
        
        # Verificar opções de exportação
        export_button = page.locator("button:has-text('Exportar Dados')")
        if export_button.count() > 0:
            expect(export_button).to_be_visible()
    
    def test_user_account_deletion_request(self, logged_in_client: Page, base_url: str):
        """Testa solicitação de exclusão de conta"""
        page = logged_in_client
        
        # Navegar para exclusão de conta
        page.goto(f"{base_url}/conta/excluir")
        
        # Verificar aviso de exclusão
        expect(page.locator("text=Excluir Conta")).to_be_visible()
        expect(page.locator("text=Esta ação não pode ser desfeita")).to_be_visible()
        
        # Verificar campo de confirmação
        confirmation_input = page.locator("input[name='confirmacao']")
        if confirmation_input.count() > 0:
            expect(confirmation_input).to_be_visible()
    
    def test_user_activity_history(self, logged_in_client: Page, base_url: str):
        """Testa histórico de atividades do usuário"""
        page = logged_in_client
        
        # Navegar para histórico
        page.goto(f"{base_url}/conta/historico")
        
        # Verificar título
        expect(page.locator("text=Histórico de Atividades")).to_be_visible()
        
        # Verificar se há registros de atividade
        activity_list = page.locator(".activity-list, .timeline")
        if activity_list.count() > 0:
            expect(activity_list).to_be_visible()
    
    def test_user_profile_responsive_design(self, logged_in_client: Page, base_url: str):
        """Testa design responsivo do perfil"""
        page = logged_in_client
        
        # Testar em mobile
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{base_url}/perfil")
        
        expect(page.locator("text=Meu Perfil")).to_be_visible()
        expect(page.locator("text=Cliente Teste")).to_be_visible()
        
        # Testar em tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator("text=Meu Perfil")).to_be_visible()
        
        # Voltar ao desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        expect(page.locator("text=Meu Perfil")).to_be_visible()