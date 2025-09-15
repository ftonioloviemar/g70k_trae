#!/usr/bin/env python3
"""
Script para debugar a estrutura da sessão do sergio@reis.com
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from fastlite import Database
from app.auth import get_auth_manager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_sergio_session():
    """Debug da estrutura da sessão do sergio@reis.com"""
    
    # Usar caminho direto do banco
    db_path = Path("data/viemar_garantia.db")
    
    if not db_path.exists():
        logger.error(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("🔍 DEBUG DA SESSÃO DO SERGIO@REIS.COM\n")
        
        # 1. Verificar usuário no banco
        logger.info("1. Verificando usuário no banco...")
        cursor.execute(
            "SELECT id, email, nome, tipo_usuario, confirmado FROM usuarios WHERE email = ?",
            ('sergio@reis.com',)
        )
        sergio = cursor.fetchone()
        
        if not sergio:
            logger.error("❌ Usuário sergio@reis.com não encontrado!")
            return False
        
        sergio_id, email, nome, tipo, confirmado = sergio
        logger.info(f"✅ Usuário no banco:")
        logger.info(f"   ID: {sergio_id}")
        logger.info(f"   Email: {email}")
        logger.info(f"   Nome: {nome}")
        logger.info(f"   Tipo: {tipo}")
        logger.info(f"   Confirmado: {confirmado}")
        
        # 2. Simular criação de sessão
        logger.info("\n2. Simulando criação de sessão...")
        
        # Usar o AuthManager para criar uma sessão
        db = Database(db_path)
        auth_manager = get_auth_manager()
        auth_manager.db = db  # Garantir que está usando o banco correto
        
        # Criar sessão
        session_id = auth_manager.criar_sessao(sergio_id, email, tipo)
        logger.info(f"✅ Sessão criada: {session_id[:16]}...")
        
        # 3. Obter dados da sessão
        logger.info("\n3. Obtendo dados da sessão...")
        session_data = auth_manager.obter_sessao(session_id)
        
        if session_data:
            logger.info("✅ Dados da sessão:")
            for key, value in session_data.items():
                if key in ['criado_em', 'expira_em']:
                    logger.info(f"   {key}: {value}")
                else:
                    logger.info(f"   {key}: {value}")
            
            # 4. Verificar chaves específicas
            logger.info("\n4. Verificando chaves específicas...")
            
            # Verificar se tem 'usuario_id'
            if 'usuario_id' in session_data:
                logger.info(f"✅ session_data['usuario_id'] = {session_data['usuario_id']}")
            else:
                logger.error("❌ Chave 'usuario_id' não encontrada na sessão!")
            
            # Verificar se tem 'id'
            if 'id' in session_data:
                logger.info(f"✅ session_data['id'] = {session_data['id']}")
            else:
                logger.info("ℹ️ Chave 'id' não encontrada na sessão (normal)")
            
            # 5. Testar consulta de veículos com o ID correto
            logger.info("\n5. Testando consulta de veículos...")
            
            user_id_for_query = session_data.get('usuario_id')
            if user_id_for_query:
                cursor.execute("""
                    SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
                    FROM veiculos 
                    WHERE usuario_id = ?
                    ORDER BY data_cadastro DESC
                """, (user_id_for_query,))
                
                veiculos = cursor.fetchall()
                logger.info(f"✅ Encontrados {len(veiculos)} veículo(s) com usuario_id = {user_id_for_query}")
                
                for i, v in enumerate(veiculos[:3], 1):  # Mostrar apenas os 3 primeiros
                    status = "✅ Ativo" if v[8] else "❌ Inativo"
                    logger.info(f"   {i}. {v[1]} {v[2]} | Placa: {v[4]} | {status}")
                
                if len(veiculos) > 3:
                    logger.info(f"   ... e mais {len(veiculos) - 3} veículo(s)")
            else:
                logger.error("❌ Não foi possível obter usuario_id da sessão!")
            
            # 6. Simular o que acontece na rota
            logger.info("\n6. Simulando código da rota de veículos...")
            
            # Simular request.state.usuario = session_data
            user = session_data
            
            logger.info(f"user = {user}")
            logger.info(f"user['tipo_usuario'] = {user.get('tipo_usuario')}")
            
            if user.get('tipo_usuario') != 'cliente':
                logger.warning(f"⚠️ Usuário não é cliente! Tipo: {user.get('tipo_usuario')}")
                logger.warning("   Isso pode explicar por que não vê os veículos")
            else:
                logger.info("✅ Usuário é cliente")
            
            # Testar acesso ao usuario_id
            try:
                usuario_id_rota = user['usuario_id']
                logger.info(f"✅ user['usuario_id'] = {usuario_id_rota}")
            except KeyError as e:
                logger.error(f"❌ Erro ao acessar user['usuario_id']: {e}")
                logger.error("   Chaves disponíveis:")
                for key in user.keys():
                    logger.error(f"     - {key}")
            
            return True
        else:
            logger.error("❌ Não foi possível obter dados da sessão!")
            return False
    
    except Exception as e:
        logger.error(f"❌ Erro durante debug: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def check_all_sessions():
    """Verifica todas as sessões ativas"""
    
    try:
        logger.info("\n🔍 VERIFICANDO TODAS AS SESSÕES ATIVAS\n")
        
        auth_manager = get_auth_manager()
        
        if not auth_manager.sessions:
            logger.info("ℹ️ Nenhuma sessão ativa encontrada")
            return
        
        logger.info(f"📊 Total de sessões ativas: {len(auth_manager.sessions)}")
        
        for i, (session_id, session_data) in enumerate(auth_manager.sessions.items(), 1):
            logger.info(f"\n{i}. Sessão: {session_id[:16]}...")
            logger.info(f"   Email: {session_data.get('usuario_email')}")
            logger.info(f"   ID: {session_data.get('usuario_id')}")
            logger.info(f"   Tipo: {session_data.get('tipo_usuario')}")
            logger.info(f"   Criada: {session_data.get('criado_em')}")
            logger.info(f"   Expira: {session_data.get('expira_em')}")
    
    except Exception as e:
        logger.error(f"❌ Erro ao verificar sessões: {e}")

if __name__ == "__main__":
    logger.info("🔍 DEBUG DA ESTRUTURA DE SESSÃO\n")
    
    # 1. Debug da sessão do sergio
    logger.info("Etapa 1: Debug da sessão do sergio@reis.com...")
    if debug_sergio_session():
        logger.info("\n✅ Debug da sessão concluído com sucesso!")
    else:
        logger.error("\n❌ Falha no debug da sessão")
    
    # 2. Verificar todas as sessões
    logger.info("\nEtapa 2: Verificando todas as sessões...")
    check_all_sessions()
    
    logger.info("\n✨ Debug concluído!")