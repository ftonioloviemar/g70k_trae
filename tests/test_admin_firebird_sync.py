#!/usr/bin/env python3
"""
Teste automatizado para verificar a funcionalidade de sincronização do Firebird
com autenticação de administrador.
"""

import os
import sys
import time
import requests
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.logger import get_logger

# Configurar logger
logger = get_logger(__name__)

def test_admin_login_and_firebird_sync():
    """
    Testa o login de administrador e a sincronização com Firebird
    """
    base_url = "http://localhost:8000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        logger.info("Iniciando teste de login e sincronização...")
        
        # 1. Fazer login como administrador
        logger.info("Fazendo login como administrador...")
        login_data = {
            'email': 'ftoniolo@viemar.com.br',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
        
        if login_response.status_code != 200:
            logger.error(f"Erro no login: Status {login_response.status_code}")
            return False
            
        # Verificar se foi redirecionado para /admin (login bem-sucedido para admin)
        if '/admin' in login_response.url:
            logger.info("✅ Login realizado com sucesso - redirecionado para área administrativa")
        elif 'erro=' in login_response.url:
            logger.error(f"❌ Login falhou - erro nas credenciais: {login_response.url}")
            return False
        else:
            logger.error(f"❌ Login falhou - redirecionado para: {login_response.url}")
            return False
            
        # Verificar se o cookie de sessão foi definido
        session_cookies = session.cookies.get_dict()
        if 'session_id' in session_cookies:
            logger.info("✅ Cookie de sessão definido corretamente")
        else:
            logger.warning("⚠️ Cookie de sessão não encontrado")
        
        # 2. Acessar página de sincronização
        logger.info("Acessando página de sincronização...")
        sync_page_response = session.get(f"{base_url}/admin/produtos/sync")
        
        if sync_page_response.status_code != 200:
            logger.error(f"Erro ao acessar página de sincronização: Status {sync_page_response.status_code}")
            return False
            
        logger.info("✅ Página de sincronização acessada com sucesso")
        
        # 3. Testar conexão com Firebird
        logger.info("Testando conexão com Firebird...")
        test_connection_response = session.post(f"{base_url}/admin/produtos/test-firebird")
        
        if test_connection_response.status_code == 200:
            logger.info("✅ Teste de conexão com Firebird realizado")
            # Verificar resposta JSON
            try:
                test_result = test_connection_response.json()
                if test_result.get('success'):
                    logger.info("✅ Conexão com Firebird bem-sucedida")
                else:
                    logger.warning(f"⚠️ Teste de conexão falhou: {test_result.get('error', 'Erro desconhecido')}")
            except:
                logger.warning("⚠️ Resposta de teste de conexão não é JSON válido")
        else:
            logger.warning(f"⚠️ Teste de conexão retornou status {test_connection_response.status_code}")
        
        # 4. Executar sincronização
        logger.info("Executando sincronização de produtos...")
        sync_response = session.post(f"{base_url}/admin/produtos/sync-execute")
        
        if sync_response.status_code == 200:
            logger.info("✅ Sincronização executada com sucesso")
            
            # Verificar resposta JSON da sincronização
            try:
                sync_result = sync_response.json()
                if sync_result.get('success'):
                    stats = sync_result.get('stats', {})
                    logger.info(f"✅ Sincronização bem-sucedida: {stats}")
                    
                    # Log das estatísticas detalhadas
                    if isinstance(stats, dict):
                        total = stats.get('total_erp', 0)
                        inseridos = stats.get('inseridos', 0)
                        atualizados = stats.get('atualizados', 0)
                        erros = stats.get('erros', 0)
                        logger.info(f"📊 Estatísticas: Total ERP: {total}, Inseridos: {inseridos}, Atualizados: {atualizados}, Erros: {erros}")
                else:
                    logger.error(f"❌ Sincronização falhou: {sync_result.get('error', 'Erro desconhecido')}")
                    return False
            except:
                logger.warning("⚠️ Resposta de sincronização não é JSON válido")
                
        else:
            logger.error(f"❌ Erro na sincronização: Status {sync_response.status_code}")
            return False
        
        # 5. Verificar logs para problemas de encoding
        logger.info("Verificando logs para problemas de encoding...")
        
        # Aguardar um pouco para os logs serem escritos
        time.sleep(2)
        
        # Ler logs recentes
        log_dir = Path(__file__).parent.parent / 'logs'
        if log_dir.exists():
            log_files = list(log_dir.glob('*.log'))
            if log_files:
                latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                
                with open(latest_log, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    
                # Verificar se há erros de encoding nos logs recentes
                encoding_errors = [
                    'UnicodeDecodeError',
                    'codec can\'t decode',
                    'invalid continuation byte',
                    'encoding error'
                ]
                
                found_errors = []
                for error in encoding_errors:
                    if error.lower() in log_content.lower():
                        found_errors.append(error)
                
                if found_errors:
                    logger.warning(f"⚠️ Possíveis erros de encoding encontrados nos logs: {found_errors}")
                else:
                    logger.info("✅ Nenhum erro de encoding encontrado nos logs recentes")
        
        logger.info("🎉 Teste completo realizado com sucesso!")
        return True
        
    except requests.exceptions.ConnectionError:
        logger.error("❌ Erro de conexão - verifique se o servidor está rodando em http://localhost:8000")
        return False
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        return False

def main():
    """
    Função principal
    """
    logger.info("=== TESTE DE AUTENTICAÇÃO E SINCRONIZAÇÃO FIREBIRD ===")
    
    success = test_admin_login_and_firebird_sync()
    
    if success:
        logger.info("\n🎉 Todos os testes passaram com sucesso!")
        print("\n🎉 Teste de autenticação e sincronização concluído com sucesso!")
        return 0
    else:
        logger.error("\n💥 Alguns testes falharam")
        print("\n💥 Teste falhou - verifique os logs para mais detalhes")
        return 1

if __name__ == '__main__':
    sys.exit(main())