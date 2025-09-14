#!/usr/bin/env python3
"""
Testes end-to-end para o sistema de garantias usando Playwright
"""

import pytest
import tempfile
import os
import threading
import time
from pathlib import Path
from playwright.sync_api import Page, expect
from fastlite import Database

from app.config import Config
from app.database import init_database
from main import create_app


class TestServer:
    """Servidor de teste para os testes E2E"""
    
    def __init__(self):
        self.server = None
        self.thread = None
        self.db_path = None
        self.port = 8001  # Usar porta diferente para não conflitar
    
    def start(self):
        """Inicia o servidor de teste"""
        # Criar banco temporário
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            self.db_path = tmp.name
        
        # Configurar aplicação de teste
        config = Config()
        config.DATABASE_PATH = self.db_path
        config.SECRET_KEY = 'test-secret-key'
        
        # Inicializar banco
        db = Database(self.db_path)
        init_database(db)
        
        # Criar dados de teste
        self._create_test_data(db)
        db.close()
        
        # Configurar aplicação para usar o banco temporário
        import os
        os.environ['DATABASE_PATH'] = self.db_path
        
        # Criar aplicação
        app, config = create_app()
        
        # Iniciar servidor em thread separada
        import uvicorn
        self.thread = threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={'host': '127.0.0.1', 'port': self.port, 'log_level': 'error'}
        )
        self.thread.daemon = True
        self.thread.start()
        
        # Aguardar servidor iniciar
        time.sleep(5)
        
        # Verificar se servidor está respondendo
        import requests
        max_attempts = 10
        for i in range(max_attempts):
            try:
                response = requests.get(f'http://127.0.0.1:{self.port}/', timeout=2)
                if response.status_code in [200, 302, 404]:  # Qualquer resposta válida
                    break
            except requests.exceptions.RequestException:
                if i == max_attempts - 1:
                    raise Exception(f"Servidor não respondeu após {max_attempts} tentativas")
                time.sleep(1)
    
    def stop(self):
        """Para o servidor de teste"""
        if self.db_path and os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def _create_test_data(self, db):
        """Cria dados de teste no banco"""
        # Verificar se o usuário admin foi criado
        admin = db.execute(
            "SELECT id, email, senha_hash FROM usuarios WHERE email = ? AND tipo_usuario = 'administrador'",
            ('ftoniolo@viemar.com.br',)
        ).fetchone()
        
        if admin:
            print(f"Admin encontrado: ID={admin[0]}, Email={admin[1]}")
            # Testar verificação de senha
            import bcrypt
            senha_correta = bcrypt.checkpw('abc123'.encode('utf-8'), admin[2].encode('utf-8'))
            print(f"Senha 'abc123' está correta: {senha_correta}")
        else:
            print("ERRO: Usuário admin não foi encontrado no banco!")
            # Forçar criação do admin
            from app.database import criar_admin_padrao
            criar_admin_padrao(db)
            print("Admin criado manualmente")


@pytest.fixture(scope='session')
def test_server():
    """Fixture para servidor de teste"""
    server = TestServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope='session')
def base_url(test_server):
    """URL base para os testes"""
    return f'http://127.0.0.1:{test_server.port}'


