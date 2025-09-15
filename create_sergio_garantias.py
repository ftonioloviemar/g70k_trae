#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar garantias de teste para sergio@reis.com
"""

import sqlite3
from datetime import datetime, timedelta

def criar_garantias_sergio():
    """Cria garantias de teste para sergio@reis.com"""
    print("🔧 CRIANDO GARANTIAS PARA SERGIO@REIS.COM")
    print("=" * 50)
    
    conn = sqlite3.connect('viemar_garantia.db')
    cursor = conn.cursor()
    
    # Buscar usuário sergio@reis.com
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", ('sergio@reis.com',))
    usuario = cursor.fetchone()
    
    if not usuario:
        print("❌ Usuário sergio@reis.com não encontrado!")
        return
    
    user_id = usuario[0]
    print(f"✅ Usuário encontrado: ID={user_id}")
    
    # Buscar veículos do usuário
    cursor.execute("SELECT id, marca, modelo, placa FROM veiculos WHERE usuario_id = ?", (user_id,))
    veiculos = cursor.fetchall()
    
    if not veiculos:
        print("❌ Nenhum veículo encontrado para o usuário!")
        return
    
    print(f"✅ Encontrados {len(veiculos)} veículos")
    
    # Buscar produtos disponíveis
    cursor.execute("SELECT id, sku, descricao FROM produtos WHERE ativo = 1")
    produtos = cursor.fetchall()
    
    if not produtos:
        print("❌ Nenhum produto encontrado!")
        return
    
    print(f"✅ Encontrados {len(produtos)} produtos")
    
    # Verificar garantias existentes
    cursor.execute("SELECT COUNT(*) FROM garantias WHERE usuario_id = ?", (user_id,))
    garantias_existentes = cursor.fetchone()[0]
    
    if garantias_existentes > 0:
        print(f"⚠️ Usuário já possui {garantias_existentes} garantias")
        resposta = input("Deseja continuar e criar mais garantias? (s/n): ")
        if resposta.lower() != 's':
            print("❌ Operação cancelada")
            return
    
    # Criar garantias de teste
    garantias_criadas = 0
    data_base = datetime.now() - timedelta(days=30)  # 30 dias atrás
    
    for i, veiculo in enumerate(veiculos[:3]):  # Máximo 3 garantias
        veiculo_id, marca, modelo, placa = veiculo
        produto = produtos[i % len(produtos)]  # Rotacionar produtos
        produto_id, sku, descricao = produto
        
        # Dados da garantia
        lote_fabricacao = f"LOTE{2024000 + i + 1:03d}"
        data_instalacao = data_base + timedelta(days=i * 5)
        data_vencimento = data_instalacao + timedelta(days=730)  # 2 anos
        quilometragem = 15000 + (i * 5000)
        nota_fiscal = f"NF{12345 + i:05d}"
        estabelecimento = f"Oficina Teste {i + 1}"
        observacoes = f"Garantia de teste {i + 1} para {marca} {modelo}"
        
        try:
            cursor.execute("""
                INSERT INTO garantias (
                    usuario_id, produto_id, veiculo_id, lote_fabricacao,
                    data_instalacao, data_vencimento, ativo, nota_fiscal,
                    nome_estabelecimento, quilometragem, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, produto_id, veiculo_id, lote_fabricacao,
                data_instalacao.isoformat(), data_vencimento.isoformat(), True,
                nota_fiscal, estabelecimento, quilometragem, observacoes
            ))
            
            garantia_id = cursor.lastrowid
            garantias_criadas += 1
            
            print(f"\n✅ Garantia {garantias_criadas} criada:")
            print(f"   ID: {garantia_id}")
            print(f"   Produto: {sku} - {descricao}")
            print(f"   Veículo: {marca} {modelo} - {placa}")
            print(f"   Lote: {lote_fabricacao}")
            print(f"   Instalação: {data_instalacao.strftime('%d/%m/%Y')}")
            print(f"   Vencimento: {data_vencimento.strftime('%d/%m/%Y')}")
            print(f"   Quilometragem: {quilometragem:,} km")
            
        except Exception as e:
            print(f"❌ Erro ao criar garantia {i + 1}: {e}")
    
    # Confirmar alterações
    conn.commit()
    conn.close()
    
    print(f"\n🎉 RESUMO:")
    print(f"Garantias criadas: {garantias_criadas}")
    print(f"Total de garantias do usuário: {garantias_existentes + garantias_criadas}")
    
    return garantias_criadas

def verificar_garantias_criadas():
    """Verifica as garantias criadas"""
    print("\n🔍 VERIFICANDO GARANTIAS CRIADAS")
    print("=" * 40)
    
    conn = sqlite3.connect('viemar_garantia.db')
    cursor = conn.cursor()
    
    # Buscar usuário
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", ('sergio@reis.com',))
    usuario = cursor.fetchone()
    
    if not usuario:
        print("❌ Usuário não encontrado!")
        return
    
    user_id = usuario[0]
    
    # Buscar garantias
    cursor.execute("""
        SELECT g.id, g.lote_fabricacao, g.data_instalacao, g.data_vencimento,
               p.sku, p.descricao, v.marca, v.modelo, v.placa
        FROM garantias g
        JOIN produtos p ON g.produto_id = p.id
        JOIN veiculos v ON g.veiculo_id = v.id
        WHERE g.usuario_id = ?
        ORDER BY g.data_cadastro DESC
    """, (user_id,))
    
    garantias = cursor.fetchall()
    
    print(f"Total de garantias: {len(garantias)}")
    
    for i, garantia in enumerate(garantias, 1):
        gid, lote, data_instalacao, data_vencimento, sku, descricao, marca, modelo, placa = garantia
        print(f"\n{i}. Garantia #{gid}")
        print(f"   Produto: {sku} - {descricao}")
        print(f"   Veículo: {marca} {modelo} - {placa}")
        print(f"   Lote: {lote}")
        print(f"   Instalação: {datetime.fromisoformat(data_instalacao).strftime('%d/%m/%Y')}")
        print(f"   Vencimento: {datetime.fromisoformat(data_vencimento).strftime('%d/%m/%Y')}")
    
    conn.close()

if __name__ == "__main__":
    try:
        garantias_criadas = criar_garantias_sergio()
        if garantias_criadas > 0:
            verificar_garantias_criadas()
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")