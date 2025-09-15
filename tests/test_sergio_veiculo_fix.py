#!/usr/bin/env python3
"""
Script para testar e corrigir o cadastro de veículos do sergio@reis.com
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from fastlite import Database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sergio_veiculo_cadastro():
    """Testa o cadastro de veículo para sergio@reis.com"""
    
    # Usar caminho direto do banco
    db_path = Path("data/viemar_garantia.db")
    
    if not db_path.exists():
        logger.error(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco com foreign keys habilitadas
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        logger.info("🔍 TESTANDO CADASTRO DE VEÍCULO PARA SERGIO@REIS.COM\n")
        
        # 1. Verificar se o usuário sergio@reis.com existe
        logger.info("1. Verificando usuário sergio@reis.com...")
        cursor.execute(
            "SELECT id, email, nome, tipo_usuario, confirmado FROM usuarios WHERE email = ?",
            ('sergio@reis.com',)
        )
        sergio = cursor.fetchone()
        
        if not sergio:
            logger.error("❌ Usuário sergio@reis.com não encontrado!")
            return False
        
        sergio_id, email, nome, tipo, confirmado = sergio
        logger.info(f"✅ Usuário encontrado: ID {sergio_id} | {email} | {nome} | {tipo} | Confirmado: {confirmado}")
        
        if not confirmado:
            logger.error("❌ Usuário não está confirmado!")
            return False
        
        # 2. Verificar veículos existentes
        logger.info("\n2. Verificando veículos existentes...")
        cursor.execute(
            "SELECT id, marca, modelo, placa, ativo FROM veiculos WHERE usuario_id = ?",
            (sergio_id,)
        )
        veiculos_existentes = cursor.fetchall()
        
        logger.info(f"Veículos existentes: {len(veiculos_existentes)}")
        for veiculo in veiculos_existentes:
            status = "✅ Ativo" if veiculo[4] else "❌ Inativo"
            logger.info(f"  ID: {veiculo[0]} | {veiculo[1]} {veiculo[2]} | Placa: {veiculo[3]} | {status}")
        
        # 3. Testar inserção de novo veículo
        logger.info("\n3. Testando inserção de novo veículo...")
        
        # Gerar dados únicos
        timestamp = datetime.now().strftime('%H%M%S')
        placa_teste = f"SRG{timestamp[1:4]}"
        chassi_teste = f"SERGIO{timestamp}123456789"
        
        veiculo_data = {
            'usuario_id': sergio_id,
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano_modelo': '2023',
            'placa': placa_teste,
            'cor': 'Branco',
            'chassi': chassi_teste,
            'data_cadastro': datetime.now().isoformat(),
            'ativo': True
        }
        
        logger.info(f"Dados do veículo de teste: {veiculo_data}")
        
        try:
            # Inserir veículo
            cursor.execute("""
                INSERT INTO veiculos (
                    usuario_id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                veiculo_data['usuario_id'],
                veiculo_data['marca'],
                veiculo_data['modelo'],
                veiculo_data['ano_modelo'],
                veiculo_data['placa'],
                veiculo_data['cor'],
                veiculo_data['chassi'],
                veiculo_data['data_cadastro'],
                veiculo_data['ativo']
            ))
            
            # Obter ID do veículo inserido
            veiculo_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"✅ Veículo inserido com sucesso! ID: {veiculo_id}")
            
            # 4. Verificar se o veículo foi inserido corretamente
            logger.info("\n4. Verificando veículo inserido...")
            cursor.execute("""
                SELECT id, usuario_id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
                FROM veiculos 
                WHERE id = ?
            """, (veiculo_id,))
            
            veiculo_inserido = cursor.fetchone()
            
            if veiculo_inserido:
                logger.info("✅ Veículo encontrado no banco:")
                logger.info(f"  ID: {veiculo_inserido[0]}")
                logger.info(f"  Usuario ID: {veiculo_inserido[1]}")
                logger.info(f"  Marca: {veiculo_inserido[2]}")
                logger.info(f"  Modelo: {veiculo_inserido[3]}")
                logger.info(f"  Ano/Modelo: {veiculo_inserido[4]}")
                logger.info(f"  Placa: {veiculo_inserido[5]}")
                logger.info(f"  Cor: {veiculo_inserido[6]}")
                logger.info(f"  Chassi: {veiculo_inserido[7]}")
                logger.info(f"  Data Cadastro: {veiculo_inserido[8]}")
                logger.info(f"  Ativo: {veiculo_inserido[9]}")
            else:
                logger.error("❌ Veículo não encontrado após inserção!")
                return False
            
            # 5. Testar consulta como faria a aplicação
            logger.info("\n5. Testando consulta da aplicação...")
            cursor.execute("""
                SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
                FROM veiculos 
                WHERE usuario_id = ? 
                ORDER BY data_cadastro DESC
            """, (sergio_id,))
            
            veiculos_usuario = cursor.fetchall()
            logger.info(f"✅ Encontrados {len(veiculos_usuario)} veículo(s) para o usuário:")
            
            for v in veiculos_usuario:
                status = "✅ Ativo" if v[8] else "❌ Inativo"
                logger.info(f"  ID: {v[0]} | {v[1]} {v[2]} | Placa: {v[4]} | {status}")
            
            # 6. Verificar se o veículo de teste está na lista
            placas_encontradas = [v[4] for v in veiculos_usuario]
            if placa_teste in placas_encontradas:
                logger.info(f"✅ Placa de teste {placa_teste} encontrada na lista!")
            else:
                logger.error(f"❌ Placa de teste {placa_teste} NÃO encontrada na lista!")
                return False
            
            # 7. Limpar veículo de teste
            logger.info("\n6. Limpando veículo de teste...")
            cursor.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
            conn.commit()
            logger.info(f"✅ Veículo de teste removido (ID: {veiculo_id})")
            
            logger.info("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir veículo: {e}")
            conn.rollback()
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def fix_database_foreign_keys():
    """Corrige configuração de foreign keys no banco"""
    
    # Usar caminho direto do banco
    db_path = Path("data/viemar_garantia.db")
    
    if not db_path.exists():
        logger.error(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Usar fastlite para garantir configuração correta
        db = Database(db_path)
        
        logger.info("🔧 Configurando foreign keys no banco...")
        
        # Habilitar foreign keys
        db.execute("PRAGMA foreign_keys = ON")
        
        # Verificar se foi habilitado
        result = db.execute("PRAGMA foreign_keys").fetchone()
        if result and result[0]:
            logger.info("✅ Foreign keys habilitadas com sucesso")
        else:
            logger.error("❌ Falha ao habilitar foreign keys")
            return False
        
        # Verificar integridade
        integrity_check = db.execute("PRAGMA foreign_key_check").fetchall()
        if integrity_check:
            logger.warning(f"⚠️ Problemas de integridade encontrados: {len(integrity_check)}")
            for issue in integrity_check:
                logger.warning(f"  {issue}")
        else:
            logger.info("✅ Integridade referencial OK")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar banco: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚗 TESTE DE CADASTRO DE VEÍCULO - SERGIO@REIS.COM\n")
    
    # 1. Corrigir configuração do banco
    logger.info("Etapa 1: Configurando banco de dados...")
    if not fix_database_foreign_keys():
        logger.error("❌ Falha na configuração do banco")
        exit(1)
    
    # 2. Testar cadastro
    logger.info("\nEtapa 2: Testando cadastro de veículo...")
    if test_sergio_veiculo_cadastro():
        logger.info("\n✅ SUCESSO: O cadastro de veículos está funcionando corretamente!")
        logger.info("\n📝 PRÓXIMOS PASSOS:")
        logger.info("   1. Acesse http://localhost:8000")
        logger.info("   2. Faça login com sergio@reis.com / 123456")
        logger.info("   3. Vá em 'Meus Veículos' e cadastre um novo veículo")
        logger.info("   4. Verifique se o veículo aparece na lista")
    else:
        logger.error("\n❌ FALHA: Há problemas com o cadastro de veículos")
        logger.error("\n🔍 INVESTIGAÇÃO NECESSÁRIA:")
        logger.error("   1. Verifique os logs da aplicação")
        logger.error("   2. Teste manualmente via interface web")
        logger.error("   3. Verifique se há erros JavaScript no navegador")
    
    logger.info("\n✨ Teste concluído!")