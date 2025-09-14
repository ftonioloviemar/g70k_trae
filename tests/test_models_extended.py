"""Testes estendidos para modelos com foco em cobertura"""
import pytest
from datetime import datetime, date
from models.veiculo import Veiculo
from models.garantia import Garantia
from models.produto import Produto
from models.usuario import Usuario


class TestVeiculoExtended:
    """Testes estendidos para o modelo Veiculo"""
    
    def test_validar_placa_formato_antigo_valido(self):
        """Testa validação de placa formato antigo válido"""
        assert Veiculo.validar_placa('ABC1234') == True
        assert Veiculo.validar_placa('XYZ9876') == True
        
    def test_validar_placa_formato_mercosul_valido(self):
        """Testa validação de placa formato Mercosul válido"""
        assert Veiculo.validar_placa('ABC1D23') == True
        assert Veiculo.validar_placa('XYZ9A87') == True
        
    def test_validar_placa_formato_invalido(self):
        """Testa validação de placa com formato inválido"""
        assert Veiculo.validar_placa('ABC12345') == False  # Muito longa
        assert Veiculo.validar_placa('AB1234') == False    # Muito curta
        assert Veiculo.validar_placa('ABCD123') == False   # 4 letras
        assert Veiculo.validar_placa('123ABCD') == False   # Números primeiro
        assert Veiculo.validar_placa('') == False          # Vazio
        assert Veiculo.validar_placa('ABC12D3') == False   # Formato inválido
        
    def test_desativar_veiculo(self):
        """Testa desativação de veículo"""
        veiculo = Veiculo(marca="Honda", modelo="Civic", ano_modelo="2020", placa="ABC1234")
        assert veiculo.ativo == True  # Padrão é ativo
        
        veiculo.desativar()
        assert veiculo.ativo == False
        
    def test_reativar_veiculo(self):
        """Testa reativação de veículo"""
        veiculo = Veiculo(marca="Honda", modelo="Civic", ano_modelo="2020", placa="ABC1234")
        veiculo.desativar()
        assert veiculo.ativo == False
        
        veiculo.reativar()
        assert veiculo.ativo == True
        
    def test_formatar_placa(self):
        """Testa formatação de placa"""
        veiculo = Veiculo(placa="ABC1234")
        placa_formatada = veiculo.formatar_placa()
        assert placa_formatada == "ABC-1234"
        
    def test_formatar_placa_estatico(self):
        """Testa formatação estática de placa"""
        placa_formatada = Veiculo.formatar_placa_estatico("ABC1234")
        assert placa_formatada == "ABC-1234"
        
        placa_formatada = Veiculo.formatar_placa_estatico("ABC1D23")
        assert placa_formatada == "ABC1D23"
        
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        veiculo = Veiculo(marca="Honda", modelo="Civic", ano_modelo="2020", placa="ABC1234")
        veiculo_dict = veiculo.to_dict()
        
        assert isinstance(veiculo_dict, dict)
        assert veiculo_dict['marca'] == "Honda"
        assert veiculo_dict['modelo'] == "Civic"
        assert veiculo_dict['placa'] == "ABC1234"
        
    def test_from_dict(self):
        """Testa criação a partir de dicionário"""
        data = {
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano_modelo': '2021',
            'placa': 'XYZ5678'
        }
        
        veiculo = Veiculo.from_dict(data)
        assert veiculo.marca == "Toyota"
        assert veiculo.modelo == "Corolla"
        assert veiculo.placa == "XYZ5678"
        
    def test_str_repr(self):
        """Testa representações string"""
        veiculo = Veiculo(marca="Honda", modelo="Civic", placa="ABC1234")
        
        str_repr = str(veiculo)
        assert "Honda" in str_repr
        assert "Civic" in str_repr
        
        repr_str = repr(veiculo)
        assert "Veiculo" in repr_str
        assert "ABC1234" in repr_str


