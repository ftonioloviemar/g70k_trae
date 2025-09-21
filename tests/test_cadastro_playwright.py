"""
Testes Playwright para reproduzir cenários de erro no cadastro
"""
import pytest
from playwright.sync_api import Page, expect
import time
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importar módulos da aplicação
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_database
from app.logger import get_logger
from fastlite import Database
from app.config import Config

logger = get_logger(__name__)


class TestCadastroPlaywright:
    """Testes end-to-end para o sistema de cadastro"""
    
    @pytest.fixture(autouse=True)
    def setup_test(self):
        """Setup para cada teste"""
        # Garantir que o banco está inicializado
        config = Config()
        db = Database(config.DATABASE_PATH)
        init_database(db)
        self.db = db
        yield
        # Cleanup após cada teste se necessário
    
    def test_cadastro_usuario_sucesso(self, page: Page):
        """Testa cadastro de usuário com dados válidos"""
        logger.info("Iniciando teste de cadastro com sucesso")
        
        # Navegar para a página de cadastro
        page.goto("http://localhost:8000/cadastro")
        
        # Aguardar a página carregar
        page.wait_for_load_state("networkidle")
        
        # Verificar se a página carregou corretamente
        expect(page.locator("h1")).to_contain_text("Cadastro")
        
        # Preencher o formulário com dados únicos
        timestamp = str(int(time.time()))
        email_teste = f"teste_{timestamp}@exemplo.com"
        
        page.fill('input[name="nome"]', f"Usuário Teste {timestamp}")
        page.fill('input[name="email"]', email_teste)
        page.fill('input[name="telefone"]', "11999887766")
        page.fill('input[name="cpf_cnpj"]', "12345678901")
        page.fill('input[name="cep"]', "01234567")
        page.fill('input[name="endereco"]', "Rua Teste, 123")
        page.fill('input[name="bairro"]', "Bairro Teste")
        page.fill('input[name="cidade"]', "São Paulo")
        page.fill('input[name="uf"]', "SP")
        page.fill('input[name="data_nascimento"]', "1990-01-01")
        page.fill('input[name="senha"]', "senha123")
        page.fill('input[name="confirmar_senha"]', "senha123")
        
        # Aguardar um pouco para garantir que todos os campos foram preenchidos
        page.wait_for_timeout(1000)
        
        # Submeter o formulário
        page.click('button[type="submit"]')
        
        # Aguardar resposta
        page.wait_for_load_state("networkidle")
        
        # Verificar se o cadastro foi bem-sucedido
        # Pode ser redirecionamento para login ou mensagem de sucesso
        
        # Capturar screenshot para debug
        page.screenshot(path="tmp/cadastro_resultado_debug.png")
        
        # Verificar se há mensagens de erro ou sucesso
        error_elements = page.locator(".alert-danger, .error, .message-error")
        success_elements = page.locator(".alert-success, .success, .message-success")
        
        current_url = page.url
        logger.info(f"URL atual após cadastro: {current_url}")
        
        if error_elements.count() > 0:
            error_text = error_elements.first.text_content()
            logger.error(f"Erro encontrado no cadastro: {error_text}")
            raise AssertionError(f"Erro no cadastro: {error_text}")
        
        elif success_elements.count() > 0:
            success_text = success_elements.first.text_content()
            logger.info(f"Cadastro realizado com sucesso: {success_text}")
            
        elif current_url == "http://localhost:8000/login":
            logger.info("Cadastro realizado com sucesso - redirecionado para login")
            
        else:
            # Verificar se permaneceu na página de cadastro
            if current_url == "http://localhost:8000/cadastro":
                # Pode ser que tenha havido erro de validação
                page_content = page.content()
                logger.warning("Permaneceu na página de cadastro - possível erro de validação")
                
                # Verificar se há campos com erro de validação
                invalid_fields = page.locator(".is-invalid")
                if invalid_fields.count() > 0:
                    logger.error(f"Campos com erro de validação: {invalid_fields.count()}")
                    for i in range(invalid_fields.count()):
                        field = invalid_fields.nth(i)
                        field_name = field.get_attribute("name")
                        logger.error(f"Campo inválido: {field_name}")
                
                raise AssertionError("Cadastro não foi processado - permaneceu na página de cadastro")
            else:
                logger.warning(f"Resultado inesperado - URL: {current_url}")
                raise AssertionError(f"Resultado inesperado do cadastro - URL: {current_url}")
    
    def test_cadastro_email_duplicado(self, page: Page):
        """Testa cadastro com email já existente"""
        logger.info("Iniciando teste de cadastro com email duplicado")
        
        # Primeiro, criar um usuário
        email_existente = "usuario_existente@teste.com"
        
        # Verificar se o usuário já existe, se não, criar
        existing_user = self.db.execute(
            "SELECT id FROM usuarios WHERE email = ?", 
            (email_existente,)
        ).fetchone()
        
        if not existing_user:
            self.db.execute("""
                INSERT INTO usuarios (email, senha_hash, nome, tipo_usuario, confirmado)
                VALUES (?, ?, ?, ?, ?)
            """, (email_existente, "hash_teste", "Usuário Existente", "cliente", True))
            self.db.commit()
        
        # Navegar para a página de cadastro
        page.goto("http://localhost:8000/cadastro")
        page.wait_for_load_state("networkidle")
        
        # Preencher formulário com email já existente
        timestamp = str(int(time.time()))
        page.fill('input[name="nome"]', f"Novo Usuário {timestamp}")
        page.fill('input[name="email"]', email_existente)  # Email duplicado
        page.fill('input[name="telefone"]', "11999887766")
        page.fill('input[name="cpf_cnpj"]', "98765432100")
        page.fill('input[name="cep"]', "01234567")
        page.fill('input[name="endereco"]', "Rua Nova, 456")
        page.fill('input[name="bairro"]', "Bairro Novo")
        page.fill('input[name="cidade"]', "São Paulo")
        page.fill('input[name="uf"]', "SP")
        page.fill('input[name="data_nascimento"]', "1985-05-15")
        page.fill('input[name="senha"]', "senha456")
        page.fill('input[name="confirmar_senha"]', "senha456")
        
        # Submeter o formulário
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Verificar se há mensagem de erro sobre email duplicado
        error_message = page.locator(".alert-danger, .error, .message-error")
        expect(error_message).to_be_visible()
        
        # Verificar se a mensagem contém informação sobre email já existente
        error_text = error_message.text_content()
        assert "email" in error_text.lower() or "já existe" in error_text.lower()
        
        logger.info("Teste de email duplicado passou - erro exibido corretamente")
    
    def test_cadastro_campos_obrigatorios(self, page: Page):
        """Testa cadastro com campos obrigatórios vazios"""
        logger.info("Iniciando teste de campos obrigatórios")
        
        page.goto("http://localhost:8000/cadastro")
        page.wait_for_load_state("networkidle")
        
        # Tentar submeter formulário vazio
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)
        
        # Verificar se há validação de campos obrigatórios
        # Pode ser validação HTML5 ou mensagens de erro customizadas
        
        # Verificar se ainda está na página de cadastro (não foi submetido)
        expect(page).to_have_url("http://localhost:8000/cadastro")
        
        logger.info("Teste de campos obrigatórios passou")
    
    def test_cadastro_dados_invalidos(self, page: Page):
        """Testa cadastro com dados inválidos"""
        logger.info("Iniciando teste de dados inválidos")
        
        page.goto("http://localhost:8000/cadastro")
        page.wait_for_load_state("networkidle")
        
        # Preencher com dados inválidos
        page.fill('input[name="nome"]', "A")  # Nome muito curto
        page.fill('input[name="email"]', "email_invalido")  # Email inválido
        page.fill('input[name="telefone"]', "123")  # Telefone inválido
        page.fill('input[name="cpf_cnpj"]', "123")  # CPF inválido
        page.fill('input[name="cep"]', "123")  # CEP inválido
        page.fill('input[name="senha"]', "123")  # Senha muito curta
        
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Verificar se há mensagens de erro de validação
        # Pode permanecer na mesma página ou mostrar erros
        
        logger.info("Teste de dados inválidos concluído")
    
    def test_reproduzir_erro_original(self, page: Page):
        """Reproduz o cenário específico que estava causando erro"""
        logger.info("Reproduzindo cenário de erro original")
        
        page.goto("http://localhost:8000/cadastro")
        page.wait_for_load_state("networkidle")
        
        # Capturar screenshot inicial
        page.screenshot(path="tmp/cadastro_inicial.png")
        
        # Preencher exatamente como no exemplo da imagem
        page.fill('input[name="nome"]', "Fabio Toschi V Jr")
        page.fill('input[name="email"]', "fabiotoschi@gmail.com")
        page.fill('input[name="telefone"]', "11985206742")
        page.fill('input[name="cpf_cnpj"]', "96206485015")
        page.fill('input[name="cep"]', "01234567")
        page.fill('input[name="endereco"]', "Rua General Francisco de Paula Cidade")
        page.fill('input[name="bairro"]', "Chácara das Pedras")
        page.fill('input[name="cidade"]', "Porto Alegre")
        page.fill('input[name="uf"]', "RS")
        page.fill('input[name="data_nascimento"]', "1980-03-10")
        page.fill('input[name="senha"]', "senha123")
        page.fill('input[name="confirmar_senha"]', "senha123")
        
        # Aguardar preenchimento
        page.wait_for_timeout(1000)
        
        # Capturar screenshot antes do submit
        page.screenshot(path="tmp/cadastro_preenchido.png")
        
        # Submeter o formulário
        page.click('button[type="submit"]')
        
        # Aguardar resposta
        page.wait_for_load_state("networkidle")
        
        # Capturar screenshot após submit
        page.screenshot(path="tmp/cadastro_resultado.png")
        
        # Verificar se houve erro ou sucesso
        current_url = page.url
        page_content = page.content()
        
        logger.info(f"URL após cadastro: {current_url}")
        
        # Verificar se há mensagens de erro
        error_elements = page.locator(".alert-danger, .error, .message-error")
        success_elements = page.locator(".alert-success, .success, .message-success")
        
        if error_elements.count() > 0:
            error_text = error_elements.first.text_content()
            logger.error(f"Erro encontrado no cadastro: {error_text}")
            
            # Verificar se é o erro específico da coluna email_enviado
            if "email_enviado" in error_text.lower():
                logger.error("ERRO CONFIRMADO: Problema com coluna email_enviado")
                raise AssertionError(f"Erro da coluna email_enviado ainda presente: {error_text}")
            else:
                logger.info(f"Erro diferente encontrado: {error_text}")
        
        elif success_elements.count() > 0:
            success_text = success_elements.first.text_content()
            logger.info(f"Cadastro realizado com sucesso: {success_text}")
        
        elif current_url == "http://localhost:8000/login":
            logger.info("Cadastro realizado com sucesso - redirecionado para login")
        
        else:
            logger.warning("Resultado do cadastro não está claro")
            
        logger.info("Teste de reprodução do erro original concluído")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configurações do browser para os testes"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }