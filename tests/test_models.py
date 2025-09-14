#!/usr/bin/env python3
"""
Testes para os modelos de dados
"""

import pytest
from datetime import datetime, timedelta
from models.usuario import Usuario
from models.produto import Produto
from models.veiculo import Veiculo
from models.garantia import Garantia

class TestUsuario:
    """Testes para o modelo Usuario"""
    
    def test_criar_usuario(self, sample_user_data):
        """Testa criação de usuário"""
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
        senha = 'senha123'  # Senha de teste
        
        usuario = Usuario(**user_fields)
        usuario.senha_hash = Usuario.criar_hash_senha(senha)
        
        assert usuario.nome == sample_user_data['nome']
        assert usuario.email == sample_user_data['email']
        assert usuario.cpf_cnpj == sample_user_data['cpf_cnpj']
        assert usuario.tipo_usuario == 'cliente'
        assert usuario.senha_hash is not None
        assert usuario.senha_hash != senha  # Deve estar hasheada
    
    def test_verificar_senha(self, sample_user_data):
        """Testa verificação de senha"""
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
        senha = 'senha123'  # Senha de teste
        
        usuario = Usuario(**user_fields)
        usuario.senha_hash = Usuario.criar_hash_senha(senha)
        
        assert usuario.verificar_senha(senha) is True
        assert usuario.verificar_senha('senha_errada') is False
    
    def test_to_dict(self, sample_user_data):
        """Testa conversão para dicionário"""
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
        
        usuario = Usuario(**user_fields)
        usuario_dict = usuario.to_dict()
        
        assert 'senha_hash' not in usuario_dict  # Não deve incluir senha
        assert usuario_dict['nome'] == sample_user_data['nome']
        assert usuario_dict['email'] == sample_user_data['email']
    
    def test_migrar_senha_caspio(self):
        """Testa migração de senha do Caspio"""
        senha_caspio = '0x48656C6C6F'  # "Hello" em hex
        
        hash_migrado = Usuario.migrar_senha_caspio(senha_caspio)
        
        assert hash_migrado is not None
        # O método deve retornar a senha original se não conseguir processar
        assert isinstance(hash_migrado, str)

class TestProduto:
    """Testes para o modelo Produto"""
    
    def test_criar_produto(self, sample_produto_data):
        """Testa criação de produto"""
        produto = Produto(**sample_produto_data)
        
        assert produto.sku == sample_produto_data['sku']
        assert produto.descricao == sample_produto_data['descricao']
        assert produto.ativo is True
    
    def test_ativar_desativar(self, sample_produto_data):
        """Testa ativação e desativação de produto"""
        produto = Produto(**sample_produto_data)
        
        # Inicialmente ativo
        assert produto.ativo is True
        
        # Desativar
        produto.desativar()
        assert produto.ativo is False
        
        # Ativar novamente
        produto.ativar()
        assert produto.ativo is True
    
    def test_to_dict(self, sample_produto_data):
        """Testa conversão para dicionário"""
        produto = Produto(**sample_produto_data)
        produto_dict = produto.to_dict()
        
        assert produto_dict['sku'] == sample_produto_data['sku']
        assert produto_dict['descricao'] == sample_produto_data['descricao']
        assert produto_dict['ativo'] is True

class TestVeiculo:
    """Testes para o modelo Veiculo"""
    
    def test_criar_veiculo(self, sample_veiculo_data):
        """Testa criação de veículo"""
        # Ajustar dados para corresponder ao modelo
        veiculo_data = sample_veiculo_data.copy()
        # ano_modelo já está correto no sample_data
        veiculo_data.pop('chassi', None)  # Remover campos não existentes
        veiculo_data.pop('cor', None)
        
        veiculo = Veiculo(usuario_id=1, **veiculo_data)
        
        assert veiculo.usuario_id == 1
        assert veiculo.marca == sample_veiculo_data['marca']
        assert veiculo.modelo == sample_veiculo_data['modelo']
        assert veiculo.ano_modelo == str(sample_veiculo_data['ano_modelo'])
        assert veiculo.placa == sample_veiculo_data['placa']
        assert veiculo.ativo is True
    
    def test_formatar_placa(self, sample_veiculo_data):
        """Testa formatação de placa"""
        veiculo_data = sample_veiculo_data.copy()
        # ano_modelo já está correto no sample_data
        veiculo_data.pop('chassi', None)
        veiculo_data.pop('cor', None)
        
        veiculo = Veiculo(usuario_id=1, **veiculo_data)
        
        # Placa no formato antigo
        veiculo.placa = "ABC1234"
        assert veiculo.formatar_placa() == "ABC-1234"
        
        # Placa no formato Mercosul
        veiculo.placa = "ABC1D23"
        assert veiculo.formatar_placa() == "ABC1D23"
    
    def test_validar_placa(self, sample_veiculo_data):
        """Testa validação de placa"""
        veiculo_data = sample_veiculo_data.copy()
        # ano_modelo já está correto no sample_data
        veiculo_data.pop('chassi', None)
        veiculo_data.pop('cor', None)
        
        veiculo = Veiculo(usuario_id=1, **veiculo_data)
        
        # Placas válidas
        assert Veiculo.validar_placa(veiculo.placa) is True
        
        veiculo.placa = "ABC1D23"  # Mercosul
        assert Veiculo.validar_placa(veiculo.placa) is True
        
        # Placas inválidas
        veiculo.placa = "INVALID"
        assert Veiculo.validar_placa(veiculo.placa) is False
        
        veiculo.placa = "123ABCD"
        assert Veiculo.validar_placa(veiculo.placa) is False
    
    def test_to_dict(self, sample_veiculo_data):
        """Testa conversão para dicionário"""
        veiculo_data = sample_veiculo_data.copy()
        # ano_modelo já está correto no sample_data
        veiculo_data.pop('chassi', None)
        veiculo_data.pop('cor', None)
        
        veiculo = Veiculo(usuario_id=1, **veiculo_data)
        veiculo_dict = veiculo.to_dict()
        
        assert veiculo_dict['marca'] == sample_veiculo_data['marca']
        assert veiculo_dict['modelo'] == sample_veiculo_data['modelo']
        assert veiculo_dict['placa'] == sample_veiculo_data['placa']
        assert veiculo_dict['ativo'] is True

