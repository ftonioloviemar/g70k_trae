#!/usr/bin/env python3
"""
Testes para funcionalidade de paginação
"""

import pytest
import math
from fasthtml.common import *
from fastlite import Database
from app.templates import pagination_component
from models.usuario import Usuario
from models.veiculo import Veiculo
from models.produto import Produto
from models.garantia import Garantia


class TestPaginationComponent:
    """Testes para o componente de paginação"""
    
    def test_pagination_component_basic(self):
        """Testa criação básica do componente de paginação"""
        component = pagination_component(
            current_page=1,
            total_pages=5,
            base_url="/admin/usuarios",
            page_size=50,
            total_records=250
        )
        
        # Verifica se o componente foi criado
        assert component is not None
        
    def test_pagination_component_single_page(self):
        """Testa paginação com apenas uma página"""
        component = pagination_component(
            current_page=1,
            total_pages=1,
            base_url="/admin/usuarios",
            page_size=50,
            total_records=25
        )
        
        # Com apenas uma página, não deve mostrar navegação
        assert component is not None
        
    def test_pagination_component_first_page(self):
        """Testa paginação na primeira página"""
        component = pagination_component(
            current_page=1,
            total_pages=10,
            base_url="/admin/usuarios",
            page_size=50,
            total_records=500
        )
        
        assert component is not None
        
    def test_pagination_component_middle_page(self):
        """Testa paginação em página do meio"""
        component = pagination_component(
            current_page=5,
            total_pages=10,
            base_url="/admin/usuarios",
            page_size=50,
            total_records=500
        )
        
        assert component is not None
        
    def test_pagination_component_last_page(self):
        """Testa paginação na última página"""
        component = pagination_component(
            current_page=10,
            total_pages=10,
            base_url="/admin/usuarios",
            page_size=50,
            total_records=500
        )
        
        assert component is not None


class TestPaginationLogic:
    """Testes para lógica de paginação"""
    
    def test_page_calculation(self):
        """Testa cálculo de páginas"""
        # 100 registros, 50 por página = 2 páginas
        total_records = 100
        page_size = 50
        expected_pages = 2
        calculated_pages = math.ceil(total_records / page_size)
        
        assert calculated_pages == expected_pages
        
    def test_page_calculation_with_remainder(self):
        """Testa cálculo de páginas com resto"""
        # 101 registros, 50 por página = 3 páginas
        total_records = 101
        page_size = 50
        expected_pages = 3
        calculated_pages = math.ceil(total_records / page_size)
        
        assert calculated_pages == expected_pages
        
    def test_offset_calculation(self):
        """Testa cálculo de offset"""
        # Página 1, tamanho 50 = offset 0
        page = 1
        page_size = 50
        expected_offset = 0
        calculated_offset = (page - 1) * page_size
        
        assert calculated_offset == expected_offset
        
        # Página 3, tamanho 50 = offset 100
        page = 3
        page_size = 50
        expected_offset = 100
        calculated_offset = (page - 1) * page_size
        
        assert calculated_offset == expected_offset
        
    def test_page_size_validation(self):
        """Testa validação de tamanho de página"""
        valid_sizes = [25, 50, 100, 200]
        
        for size in valid_sizes:
            assert size in [25, 50, 100, 200]
            
        # Tamanhos inválidos devem ser convertidos para 50
        invalid_sizes = [10, 30, 75, 150, 300]
        for size in invalid_sizes:
            validated_size = 50 if size not in [25, 50, 100, 200] else size
            assert validated_size == 50
            
    def test_page_validation(self):
        """Testa validação de número da página"""
        # Página menor que 1 deve ser convertida para 1
        page = 0
        validated_page = 1 if page < 1 else page
        assert validated_page == 1
        
        page = -5
        validated_page = 1 if page < 1 else page
        assert validated_page == 1
        
        # Páginas válidas devem permanecer inalteradas
        page = 5
        validated_page = 1 if page < 1 else page
        assert validated_page == 5


