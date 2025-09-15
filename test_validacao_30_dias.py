#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para validação de garantias com mais de 30 dias de instalação
"""

import requests
from datetime import datetime, timedelta
import sqlite3

def test_validacao_30_dias():
    """Testa a validação de 30 dias na criação de garantias"""
    print("🧪 TESTANDO VALIDAÇÃO DE 30 DIAS")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Verificar se servidor está rodando
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✅ Servidor respondendo: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor não está rodando: {e}")
        return False
    
    # Fazer login como sergio@reis.com
    session = requests.Session()
    
    login_data = {
        'email': 'sergio@reis.com',
        'senha': '123456'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response: {login_response.status_code} - {login_response.url}")
    
    if '/cliente' not in login_response.url:
        print("❌ Falha no login")
        return False
    
    print("✅ Login realizado com sucesso")
    
    # Buscar dados necessários do banco
    conn = sqlite3.connect('viemar_garantia.db')
    cursor = conn.cursor()
    
    # Buscar usuário
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", ('sergio@reis.com',))
    usuario = cursor.fetchone()
    if not usuario:
        print("❌ Usuário não encontrado")
        return False
    
    user_id = usuario[0]
    
    # Buscar primeiro produto e veículo
    cursor.execute("SELECT id FROM produtos WHERE ativo = 1 LIMIT 1")
    produto = cursor.fetchone()
    
    cursor.execute("SELECT id FROM veiculos WHERE usuario_id = ? AND ativo = 1 LIMIT 1", (user_id,))
    veiculo = cursor.fetchone()
    
    if not produto or not veiculo:
        print("❌ Produto ou veículo não encontrado")
        return False
    
    produto_id = produto[0]
    veiculo_id = veiculo[0]
    
    conn.close()
    
    print(f"✅ Dados encontrados: produto_id={produto_id}, veiculo_id={veiculo_id}")
    
    # Teste 1: Data de instalação válida (dentro de 30 dias)
    print("\n📋 TESTE 1: Data válida (hoje)")
    data_valida = datetime.now().date().strftime('%Y-%m-%d')
    
    garantia_data_valida = {
        'produto_id': produto_id,
        'veiculo_id': veiculo_id,
        'lote_fabricacao': 'TESTE001',
        'data_instalacao': data_valida,
        'nota_fiscal': 'NF123456',
        'nome_estabelecimento': 'Oficina Teste',
        'quilometragem': '50000',
        'observacoes': 'Teste validação 30 dias'
    }
    
    response_valida = session.post(f"{base_url}/cliente/garantias/nova", data=garantia_data_valida)
    print(f"Resposta data válida: {response_valida.status_code}")
    
    if response_valida.status_code == 302 or '/garantias' in response_valida.url:
        print("✅ Data válida aceita corretamente")
        teste1_ok = True
    else:
        print("❌ Data válida rejeitada incorretamente")
        print(f"Conteúdo: {response_valida.text[:500]}")
        teste1_ok = False
    
    # Teste 2: Data de instalação inválida (mais de 30 dias)
    print("\n📋 TESTE 2: Data inválida (35 dias atrás)")
    data_invalida = (datetime.now().date() - timedelta(days=35)).strftime('%Y-%m-%d')
    
    garantia_data_invalida = {
        'produto_id': produto_id,
        'veiculo_id': veiculo_id,
        'lote_fabricacao': 'TESTE002',
        'data_instalacao': data_invalida,
        'nota_fiscal': 'NF789012',
        'nome_estabelecimento': 'Oficina Teste 2',
        'quilometragem': '60000',
        'observacoes': 'Teste validação 30 dias - deve falhar'
    }
    
    response_invalida = session.post(f"{base_url}/cliente/garantias/nova", data=garantia_data_invalida)
    print(f"Resposta data inválida: {response_invalida.status_code}")
    
    # Verificar se a mensagem de erro está presente
    if 'superior a 30 dias' in response_invalida.text:
        print("✅ Data inválida rejeitada corretamente com mensagem apropriada")
        teste2_ok = True
    else:
        print("❌ Data inválida não foi rejeitada ou mensagem incorreta")
        print(f"Conteúdo: {response_invalida.text[:500]}")
        teste2_ok = False
    
    # Teste 3: Data limite (exatamente 30 dias)
    print("\n📋 TESTE 3: Data limite (exatamente 30 dias atrás)")
    data_limite = (datetime.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    garantia_data_limite = {
        'produto_id': produto_id,
        'veiculo_id': veiculo_id,
        'lote_fabricacao': 'TESTE003',
        'data_instalacao': data_limite,
        'nota_fiscal': 'NF345678',
        'nome_estabelecimento': 'Oficina Teste 3',
        'quilometragem': '70000',
        'observacoes': 'Teste validação 30 dias - limite'
    }
    
    response_limite = session.post(f"{base_url}/cliente/garantias/nova", data=garantia_data_limite)
    print(f"Resposta data limite: {response_limite.status_code}")
    
    if response_limite.status_code == 302 or '/garantias' in response_limite.url:
        print("✅ Data limite (30 dias) aceita corretamente")
        teste3_ok = True
    else:
        print("❌ Data limite rejeitada incorretamente")
        print(f"Conteúdo: {response_limite.text[:500]}")
        teste3_ok = False
    
    # Teste 4: Data futura (deve continuar sendo rejeitada)
    print("\n📋 TESTE 4: Data futura (deve ser rejeitada)")
    data_futura = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    garantia_data_futura = {
        'produto_id': produto_id,
        'veiculo_id': veiculo_id,
        'lote_fabricacao': 'TESTE004',
        'data_instalacao': data_futura,
        'nota_fiscal': 'NF901234',
        'nome_estabelecimento': 'Oficina Teste 4',
        'quilometragem': '80000',
        'observacoes': 'Teste validação data futura'
    }
    
    response_futura = session.post(f"{base_url}/cliente/garantias/nova", data=garantia_data_futura)
    print(f"Resposta data futura: {response_futura.status_code}")
    
    if 'não pode ser futura' in response_futura.text:
        print("✅ Data futura rejeitada corretamente")
        teste4_ok = True
    else:
        print("❌ Data futura não foi rejeitada")
        print(f"Conteúdo: {response_futura.text[:500]}")
        teste4_ok = False
    
    # Resumo dos testes
    print("\n🎯 RESUMO DOS TESTES")
    print("=" * 30)
    print(f"Teste 1 (data válida): {'✅ PASSOU' if teste1_ok else '❌ FALHOU'}")
    print(f"Teste 2 (>30 dias): {'✅ PASSOU' if teste2_ok else '❌ FALHOU'}")
    print(f"Teste 3 (=30 dias): {'✅ PASSOU' if teste3_ok else '❌ FALHOU'}")
    print(f"Teste 4 (data futura): {'✅ PASSOU' if teste4_ok else '❌ FALHOU'}")
    
    todos_ok = teste1_ok and teste2_ok and teste3_ok and teste4_ok
    print(f"\n🏆 RESULTADO GERAL: {'✅ TODOS OS TESTES PASSARAM' if todos_ok else '❌ ALGUNS TESTES FALHARAM'}")
    
    return todos_ok

if __name__ == "__main__":
    try:
        sucesso = test_validacao_30_dias()
        exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado pelo usuário")
        exit(1)
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        exit(1)