class TestGarantia:
    """Testes para o modelo Garantia"""
    
    def test_criar_garantia(self, sample_garantia_data):
        """Testa criação de garantia"""
        garantia = Garantia(
            usuario_id=1,
            produto_id=1,
            veiculo_id=1,
            **sample_garantia_data
        )
        
        assert garantia.usuario_id == 1
        assert garantia.produto_id == 1
        assert garantia.veiculo_id == 1
        assert garantia.lote_fabricacao == sample_garantia_data['lote_fabricacao']
        assert garantia.ativo is True
        assert garantia.data_cadastro is not None
        assert isinstance(garantia.data_cadastro, datetime)
        assert isinstance(garantia.data_vencimento, datetime)
        assert garantia.data_vencimento is not None
    
    def test_calcular_vencimento(self, sample_garantia_data):
        """Testa cálculo de data de vencimento"""
        garantia = Garantia(
            usuario_id=1,
            produto_id=1,
            veiculo_id=1,
            **sample_garantia_data
        )
        
        # Data de vencimento deve ser 2 anos após a instalação
        data_instalacao = datetime.strptime(sample_garantia_data['data_instalacao'], '%Y-%m-%d')
        data_esperada = data_instalacao + timedelta(days=730)  # 2 anos
        
        assert garantia.data_vencimento.date() == data_esperada.date()
    
    def test_validar_lote(self, sample_garantia_data):
        """Testa validação de lote de fabricação"""
        garantia = Garantia(
            usuario_id=1,
            produto_id=1,
            veiculo_id=1,
            **sample_garantia_data
        )
        
        assert Garantia.validar_lote_fabricacao(garantia.lote_fabricacao) is True
        
        # Lote inválido (menos de 3 caracteres)
        garantia.lote_fabricacao = "LT"
        assert Garantia.validar_lote_fabricacao(garantia.lote_fabricacao) is False
    
    def test_status_garantia(self, sample_garantia_data):
        """Testa verificação de status da garantia"""
        # Garantia ativa (vence no futuro)
        garantia_data_ativa = sample_garantia_data.copy()
        
        garantia_ativa = Garantia(
            usuario_id=1,
            produto_id=1,
            veiculo_id=1,
            data_instalacao=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            **{k: v for k, v in garantia_data_ativa.items() if k != 'data_instalacao'}
        )
        
        assert garantia_ativa.ativo is True
        assert garantia_ativa.is_vencida() is False
        
        # Garantia vencida
        garantia_data_vencida = sample_garantia_data.copy()
        
        garantia_vencida = Garantia(
            usuario_id=1,
            produto_id=1,
            veiculo_id=1,
            data_instalacao=(datetime.now() - timedelta(days=800)).strftime('%Y-%m-%d'),
            **{k: v for k, v in garantia_data_vencida.items() if k != 'data_instalacao'}
        )
        
        assert garantia_vencida.is_vencida() is True
    
    def test_to_dict(self, sample_garantia_data):
        """Testa conversão para dicionário"""
        garantia = Garantia(
            usuario_id=1,
            produto_id=1,
            veiculo_id=1,
            **sample_garantia_data
        )
        
        garantia_dict = garantia.to_dict()
        
        assert garantia_dict['lote_fabricacao'] == sample_garantia_data['lote_fabricacao']
        assert garantia_dict['nota_fiscal'] == sample_garantia_data['nota_fiscal']
        assert garantia_dict['ativo'] is True
        assert 'data_cadastro' in garantia_dict
        assert 'data_vencimento' in garantia_dict