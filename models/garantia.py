#!/usr/bin/env python3
"""
Modelo de dados para garantias ativadas
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from app.date_utils import parse_iso_date, format_date_br

@dataclass
class Garantia:
    """Modelo de garantia ativada"""
    
    id: Optional[int] = None
    usuario_id: int = 0
    produto_id: int = 0
    veiculo_id: int = 0
    lote_fabricacao: str = ''
    data_instalacao: Optional[datetime] = None
    nota_fiscal: str = ''
    nome_estabelecimento: str = ''
    quilometragem: int = 0
    data_cadastro: Optional[datetime] = None
    data_vencimento: Optional[datetime] = None
    ativo: bool = True
    observacoes: str = ''
    
    def __post_init__(self):
        """Inicialização após criação do objeto"""
        if self.data_cadastro is None:
            self.data_cadastro = datetime.now()
        
        # Converter string de data para datetime se necessário
        if isinstance(self.data_instalacao, str):
            self.data_instalacao = parse_iso_date(self.data_instalacao)
        
        # Calcular data de vencimento (2 anos a partir da instalação)
        if self.data_instalacao and not self.data_vencimento:
            self.data_vencimento = self.data_instalacao + timedelta(days=730)  # 2 anos
    
    def to_dict(self) -> dict:
        """Converte a garantia para dicionário"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'produto_id': self.produto_id,
            'veiculo_id': self.veiculo_id,
            'lote_fabricacao': self.lote_fabricacao,
            'data_instalacao': self.data_instalacao.isoformat() if self.data_instalacao else None,
            'nota_fiscal': self.nota_fiscal,
            'nome_estabelecimento': self.nome_estabelecimento,
            'quilometragem': self.quilometragem,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'ativo': self.ativo,
            'observacoes': self.observacoes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Garantia':
        """Cria garantia a partir de dicionário"""
        garantia = cls()
        for key, value in data.items():
            if hasattr(garantia, key):
                if key in ['data_instalacao', 'data_cadastro', 'data_vencimento'] and value:
                    if isinstance(value, str):
                        setattr(garantia, key, parse_iso_date(value))
                    else:
                        setattr(garantia, key, value)
                else:
                    setattr(garantia, key, value)
        return garantia
    
    def calcular_data_vencimento(self) -> Optional[datetime]:
        """Calcula a data de vencimento da garantia (70.000 km ou 2 anos)"""
        if not self.data_instalacao:
            return None
        
        # A garantia vence em 2 anos ou 70.000 km, o que ocorrer primeiro
        data_2_anos = self.data_instalacao + timedelta(days=730)
        return data_2_anos
    
    def is_vencida(self) -> bool:
        """Verifica se a garantia está vencida"""
        if not self.data_vencimento:
            return False
        return datetime.now() > self.data_vencimento
    
    def dias_para_vencimento(self) -> Optional[int]:
        """Retorna quantos dias faltam para o vencimento"""
        if not self.data_vencimento:
            return None
        
        delta = self.data_vencimento - datetime.now()
        return delta.days if delta.days > 0 else 0
    
    def km_restantes(self) -> int:
        """Calcula quantos km restam na garantia (assumindo limite de 70.000 km)"""
        km_limite = 70000
        return max(0, km_limite - self.quilometragem)
    
    def status_garantia(self) -> str:
        """Retorna o status atual da garantia"""
        if not self.ativo:
            return "Inativa"
        
        if self.is_vencida():
            return "Vencida"
        
        dias_restantes = self.dias_para_vencimento()
        km_restantes = self.km_restantes()
        
        if dias_restantes and dias_restantes <= 30:
            return "Próxima do vencimento"
        
        if km_restantes <= 5000:
            return "Próxima do limite de KM"
        
        return "Ativa"
    
    @staticmethod
    def validar_lote_fabricacao(lote_fabricacao: str) -> bool:
        """Valida se o lote de fabricação tem pelo menos 5 caracteres"""
        return len(lote_fabricacao.strip()) >= 3
    
    def desativar(self, motivo: str = ''):
        """Desativa a garantia"""
        self.ativo = False
        if motivo:
            self.observacoes += f"\nDesativada em {format_date_br(datetime.now())}: {motivo}"
    
    def reativar(self, motivo: str = ''):
        """Reativa a garantia"""
        self.ativo = True
        if motivo:
            self.observacoes += f"\nReativada em {format_date_br(datetime.now())}: {motivo}"
    
    def __str__(self) -> str:
        """Representação em string da garantia"""
        return f"Garantia {self.id} - Lote: {self.lote_fabricacao} - Status: {self.status_garantia()}"
    
    def __repr__(self) -> str:
        """Representação para debug"""
        return f"Garantia(id={self.id}, lote='{self.lote_fabricacao}', status='{self.status_garantia()}')"