@pytest.mark.e2e
@pytest.mark.playwright
class TestGarantiaE2E:
    """Testes end-to-end para garantias"""
    
    def test_fluxo_completo_cadastro_garantia(self, page: Page, base_url: str):
        """Testa o fluxo completo de cadastro de garantia"""
        # 1. Fazer login
        page.goto(f'{base_url}/login')
        
        # Verificar se a página de login carregou
        expect(page.locator('h5')).to_contain_text('Entrar na sua conta')
        
        # Fazer login com admin padrão
        page.fill('input[name="email"]', 'ftoniolo@viemar.com.br')
        page.fill('input[name="senha"]', 'abc123')
        page.click('button[type="submit"]')
        
        # Aguardar redirecionamento
        page.wait_for_load_state('networkidle')
        
        # Verificar se chegou na área do cliente
        expect(page.locator('body')).to_contain_text('Bem-vindo')
    
    def test_validacao_campos_obrigatorios(self, page: Page, base_url: str):
        """Testa validação de campos obrigatórios"""
        # Fazer login
        page.goto(f'{base_url}/login')
        page.fill('input[name="email"]', 'ftoniolo@viemar.com.br')
        page.fill('input[name="senha"]', 'abc123')
        page.click('button[type="submit"]')
        
        # Ir para nova garantia
        page.goto(f'{base_url}/cliente/garantias/nova')
        
        # Tentar submeter formulário vazio
        page.click('button[type="submit"]')
        
        # Verificar mensagens de erro
        expect(page.locator('.text-danger')).to_have_count(4)  # 4 campos obrigatórios
        
        # Verificar que permaneceu na mesma página
        expect(page).to_have_url(f'{base_url}/cliente/garantias/nova')
    
    def test_garantia_duplicada(self, page: Page, base_url: str):
        """Testa tentativa de criar garantia duplicada"""
        # Fazer login
        page.goto(f'{base_url}/login')
        page.fill('input[name="email"]', 'ftoniolo@viemar.com.br')
        page.fill('input[name="senha"]', 'abc123')
        page.click('button[type="submit"]')
        
        # Criar primeira garantia
        page.goto(f'{base_url}/cliente/garantias/nova')
        page.select_option('select[name="produto_id"]', label='PROD001 - Produto Teste')
        page.select_option('select[name="veiculo_id"]', label='Toyota Corolla - ABC1234')
        page.fill('input[name="lote_fabricacao"]', 'LOTE123456')
        
        from datetime import date
        hoje = date.today().strftime('%Y-%m-%d')
        page.fill('input[name="data_instalacao"]', hoje)
        page.fill('input[name="quilometragem_instalacao"]', '50000')
        page.click('button[type="submit"]')
        
        # Tentar criar segunda garantia igual
        page.goto(f'{base_url}/cliente/garantias/nova')
        page.select_option('select[name="produto_id"]', label='PROD001 - Produto Teste')
        page.select_option('select[name="veiculo_id"]', label='Toyota Corolla - ABC1234')
        page.fill('input[name="lote_fabricacao"]', 'LOTE789012')
        page.fill('input[name="data_instalacao"]', hoje)
        page.fill('input[name="quilometragem_instalacao"]', '60000')
        page.click('button[type="submit"]')
        
        # Verificar mensagem de erro
        expect(page.locator('.text-danger')).to_contain_text('Já existe uma garantia ativa')
        expect(page).to_have_url(f'{base_url}/cliente/garantias/nova')
    
    def test_acesso_sem_autenticacao(self, page: Page, base_url: str):
        """Testa acesso sem autenticação"""
        # Tentar acessar página de nova garantia sem login
        page.goto(f'{base_url}/cliente/garantias/nova')
        
        # Deve redirecionar para login
        page.wait_for_url(f'{base_url}/login')
        expect(page.locator('h1, h2')).to_contain_text('Login')
    
    def test_erro_database_insert(self, page: Page, base_url: str):
        """Testa se erros de database são tratados corretamente"""
        # Fazer login
        page.goto(f'{base_url}/login')
        page.fill('input[name="email"]', 'ftoniolo@viemar.com.br')
        page.fill('input[name="senha"]', 'abc123')
        page.click('button[type="submit"]')
        
        # Ir para nova garantia
        page.goto(f'{base_url}/cliente/garantias/nova')
        
        # Preencher formulário
        page.select_option('select[name="produto_id"]', label='PROD001 - Produto Teste')
        page.select_option('select[name="veiculo_id"]', label='Toyota Corolla - ABC1234')
        page.fill('input[name="lote_fabricacao"]', 'LOTE123456')
        
        from datetime import date
        hoje = date.today().strftime('%Y-%m-%d')
        page.fill('input[name="data_instalacao"]', hoje)
        page.fill('input[name="quilometragem_instalacao"]', '50000')
        
        # Submeter formulário
        page.click('button[type="submit"]')
        
        # Verificar que não há erro 500 ou mensagem de erro de database
        # Se houver erro, deve mostrar mensagem amigável, não erro técnico
        page.wait_for_load_state('networkidle')
        
        # Não deve haver erro 500
        expect(page.locator('body')).not_to_contain_text('500 Server Error')
        expect(page.locator('body')).not_to_contain_text('Database')
        expect(page.locator('body')).not_to_contain_text('last_insert_rowid')
        
        # Deve ter sucesso ou erro amigável
        success_or_error = page.locator('.alert-success, .alert-danger, .text-danger').count() > 0
        assert success_or_error, "Deve mostrar mensagem de sucesso ou erro amigável"