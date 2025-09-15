#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar as garantias do usuário sergio@reis.com
Verifica se as garantias estão no banco de dados e se aparecem na interface web
"""

import sqlite3
import requests
from datetime import datetime

def verificar_garantias_banco():
    """Verifica as garantias de sergio@reis.com no banco de dados"""
    print("=== VERIFICANDO GARANTIAS NO BANCO DE DADOS ===")
    
    conn = sqlite3.connect('viemar_garantia.db')
    cursor = conn.cursor()
    
    # Buscar usuário sergio@reis.com
    cursor.execute("SELECT id, email, nome FROM usuarios WHERE email = ?", ('sergio@reis.com',))
    usuario = cursor.fetchone()
    
    if not usuario:
        print("❌ Usuário sergio@reis.com não encontrado!")
        return
    
    user_id, email, nome = usuario
    print(f"✅ Usuário encontrado: ID={user_id}, Email={email}, Nome={nome}")
    
    # Buscar garantias do usuário
    cursor.execute("""
        SELECT g.id, g.lote_fabricacao, g.data_instalacao, g.data_cadastro, g.data_vencimento, g.ativo,
               v.marca, v.modelo, v.placa, p.sku, p.descricao as produto_nome
        FROM garantias g
        LEFT JOIN veiculos v ON g.veiculo_id = v.id
        LEFT JOIN produtos p ON g.produto_id = p.id
        WHERE g.usuario_id = ?
        ORDER BY g.data_cadastro DESC
    """, (user_id,))
    
    garantias = cursor.fetchall()
    
    print(f"\n📊 Total de garantias encontradas: {len(garantias)}")
    
    if garantias:
        print("\n=== DETALHES DAS GARANTIAS ===")
        for i, garantia in enumerate(garantias, 1):
            gid, lote, data_instalacao, data_cadastro, data_vencimento, ativo, marca, modelo, placa, sku, produto = garantia
            print(f"\n{i}. Garantia ID: {gid}")
            print(f"   Lote: {lote}")
            print(f"   Data Instalação: {data_instalacao}")
            print(f"   Data Cadastro: {data_cadastro}")
            print(f"   Data Vencimento: {data_vencimento}")
            print(f"   Ativo: {ativo}")
            print(f"   Veículo: {marca} {modelo} - {placa}")
            print(f"   Produto: {sku} - {produto}")
    else:
        print("❌ Nenhuma garantia encontrada para sergio@reis.com")
        
        # Verificar se existem garantias sem usuario_id
        cursor.execute("""
            SELECT COUNT(*) FROM garantias WHERE usuario_id IS NULL
        """)
        garantias_orfas = cursor.fetchone()[0]
        print(f"\n🔍 Garantias sem usuário: {garantias_orfas}")
        
        # Verificar se existem veículos do usuário
        cursor.execute("""
            SELECT COUNT(*) FROM veiculos WHERE usuario_id = ?
        """, (user_id,))
        veiculos_count = cursor.fetchone()[0]
        print(f"🔍 Veículos do usuário: {veiculos_count}")
    
    conn.close()
    return len(garantias)

def testar_interface_web():
    """Testa a interface web das garantias"""
    print("\n=== TESTANDO INTERFACE WEB ===")
    
    session = requests.Session()
    
    # Verificar se servidor está rodando
    try:
        response = session.get('http://localhost:8000')
        print(f"✅ Servidor respondendo: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando!")
        return False
    
    # Fazer login
    login_data = {
        'email': 'sergio@reis.com',
        'senha': '123456'
    }
    
    response = session.post('http://localhost:8000/login', data=login_data)
    print(f"Login response: {response.status_code} - {response.url}")
    
    if '/cliente' not in response.url:
        print("❌ Login falhou!")
        return False
    
    print("✅ Login realizado com sucesso")
    
    # Acessar página de garantias
    response = session.get('http://localhost:8000/cliente/garantias')
    print(f"Página garantias: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        
        # Verificar se há tabela de garantias
        if '<table' in content:
            print("✅ Tabela encontrada na página")
            
            # Contar linhas de dados (tr com td)
            import re
            data_rows = re.findall(r'<tr[^>]*>.*?<td', content, re.DOTALL)
            print(f"📊 Linhas de dados na tabela: {len(data_rows)}")
            
            # Verificar se há garantias específicas
            if 'LOTE' in content or 'lote' in content.lower():
                print("✅ Lotes de fabricação encontrados na página")
            else:
                print("❌ Nenhum lote de fabricação encontrado")
                
            # Verificar mensagens
            if 'Nenhuma garantia' in content or 'não possui garantias' in content:
                print("⚠️ Mensagem de 'nenhuma garantia' encontrada")
                
        else:
            print("❌ Nenhuma tabela encontrada na página")
            
        # Salvar HTML para análise
        with open('debug_garantias_page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("💾 HTML salvo em debug_garantias_page.html")
        
    else:
        print(f"❌ Erro ao acessar página de garantias: {response.status_code}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DAS GARANTIAS DE SERGIO@REIS.COM")
    print("=" * 50)
    
    # Verificar banco de dados
    garantias_count = verificar_garantias_banco()
    
    # Testar interface web
    web_ok = testar_interface_web()
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DO DIAGNÓSTICO")
    print(f"Garantias no banco: {garantias_count}")
    print(f"Interface web: {'✅ OK' if web_ok else '❌ Problema'}")
    
    if garantias_count == 0:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Criar garantias de teste para sergio@reis.com")
        print("2. Verificar se a rota de garantias está funcionando")
    elif garantias_count > 0 and not web_ok:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Verificar rota /garantias")
        print("2. Verificar consulta SQL na função listar_garantias")
        print("3. Verificar renderização da tabela")