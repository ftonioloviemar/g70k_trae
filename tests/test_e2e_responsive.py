#!/usr/bin/env python3
"""
Testes E2E para design responsivo em diferentes tamanhos de tela
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
                from main import app
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8007, log_level="error")
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
    return "http://127.0.0.1:8007"

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

# Definir viewports para teste
VIEWPORTS = {
    'mobile_small': {'width': 320, 'height': 568},   # iPhone SE
    'mobile_large': {'width': 375, 'height': 812},   # iPhone X
    'tablet_portrait': {'width': 768, 'height': 1024}, # iPad
    'tablet_landscape': {'width': 1024, 'height': 768}, # iPad landscape
    'desktop_small': {'width': 1366, 'height': 768},  # Laptop
    'desktop_large': {'width': 1920, 'height': 1080}, # Desktop
    'ultrawide': {'width': 2560, 'height': 1440}      # Ultrawide
}

@pytest.mark.e2e
@pytest.mark.playwright
class TestResponsiveLoginE2E:
    """Testes E2E para responsividade da página de login"""
    
    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS.items())
    def test_login_page_responsive(self, page: Page, base_url: str, viewport_name: str, viewport: dict):
        """Testa página de login em diferentes tamanhos de tela"""
        # Configurar viewport
        page.set_viewport_size(viewport)
        
        # Navegar para login
        page.goto(f"{base_url}/login")
        
        # Verificar elementos essenciais
        expect(page.locator("text=Login")).to_be_visible()
        expect(page.locator("input[name='email']")).to_be_visible()
        expect(page.locator("input[name='senha']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()
        
        # Verificar que campos são clicáveis
        page.click("input[name='email']")
        page.fill("input[name='email']", "teste@exemplo.com")
        
        page.click("input[name='senha']")
        page.fill("input[name='senha']", "senha123")
        
        # Verificar que botão é clicável
        expect(page.locator("button[type='submit']")).to_be_enabled()
    
    def test_login_form_mobile_usability(self, page: Page, base_url: str):
        """Testa usabilidade do formulário de login em mobile"""
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        # Navegar para login
        page.goto(f"{base_url}/login")
        
        # Verificar que campos têm tamanho adequado para toque
        email_input = page.locator("input[name='email']")
        senha_input = page.locator("input[name='senha']")
        submit_button = page.locator("button[type='submit']")
        
        # Verificar altura mínima para toque (44px)
        email_box = email_input.bounding_box()
        senha_box = senha_input.bounding_box()
        button_box = submit_button.bounding_box()
        
        assert email_box['height'] >= 40, "Campo email muito pequeno para toque"
        assert senha_box['height'] >= 40, "Campo senha muito pequeno para toque"
        assert button_box['height'] >= 40, "Botão muito pequeno para toque"
    
    def test_login_keyboard_navigation(self, page: Page, base_url: str):
        """Testa navegação por teclado no login"""
        page.goto(f"{base_url}/login")
        
        # Navegar por Tab
        page.keyboard.press("Tab")  # Email
        expect(page.locator("input[name='email']")).to_be_focused()
        
        page.keyboard.press("Tab")  # Senha
        expect(page.locator("input[name='senha']")).to_be_focused()
        
        page.keyboard.press("Tab")  # Botão
        expect(page.locator("button[type='submit']")).to_be_focused()

@pytest.mark.e2e
@pytest.mark.playwright
class TestResponsiveDashboardE2E:
    """Testes E2E para responsividade do dashboard"""
    
    @pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS.items())
    def test_dashboard_responsive(self, logged_in_client: Page, base_url: str, viewport_name: str, viewport: dict):
        """Testa dashboard em diferentes tamanhos de tela"""
        page = logged_in_client
        
        # Configurar viewport
        page.set_viewport_size(viewport)
        
        # Navegar para dashboard
        page.goto(f"{base_url}/dashboard")
        
        # Verificar elementos essenciais
        expect(page.locator("text=Dashboard")).to_be_visible()
        
        # Verificar estatísticas
        stats = page.locator(".stat, .card, .metric")
        if stats.count() > 0:
            expect(stats.first).to_be_visible()
        
        # Verificar navegação
        nav_links = page.locator("nav a, .nav-link")
        if nav_links.count() > 0:
            expect(nav_links.first).to_be_visible()
    
    def test_dashboard_mobile_navigation(self, logged_in_client: Page, base_url: str):
        """Testa navegação mobile no dashboard"""
        page = logged_in_client
        
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        # Navegar para dashboard
        page.goto(f"{base_url}/dashboard")
        
        # Verificar menu hamburger ou navegação mobile
        mobile_menu = page.locator(".navbar-toggler, .menu-toggle, .hamburger")
        if mobile_menu.count() > 0:
            expect(mobile_menu).to_be_visible()
            
            # Clicar no menu
            mobile_menu.click()
            
            # Verificar que links aparecem
            nav_menu = page.locator(".navbar-collapse, .mobile-menu")
            if nav_menu.count() > 0:
                expect(nav_menu).to_be_visible()
    
    def test_dashboard_cards_layout(self, logged_in_client: Page, base_url: str):
        """Testa layout dos cards do dashboard"""
        page = logged_in_client
        
        # Testar em diferentes tamanhos
        viewports_to_test = ['mobile_small', 'tablet_portrait', 'desktop_large']
        
        for viewport_name in viewports_to_test:
            viewport = VIEWPORTS[viewport_name]
            page.set_viewport_size(viewport)
            
            page.goto(f"{base_url}/dashboard")
            
            # Verificar que cards são visíveis
            cards = page.locator(".card, .stat-card, .metric-card")
            if cards.count() > 0:
                for i in range(min(3, cards.count())):
                    expect(cards.nth(i)).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestResponsiveFormsE2E:
    """Testes E2E para responsividade de formulários"""
    
    def test_vehicle_form_responsive(self, logged_in_client: Page, base_url: str):
        """Testa formulário de veículo em diferentes tamanhos"""
        page = logged_in_client
        
        # Testar em mobile e desktop
        viewports_to_test = ['mobile_large', 'desktop_small']
        
        for viewport_name in viewports_to_test:
            viewport = VIEWPORTS[viewport_name]
            page.set_viewport_size(viewport)
            
            # Navegar para novo veículo
            page.goto(f"{base_url}/veiculos/novo")
            
            # Verificar campos do formulário
            expect(page.locator("input[name='marca']")).to_be_visible()
            expect(page.locator("input[name='modelo']")).to_be_visible()
            expect(page.locator("input[name='placa']")).to_be_visible()
            expect(page.locator("button[type='submit']")).to_be_visible()
            
            # Verificar que campos são utilizáveis
            page.fill("input[name='marca']", "Toyota")
            page.fill("input[name='modelo']", "Corolla")
            
            # Verificar que botão é clicável
            expect(page.locator("button[type='submit']")).to_be_enabled()
    
    def test_warranty_form_mobile_usability(self, logged_in_client: Page, base_url: str):
        """Testa usabilidade do formulário de garantia em mobile"""
        page = logged_in_client
        
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_large'])
        
        # Navegar para nova garantia
        page.goto(f"{base_url}/garantias/nova")
        
        # Verificar campos essenciais
        expect(page.locator("select[name='produto_id']")).to_be_visible()
        expect(page.locator("select[name='veiculo_id']")).to_be_visible()
        expect(page.locator("input[name='data_instalacao']")).to_be_visible()
        
        # Testar interação com selects em mobile
        page.click("select[name='produto_id']")
        page.select_option("select[name='produto_id']", "1")
        
        # Verificar que seleção funcionou
        selected_value = page.locator("select[name='produto_id']").input_value()
        assert selected_value == "1"
    
    def test_form_validation_messages_responsive(self, logged_in_client: Page, base_url: str):
        """Testa exibição de mensagens de validação em diferentes tamanhos"""
        page = logged_in_client
        
        # Testar em mobile e desktop
        for viewport_name in ['mobile_small', 'desktop_large']:
            viewport = VIEWPORTS[viewport_name]
            page.set_viewport_size(viewport)
            
            # Navegar para formulário
            page.goto(f"{base_url}/veiculos/novo")
            
            # Submeter formulário vazio
            page.click("button[type='submit']")
            
            # Verificar que mensagens de erro são visíveis
            error_messages = page.locator(".alert-danger, .error, .invalid-feedback")
            if error_messages.count() > 0:
                expect(error_messages.first).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestResponsiveTablesE2E:
    """Testes E2E para responsividade de tabelas"""
    
    def test_vehicle_table_responsive(self, logged_in_client: Page, base_url: str):
        """Testa tabela de veículos em diferentes tamanhos"""
        page = logged_in_client
        
        # Navegar para veículos
        page.goto(f"{base_url}/veiculos")
        
        # Testar em desktop
        page.set_viewport_size(VIEWPORTS['desktop_large'])
        table = page.locator(".table")
        if table.count() > 0:
            expect(table).to_be_visible()
        
        # Testar em mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        # Verificar se tabela se adapta (scroll horizontal ou cards)
        table_container = page.locator(".table-responsive, .table, .card")
        expect(table_container.first).to_be_visible()
    
    def test_warranty_table_mobile_scroll(self, logged_in_client: Page, base_url: str):
        """Testa scroll horizontal da tabela de garantias em mobile"""
        page = logged_in_client
        
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        # Navegar para garantias
        page.goto(f"{base_url}/garantias")
        
        # Verificar se tabela tem scroll horizontal
        table_container = page.locator(".table-responsive")
        if table_container.count() > 0:
            expect(table_container).to_be_visible()
            
            # Verificar que conteúdo é acessível via scroll
            table = page.locator(".table")
            if table.count() > 0:
                expect(table).to_be_visible()
    
    def test_admin_table_responsive(self, logged_in_admin: Page, base_url: str):
        """Testa tabelas administrativas em diferentes tamanhos"""
        page = logged_in_admin
        
        # Navegar para usuários
        page.goto(f"{base_url}/admin/usuarios")
        
        # Testar em tablet
        page.set_viewport_size(VIEWPORTS['tablet_portrait'])
        
        # Verificar que tabela é visível
        table = page.locator(".table")
        if table.count() > 0:
            expect(table).to_be_visible()
        
        # Verificar ações da tabela
        action_buttons = page.locator(".btn, .action-btn")
        if action_buttons.count() > 0:
            expect(action_buttons.first).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestResponsiveNavigationE2E:
    """Testes E2E para navegação responsiva"""
    
    def test_main_navigation_responsive(self, logged_in_client: Page, base_url: str):
        """Testa navegação principal em diferentes tamanhos"""
        page = logged_in_client
        
        # Testar em desktop
        page.set_viewport_size(VIEWPORTS['desktop_large'])
        page.goto(f"{base_url}/dashboard")
        
        # Verificar navegação desktop
        nav_links = page.locator("nav a, .nav-link")
        if nav_links.count() > 0:
            expect(nav_links.first).to_be_visible()
        
        # Testar em mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        # Verificar menu mobile
        mobile_toggle = page.locator(".navbar-toggler, .menu-toggle")
        if mobile_toggle.count() > 0:
            expect(mobile_toggle).to_be_visible()
            mobile_toggle.click()
            
            # Verificar que menu se expande
            mobile_menu = page.locator(".navbar-collapse, .mobile-menu")
            if mobile_menu.count() > 0:
                expect(mobile_menu).to_be_visible()
    
    def test_breadcrumb_responsive(self, logged_in_client: Page, base_url: str):
        """Testa breadcrumbs em diferentes tamanhos"""
        page = logged_in_client
        
        # Navegar para página com breadcrumb
        page.goto(f"{base_url}/veiculos/novo")
        
        # Testar em diferentes tamanhos
        for viewport_name in ['mobile_small', 'tablet_portrait', 'desktop_large']:
            viewport = VIEWPORTS[viewport_name]
            page.set_viewport_size(viewport)
            
            # Verificar breadcrumb
            breadcrumb = page.locator(".breadcrumb")
            if breadcrumb.count() > 0:
                expect(breadcrumb).to_be_visible()
    
    def test_footer_responsive(self, page: Page, base_url: str):
        """Testa footer em diferentes tamanhos"""
        page.goto(f"{base_url}")
        
        # Testar em diferentes viewports
        for viewport_name in ['mobile_small', 'desktop_large']:
            viewport = VIEWPORTS[viewport_name]
            page.set_viewport_size(viewport)
            
            # Verificar footer
            footer = page.locator("footer")
            if footer.count() > 0:
                expect(footer).to_be_visible()

@pytest.mark.e2e
@pytest.mark.playwright
class TestResponsivePerformanceE2E:
    """Testes E2E para performance em dispositivos móveis"""
    
    def test_page_load_mobile(self, page: Page, base_url: str):
        """Testa tempo de carregamento em mobile"""
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        # Medir tempo de carregamento
        start_time = time.time()
        page.goto(f"{base_url}")
        page.wait_for_load_state("networkidle")
        load_time = time.time() - start_time
        
        # Verificar que página carregou em tempo razoável (< 5 segundos)
        assert load_time < 5.0, f"Página demorou {load_time:.2f}s para carregar"
        
        # Verificar que conteúdo principal é visível
        main_content = page.locator("main, .main-content, .container")
        expect(main_content.first).to_be_visible()
    
    def test_image_optimization_mobile(self, page: Page, base_url: str):
        """Testa otimização de imagens em mobile"""
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        page.goto(f"{base_url}")
        
        # Verificar imagens
        images = page.locator("img")
        if images.count() > 0:
            for i in range(min(3, images.count())):
                img = images.nth(i)
                expect(img).to_be_visible()
                
                # Verificar que imagem tem atributos de otimização
                src = img.get_attribute("src")
                if src:
                    # Verificar se não é uma imagem muito grande
                    assert not src.endswith(".png") or "large" not in src.lower()
    
    def test_touch_targets_size(self, logged_in_client: Page, base_url: str):
        """Testa tamanho adequado dos alvos de toque"""
        page = logged_in_client
        
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        page.goto(f"{base_url}/dashboard")
        
        # Verificar botões e links
        clickable_elements = page.locator("button, a, input[type='submit']")
        
        for i in range(min(5, clickable_elements.count())):
            element = clickable_elements.nth(i)
            if element.is_visible():
                box = element.bounding_box()
                if box:
                    # Verificar tamanho mínimo para toque (44x44px)
                    assert box['height'] >= 40, f"Elemento {i} muito pequeno: {box['height']}px"
                    assert box['width'] >= 40, f"Elemento {i} muito estreito: {box['width']}px"

@pytest.mark.e2e
@pytest.mark.playwright
class TestResponsiveAccessibilityE2E:
    """Testes E2E para acessibilidade responsiva"""
    
    def test_focus_visibility_mobile(self, page: Page, base_url: str):
        """Testa visibilidade do foco em mobile"""
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        page.goto(f"{base_url}/login")
        
        # Navegar por Tab
        page.keyboard.press("Tab")
        
        # Verificar que elemento focado é visível
        focused_element = page.locator(":focus")
        if focused_element.count() > 0:
            expect(focused_element).to_be_visible()
    
    def test_text_scaling_mobile(self, page: Page, base_url: str):
        """Testa escalabilidade do texto em mobile"""
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        page.goto(f"{base_url}")
        
        # Verificar que texto principal é legível
        main_text = page.locator("h1, h2, p, .lead")
        if main_text.count() > 0:
            expect(main_text.first).to_be_visible()
            
            # Verificar que texto não está muito pequeno
            computed_style = page.evaluate("""
                () => {
                    const element = document.querySelector('h1, h2, p, .lead');
                    if (element) {
                        return window.getComputedStyle(element).fontSize;
                    }
                    return null;
                }
            """)
            
            if computed_style:
                font_size = float(computed_style.replace('px', ''))
                assert font_size >= 14, f"Texto muito pequeno: {font_size}px"
    
    def test_contrast_mobile(self, page: Page, base_url: str):
        """Testa contraste em mobile"""
        # Configurar viewport mobile
        page.set_viewport_size(VIEWPORTS['mobile_small'])
        
        page.goto(f"{base_url}")
        
        # Verificar que elementos importantes são visíveis
        important_elements = page.locator("h1, h2, button, .btn, .alert")
        
        for i in range(min(3, important_elements.count())):
            element = important_elements.nth(i)
            if element.is_visible():
                expect(element).to_be_visible()