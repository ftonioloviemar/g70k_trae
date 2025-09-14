#!/usr/bin/env python3
"""
Modelo de dados para produtos elegíveis para garantia
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Produto:
    """Modelo de produto elegível para garantia"""
    
    id: Optional[int] = None
    sku: str = ''
    descricao: str = ''
    ativo: bool = True
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicialização após criação do objeto"""
        if self.data_cadastro is None:
            self.data_cadastro = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte o produto para dicionário"""
        return {
            'id': self.id,
            'sku': self.sku,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Produto':
        """Cria produto a partir de dicionário"""
        produto = cls()
        for key, value in data.items():
            if hasattr(produto, key):
                if key in ['data_cadastro', 'data_atualizacao'] and value:
                    if isinstance(value, str):
                        setattr(produto, key, datetime.fromisoformat(value))
                    else:
                        setattr(produto, key, value)
                else:
                    setattr(produto, key, value)
        return produto
    
    def ativar(self):
        """Ativa o produto"""
        self.ativo = True
        self.data_atualizacao = datetime.now()
    
    def desativar(self):
        """Desativa o produto"""
        self.ativo = False
        self.data_atualizacao = datetime.now()
    
    def atualizar_descricao(self, nova_descricao: str):
        """Atualiza a descrição do produto"""
        self.descricao = nova_descricao
        self.data_atualizacao = datetime.now()
    
    def __str__(self) -> str:
        """Representação em string do produto"""
        return f"{self.sku} - {self.descricao}"
    
    def __repr__(self) -> str:
        """Representação para debug"""
        return f"Produto(id={self.id}, sku='{self.sku}', descricao='{self.descricao}', ativo={self.ativo})"