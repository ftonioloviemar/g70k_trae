#!/usr/bin/env python3
"""
Testes para o modelo Garantia
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from models.garantia import Garantia


class TestGarantia:
    """Testes para a classe Garantia"""
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão"""
        garantia = Garantia()
        
        assert garantia.id is None
        assert garantia.usuario_id == 0
        assert garantia.produto_id == 0
        assert garantia.veiculo_id == 0
        assert garantia.lote_fabricacao == ''
        assert garantia.data_instalacao is None
        assert garantia.nota_fiscal == ''
        assert garantia.nome_estabelecimento == ''
        assert garantia.quilometragem == 0
        assert garantia.data_cadastro is not None  # Deve ser definida automaticamente
        assert garantia.data_vencimento is None
        assert garantia.ativo is True
        assert garantia.observacoes == ''
    
    def test_init_with_values(self):
        """Testa inicialização com valores específicos"""
        data_instalacao = datetime(2024, 1, 15)
        
        garantia = Garantia(
            id=1,
            usuario_id=123,
            produto_id=456,
            veiculo_id=789,
            lote_fabricacao="LOTE123",
            data_instalacao=data_instalacao,
            nota_fiscal="NF001",
            nome_estabelecimento="Oficina Teste",
            quilometragem=15000,
            ativo=True,
            observacoes="Teste"
        )
        
        assert garantia.id == 1
        assert garantia.usuario_id == 123
        assert garantia.produto_id == 456
        assert garantia.veiculo_id == 789
        assert garantia.lote_fabricacao == "LOTE123"
        assert garantia.data_instalacao == data_instalacao
        assert garantia.nota_fiscal == "NF001"
        assert garantia.nome_estabelecimento == "Oficina Teste"
        assert garantia.quilometragem == 15000
        assert garantia.ativo is True
        assert garantia.observacoes == "Teste"
    
    def test_post_init_data_cadastro(self):
        """Testa se data_cadastro é definida automaticamente"""
        with patch('models.garantia.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat = datetime.fromisoformat
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            garantia = Garantia()
            
            assert garantia.data_cadastro == mock_now
    
    def test_post_init_data_vencimento_calculation(self):
        """Testa cálculo automático da data de vencimento"""
        data_instalacao = datetime(2024, 1, 15)
        
        garantia = Garantia(data_instalacao=data_instalacao)
        
        expected_vencimento = data_instalacao + timedelta(days=730)
        assert garantia.data_vencimento == expected_vencimento
    
    def test_post_init_string_to_datetime_conversion(self):
        """Testa conversão de string para datetime"""
        garantia = Garantia(data_instalacao="2024-01-15T10:30:00")
        
        assert isinstance(garantia.data_instalacao, datetime)
        assert garantia.data_instalacao == datetime(2024, 1, 15, 10, 30, 0)
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        data_instalacao = datetime(2024, 1, 15, 10, 30, 0)
        data_cadastro = datetime(2024, 1, 10, 9, 0, 0)
        data_vencimento = datetime(2026, 1, 15, 10, 30, 0)
        
        garantia = Garantia(
            id=1,
            usuario_id=123,
            produto_id=456,
            veiculo_id=789,
            lote_fabricacao="LOTE123",
            data_instalacao=data_instalacao,
            nota_fiscal="NF001",
            nome_estabelecimento="Oficina Teste",
            quilometragem=15000,
            data_cadastro=data_cadastro,
            data_vencimento=data_vencimento,
            ativo=True,
            observacoes="Teste"
        )
        
        result = garantia.to_dict()
        
        expected = {
            'id': 1,
            'usuario_id': 123,
            'produto_id': 456,
            'veiculo_id': 789,
            'lote_fabricacao': 'LOTE123',
            'data_instalacao': '2024-01-15T10:30:00',
            'nota_fiscal': 'NF001',
            'nome_estabelecimento': 'Oficina Teste',
            'quilometragem': 15000,
            'data_cadastro': '2024-01-10T09:00:00',
            'data_vencimento': '2026-01-15T10:30:00',
            'ativo': True,
            'observacoes': 'Teste'
        }
        
        assert result == expected
    
    @patch('models.garantia.datetime')
    def test_to_dict_with_none_dates(self, mock_datetime):
        """Testa conversão para dicionário com datas None"""
        # Mock para evitar data_cadastro automática
        mock_datetime.now.return_value = None
        mock_datetime.fromisoformat = datetime.fromisoformat
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        garantia = Garantia(
            id=1,
            data_instalacao=None,
            data_vencimento=None
        )
        # Força data_cadastro como None após inicialização
        garantia.data_cadastro = None
        
        result = garantia.to_dict()
        
        assert result['data_instalacao'] is None
        assert result['data_cadastro'] is None
        assert result['data_vencimento'] is None
    
    def test_from_dict(self):
        """Testa criação a partir de dicionário"""
        data = {
            'id': 1,
            'usuario_id': 123,
            'produto_id': 456,
            'veiculo_id': 789,
            'lote_fabricacao': 'LOTE123',
            'data_instalacao': '2024-01-15T10:30:00',
            'nota_fiscal': 'NF001',
            'nome_estabelecimento': 'Oficina Teste',
            'quilometragem': 15000,
            'data_cadastro': '2024-01-10T09:00:00',
            'data_vencimento': '2026-01-15T10:30:00',
            'ativo': True,
            'observacoes': 'Teste'
        }
        
        garantia = Garantia.from_dict(data)
        
        assert garantia.id == 1
        assert garantia.usuario_id == 123
        assert garantia.produto_id == 456
        assert garantia.veiculo_id == 789
        assert garantia.lote_fabricacao == 'LOTE123'
        assert garantia.data_instalacao == datetime(2024, 1, 15, 10, 30, 0)
        assert garantia.nota_fiscal == 'NF001'
        assert garantia.nome_estabelecimento == 'Oficina Teste'
        assert garantia.quilometragem == 15000
        assert garantia.data_cadastro == datetime(2024, 1, 10, 9, 0, 0)
        assert garantia.data_vencimento == datetime(2026, 1, 15, 10, 30, 0)
        assert garantia.ativo is True
        assert garantia.observacoes == 'Teste'
    
    def test_from_dict_with_datetime_objects(self):
        """Testa from_dict com objetos datetime"""
        data_instalacao = datetime(2024, 1, 15, 10, 30, 0)
        
        data = {
            'id': 1,
            'data_instalacao': data_instalacao
        }
        
        garantia = Garantia.from_dict(data)
        
        assert garantia.data_instalacao == data_instalacao
    
    def test_from_dict_ignores_unknown_keys(self):
        """Testa se from_dict ignora chaves desconhecidas"""
        data = {
            'id': 1,
            'unknown_key': 'unknown_value',
            'lote_fabricacao': 'LOTE123'
        }
        
        garantia = Garantia.from_dict(data)
        
        assert garantia.id == 1
        assert garantia.lote_fabricacao == 'LOTE123'
        assert not hasattr(garantia, 'unknown_key')
    
    def test_calcular_data_vencimento(self):
        """Testa cálculo da data de vencimento"""
        data_instalacao = datetime(2024, 1, 15)
        garantia = Garantia(data_instalacao=data_instalacao)
        
        result = garantia.calcular_data_vencimento()
        expected = data_instalacao + timedelta(days=730)
        
        assert result == expected
    
    def test_calcular_data_vencimento_sem_instalacao(self):
        """Testa cálculo sem data de instalação"""
        garantia = Garantia()
        
        result = garantia.calcular_data_vencimento()
        
        assert result is None
    
    def test_is_vencida_true(self):
        """Testa se garantia está vencida"""
        data_vencimento = datetime.now() - timedelta(days=1)
        garantia = Garantia(data_vencimento=data_vencimento)
        
        assert garantia.is_vencida() is True
    
    def test_is_vencida_false(self):
        """Testa se garantia não está vencida"""
        data_vencimento = datetime.now() + timedelta(days=1)
        garantia = Garantia(data_vencimento=data_vencimento)
        
        assert garantia.is_vencida() is False
    
    def test_is_vencida_sem_data_vencimento(self):
        """Testa is_vencida sem data de vencimento"""
        garantia = Garantia()
        
        assert garantia.is_vencida() is False
    
    def test_dias_para_vencimento(self):
        """Testa cálculo de dias para vencimento"""
        data_vencimento = datetime.now() + timedelta(days=30)
        garantia = Garantia(data_vencimento=data_vencimento)
        
        result = garantia.dias_para_vencimento()
        
        assert result == 30
    
    def test_dias_para_vencimento_vencida(self):
        """Testa dias para vencimento quando já vencida"""
        data_vencimento = datetime.now() - timedelta(days=5)
        garantia = Garantia(data_vencimento=data_vencimento)
        
        result = garantia.dias_para_vencimento()
        
        assert result == 0
    
    def test_dias_para_vencimento_sem_data(self):
        """Testa dias para vencimento sem data"""
        garantia = Garantia()
        
        result = garantia.dias_para_vencimento()
        
        assert result is None
    
    def test_km_restantes(self):
        """Testa cálculo de km restantes"""
        garantia = Garantia(quilometragem=30000)
        
        result = garantia.km_restantes()
        
        assert result == 40000  # 70000 - 30000
    
    def test_km_restantes_limite_excedido(self):
        """Testa km restantes quando limite foi excedido"""
        garantia = Garantia(quilometragem=80000)
        
        result = garantia.km_restantes()
        
        assert result == 0
    
    def test_status_garantia_inativa(self):
        """Testa status de garantia inativa"""
        garantia = Garantia(ativo=False)
        
        assert garantia.status_garantia() == "Inativa"
    
    def test_status_garantia_vencida(self):
        """Testa status de garantia vencida"""
        data_vencimento = datetime.now() - timedelta(days=1)
        garantia = Garantia(data_vencimento=data_vencimento, ativo=True)
        
        assert garantia.status_garantia() == "Vencida"
    
    def test_status_garantia_proxima_vencimento(self):
        """Testa status próxima do vencimento"""
        data_vencimento = datetime.now() + timedelta(days=15)
        garantia = Garantia(
            data_vencimento=data_vencimento,
            quilometragem=30000,
            ativo=True
        )
        
        assert garantia.status_garantia() == "Próxima do vencimento"
    
    def test_status_garantia_proxima_limite_km(self):
        """Testa status próxima do limite de KM"""
        data_vencimento = datetime.now() + timedelta(days=365)
        garantia = Garantia(
            data_vencimento=data_vencimento,
            quilometragem=67000,  # Restam 3000 km
            ativo=True
        )
        
        assert garantia.status_garantia() == "Próxima do limite de KM"
    
    def test_status_garantia_ativa(self):
        """Testa status de garantia ativa"""
        data_vencimento = datetime.now() + timedelta(days=365)
        garantia = Garantia(
            data_vencimento=data_vencimento,
            quilometragem=30000,
            ativo=True
        )
        
        assert garantia.status_garantia() == "Ativa"
    
    def test_validar_lote_fabricacao_valido(self):
        """Testa validação de lote válido"""
        assert Garantia.validar_lote_fabricacao("LOTE123") is True
        assert Garantia.validar_lote_fabricacao("ABC") is True
        assert Garantia.validar_lote_fabricacao("  XYZ  ") is True  # Com espaços
    
    def test_validar_lote_fabricacao_invalido(self):
        """Testa validação de lote inválido"""
        assert Garantia.validar_lote_fabricacao("") is False
        assert Garantia.validar_lote_fabricacao("AB") is False
        assert Garantia.validar_lote_fabricacao("  ") is False  # Só espaços
    
    @patch('models.garantia.datetime')
    def test_desativar(self, mock_datetime):
        """Testa desativação da garantia"""
        mock_now = datetime(2024, 1, 15, 10, 30, 0)
        mock_datetime.now.return_value = mock_now
        
        garantia = Garantia(ativo=True, observacoes="Observação inicial")
        
        garantia.desativar("Motivo do teste")
        
        assert garantia.ativo is False
        assert "Desativada em 15/01/2024: Motivo do teste" in garantia.observacoes
    
    def test_desativar_sem_motivo(self):
        """Testa desativação sem motivo"""
        garantia = Garantia(ativo=True)
        
        garantia.desativar()
        
        assert garantia.ativo is False
        # Observações não devem ser alteradas se não há motivo
        assert garantia.observacoes == ""
    
    @patch('models.garantia.datetime')
    def test_reativar(self, mock_datetime):
        """Testa reativação da garantia"""
        mock_now = datetime(2024, 1, 15, 10, 30, 0)
        mock_datetime.now.return_value = mock_now
        
        garantia = Garantia(ativo=False, observacoes="Observação inicial")
        
        garantia.reativar("Motivo da reativação")
        
        assert garantia.ativo is True
        assert "Reativada em 15/01/2024: Motivo da reativação" in garantia.observacoes
    
    def test_reativar_sem_motivo(self):
        """Testa reativação sem motivo"""
        garantia = Garantia(ativo=False)
        
        garantia.reativar()
        
        assert garantia.ativo is True
        # Observações não devem ser alteradas se não há motivo
        assert garantia.observacoes == ""
    
    def test_str_representation(self):
        """Testa representação em string"""
        garantia = Garantia(
            id=1,
            lote_fabricacao="LOTE123",
            ativo=True,
            quilometragem=30000
        )
        
        result = str(garantia)
        
        assert "Garantia 1" in result
        assert "Lote: LOTE123" in result
        assert "Status:" in result
    
    def test_repr_representation(self):
        """Testa representação para debug"""
        garantia = Garantia(
            id=1,
            lote_fabricacao="LOTE123",
            ativo=True,
            quilometragem=30000
        )
        
        result = repr(garantia)
        
        assert "Garantia(id=1" in result
        assert "lote='LOTE123'" in result
        assert "status=" in result