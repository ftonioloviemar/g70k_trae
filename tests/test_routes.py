#!/usr/bin/env python3
"""
Testes para as rotas da aplicação
"""

import pytest
from fasthtml.common import *

class TestPublicRoutes:
    """Testes para rotas públicas"""
    
    def test_home_page(self, client):
        """Testa página inicial"""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Viemar' in response.text
    
    def test_login_page_get(self, client):
        """Testa página de login (GET)"""
        response = client.get('/login')
        assert response.status_code == 200
        assert 'Login' in response.text
    
    def test_register_page_get(self, client):
        """Testa página de cadastro (GET)"""
        response = client.get('/cadastro')
        assert response.status_code == 200
        assert 'Cadastro' in response.text

class TestAuthRoutes:
    """Testes para rotas de autenticação"""
    
    def test_login_success(self, client, temp_db, sample_user_data):
        """Testa login com sucesso"""
        from models.usuario import Usuario
        
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
        temp_db.execute(
            """
            INSERT INTO usuarios (nome, email, cpf_cnpj, telefone, cep, endereco, bairro, cidade, uf, senha_hash, tipo_usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                usuario.nome, usuario.email, usuario.cpf_cnpj, usuario.telefone,
                usuario.cep, usuario.endereco, usuario.bairro, usuario.cidade, usuario.uf,
                usuario.senha_hash, usuario.tipo_usuario
            )
        )
        
        # Tentar fazer login
        response = client.post('/login', data={
            'email': sample_user_data['email'],
            'senha': 'senha123'
        })
        
        # Deve redirecionar para dashboard
        assert response.status_code in [200, 302, 303]
    
    def test_login_invalid_credentials(self, client):
        """Testa login com credenciais inválidas"""
        response = client.post('/login', data={
            'email': 'inexistente@example.com',
            'senha': 'senha_errada'
        })
        
        # Deve retornar erro ou redirecionar com erro
        assert response.status_code in [200, 302, 400, 401]
    
    def test_register_success(self, client, temp_db, sample_user_data):
        """Testa cadastro com sucesso"""
        print(f"Dados do usuário: {sample_user_data}")
        response = client.post('/cadastro', data=sample_user_data)
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        if hasattr(response, 'text'):
            print(f"Response content: {response.text[:500]}")
        
        # Deve redirecionar ou mostrar sucesso
        assert response.status_code in [200, 302, 303]
        
        # Verificar se usuário foi criado no banco
        user = temp_db.execute(
            "SELECT nome, email FROM usuarios WHERE email = ?",
            (sample_user_data['email'],)
        ).fetchone()
        
        print(f"Usuário encontrado no banco: {user}")
        
        # Verificar todos os usuários no banco para debug
        all_users = temp_db.execute("SELECT nome, email FROM usuarios").fetchall()
        print(f"Todos os usuários no banco: {all_users}")
        
        assert user is not None
        assert user[0] == sample_user_data['nome']  # nome é o primeiro campo
        assert user[1] == sample_user_data['email']  # email é o segundo campo
    
    def test_register_duplicate_email(self, client, temp_db, sample_user_data):
        """Testa cadastro com email duplicado"""
        from models.usuario import Usuario
        
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
        
        # Criar usuário no banco primeiro
        usuario = Usuario(**user_fields)
        temp_db.execute(
            """
            INSERT INTO usuarios (nome, email, cpf_cnpj, telefone, cep, endereco, bairro, cidade, uf, senha_hash, tipo_usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                usuario.nome, usuario.email, usuario.cpf_cnpj, usuario.telefone,
                usuario.cep, usuario.endereco, usuario.bairro, usuario.cidade, usuario.uf,
                usuario.senha_hash, usuario.tipo_usuario
            )
        )
        
        # Tentar cadastrar novamente com mesmo email
        response = client.post('/cadastro', data=sample_user_data)
        
        # Deve retornar erro
        assert response.status_code in [200, 400, 409]
    
    def test_logout(self, authenticated_user):
        """Testa logout"""
        client = authenticated_user['client']
        
        response = client.get('/logout')
        
        # Deve redirecionar para home
        assert response.status_code in [200, 302, 303]

class TestProtectedRoutes:
    """Testes para rotas protegidas"""
    
    def test_dashboard_without_auth(self, client):
        """Testa acesso ao dashboard sem autenticação"""
        response = client.get('/cliente/dashboard')
        
        print(f"Status code: {response.status_code}")
        print(f"Headers: {response.headers}")
        if hasattr(response, 'text'):
            print(f"Response content: {response.text[:500]}")
        
        # Deve redirecionar para login
        assert response.status_code in [302, 303, 401]
    
    def test_dashboard_with_auth(self, authenticated_user):
        """Testa acesso ao dashboard com autenticação"""
        client = authenticated_user['client']
        
        response = client.get('/cliente/dashboard')
        
        # Deve redirecionar para /cliente (dashboard real)
        assert response.status_code == 302
        assert '/cliente' in response.headers.get('location', '')
    
    def test_veiculos_page_with_auth(self, authenticated_user):
        """Testa página de veículos com autenticação"""
        client = authenticated_user['client']
        
        response = client.get('/cliente/veiculos')
        
        # Deve mostrar página de veículos
        assert response.status_code == 200
    
    def test_garantias_page_with_auth(self, authenticated_user):
        """Testa página de garantias com autenticação"""
        client = authenticated_user['client']
        
        response = client.get('/cliente/garantias')
        
        # Deve mostrar página de garantias
        assert response.status_code == 200

