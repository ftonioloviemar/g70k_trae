#!/usr/bin/env python3
"""
Script para testar o cadastro de veículos e identificar problemas
"""

import logging
import sys
import os
from datetime import datetime
from fastlite import Database
from app.config import Config
from models.veiculo import Veiculo

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Testa o cadastro de veículos"""
    
    # Configurar banco
    config = Config()
    db = Database(config.DATABASE_PATH)
    
    logger.info(f"Usando banco de dados: {config.DATABASE_PATH}")
    
    # Verificar estrutura da tabela veículos
    logger.info("Verificando estrutura da tabela veículos...")
    try:
        schema = db.execute("PRAGMA table_info(veiculos)").fetchall()
        logger.info("Estrutura da tabela veículos:")
        for col in schema:
            logger.info(f"  {col[1]} {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]})")
    except Exception as e:
        logger.error(f"Erro ao verificar estrutura da tabela: {e}")
        return
    
    # Verificar se há usuários de teste
    logger.info("Verificando usuários disponíveis...")
    try:
        usuarios = db.execute("SELECT id, email, tipo_usuario FROM usuarios WHERE tipo_usuario = 'cliente' LIMIT 5").fetchall()
        if not usuarios:
            logger.error("Nenhum usuário cliente encontrado no banco")
            return
        
        logger.info("Usuários clientes encontrados:")
        for user in usuarios:
            logger.info(f"  ID: {user[0]}, Email: {user[1]}, Tipo: {user[2]}")
        
        # Usar o primeiro usuário para teste
        usuario_teste = usuarios[0]
        usuario_id = usuario_teste[0]
        
    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {e}")
        return
    
    # Testar cadastro de veículo
    logger.info(f"Testando cadastro de veículo para usuário ID {usuario_id}...")
    
    dados_veiculo = {
        'usuario_id': usuario_id,
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'ano_modelo': '2020',
        'placa': 'ABC1234',
        'cor': 'Branco',
        'chassi': '9BWZZZ377VT004251',
        'data_cadastro': datetime.now(),
        'ativo': True
    }
    
    try:
        # Verificar se a placa já existe
        placa_existente = db.execute(
            "SELECT id FROM veiculos WHERE placa = ? AND ativo = TRUE",
            (dados_veiculo['placa'],)
        ).fetchone()
        
        if placa_existente:
            logger.info(f"Placa {dados_veiculo['placa']} já existe (ID: {placa_existente[0]}). Usando placa diferente.")
            dados_veiculo['placa'] = f"TST{datetime.now().strftime('%H%M')}"
        
        # Inserir veículo
        logger.info("Inserindo veículo no banco...")
        result = db.execute("""
            INSERT INTO veiculos (
                usuario_id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados_veiculo['usuario_id'], 
            dados_veiculo['marca'], 
            dados_veiculo['modelo'], 
            dados_veiculo['ano_modelo'],
            dados_veiculo['placa'], 
            dados_veiculo['cor'], 
            dados_veiculo['chassi'], 
            dados_veiculo['data_cadastro'].isoformat(), 
            dados_veiculo['ativo']
        ))
        
        # Obter ID do veículo inserido
        veiculo_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        logger.info(f"Veículo inserido com sucesso! ID: {veiculo_id}")
        
        # Verificar se o veículo foi inserido corretamente
        veiculo_inserido = db.execute("""
            SELECT id, usuario_id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
            FROM veiculos 
            WHERE id = ?
        """, (veiculo_id,)).fetchone()
        
        if veiculo_inserido:
            logger.info("Dados do veículo inserido:")
            logger.info(f"  ID: {veiculo_inserido[0]}")
            logger.info(f"  Usuário ID: {veiculo_inserido[1]}")
            logger.info(f"  Marca: {veiculo_inserido[2]}")
            logger.info(f"  Modelo: {veiculo_inserido[3]}")
            logger.info(f"  Ano/Modelo: {veiculo_inserido[4]}")
            logger.info(f"  Placa: {veiculo_inserido[5]}")
            logger.info(f"  Cor: {veiculo_inserido[6]}")
            logger.info(f"  Chassi: {veiculo_inserido[7]}")
            logger.info(f"  Data Cadastro: {veiculo_inserido[8]}")
            logger.info(f"  Ativo: {veiculo_inserido[9]}")
        else:
            logger.error("Veículo não foi encontrado após inserção!")
        
        # Testar busca de veículos do usuário (simulando a listagem)
        logger.info(f"Testando listagem de veículos do usuário {usuario_id}...")
        veiculos_usuario = db.execute("""
            SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
            FROM veiculos 
            WHERE usuario_id = ? 
            ORDER BY data_cadastro DESC
        """, (usuario_id,)).fetchall()
        
        logger.info(f"Encontrados {len(veiculos_usuario)} veículos para o usuário:")
        for v in veiculos_usuario:
            logger.info(f"  {v[1]} {v[2]} - {v[4]} (ID: {v[0]}, Ativo: {v[8]})")
        
        # Limpar o veículo de teste
        logger.info(f"Removendo veículo de teste (ID: {veiculo_id})...")
        db.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
        logger.info("Veículo de teste removido com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao testar cadastro de veículo: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return
    
    logger.info("Teste de cadastro de veículo concluído com sucesso!")

if __name__ == "__main__":
    main()