class TestGarantiaExtended:
    """Testes estendidos para o modelo Garantia"""
    
    def test_dias_para_vencimento(self):
        """Testa cálculo de dias para vencimento da garantia"""
        from datetime import datetime, timedelta
        
        # Garantia com 30 dias restantes
        data_vencimento = datetime.now() + timedelta(days=30)
        garantia = Garantia(
            produto_id=1,
            veiculo_id=1,
            usuario_id=1,
            data_instalacao=datetime.now(),
            data_vencimento=data_vencimento,
            nota_fiscal="123",
            lote_fabricacao="LOTE123"
        )
        
        dias = garantia.dias_para_vencimento()
        assert 29 <= dias <= 30  # Margem para diferenças de tempo
        
    def test_is_vencida(self):
        """Testa verificação se garantia está vencida"""
        from datetime import datetime, timedelta
        
        # Garantia vencida
        data_vencimento = datetime.now() - timedelta(days=1)
        garantia = Garantia(
            produto_id=1,
            veiculo_id=1,
            usuario_id=1,
            data_instalacao=datetime.now() - timedelta(days=365),
            data_vencimento=data_vencimento,
            nota_fiscal="123",
            lote_fabricacao="LOTE123"
        )
        
        assert garantia.is_vencida() == True
        
        # Garantia válida
        data_vencimento = datetime.now() + timedelta(days=30)
        garantia.data_vencimento = data_vencimento
        assert garantia.is_vencida() == False
        
    def test_km_restantes(self):
        """Testa cálculo de km restantes da garantia"""
        garantia = Garantia(
            produto_id=1,
            veiculo_id=1,
            usuario_id=1,
            quilometragem=50000,
            lote_fabricacao="LOTE123"
        )
        
        km_restantes = garantia.km_restantes()
        assert km_restantes == 20000  # 70000 - 50000
        
    def test_status_garantia(self):
        """Testa status da garantia"""
        from datetime import datetime, timedelta
        
        # Garantia ativa
        garantia = Garantia(
            produto_id=1,
            veiculo_id=1,
            usuario_id=1,
            data_vencimento=datetime.now() + timedelta(days=30),
            lote_fabricacao="LOTE123",
            ativo=True
        )
        
        status = garantia.status_garantia()
        assert status in ['Ativa', 'Vencida', 'Inativa', 'Próxima do vencimento', 'Próxima do limite de KM']
        
    def test_validar_lote_fabricacao(self):
        """Testa validação de lote de fabricação"""
        assert Garantia.validar_lote_fabricacao('LOTE123') == True
        assert Garantia.validar_lote_fabricacao('') == False
        
    def test_desativar_garantia(self):
        """Testa desativação de garantia"""
        garantia = Garantia(
            produto_id=1,
            veiculo_id=1,
            usuario_id=1,
            lote_fabricacao="LOTE123",
            ativo=True
        )
        
        garantia.desativar("Teste")
        assert garantia.ativo == False
        
    def test_reativar_garantia(self):
        """Testa reativação de garantia"""
        garantia = Garantia(
            produto_id=1,
            veiculo_id=1,
            usuario_id=1,
            lote_fabricacao="LOTE123",
            ativo=False
        )
        
        garantia.reativar("Teste")
        assert garantia.ativo == True
        
    def test_calcular_data_vencimento(self):
        """Testa cálculo da data de vencimento"""
        from datetime import datetime, timedelta
        
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            data_instalacao=datetime(2024, 1, 1)
        )
        
        data_vencimento = garantia.calcular_data_vencimento()
        expected_date = datetime(2024, 1, 1) + timedelta(days=730)
        assert data_vencimento == expected_date
        
    def test_calcular_data_vencimento_sem_instalacao(self):
        """Testa cálculo sem data de instalação"""
        garantia = Garantia(lote_fabricacao="LOTE123")
        assert garantia.calcular_data_vencimento() is None
        
    def test_is_vencida_true(self):
        """Testa garantia vencida"""
        from datetime import datetime, timedelta
        
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            data_vencimento=datetime.now() - timedelta(days=1)
        )
        assert garantia.is_vencida() == True
        
    def test_is_vencida_false(self):
        """Testa garantia não vencida"""
        from datetime import datetime, timedelta
        
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            data_vencimento=datetime.now() + timedelta(days=30)
        )
        assert garantia.is_vencida() == False
        
    def test_is_vencida_sem_data(self):
        """Testa garantia sem data de vencimento"""
        garantia = Garantia(lote_fabricacao="LOTE123")
        assert garantia.is_vencida() == False
        
    def test_dias_para_vencimento(self):
        """Testa cálculo de dias para vencimento"""
        from datetime import datetime, timedelta
        
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            data_vencimento=datetime.now() + timedelta(days=30)
        )
        dias = garantia.dias_para_vencimento()
        assert dias >= 29 and dias <= 30  # Margem para execução do teste
        
    def test_dias_para_vencimento_sem_data(self):
        """Testa dias para vencimento sem data"""
        garantia = Garantia(lote_fabricacao="LOTE123")
        assert garantia.dias_para_vencimento() is None
        
    def test_km_restantes(self):
        """Testa cálculo de km restantes"""
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            quilometragem=50000
        )
        assert garantia.km_restantes() == 20000
        
    def test_km_restantes_limite_excedido(self):
        """Testa km restantes quando limite foi excedido"""
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            quilometragem=80000
        )
        assert garantia.km_restantes() == 0
        
    def test_status_garantia_inativa(self):
        """Testa status de garantia inativa"""
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            ativo=False
        )
        assert garantia.status_garantia() == "Inativa"
        
    def test_status_garantia_vencida(self):
        """Testa status de garantia vencida"""
        from datetime import datetime, timedelta
        
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            ativo=True,
            data_vencimento=datetime.now() - timedelta(days=1)
        )
        assert garantia.status_garantia() == "Vencida"
        
    def test_status_garantia_proxima_vencimento(self):
        """Testa status próxima do vencimento"""
        from datetime import datetime, timedelta
        
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            ativo=True,
            data_vencimento=datetime.now() + timedelta(days=15),
            quilometragem=30000
        )
        assert garantia.status_garantia() == "Próxima do vencimento"
        
    def test_status_garantia_proxima_km(self):
        """Testa status próxima do limite de KM"""
        from datetime import datetime, timedelta
        
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            ativo=True,
            data_vencimento=datetime.now() + timedelta(days=365),
            quilometragem=67000
        )
        assert garantia.status_garantia() == "Próxima do limite de KM"
        
    def test_status_garantia_ativa(self):
        """Testa status de garantia ativa"""
        from datetime import datetime, timedelta
        
        garantia = Garantia(
            lote_fabricacao="LOTE123",
            ativo=True,
            data_vencimento=datetime.now() + timedelta(days=365),
            quilometragem=30000
        )
        assert garantia.status_garantia() == "Ativa"
        
    def test_validar_lote_fabricacao_valido(self):
        """Testa validação de lote válido"""
        assert Garantia.validar_lote_fabricacao("LOTE123") == True
        assert Garantia.validar_lote_fabricacao("ABC") == True
        
    def test_validar_lote_fabricacao_invalido(self):
        """Testa validação de lote inválido"""
        assert Garantia.validar_lote_fabricacao("AB") == False
        assert Garantia.validar_lote_fabricacao("") == False
        assert Garantia.validar_lote_fabricacao("  ") == False
        
    def test_str_repr_garantia(self):
        """Testa representações string da garantia"""
        garantia = Garantia(
            id=1,
            lote_fabricacao="LOTE123",
            ativo=True
        )
        
        str_repr = str(garantia)
        assert "Garantia 1" in str_repr
        assert "LOTE123" in str_repr
        
        repr_str = repr(garantia)
        assert "Garantia(" in repr_str
        assert "LOTE123" in repr_str


