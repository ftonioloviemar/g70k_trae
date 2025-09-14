#!/usr/bin/env python3
"""
Testes E2E expandidos para autenticação
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

# Configuração do banco temporário
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
        import bcrypt
        
        # Usuário cliente
        senha_cliente = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('cliente@teste.com', senha_cliente, 'Cliente Teste', 'cliente', True))
        
        # Usuário admin
        senha_admin = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.execute("""
            INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
            VALUES (?, ?, ?, ?, ?)
        """, ('admin@teste.com', senha_admin, 'Admin Teste', 'administrador', True))
        
        # Produto de teste
        db.execute("""
            INSERT INTO produtos (sku, descricao, ativo)
            VALUES (?, ?, ?)
        """, ('PROD001', 'Produto Teste', True))
        
        return db
    
    def start_server(self):
        """Inicia servidor de teste"""
        def run_server():
            try:
                from main import create_app
                import uvicorn
                app, _ = create_app()
                uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")
            except Exception as e:
                print(f"Erro ao iniciar servidor: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        time.sleep(5)  # Aguardar servidor iniciar completamente
    
    def stop_server(self):
        """Para servidor e limpa recursos"""
        # Limpar variável de ambiente primeiro
        if 'DATABASE_PATH' in os.environ:
            del os.environ['DATABASE_PATH']
            
        # Aguardar um pouco antes de limpar arquivos
        time.sleep(2)
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # Tentar novamente após aguardar
                time.sleep(3)
                try:
                    shutil.rmtree(self.temp_dir)
                except PermissionError:
                    print(f"Aviso: Não foi possível remover {self.temp_dir}")
                    pass

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
    return "http://127.0.0.1:8001"

@pytest.mark.e2e
@pytest.mark.playwright
class TestAuthenticationE2E:
    """Testes E2E expandidos para autenticação"""
    
    def test_login_page_elements(self, page: Page, base_url: str):
        """Testa elementos da página de login"""
        page.goto(f"{base_url}/login")
        
        # Verificar título
        expect(page).to_have_title("Login - Sistema de Garantias")
        
        # Verificar elementos do formulário
        expect(page.locator("input[name='email']")).to_be_visible()
        expect(page.locator("input[name='senha']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()
        
        # Verificar links
        expect(page.locator("a[href='/cadastro']")).to_be_visible()
        expect(page.locator("text=Não tem conta? Cadastre-se")).to_be_visible()
    
    def test_login_success_cliente(self, page: Page, base_url: str):
        """Testa login bem-sucedido de cliente"""
        page.goto(f"{base_url}/login")
        
        # Preencher formulário
        page.fill("input[name='email']", "cliente@teste.com")
        page.fill("input[name='senha']", "123456")
        
        # Submeter
        page.click("button[type='submit']")
        
        # Verificar redirecionamento para dashboard do cliente
        expect(page).to_have_url(f"{base_url}/cliente")
        expect(page.locator("text=Bem-vindo")).to_be_visible()
    
    def test_login_success_admin(self, page: Page, base_url: str):
        """Testa login bem-sucedido de admin"""
        page.goto(f"{base_url}/login")
        
        # Preencher formulário
        page.fill("input[name='email']", "admin@teste.com")
        page.fill("input[name='senha']", "admin123")
        
        # Submeter
        page.click("button[type='submit']")
        
        # Verificar redirecionamento para dashboard do admin
        expect(page).to_have_url(f"{base_url}/admin")
        expect(page.locator("text=Dashboard")).to_be_visible()
    
    def test_login_invalid_credentials(self, page: Page, base_url: str):
        """Testa login com credenciais inválidas"""
        page.goto(f"{base_url}/login")
        
        # Preencher com credenciais inválidas
        page.fill("input[name='email']", "invalido@teste.com")
        page.fill("input[name='senha']", "senhaerrada")
        
        # Submeter
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        expect(page.locator(".alert-danger")).to_be_visible()
        expect(page.locator("text=Email ou senha inválidos")).to_be_visible()
    
    def test_login_empty_fields(self, page: Page, base_url: str):
        """Testa login com campos vazios"""
        page.goto(f"{base_url}/login")
        
        # Submeter sem preencher
        page.click("button[type='submit']")
        
        # Verificar validação HTML5
        expect(page.locator("input[name='email']:invalid")).to_be_visible()
    
    def test_logout_functionality(self, page: Page, base_url: str):
        """Testa funcionalidade de logout"""
        # Fazer login primeiro
        page.goto(f"{base_url}/login")
        page.fill("input[name='email']", "cliente@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # Verificar login
        expect(page).to_have_url(f"{base_url}/cliente")
        
        # Fazer logout
        page.click("a[href='/logout']")
        
        # Verificar redirecionamento
        expect(page).to_have_url(f"{base_url}/")
        expect(page.locator("text=Login")).to_be_visible()
    
    def test_register_page_elements(self, page: Page, base_url: str):
        """Testa elementos da página de cadastro"""
        page.goto(f"{base_url}/cadastro")
        
        # Verificar título
        expect(page).to_have_title("Cadastro - Sistema de Garantias")
        
        # Verificar campos obrigatórios
        expect(page.locator("input[name='nome']")).to_be_visible()
        expect(page.locator("input[name='email']")).to_be_visible()
        expect(page.locator("input[name='senha']")).to_be_visible()
        expect(page.locator("input[name='confirmar_senha']")).to_be_visible()
        expect(page.locator("input[name='telefone']")).to_be_visible()
        expect(page.locator("input[name='cpf_cnpj']")).to_be_visible()
        
        # Verificar botão de submit
        expect(page.locator("button[type='submit']")).to_be_visible()
    
    def test_register_success(self, page: Page, base_url: str):
        """Testa cadastro bem-sucedido"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher formulário
        page.fill("input[name='nome']", "Novo Cliente")
        page.fill("input[name='email']", "novo@teste.com")
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "123456")
        page.fill("input[name='telefone']", "(11) 99999-9999")
        page.fill("input[name='cpf_cnpj']", "123.456.789-00")
        page.fill("input[name='cep']", "01234-567")
        
        # Submeter
        page.click("button[type='submit']")
        
        # Verificar redirecionamento para página de sucesso
        expect(page).to_have_url(f"{base_url}/cadastro/sucesso")
        expect(page.locator("text=Cadastro realizado com sucesso")).to_be_visible()
    
    def test_register_duplicate_email(self, page: Page, base_url: str):
        """Testa cadastro com email duplicado"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher com email já existente
        page.fill("input[name='nome']", "Cliente Duplicado")
        page.fill("input[name='email']", "cliente@teste.com")  # Email já existe
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "123456")
        page.fill("input[name='telefone']", "(11) 88888-8888")
        page.fill("input[name='cpf_cnpj']", "987.654.321-00")
        
        # Submeter
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        expect(page.locator(".alert-danger")).to_be_visible()
        expect(page.locator("text=Email já cadastrado")).to_be_visible()
    
    def test_register_password_mismatch(self, page: Page, base_url: str):
        """Testa cadastro com senhas não coincidentes"""
        page.goto(f"{base_url}/cadastro")
        
        # Preencher com senhas diferentes
        page.fill("input[name='nome']", "Cliente Senha")
        page.fill("input[name='email']", "senha@teste.com")
        page.fill("input[name='senha']", "123456")
        page.fill("input[name='confirmar_senha']", "654321")  # Senha diferente
        page.fill("input[name='telefone']", "(11) 77777-7777")
        page.fill("input[name='cpf_cnpj']", "111.222.333-44")
        
        # Submeter
        page.click("button[type='submit']")
        
        # Verificar mensagem de erro
        expect(page.locator(".alert-danger")).to_be_visible()
        expect(page.locator("text=Senhas não coincidem")).to_be_visible()
    
    def test_protected_route_redirect(self, page: Page, base_url: str):
        """Testa redirecionamento de rotas protegidas"""
        # Tentar acessar dashboard sem login
        page.goto(f"{base_url}/cliente")
        
        # Verificar redirecionamento para login
        expect(page).to_have_url(f"{base_url}/login")
    
    def test_admin_route_protection(self, page: Page, base_url: str):
        """Testa proteção de rotas administrativas"""
        # Login como cliente
        page.goto(f"{base_url}/login")
        page.fill("input[name='email']", "cliente@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # Tentar acessar área admin
        page.goto(f"{base_url}/admin")
        
        # Verificar redirecionamento ou erro de acesso
        expect(page).to_have_url(f"{base_url}/cliente")
    
    def test_session_persistence(self, page: Page, base_url: str):
        """Testa persistência da sessão"""
        # Fazer login
        page.goto(f"{base_url}/login")
        page.fill("input[name='email']", "cliente@teste.com")
        page.fill("input[name='senha']", "123456")
        page.click("button[type='submit']")
        
        # Navegar para outra página
        page.goto(f"{base_url}/sobre")
        
        # Voltar para dashboard - deve manter sessão
        page.goto(f"{base_url}/cliente")
        expect(page.locator("text=Dashboard do Cliente")).to_be_visible()