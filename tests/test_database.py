#!/usr/bin/env python3
"""
Testes para o banco de dados
"""

import pytest
import tempfile
import os
from fastlite import Database

from app.database import init_database, criar_admin_padrao, get_database_stats

class TestDatabase:
    """Testes para operações do banco de dados"""
    
    def test_init_database(self):
        """Testa inicialização do banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = Database(db_path)
            init_database(db)
            
            # Verificar se as tabelas foram criadas
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [table[0] for table in tables]
            
            assert 'usuarios' in table_names
            assert 'produtos' in table_names
            assert 'veiculos' in table_names
            assert 'garantias' in table_names
            
            db.close()
        finally:
            os.unlink(db_path)
    
    def test_create_admin_user(self, temp_db):
        """Testa criação do usuário administrador"""
        criar_admin_padrao(temp_db)
        
        # Verificar se admin foi criado
        admin = temp_db.execute(
            "SELECT email, tipo_usuario FROM usuarios WHERE tipo_usuario = 'administrador'"
        ).fetchone()
        
        assert admin is not None
        assert admin[0] == 'ftoniolo@viemar.com.br'  # email
        assert admin[1] == 'administrador'  # tipo_usuario
    
    def test_get_database_stats(self, temp_db, sample_user_data, sample_produto_data):
        """Testa obtenção de estatísticas do banco"""
        from models.usuario import Usuario
        from models.produto import Produto
        
        # Criar alguns dados de teste
        usuario = Usuario(**sample_user_data)
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
        
        produto = Produto(**sample_produto_data)
        temp_db.execute(
            "INSERT INTO produtos (sku, descricao, ativo) VALUES (?, ?, ?)",
            (produto.sku, produto.descricao, produto.ativo)
        )
        
        # Obter estatísticas
        stats = get_database_stats(temp_db)
        
        assert 'total_usuarios' in stats
        assert 'total_produtos' in stats
        assert 'total_veiculos' in stats
        assert 'total_garantias' in stats
        assert stats['total_usuarios'] >= 1
        assert stats['total_produtos'] >= 1

class TestDatabaseConstraints:
    """Testes para restrições do banco de dados"""
    
    def test_unique_email_constraint(self, temp_db, sample_user_data):
        """Testa restrição de email único"""
        from models.usuario import Usuario
        
        # Criar primeiro usuário
        usuario1 = Usuario(**sample_user_data)
        temp_db.execute(
            """
            INSERT INTO usuarios (nome, email, cpf_cnpj, telefone, cep, endereco, cidade, uf, senha_hash, tipo_usuario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    usuario1.nome, usuario1.email, usuario1.cpf_cnpj, usuario1.telefone,
                    usuario1.cep, usuario1.endereco, usuario1.cidade, usuario1.uf,
                    usuario1.senha_hash, usuario1.tipo_usuario
                )
        )
        
        # Tentar criar segundo usuário com mesmo email
        usuario2_data = sample_user_data.copy()
        usuario2_data['nome'] = 'Outro Nome'
        usuario2 = Usuario(**usuario2_data)
        
        with pytest.raises(Exception):  # Deve gerar erro de constraint
            temp_db.execute(
                """
                INSERT INTO usuarios (nome, email, cpf_cnpj, telefone, cep, endereco, cidade, uf, senha_hash, tipo_usuario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    usuario2.nome, usuario2.email, usuario2.cpf_cnpj, usuario2.telefone,
                    usuario2.cep, usuario2.endereco, usuario2.cidade, usuario2.uf,
                    usuario2.senha_hash, usuario2.tipo_usuario
                )
            )
    
    def test_unique_sku_constraint(self, temp_db, sample_produto_data):
        """Testa restrição de SKU único"""
        from models.produto import Produto
        
        # Criar primeiro produto
        produto1 = Produto(**sample_produto_data)
        temp_db.execute(
            "INSERT INTO produtos (sku, descricao, ativo) VALUES (?, ?, ?)",
            (produto1.sku, produto1.descricao, produto1.ativo)
        )
        
        # Tentar criar segundo produto com mesmo SKU
        produto2_data = sample_produto_data.copy()
        produto2_data['descricao'] = 'Outra Descrição'
        produto2 = Produto(**produto2_data)
        
        with pytest.raises(Exception):  # Deve gerar erro de constraint
            temp_db.execute(
                "INSERT INTO produtos (sku, descricao, ativo) VALUES (?, ?, ?)",
                (produto2.sku, produto2.descricao, produto2.ativo)
            )
    
    def test_foreign_key_constraints(self, temp_db, sample_veiculo_data):
        """Testa restrições de chave estrangeira"""
        from models.veiculo import Veiculo
        
        # Tentar criar veículo com usuario_id inexistente
        veiculo = Veiculo(usuario_id=999, **sample_veiculo_data)
        
        with pytest.raises(Exception):  # Deve gerar erro de foreign key
            temp_db.execute(
                """
                INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa, chassi, cor)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    veiculo.usuario_id, veiculo.marca, veiculo.modelo,
                    veiculo.ano_modelo, veiculo.placa, veiculo.chassi, veiculo.cor
                )
            )