class TestVeiculoExtended:
    """Testes estendidos para o modelo Veiculo"""
    
    def test_formatar_placa_formato_antigo(self):
        """Testa formatação de placa formato antigo"""
        veiculo = Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano_modelo="2020",
            placa="ABC1234"
        )
        assert veiculo.formatar_placa() == "ABC-1234"
        
    def test_formatar_placa_mercosul(self):
        """Testa formatação de placa Mercosul"""
        veiculo = Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano_modelo="2020",
            placa="ABC1D23"
        )
        assert veiculo.formatar_placa() == "ABC1D23"
        
    def test_formatar_placa_com_espacos(self):
        """Testa formatação de placa com espaços"""
        veiculo = Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano_modelo="2020",
            placa="ABC 1234"
        )
        assert veiculo.formatar_placa() == "ABC-1234"
        
    def test_formatar_placa_estatico_antigo(self):
        """Testa formatação estática de placa formato antigo"""
        resultado = Veiculo.formatar_placa_estatico("abc1234")
        assert resultado == "ABC-1234"
        
    def test_formatar_placa_estatico_mercosul(self):
        """Testa formatação estática de placa Mercosul"""
        resultado = Veiculo.formatar_placa_estatico("abc1d23")
        assert resultado == "ABC1D23"
        
    def test_formatar_placa_estatico_com_hifen(self):
        """Testa formatação estática removendo hífen"""
        resultado = Veiculo.formatar_placa_estatico("ABC-1234")
        assert resultado == "ABC-1234"
        
    def test_validar_placa_formato_antigo_valido(self):
        """Testa validação de placa formato antigo válida"""
        assert Veiculo.validar_placa("ABC1234") == True
        assert Veiculo.validar_placa("XYZ9876") == True
        
    def test_validar_placa_mercosul_valido(self):
        """Testa validação de placa Mercosul válida"""
        assert Veiculo.validar_placa("ABC1D23") == True
        assert Veiculo.validar_placa("XYZ2E45") == True
        
    def test_validar_placa_com_hifen(self):
        """Testa validação de placa com hífen"""
        assert Veiculo.validar_placa("ABC-1234") == True
        
    def test_validar_placa_invalida_tamanho(self):
        """Testa validação de placa com tamanho inválido"""
        assert Veiculo.validar_placa("ABC123") == False
        assert Veiculo.validar_placa("ABC12345") == False
        assert Veiculo.validar_placa("") == False
        
    def test_validar_placa_invalida_formato(self):
        """Testa validação de placa com formato inválido"""
        assert Veiculo.validar_placa("1234567") == False
        assert Veiculo.validar_placa("ABCDEFG") == False
        assert Veiculo.validar_placa("AB1234C") == False
        
    def test_atualizar_veiculo(self):
        """Testa atualização de dados do veículo"""
        from datetime import datetime, timedelta
        import time
        
        veiculo = Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano_modelo="2020",
            placa="ABC1234",
            data_atualizacao=datetime.now() - timedelta(seconds=1)
        )
        
        data_antes = veiculo.data_atualizacao
        time.sleep(0.01)  # Pequeno delay para garantir diferença de tempo
        veiculo.atualizar(marca="Honda", modelo="Civic")
        
        assert veiculo.marca == "Honda"
        assert veiculo.modelo == "Civic"
        assert veiculo.data_atualizacao > data_antes
        
    def test_atualizar_veiculo_campos_protegidos(self):
        """Testa que campos protegidos não são atualizados"""
        veiculo = Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano_modelo="2020",
            placa="ABC1234"
        )
        
        id_original = veiculo.id
        data_cadastro_original = veiculo.data_cadastro
        
        veiculo.atualizar(id=999, data_cadastro=datetime.now())
        
        assert veiculo.id == id_original
        assert veiculo.data_cadastro == data_cadastro_original
        
    def test_desativar_veiculo(self):
        """Testa desativação do veículo"""
        from datetime import datetime, timedelta
        import time
        
        veiculo = Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano_modelo="2020",
            placa="ABC1234",
            data_atualizacao=datetime.now() - timedelta(seconds=1)
        )
        
        assert veiculo.ativo == True
        data_antes = veiculo.data_atualizacao
        time.sleep(0.01)  # Pequeno delay para garantir diferença de tempo
        
        veiculo.desativar()
        
        assert veiculo.ativo == False
        assert veiculo.data_atualizacao > data_antes
        
    def test_reativar_veiculo(self):
        """Testa reativação do veículo"""
        from datetime import datetime, timedelta
        import time
        
        veiculo = Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano_modelo="2020",
            placa="ABC1234",
            ativo=False,
            data_atualizacao=datetime.now() - timedelta(seconds=1)
        )
        
        assert veiculo.ativo == False
        data_antes = veiculo.data_atualizacao
        time.sleep(0.01)  # Pequeno delay para garantir diferença de tempo
        
        veiculo.reativar()
        
        assert veiculo.ativo == True
        assert veiculo.data_atualizacao > data_antes
        
    def test_str_repr_veiculo(self):
        """Testa representações string do veículo"""
        veiculo = Veiculo(
            id=1,
            marca="Toyota",
            modelo="Corolla",
            ano_modelo="2020",
            placa="ABC1234"
        )
        
        str_repr = str(veiculo)
        assert "Toyota" in str_repr
        assert "Corolla" in str_repr
        assert "2020" in str_repr
        assert "ABC-1234" in str_repr
        
        repr_str = repr(veiculo)
        assert "Veiculo(" in repr_str
        assert "Toyota" in repr_str
        assert "ABC1234" in repr_str


