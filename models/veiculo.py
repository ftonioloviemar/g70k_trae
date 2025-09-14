#!/usr/bin/env python3
"""
Modelo de dados para veículos dos clientes
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Veiculo:
    """Modelo de veículo do cliente"""
    
    id: Optional[int] = None
    usuario_id: int = 0
    marca: str = ''
    modelo: str = ''
    ano_modelo: str = ''
    placa: str = ''
    cor: str = ''
    chassi: str = ''
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    ativo: bool = True
    
    def __post_init__(self):
        """Inicialização após criação do objeto"""
        if self.data_cadastro is None:
            self.data_cadastro = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte o veículo para dicionário"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'marca': self.marca,
            'modelo': self.modelo,
            'ano_modelo': self.ano_modelo,
            'placa': self.placa,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'ativo': self.ativo
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Veiculo':
        """Cria veículo a partir de dicionário"""
        veiculo = cls()
        for key, value in data.items():
            if hasattr(veiculo, key):
                if key in ['data_cadastro', 'data_atualizacao'] and value:
                    if isinstance(value, str):
                        setattr(veiculo, key, datetime.fromisoformat(value))
                    else:
                        setattr(veiculo, key, value)
                else:
                    setattr(veiculo, key, value)
        return veiculo
    
    def formatar_placa(self) -> str:
        """Formata a placa no padrão brasileiro"""
        placa = self.placa.upper().replace('-', '').replace(' ', '')
        if len(placa) == 7:
            # Formato antigo: ABC-1234
            if placa[:3].isalpha() and placa[3:].isdigit():
                return f"{placa[:3]}-{placa[3:]}"
            # Formato Mercosul: ABC1D23
            elif placa[:3].isalpha() and placa[4].isalpha():
                return f"{placa[:3]}{placa[3]}{placa[4]}{placa[5:]}"
        return self.placa
    
    @staticmethod
    def formatar_placa_estatico(placa: str) -> str:
        """Formata a placa no padrão brasileiro (método estático)"""
        placa_limpa = placa.upper().replace('-', '').replace(' ', '')
        if len(placa_limpa) == 7:
            # Formato antigo: ABC-1234
            if placa_limpa[:3].isalpha() and placa_limpa[3:].isdigit():
                return f"{placa_limpa[:3]}-{placa_limpa[3:]}"
            # Formato Mercosul: ABC1D23
            elif placa_limpa[:3].isalpha() and placa_limpa[4].isalpha():
                return f"{placa_limpa[:3]}{placa_limpa[3]}{placa_limpa[4]}{placa_limpa[5:]}"
        return placa

    @staticmethod
    def validar_placa(placa: str) -> bool:
        """Valida se a placa está no formato correto"""
        placa = placa.upper().replace('-', '').replace(' ', '')
        
        if len(placa) != 7:
            return False
        
        # Formato antigo: ABC1234
        if placa[:3].isalpha() and placa[3:].isdigit():
            return True
        
        # Formato Mercosul: ABC1D23
        if (placa[:3].isalpha() and 
            placa[3].isdigit() and 
            placa[4].isalpha() and 
            placa[5:].isdigit()):
            return True
        
        return False
    
    def atualizar(self, **kwargs):
        """Atualiza os dados do veículo"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'usuario_id', 'data_cadastro']:
                setattr(self, key, value)
        self.data_atualizacao = datetime.now()
    
    def desativar(self):
        """Desativa o veículo"""
        self.ativo = False
        self.data_atualizacao = datetime.now()
    
    def reativar(self):
        """Reativa o veículo"""
        self.ativo = True
        self.data_atualizacao = datetime.now()
    
    def __str__(self) -> str:
        """Representação em string do veículo"""
        return f"{self.marca} {self.modelo} {self.ano_modelo} - {self.formatar_placa()}"
    
    def __repr__(self) -> str:
        """Representação para debug"""
        return f"Veiculo(id={self.id}, marca='{self.marca}', modelo='{self.modelo}', placa='{self.placa}')"