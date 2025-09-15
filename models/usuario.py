#!/usr/bin/env python3
"""
Modelo de dados para usuários (clientes e administradores)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import bcrypt
import json
import secrets

@dataclass
class Usuario:
    """Modelo de usuário do sistema"""
    
    id: Optional[int] = None
    email: str = ''
    senha_hash: str = ''
    nome: str = ''
    tipo_usuario: str = 'cliente'  # 'cliente' ou 'administrador'
    confirmado: bool = False
    email_enviado: bool = False  # Controla se o email de confirmação foi enviado
    cep: str = ''
    endereco: str = ''
    bairro: str = ''
    cidade: str = ''
    uf: str = ''
    telefone: str = ''
    cpf_cnpj: str = ''
    data_nascimento: Optional[datetime] = None
    data_cadastro: Optional[datetime] = None
    token_confirmacao: str = ''
    token_reset_senha: str = ''
    
    @classmethod
    def criar_hash_senha(cls, senha: str) -> str:
        """Cria hash da senha usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
    
    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha_hash.encode('utf-8'))
    
    @classmethod
    def gerar_token_confirmacao(cls) -> str:
        """Gera um token único para confirmação de email"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def migrar_senha_caspio(cls, senha_caspio: str) -> str:
        """Migra senha do formato Caspio para bcrypt"""
        # O Caspio usa um formato JSON com algoritmo e hash
        # Exemplo: {"algorithm":"cbAlg1","hash":"..."}
        try:
            if senha_caspio.startswith('0x'):
                # Converter de hex para string
                hex_data = senha_caspio[2:]
                json_str = bytes.fromhex(hex_data).decode('utf-8')
                senha_data = json.loads(json_str)
                
                # Por segurança, vamos criar um novo hash bcrypt
                # usando o hash original como "senha" temporária
                hash_original = senha_data.get('hash', senha_caspio)
                return cls.criar_hash_senha(hash_original)
            else:
                # Se não for formato Caspio, retorna a string original
                return senha_caspio
        except Exception:
            # Em caso de erro, retorna a string original
            return senha_caspio
    
    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador"""
        return self.tipo_usuario == 'administrador'
    
    def is_confirmed(self) -> bool:
        """Verifica se o email foi confirmado"""
        return self.confirmado
    
    def to_dict(self) -> dict:
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'email': self.email,
            'nome': self.nome,
            'tipo_usuario': self.tipo_usuario,
            'confirmado': self.confirmado,
            'email_enviado': self.email_enviado,
            'cep': self.cep,
            'endereco': self.endereco,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'uf': self.uf,
            'telefone': self.telefone,
            'cpf_cnpj': self.cpf_cnpj,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Usuario':
        """Cria usuário a partir de dicionário"""
        usuario = cls()
        for key, value in data.items():
            if hasattr(usuario, key):
                if key in ['data_nascimento', 'data_cadastro'] and value:
                    if isinstance(value, str):
                        setattr(usuario, key, datetime.fromisoformat(value))
                    else:
                        setattr(usuario, key, value)
                else:
                    setattr(usuario, key, value)
        return usuario