class TestProdutoExtended:
    """Testes estendidos para o modelo Produto"""
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        produto = Produto(
            sku="SKU123",
            descricao="Descrição do produto"
        )
        
        produto_dict = produto.to_dict()
        assert isinstance(produto_dict, dict)
        assert produto_dict['sku'] == "SKU123"
        assert produto_dict['descricao'] == "Descrição do produto"
        
    def test_from_dict(self):
        """Testa criação a partir de dicionário"""
        data = {
            'sku': 'SKU456',
            'descricao': 'Nova descrição',
            'ativo': False
        }
        
        produto = Produto.from_dict(data)
        assert produto.sku == "SKU456"
        assert produto.descricao == "Nova descrição"
        assert produto.ativo == False
        
    def test_str_repr(self):
        """Testa representações string"""
        produto = Produto(sku="SKU123", descricao="Produto Teste")
        
        str_repr = str(produto)
        assert "SKU123" in str_repr
        
        repr_str = repr(produto)
        assert "Produto" in repr_str
        assert "SKU123" in repr_str
        
    def test_ativar_produto(self):
        """Testa ativação de produto"""
        produto = Produto(sku="TEST001", descricao="Produto Teste")
        produto.desativar()
        assert produto.ativo == False
        
        produto.ativar()
        assert produto.ativo == True
        
    def test_desativar_produto(self):
        """Testa desativação de produto"""
        produto = Produto(sku="TEST001", descricao="Produto Teste")
        assert produto.ativo == True  # Padrão é ativo
        
        produto.desativar()
        assert produto.ativo == False
        
    def test_atualizar_descricao(self):
        """Testa atualização de descrição"""
        produto = Produto(sku="TEST001", descricao="Produto Teste")
        nova_descricao = "Nova Descrição"
        
        produto.atualizar_descricao(nova_descricao)
        assert produto.descricao == nova_descricao


