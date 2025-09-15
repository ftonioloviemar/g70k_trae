#!/usr/bin/env python3
"""
Script para testar a rota de listagem de veículos do sergio@reis.com
"""

import requests
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sergio_login_and_veiculos():
    """Testa login e listagem de veículos via HTTP"""
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    try:
        logger.info("🔐 TESTANDO LOGIN E LISTAGEM DE VEÍCULOS\n")
        
        # 1. Verificar se o servidor está rodando
        logger.info("1. Verificando servidor...")
        try:
            response = session.get(base_url, timeout=5)
            if response.status_code == 200:
                logger.info("✅ Servidor está rodando")
            else:
                logger.error(f"❌ Servidor retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro ao conectar com servidor: {e}")
            return False
        
        # 2. Fazer login
        logger.info("\n2. Fazendo login com sergio@reis.com...")
        
        # Primeiro, obter a página de login para possíveis tokens CSRF
        login_page = session.get(f"{base_url}/login")
        if login_page.status_code != 200:
            logger.error(f"❌ Erro ao acessar página de login: {login_page.status_code}")
            return False
        
        # Fazer login
        login_data = {
            'email': 'sergio@reis.com',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        logger.info(f"Status do login: {login_response.status_code}")
        logger.info(f"Headers de resposta: {dict(login_response.headers)}")
        
        # Verificar se foi redirecionado (sucesso no login)
        if login_response.status_code in [302, 303]:
            redirect_location = login_response.headers.get('location', '')
            logger.info(f"✅ Login bem-sucedido! Redirecionado para: {redirect_location}")
        elif login_response.status_code == 200:
            # Pode ser que retornou a página com erro
            if 'erro' in login_response.text.lower() or 'inválid' in login_response.text.lower():
                logger.error("❌ Credenciais inválidas")
                return False
            else:
                logger.info("✅ Login aparentemente bem-sucedido (status 200)")
        else:
            logger.error(f"❌ Erro no login: {login_response.status_code}")
            logger.error(f"Conteúdo da resposta: {login_response.text[:500]}")
            return False
        
        # 3. Acessar página de veículos
        logger.info("\n3. Acessando página de veículos...")
        
        veiculos_response = session.get(f"{base_url}/cliente/veiculos")
        
        logger.info(f"Status da página de veículos: {veiculos_response.status_code}")
        
        if veiculos_response.status_code == 200:
            logger.info("✅ Página de veículos acessada com sucesso")
            
            # Verificar conteúdo da página
            content = veiculos_response.text
            
            # Procurar por indicadores de veículos
            if 'Nenhum veículo cadastrado' in content:
                logger.error("❌ Página mostra 'Nenhum veículo cadastrado'")
                logger.info("\n📄 CONTEÚDO DA PÁGINA (primeiros 1000 caracteres):")
                logger.info(content[:1000])
                return False
            elif 'Toyota' in content or 'Volkswagen' in content or 'Honda' in content:
                logger.info("✅ Veículos encontrados na página!")
                
                # Contar quantos veículos aparecem
                import re
                placa_pattern = r'[A-Z]{3}[0-9]{4}|[A-Z]{3}[0-9][A-Z][0-9]{2}'
                placas_encontradas = re.findall(placa_pattern, content)
                logger.info(f"Placas encontradas na página: {placas_encontradas}")
                
                return True
            else:
                logger.warning("⚠️ Página carregou mas não há indicação clara de veículos")
                logger.info("\n📄 CONTEÚDO DA PÁGINA (primeiros 1500 caracteres):")
                logger.info(content[:1500])
                return False
        
        elif veiculos_response.status_code == 302:
            # Redirecionado - pode ser que não esteja logado
            redirect_location = veiculos_response.headers.get('location', '')
            logger.error(f"❌ Redirecionado para: {redirect_location} (provavelmente não logado)")
            return False
        
        else:
            logger.error(f"❌ Erro ao acessar página de veículos: {veiculos_response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        return False

def check_database_veiculos():
    """Verifica veículos diretamente no banco de dados"""
    
    db_path = Path("data/viemar_garantia.db")
    
    if not db_path.exists():
        logger.error(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("\n🗄️ VERIFICANDO BANCO DE DADOS\n")
        
        # 1. Verificar usuário sergio
        cursor.execute(
            "SELECT id, email, nome, tipo_usuario FROM usuarios WHERE email = ?",
            ('sergio@reis.com',)
        )
        sergio = cursor.fetchone()
        
        if not sergio:
            logger.error("❌ Usuário sergio@reis.com não encontrado!")
            return False
        
        sergio_id = sergio[0]
        logger.info(f"✅ Usuário encontrado: ID {sergio_id} | {sergio[1]} | {sergio[2]}")
        
        # 2. Verificar veículos
        cursor.execute("""
            SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
            FROM veiculos 
            WHERE usuario_id = ?
            ORDER BY data_cadastro DESC
        """, (sergio_id,))
        
        veiculos = cursor.fetchall()
        
        logger.info(f"\n📊 VEÍCULOS NO BANCO: {len(veiculos)}")
        
        for i, veiculo in enumerate(veiculos, 1):
            status = "✅ Ativo" if veiculo[8] else "❌ Inativo"
            logger.info(f"{i:2d}. ID: {veiculo[0]:2d} | {veiculo[1]} {veiculo[2]} ({veiculo[3]}) | Placa: {veiculo[4]} | {status}")
            logger.info(f"     Cor: {veiculo[5]} | Chassi: {veiculo[6][:15]}... | Cadastro: {veiculo[7][:10]}")
        
        return len(veiculos) > 0
    
    except Exception as e:
        logger.error(f"❌ Erro ao verificar banco: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    logger.info("🚗 TESTE DE LISTAGEM DE VEÍCULOS - SERGIO@REIS.COM\n")
    
    # 1. Verificar banco de dados
    logger.info("Etapa 1: Verificando banco de dados...")
    db_ok = check_database_veiculos()
    
    if not db_ok:
        logger.error("❌ Problemas no banco de dados")
        exit(1)
    
    # 2. Testar via HTTP
    logger.info("\nEtapa 2: Testando via interface web...")
    web_ok = test_sergio_login_and_veiculos()
    
    # 3. Resultado final
    logger.info("\n" + "="*60)
    
    if db_ok and web_ok:
        logger.info("✅ SUCESSO: Veículos estão no banco E aparecem na web!")
    elif db_ok and not web_ok:
        logger.error("❌ PROBLEMA: Veículos estão no banco mas NÃO aparecem na web!")
        logger.error("\n🔍 POSSÍVEIS CAUSAS:")
        logger.error("   1. Problema na consulta SQL da aplicação")
        logger.error("   2. Problema na sessão/autenticação")
        logger.error("   3. Problema no template/renderização")
        logger.error("   4. Cache do navegador")
    elif not db_ok and not web_ok:
        logger.error("❌ PROBLEMA: Não há veículos no banco")
    else:
        logger.warning("⚠️ SITUAÇÃO ESTRANHA: Não há veículos no banco mas aparecem na web")
    
    logger.info("\n✨ Teste concluído!")