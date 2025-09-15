#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar produtos de teste no banco de dados
"""

import sqlite3
from datetime import datetime

def verificar_produtos():
    """Verifica produtos existentes no banco"""
    print("🔍 VERIFICANDO PRODUTOS NO BANCO")
    print("=" * 40)
    
    conn = sqlite3.connect('viemar_garantia.db')
    cursor = conn.cursor()
    
    # Verificar estrutura da tabela produtos
    cursor.execute("PRAGMA table_info(produtos)")
    colunas = cursor.fetchall()
    
    print("Estrutura da tabela produtos:")
    for coluna in colunas:
        print(f"  {coluna[1]} ({coluna[2]})")
    
    # Buscar produtos existentes
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    
    print(f"\nTotal de produtos: {len(produtos)}")
    
    if produtos:
        print("\nProdutos existentes:")
        for produto in produtos:
            print(f"  ID: {produto[0]}, SKU: {produto[1]}, Descrição: {produto[2]}, Ativo: {produto[3]}")
    
    conn.close()
    return len(produtos)

def criar_produtos_teste():
    """Cria produtos de teste"""
    print("\n🔧 CRIANDO PRODUTOS DE TESTE")
    print("=" * 40)
    
    conn = sqlite3.connect('viemar_garantia.db')
    cursor = conn.cursor()
    
    produtos_teste = [
        {
            'sku': 'VIE-001',
            'descricao': 'Filtro de Combustível Viemar Premium',
            'categoria': 'Filtros',
            'preco': 89.90,
            'ativo': True
        },
        {
            'sku': 'VIE-002', 
            'descricao': 'Filtro de Óleo Viemar Standard',
            'categoria': 'Filtros',
            'preco': 45.50,
            'ativo': True
        },
        {
            'sku': 'VIE-003',
            'descricao': 'Filtro de Ar Viemar High Performance',
            'categoria': 'Filtros',
            'preco': 125.00,
            'ativo': True
        },
        {
            'sku': 'VIE-004',
            'descricao': 'Kit Filtros Completo Viemar',
            'categoria': 'Kits',
            'preco': 220.00,
            'ativo': True
        },
        {
            'sku': 'VIE-005',
            'descricao': 'Aditivo Combustível Viemar Pro',
            'categoria': 'Aditivos',
            'preco': 35.90,
            'ativo': True
        }
    ]
    
    produtos_criados = 0
    
    for produto in produtos_teste:
        try:
            # Verificar se produto já existe
            cursor.execute("SELECT id FROM produtos WHERE sku = ?", (produto['sku'],))
            existe = cursor.fetchone()
            
            if existe:
                print(f"⚠️ Produto {produto['sku']} já existe (ID: {existe[0]})")
                continue
            
            # Inserir produto
            cursor.execute("""
                INSERT INTO produtos (sku, descricao, ativo, data_cadastro)
                VALUES (?, ?, ?, ?)
            """, (
                produto['sku'],
                produto['descricao'],
                produto['ativo'],
                datetime.now().isoformat()
            ))
            
            produto_id = cursor.lastrowid
            produtos_criados += 1
            
            print(f"✅ Produto criado: {produto['sku']} - {produto['descricao']} (ID: {produto_id})")
            
        except Exception as e:
            print(f"❌ Erro ao criar produto {produto['sku']}: {e}")
    
    # Confirmar alterações
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Produtos criados: {produtos_criados}")
    return produtos_criados

if __name__ == "__main__":
    try:
        total_produtos = verificar_produtos()
        
        if total_produtos == 0:
            print("\n📦 Nenhum produto encontrado. Criando produtos de teste...")
            criar_produtos_teste()
            print("\n🔍 Verificando produtos após criação:")
            verificar_produtos()
        else:
            print(f"\n✅ Já existem {total_produtos} produtos no banco")
            
    except Exception as e:
        print(f"❌ Erro: {e}")