class TestUsuarioExtended:
    """Testes estendidos para o modelo Usuario"""
    
    def test_migrar_senha_caspio(self):
        """Testa migração de senha do Caspio"""
        senha_hex = "0x7b22616c676f726974686d223a2263624176673122"
        resultado = Usuario.migrar_senha_caspio(senha_hex)
        assert isinstance(resultado, str)
        
    def test_migrar_senha_caspio_invalida(self):
        """Testa migração de senha inválida"""
        senha_invalida = "senha_normal"
        resultado = Usuario.migrar_senha_caspio(senha_invalida)
        assert resultado == senha_invalida
        
    def test_criar_hash_senha(self):
        """Testa criação de hash de senha"""
        senha = 'senha123'
        hash_senha = Usuario.criar_hash_senha(senha)
        assert hash_senha != senha
        assert len(hash_senha) > 0
        
    def test_verificar_senha_correta(self, sample_user_data):
        """Testa verificação de senha correta"""
        usuario = Usuario(**sample_user_data)
        usuario.senha_hash = Usuario.criar_hash_senha('senha123')
        assert usuario.verificar_senha('senha123') == True
        
    def test_verificar_senha_incorreta(self, sample_user_data):
        """Testa verificação de senha incorreta"""
        usuario = Usuario(**sample_user_data)
        usuario.senha_hash = Usuario.criar_hash_senha('senha123')
        assert usuario.verificar_senha('senha_errada') == False
        
    def test_gerar_token_confirmacao(self):
        """Testa geração de token de confirmação"""
        token = Usuario.gerar_token_confirmacao()
        assert len(token) > 0
        assert isinstance(token, str)
        
    def test_is_admin_true(self, sample_user_data):
        """Testa verificação de administrador"""
        sample_user_data['tipo_usuario'] = 'administrador'
        usuario = Usuario(**sample_user_data)
        assert usuario.is_admin() == True
        
    def test_is_admin_false(self, sample_user_data):
        """Testa verificação de não administrador"""
        sample_user_data['tipo_usuario'] = 'cliente'
        usuario = Usuario(**sample_user_data)
        assert usuario.is_admin() == False
        
    def test_is_confirmed_true(self, sample_user_data):
        """Testa verificação de usuário confirmado"""
        sample_user_data['confirmado'] = True
        usuario = Usuario(**sample_user_data)
        assert usuario.is_confirmed() == True
        
    def test_is_confirmed_false(self, sample_user_data):
        """Testa verificação de usuário não confirmado"""
        sample_user_data['confirmado'] = False
        usuario = Usuario(**sample_user_data)
        assert usuario.is_confirmed() == False
        
    def test_to_dict(self, sample_user_data):
        """Testa conversão para dicionário"""
        usuario = Usuario(**sample_user_data)
        dict_data = usuario.to_dict()
        assert isinstance(dict_data, dict)
        assert 'email' in dict_data
        assert 'nome' in dict_data
        
    def test_from_dict(self, sample_user_data):
        """Testa criação a partir de dicionário"""
        usuario = Usuario.from_dict(sample_user_data)
        assert isinstance(usuario, Usuario)
        assert usuario.email == sample_user_data['email']
        assert usuario.nome == sample_user_data['nome']