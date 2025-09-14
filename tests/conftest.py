#!/usr/bin/env python3
"""
Configuração de testes para o sistema de garantia Viemar
"""

import pytest
import tempfile
import os
from pathlib import Path
from fastlite import Database
from fasthtml.common import *

from app.config import Config
from app.database import init_database
from app.auth import setup_auth
from app.routes import setup_routes
from app.routes_veiculos import setup_veiculo_routes
from app.routes_garantias import setup_garantia_routes
from app.routes_admin import setup_admin_routes

@pytest.fixture
def temp_db():
    """Cria um banco de dados temporário para testes"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Usar fastlite Database que já retorna dicionários
    from fastlite import Database
    db = Database(db_path)
    init_database(db)
    
    yield db
    
    # Cleanup
    db.close()
    os.unlink(db_path)

@pytest.fixture
def test_config():
    """Configuração para testes"""
    class TestConfig(Config):
        DATABASE_PATH = ":memory:"
        DEBUG = True
        SECRET_KEY = "test-secret-key"
        EMAIL_USER = "test@example.com"
        EMAIL_PASSWORD = "test-password"
        SMTP_SERVER = "localhost"
        SMTP_PORT = 587
    
    return TestConfig

@pytest.fixture
def app(temp_db, test_config):
    """Cria uma aplicação FastHTML para testes"""
    # Definir a variável de ambiente para usar o banco temporário
    import os
    os.environ['DATABASE_PATH'] = temp_db.db
    
    fasthtml_app = FastHTML(
        debug=True,
        default_hdrs=False,
        hdrs=[
            Link(rel='stylesheet', href='/static/style.css'),
            Meta(name='viewport', content='width=device-width, initial-scale=1'),
            Meta(charset='utf-8')
        ]
    )
    
    # Configurar autenticação
    from app.auth import init_auth
    init_auth(temp_db)
    setup_auth(fasthtml_app)
    
    # Configurar rotas
    setup_routes(fasthtml_app, temp_db)
    setup_veiculo_routes(fasthtml_app, temp_db)
    setup_garantia_routes(fasthtml_app, temp_db)
    setup_admin_routes(fasthtml_app, temp_db)
    
    return fasthtml_app

@pytest.fixture
def client(app):
    """Cliente de teste para requisições HTTP"""
    try:
        from fasthtml.common import TestClient
    except ImportError:
        from starlette.testclient import TestClient
    return TestClient(app, follow_redirects=False)

@pytest.fixture
def sample_user_data():
    """Dados de usuário para testes"""
    return {
        'nome': 'João Silva',
        'email': 'joao@example.com',
        'confirmado': True,
        'cpf_cnpj': '12345678901',
        'telefone': '11999999999',
        'cep': '01234567',
        'endereco': 'Rua Teste, 123',
        'bairro': 'Centro',
        'cidade': 'São Paulo',
        'uf': 'SP',
        'tipo_usuario': 'cliente'
    }

@pytest.fixture
def sample_produto_data():
    """Dados de produto para testes"""
    return {
        'sku': 'VIE001',
        'descricao': 'Produto Teste Viemar',
        'ativo': True
    }

@pytest.fixture
def sample_veiculo_data():
    """Dados de veículo para testes"""
    return {
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'ano_modelo': '2020',
        'placa': 'ABC1234',
        'chassi': '1HGBH41JXMN109186',
        'cor': 'Branco'
    }

@pytest.fixture
def sample_garantia_data():
    """Dados de garantia para testes"""
    return {
        'lote_fabricacao': 'LT2024001',
        'data_instalacao': '2024-01-15',
        'nota_fiscal': 'NF123456',
        'nome_estabelecimento': 'Oficina Teste',
        'quilometragem': 50000,
        'observacoes': 'Instalação realizada conforme manual'
    }

@pytest.fixture
def authenticated_user(client, temp_db, sample_user_data):
    """Usuário autenticado para testes"""
    from models.usuario import Usuario
    from app.auth import get_auth_manager
    
    # Filtrar apenas os campos válidos para o construtor Usuario
    user_fields = {
        'nome': sample_user_data['nome'],
        'email': sample_user_data['email'],
        'cpf_cnpj': sample_user_data['cpf_cnpj'],
        'telefone': sample_user_data['telefone'],
        'cep': sample_user_data['cep'],
        'endereco': sample_user_data['endereco'],
        'bairro': sample_user_data['bairro'],
        'cidade': sample_user_data['cidade'],
        'uf': sample_user_data['uf'],
        'tipo_usuario': sample_user_data['tipo_usuario']
    }
    
    # Criar usuário no banco
    usuario = Usuario(**user_fields)
    usuario.senha_hash = Usuario.criar_hash_senha('senha123')
    usuario_id = temp_db.execute(
        """
        INSERT INTO usuarios (nome, email, cpf_cnpj, telefone, cep, endereco, bairro, cidade, uf, senha_hash, tipo_usuario, confirmado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            usuario.nome, usuario.email, usuario.cpf_cnpj, usuario.telefone,
            usuario.cep, usuario.endereco, usuario.bairro, usuario.cidade, usuario.uf,
            usuario.senha_hash, usuario.tipo_usuario, True
        )
    )
    user_id = temp_db.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Criar sessão manualmente
    auth_manager = get_auth_manager()
    session_id = auth_manager.criar_sessao(user_id, sample_user_data['email'], usuario.tipo_usuario)
    
    # Definir cookie diretamente na instância do cliente
    client.cookies['viemar_session'] = session_id
    
    return {
        'id': user_id,
        'usuario': usuario,
        'client': client,
        'session_id': session_id,
        'user_data': sample_user_data
    }

@pytest.fixture
def admin_user(client, temp_db):
    """Usuário administrador para testes"""
    from models.usuario import Usuario
    
    admin_data = {
        'nome': 'Admin Teste',
        'email': 'admin@viemar.com.br',
        'cpf_cnpj': '00000000000',
        'telefone': '11888888888',
        'cep': '01000000',
        'endereco': 'Rua Admin, 1',
        'cidade': 'São Paulo',
        'uf': 'SP',
        'tipo_usuario': 'administrador'
    }
    
    # Criar admin no banco
    usuario = Usuario(**admin_data)
    usuario.senha_hash = Usuario.criar_hash_senha('admin123')
    temp_db.execute(
        """
        INSERT INTO usuarios (nome, email, cpf_cnpj, telefone, cep, endereco, cidade, uf, senha_hash, tipo_usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            usuario.nome, usuario.email, usuario.cpf_cnpj, usuario.telefone,
            usuario.cep, usuario.endereco, usuario.cidade, usuario.uf,
            usuario.senha_hash, usuario.tipo_usuario
        )
    )
    admin_id = temp_db.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Fazer login
    response = client.post('/login', data={
        'email': admin_data['email'],
        'senha': 'admin123'
    })
    
    return {
        'id': admin_id,
        'usuario': usuario,
        'client': client
    }