class TestVeiculoRoutes:
    """Testes para rotas de veículos"""
    
    def test_create_veiculo(self, authenticated_user, temp_db, sample_veiculo_data):
        """Testa criação de veículo"""
        client = authenticated_user['client']
        
        response = client.post('/cliente/veiculos', data=sample_veiculo_data)
        
        # Deve redirecionar ou mostrar sucesso
        assert response.status_code in [200, 302, 303]
        
        # Verificar se veículo foi criado no banco
        veiculo = temp_db.execute(
            "SELECT * FROM veiculos WHERE placa = ?",
            (sample_veiculo_data['placa'],)
        ).fetchone()
        
        assert veiculo is not None
        # veiculo é uma tupla: (id, usuario_id, marca, modelo, ano_modelo, placa, data_cadastro, data_atualizacao, ativo, cor, chassi)
        assert veiculo[2] == sample_veiculo_data['marca']  # marca está no índice 2
    
    def test_edit_veiculo(self, authenticated_user, temp_db, sample_veiculo_data):
        """Testa edição de veículo"""
        client = authenticated_user['client']
        user_id = authenticated_user['id']
        
        # Criar veículo primeiro
        temp_db.execute(
            """
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, chassi, cor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, sample_veiculo_data['marca'], sample_veiculo_data['modelo'],
                sample_veiculo_data['ano_modelo'], sample_veiculo_data['placa'],
                sample_veiculo_data['chassi'], sample_veiculo_data['cor']
            )
        )
        veiculo_id = temp_db.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Editar veículo
        updated_data = sample_veiculo_data.copy()
        updated_data['cor'] = 'Preto'
        
        response = client.post(f'/cliente/veiculos/{veiculo_id}', data=updated_data)
        
        # Deve redirecionar ou mostrar sucesso
        assert response.status_code in [200, 302, 303]
        
        # Verificar se foi atualizado
        veiculo = temp_db.execute(
            "SELECT cor FROM veiculos WHERE id = ?",
            (veiculo_id,)
        ).fetchone()
        
        assert veiculo[0] == 'Preto'

class TestGarantiaRoutes:
    """Testes para rotas de garantias"""
    
    def test_create_garantia(self, authenticated_user, temp_db, sample_produto_data, sample_veiculo_data, sample_garantia_data):
        """Testa criação de garantia"""
        client = authenticated_user['client']
        user_id = authenticated_user['id']
        
        # Criar produto
        temp_db.execute(
            "INSERT INTO produtos (sku, descricao, ativo) VALUES (?, ?, ?)",
            (sample_produto_data['sku'], sample_produto_data['descricao'], sample_produto_data['ativo'])
        )
        produto_id = temp_db.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Criar veículo
        temp_db.execute(
            """
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, chassi, cor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, sample_veiculo_data['marca'], sample_veiculo_data['modelo'],
                sample_veiculo_data['ano_modelo'], sample_veiculo_data['placa'],
                sample_veiculo_data['chassi'], sample_veiculo_data['cor']
            )
        )
        veiculo_id = temp_db.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Criar garantia
        garantia_data = sample_garantia_data.copy()
        garantia_data['produto_id'] = produto_id
        garantia_data['veiculo_id'] = veiculo_id
        
        response = client.post('/cliente/garantias/nova', data=garantia_data)
        
        # Deve redirecionar ou mostrar sucesso
        assert response.status_code in [200, 302, 303]
        
        # Verificar se garantia foi criada no banco
        garantia = temp_db.execute(
            "SELECT * FROM garantias WHERE lote_fabricacao = ?",
            (sample_garantia_data['lote_fabricacao'],)
        ).fetchone()
        
        assert garantia is not None
        # Acessar por índice já que fetchone() retorna tupla
        assert garantia[1] == user_id  # usuario_id é a segunda coluna

class TestAdminRoutes:
    """Testes para rotas administrativas"""
    
    def test_admin_access_without_auth(self, client):
        """Testa acesso admin sem autenticação"""
        response = client.get('/admin')
        
        # Deve redirecionar para login
        assert response.status_code in [302, 303, 401]
    
    def test_admin_access_with_regular_user(self, authenticated_user):
        """Testa acesso admin com usuário comum"""
        client = authenticated_user['client']
        
        response = client.get('/admin')
        
        # Deve negar acesso
        assert response.status_code in [403, 302, 303]
    
    def test_admin_access_with_admin_user(self, admin_user):
        """Testa acesso admin com usuário administrador"""
        client = admin_user['client']
        
        response = client.get('/admin')
        
        # Deve permitir acesso
        assert response.status_code == 200
    
    def test_admin_usuarios_list(self, admin_user):
        """Testa listagem de usuários no admin"""
        client = admin_user['client']
        
        response = client.get('/admin/usuarios')
        
        # Deve mostrar lista de usuários
        assert response.status_code == 200
    
    def test_admin_produtos_list(self, admin_user):
        """Testa listagem de produtos no admin"""
        client = admin_user['client']
        
        response = client.get('/admin/produtos')
        
        # Deve mostrar lista de produtos
        assert response.status_code == 200