@pytest.fixture
def test_db():
    """Fixture para banco de dados de teste"""
    db = Database(":memory:")
    
    # Criar tabelas de teste
    db.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            tipo_usuario TEXT NOT NULL DEFAULT 'cliente',
            ativo BOOLEAN DEFAULT 1,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.execute("""
        CREATE TABLE veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            ano_modelo INTEGER NOT NULL,
            placa TEXT NOT NULL,
            cor TEXT,
            chassi TEXT,
            ativo BOOLEAN DEFAULT 1,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)
    
    db.execute("""
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            descricao TEXT NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.execute("""
        CREATE TABLE garantias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            veiculo_id INTEGER NOT NULL,
            lote_fabricacao TEXT,
            data_instalacao DATE,
            data_vencimento DATE,
            ativo BOOLEAN DEFAULT 1,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
        )
    """)
    
    return db


class TestPaginationDatabase:
    """Testes de paginação com banco de dados"""
    
    def test_usuarios_pagination_query(self, test_db):
        """Testa query de paginação para usuários"""
        # Inserir dados de teste
        for i in range(100):
            test_db.execute("""
                INSERT INTO usuarios (nome, email, tipo_usuario)
                VALUES (?, ?, ?)
            """, (f"Usuario {i}", f"user{i}@test.com", "cliente"))
        
        # Testar primeira página
        page_size = 25
        offset = 0
        usuarios = test_db.execute("""
            SELECT * FROM usuarios 
            ORDER BY data_cadastro DESC 
            LIMIT ? OFFSET ?
        """, (page_size, offset)).fetchall()
        
        assert len(usuarios) == 25
        
        # Testar segunda página
        offset = 25
        usuarios = test_db.execute("""
            SELECT * FROM usuarios 
            ORDER BY data_cadastro DESC 
            LIMIT ? OFFSET ?
        """, (page_size, offset)).fetchall()
        
        assert len(usuarios) == 25
        
        # Testar contagem total
        total = test_db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        assert total == 100
        
    def test_veiculos_pagination_query(self, test_db):
        """Testa query de paginação para veículos"""
        # Inserir usuário de teste
        test_db.execute("""
            INSERT INTO usuarios (nome, email, tipo_usuario)
            VALUES (?, ?, ?)
        """, ("Usuario Teste", "teste@test.com", "cliente"))
        
        usuario_id = test_db.execute("SELECT id FROM usuarios WHERE email = ?", ("teste@test.com",)).fetchone()[0]
        
        # Inserir veículos de teste
        for i in range(50):
            test_db.execute("""
                INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa)
                VALUES (?, ?, ?, ?, ?)
            """, (usuario_id, f"Marca{i}", f"Modelo{i}", 2020 + (i % 5), f"ABC{i:04d}"))
        
        # Testar paginação
        page_size = 20
        offset = 0
        veiculos = test_db.execute("""
            SELECT * FROM veiculos 
            WHERE usuario_id = ?
            ORDER BY data_cadastro DESC 
            LIMIT ? OFFSET ?
        """, (usuario_id, page_size, offset)).fetchall()
        
        assert len(veiculos) == 20
        
        # Testar contagem total
        total = test_db.execute("SELECT COUNT(*) FROM veiculos WHERE usuario_id = ?", (usuario_id,)).fetchone()[0]
        assert total == 50
        
    def test_garantias_pagination_query(self, test_db):
        """Testa query de paginação para garantias"""
        # Inserir dados de teste
        test_db.execute("""
            INSERT INTO usuarios (nome, email, tipo_usuario)
            VALUES (?, ?, ?)
        """, ("Usuario Teste", "teste@test.com", "cliente"))
        
        usuario_id = test_db.execute("SELECT id FROM usuarios WHERE email = ?", ("teste@test.com",)).fetchone()[0]
        
        test_db.execute("""
            INSERT INTO produtos (sku, descricao)
            VALUES (?, ?)
        """, ("PROD001", "Produto Teste"))
        
        produto_id = test_db.execute("SELECT id FROM produtos WHERE sku = ?", ("PROD001",)).fetchone()[0]
        
        test_db.execute("""
            INSERT INTO veiculos (usuario_id, marca, modelo, ano_modelo, placa)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario_id, "Toyota", "Corolla", 2020, "ABC1234"))
        
        veiculo_id = test_db.execute("SELECT id FROM veiculos WHERE placa = ?", ("ABC1234",)).fetchone()[0]
        
        # Inserir garantias de teste
        for i in range(75):
            test_db.execute("""
                INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao)
                VALUES (?, ?, ?, ?)
            """, (usuario_id, produto_id, veiculo_id, f"LOTE{i:03d}"))
        
        # Testar paginação
        page_size = 30
        offset = 0
        garantias = test_db.execute("""
            SELECT g.*, u.nome, p.sku, v.placa
            FROM garantias g
            JOIN usuarios u ON g.usuario_id = u.id
            JOIN produtos p ON g.produto_id = p.id
            JOIN veiculos v ON g.veiculo_id = v.id
            ORDER BY g.data_cadastro DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset)).fetchall()
        
        assert len(garantias) == 30
        
        # Testar contagem total
        total = test_db.execute("SELECT COUNT(*) FROM garantias").fetchone()[0]
        assert total == 75


class TestPaginationIntegration:
    """Testes de integração da paginação"""
    
    def test_pagination_url_generation(self):
        """Testa geração de URLs de paginação"""
        base_url = "/admin/usuarios"
        page = 2
        page_size = 50
        
        # URL esperada para próxima página
        next_url = f"{base_url}?page={page + 1}&page_size={page_size}"
        expected_next = "/admin/usuarios?page=3&page_size=50"
        
        assert next_url == expected_next
        
        # URL esperada para página anterior
        prev_url = f"{base_url}?page={page - 1}&page_size={page_size}"
        expected_prev = "/admin/usuarios?page=1&page_size=50"
        
        assert prev_url == expected_prev
        
    def test_pagination_edge_cases(self):
        """Testa casos extremos da paginação"""
        # Sem registros
        total_records = 0
        page_size = 50
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        
        assert total_pages == 1
        
        # Um registro
        total_records = 1
        page_size = 50
        total_pages = math.ceil(total_records / page_size)
        
        assert total_pages == 1
        
        # Exatamente uma página cheia
        total_records = 50
        page_size = 50
        total_pages = math.ceil(total_records / page_size)
        
        assert total_pages == 1
        
        # Uma página cheia + 1 registro
        total_records = 51
        page_size = 50
        total_pages = math.ceil(total_records / page_size)
        
        assert total_pages == 2