class TestDatabaseIndexes:
    """Testes para índices do banco de dados"""
    
    def test_indexes_exist(self, temp_db):
        """Testa se os índices foram criados"""
        indexes = temp_db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL"
        ).fetchall()
        
        index_names = [index[0] for index in indexes]
        
        # Verificar se índices importantes existem
        expected_indexes = [
            'idx_usuarios_email',
            'idx_usuarios_tipo',
            'idx_produtos_sku',
            'idx_veiculos_usuario',
            'idx_garantias_usuario',
            'idx_garantias_produto',
            'idx_garantias_veiculo'
        ]
        
        for expected_index in expected_indexes:
            assert expected_index in index_names

class TestDatabaseMigration:
    """Testes para migração de dados"""
    
    def test_migrate_caspio_data_structure(self, temp_db):
        """Testa estrutura para migração de dados do Caspio"""
        # Simular dados do Caspio
        caspio_user_data = {
            'ID_CLIENTE': 1,
            'NOME': 'João Silva',
            'EMAIL': 'joao@example.com',
            'CPF_CNPJ': '12345678901',
            'TELEFONE': '11999999999',
            'CEP': '01234567',
            'ENDERECO': 'Rua Teste, 123',
            'CIDADE': 'São Paulo',
            'UF': 'SP',
            'SENHA': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # 'password' em SHA256
            'DATA_CADASTRO': '2024-01-01 10:00:00'
        }
        
        # Migrar dados (simulação)
        from models.usuario import Usuario
        
        usuario = Usuario(
            nome=caspio_user_data['NOME'],
            email=caspio_user_data['EMAIL'],
            cpf_cnpj=caspio_user_data['CPF_CNPJ'],
            telefone=caspio_user_data['TELEFONE'],
            cep=caspio_user_data['CEP'],
            endereco=caspio_user_data['ENDERECO'],
            cidade=caspio_user_data['CIDADE'],
            uf=caspio_user_data['UF'],
            tipo_usuario='cliente'
        )
        
        # Migrar senha do Caspio separadamente
        usuario.senha_hash = Usuario.migrar_senha_caspio(caspio_user_data['SENHA'])
        
        # Inserir no banco
        temp_db.execute(
            """
            INSERT INTO usuarios (nome, email, cpf_cnpj, telefone, cep, endereco, cidade, uf, senha_hash, tipo_usuario, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                usuario.nome, usuario.email, usuario.cpf_cnpj, usuario.telefone,
                usuario.cep, usuario.endereco, usuario.cidade, usuario.uf,
                usuario.senha_hash, usuario.tipo_usuario, caspio_user_data['DATA_CADASTRO']
            )
        )
        user_id = temp_db.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Verificar se foi inserido corretamente
        migrated_user = temp_db.execute(
            "SELECT nome, email, cpf_cnpj FROM usuarios WHERE id = ?",
            (user_id,)
        ).fetchone()
        
        assert migrated_user is not None
        assert migrated_user[0] == caspio_user_data['NOME']  # nome
        assert migrated_user[1] == caspio_user_data['EMAIL']  # email
        assert migrated_user[2] == caspio_user_data['CPF_CNPJ']  # cpf_cnpj
        
        # Verificar se a senha foi migrada (não podemos testar a senha original
        # pois foi convertida para bcrypt usando o hash SHA256 como base)
        assert usuario.senha_hash is not None
        assert len(usuario.senha_hash) > 0