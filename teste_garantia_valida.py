#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final para confirmar que garantias válidas (dentro de 30 dias) são aceitas.
"""

import requests
import sqlite3
from datetime import datetime, timedelta

def teste_garantia_valida():
    """Testa criação de garantia válida (dentro de 30 dias)"""
    print("🧪 TESTE FINAL: GARANTIA VÁLIDA")
    print("=" * 40)
    
    base_url = 'http://localhost:8000'
    
    # Verificar se servidor está rodando
    try:
        response = requests.get(base_url)
        print(f"✅ Servidor respondendo: {response.status_code}")
    except:
        print("❌ Servidor não está rodando")
        return
    
    # Fazer login
    session = requests.Session()
    login_data = {
        'email': 'sergio@reis.com',
        'password': '123456'
    }
    
    login_response = session.post(f'{base_url}/login', data=login_data)
    print(f"Login response: {login_response.status_code} - {login_response.url}")
    
    if 'cliente' not in login_response.url:
        print("❌ Falha no login")
        return
    
    print("✅ Login realizado com sucesso")
    
    # Testar garantia válida (15 dias atrás)
    data_valida = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
    
    garantia_data = {
        'produto_id': '1',
        'veiculo_id': '1', 
        'lote_fabricacao': f'LOTE-TESTE-VALIDO-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'data_instalacao': data_valida,
        'nota_fiscal': '99999',
        'nome_estabelecimento': 'Oficina Teste Final',
        'quilometragem': '45000',
        'observacoes': 'Teste final - garantia válida 15 dias'
    }
    
    print(f"📅 Testando garantia com data: {data_valida} (15 dias atrás)")
    
    response = session.post(f'{base_url}/cliente/garantias/nova', data=garantia_data)
    print(f"Resposta: {response.status_code}")
    
    # Verificar se foi criada no banco
    try:
        conn = sqlite3.connect('viemar_garantia.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, lote_fabricacao, data_instalacao 
            FROM garantias 
            WHERE lote_fabricacao = ?
        """, (garantia_data['lote_fabricacao'],))
        
        garantia = cursor.fetchone()
        
        if garantia:
            print(f"✅ Garantia criada com sucesso!")
            print(f"   - ID: {garantia[0]}")
            print(f"   - Lote: {garantia[1]}")
            print(f"   - Data instalação: {garantia[2]}")
            
            # Verificar se aparece na lista
            lista_response = session.get(f'{base_url}/cliente/garantias')
            if garantia_data['lote_fabricacao'] in lista_response.text:
                print("✅ Garantia aparece na lista do cliente")
            else:
                print("⚠️  Garantia não aparece na lista do cliente")
                
        else:
            print("❌ Garantia não foi criada no banco")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
    
    print("\n🎯 TESTE CONCLUÍDO")

if __name__ == "__main__":
    teste_garantia_valida()