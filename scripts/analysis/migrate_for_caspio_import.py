#!/usr/bin/env python3
"""
Script de migração para preparar o banco de dados para importação do Caspio.
Adiciona colunas necessárias para mapear dados do Caspio.
"""

import sqlite3
import os
from pathlib import Path

def check_column_exists(cursor, table_name: str, column_name: str) -> bool:
    """
    Verifica se uma coluna existe em uma tabela.
    
    Args:
        cursor: Cursor do banco de dados
        table_name: Nome da tabela
        column_name: Nome da coluna
        
    Returns:
        True se a coluna existir, False caso contrário
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_column_if_not_exists(cursor, table_name: str, column_name: str, column_type: str):
    """
    Adiciona uma coluna se ela não existir.
    
    Args:
        cursor: Cursor do banco de dados
        table_name: Nome da tabela
        column_name: Nome da coluna
        column_type: Tipo da coluna
    """
    if not check_column_exists(cursor, table_name, column_name):
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
        print(f"✓ Coluna {table_name}.{column_name} adicionada")
    else:
        print(f"- Coluna {table_name}.{column_name} já existe")

def main():
    """
    Executa a migração do banco de dados.
    """
    # Caminho do banco de dados
    db_path = Path("data/viemar_garantia.db")
    
    if not db_path.exists():
        print(f"Erro: Banco de dados não encontrado em {db_path}")
        return
    
    print("Iniciando migração para importação do Caspio...")
    
    # Conecta ao banco
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Adiciona coluna caspio_id na tabela usuarios
        add_column_if_not_exists(cursor, "usuarios", "caspio_id", "TEXT")
        
        # Adiciona coluna caspio_veiculo_id na tabela veiculos
        add_column_if_not_exists(cursor, "veiculos", "caspio_veiculo_id", "TEXT")
        
        # Adiciona colunas para garantias (tabela PRODUTO_APLICADO do Caspio)
        add_column_if_not_exists(cursor, "garantias", "referencia_produto", "TEXT")
        add_column_if_not_exists(cursor, "garantias", "lote_caspio", "TEXT")
        add_column_if_not_exists(cursor, "garantias", "oficina_nome", "TEXT")
        add_column_if_not_exists(cursor, "garantias", "oficina_nf", "TEXT")
        add_column_if_not_exists(cursor, "garantias", "data_aplicacao_caspio", "TEXT")
        add_column_if_not_exists(cursor, "garantias", "km_aplicacao", "INTEGER")
        add_column_if_not_exists(cursor, "garantias", "data_cadastro", "TEXT")
        
        # Cria índices para melhor performance
        indices = [
            ("idx_usuarios_caspio_id", "usuarios", "caspio_id"),
            ("idx_veiculos_caspio_id", "veiculos", "caspio_veiculo_id"),
            ("idx_garantias_referencia", "garantias", "referencia_produto"),
            ("idx_garantias_lote", "garantias", "lote_fabricacao"),
            ("idx_garantias_usuario", "garantias", "usuario_id"),
        ]
        
        for index_name, table_name, column_name in indices:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name});")
            print(f"✓ Índice {index_name} criado")
        
        conn.commit()
        print("\n🎉 Migração concluída com sucesso!")
        print("\nColunas adicionadas:")
        print("- usuarios.caspio_id")
        print("- veiculos.caspio_veiculo_id")
        print("- garantias.referencia_produto")
        print("- garantias.lote_caspio")
        print("- garantias.oficina_nome")
        print("- garantias.oficina_nf")
        print("- garantias.data_aplicacao_caspio")
        print("- garantias.km_aplicacao")
        print("- garantias.data_cadastro")
        print("\nÍndices criados para melhor performance.")
        
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()