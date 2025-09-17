#!/usr/bin/env python3
"""
Script de migração para preparar o banco para importação do Caspio.

Este script adiciona as colunas necessárias para suportar a importação
dos dados do Caspio mantendo referências aos IDs originais.
"""

import sqlite3
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database(db_path: str) -> bool:
    """
    Executa migração do banco de dados para suportar importação do Caspio.
    
    Args:
        db_path: Caminho para o banco SQLite
        
    Returns:
        True se migração foi bem-sucedida
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        logger.info("Iniciando migração do banco de dados")
        
        # Adiciona coluna caspio_id à tabela usuarios
        try:
            conn.execute("ALTER TABLE usuarios ADD COLUMN caspio_id TEXT")
            logger.info("Coluna caspio_id adicionada à tabela usuarios")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info("Coluna caspio_id já existe na tabela usuarios")
            else:
                raise
        
        # Adiciona coluna caspio_veiculo_id à tabela veiculos
        try:
            conn.execute("ALTER TABLE veiculos ADD COLUMN caspio_veiculo_id TEXT")
            logger.info("Coluna caspio_veiculo_id adicionada à tabela veiculos")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info("Coluna caspio_veiculo_id já existe na tabela veiculos")
            else:
                raise
        
        # Adiciona colunas necessárias para garantias do Caspio
        caspio_warranty_columns = [
            ("referencia_produto", "TEXT"),
            ("lote_caspio", "TEXT"),
            ("data_aplicacao_caspio", "TEXT"),
            ("km_aplicacao", "INTEGER"),
            ("oficina_nome", "TEXT"),
            ("oficina_nf", "TEXT")
        ]
        
        for column_name, column_type in caspio_warranty_columns:
            try:
                conn.execute(f"ALTER TABLE garantias ADD COLUMN {column_name} {column_type}")
                logger.info(f"Coluna {column_name} adicionada à tabela garantias")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    logger.info(f"Coluna {column_name} já existe na tabela garantias")
                else:
                    raise
        
        # Cria índices para as novas colunas
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_usuarios_caspio_id ON usuarios (caspio_id)",
            "CREATE INDEX IF NOT EXISTS idx_veiculos_caspio_id ON veiculos (caspio_veiculo_id)",
            "CREATE INDEX IF NOT EXISTS idx_garantias_referencia ON garantias (referencia_produto)",
            "CREATE INDEX IF NOT EXISTS idx_garantias_lote_caspio ON garantias (lote_caspio)"
        ]
        
        for index_sql in indices:
            conn.execute(index_sql)
            logger.info(f"Índice criado: {index_sql.split('ON')[1].strip()}")
        
        conn.commit()
        conn.close()
        
        logger.info("Migração concluída com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro na migração: {e}")
        return False

def verify_migration(db_path: str) -> bool:
    """
    Verifica se a migração foi aplicada corretamente.
    
    Args:
        db_path: Caminho para o banco SQLite
        
    Returns:
        True se migração está correta
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica estrutura da tabela usuarios
        cursor.execute("PRAGMA table_info(usuarios)")
        usuarios_columns = [row[1] for row in cursor.fetchall()]
        
        if 'caspio_id' not in usuarios_columns:
            logger.error("Coluna caspio_id não encontrada na tabela usuarios")
            return False
        
        # Verifica estrutura da tabela veiculos
        cursor.execute("PRAGMA table_info(veiculos)")
        veiculos_columns = [row[1] for row in cursor.fetchall()]
        
        if 'caspio_veiculo_id' not in veiculos_columns:
            logger.error("Coluna caspio_veiculo_id não encontrada na tabela veiculos")
            return False
        
        # Verifica estrutura da tabela garantias
        cursor.execute("PRAGMA table_info(garantias)")
        garantias_columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['referencia_produto', 'lote_caspio', 'oficina_nome']
        for col in required_columns:
            if col not in garantias_columns:
                logger.error(f"Coluna {col} não encontrada na tabela garantias")
                return False
        
        conn.close()
        
        logger.info("Verificação da migração: OK")
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação: {e}")
        return False

def main():
    """
    Função principal para executar a migração.
    """
    db_path = "data/viemar_garantia.db"
    
    if not Path(db_path).exists():
        logger.error(f"Banco de dados não encontrado: {db_path}")
        return
    
    print("=== MIGRAÇÃO PARA IMPORTAÇÃO DO CASPIO ===")
    print(f"Banco de dados: {db_path}")
    print("\nEsta migração irá:")
    print("- Adicionar coluna caspio_id à tabela usuarios")
    print("- Adicionar coluna caspio_veiculo_id à tabela veiculos")
    print("- Adicionar colunas do Caspio à tabela garantias")
    print("- Criar índices para melhor performance")
    
    resposta = input("\nDeseja continuar? (s/N): ").lower().strip()
    if resposta != 's':
        print("Migração cancelada")
        return
    
    # Executa migração
    if migrate_database(db_path):
        print("\n✅ Migração executada com sucesso")
        
        # Verifica migração
        if verify_migration(db_path):
            print("✅ Verificação da migração: OK")
            print("\n🎉 Banco de dados pronto para importação do Caspio!")
        else:
            print("❌ Erro na verificação da migração")
    else:
        print("❌ Erro na execução da migração")

if __name__ == "__main__":
    main()