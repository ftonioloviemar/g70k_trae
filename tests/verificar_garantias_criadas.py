#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se as garantias de teste foram realmente criadas ou rejeitadas
conforme a validação de 30 dias.
"""

import sqlite3
from datetime import datetime, timedelta

def verificar_garantias():
    """Verifica garantias criadas no banco de dados"""
    print("🔍 VERIFICANDO GARANTIAS NO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('viemar_garantia.db')
        cursor = conn.cursor()
        
        # Buscar todas as garantias de teste
        lotes_teste = [
            'LOTE-VALIDO-001',
            'LOTE-INVALIDO-001', 
            'LOTE-LIMITE-001',
            'LOTE-FUTURO-001'
        ]
        
        print("📊 Verificando garantias de teste:")
        print()
        
        for lote in lotes_teste:
            cursor.execute("""
                SELECT id, lote_fabricacao, data_instalacao, data_cadastro
                FROM garantias 
                WHERE lote_fabricacao = ?
            """, (lote,))
            
            garantia = cursor.fetchone()
            
            if garantia:
                data_instalacao = garantia[2]
                data_cadastro = garantia[3]
                
                # Calcular diferença de dias
                try:
                    data_inst = datetime.fromisoformat(data_instalacao).date()
                    hoje = datetime.now().date()
                    dias_diferenca = (hoje - data_inst).days
                    
                    print(f"✅ {lote}:")
                    print(f"   - ID: {garantia[0]}")
                    print(f"   - Data instalação: {data_instalacao}")
                    print(f"   - Dias atrás: {dias_diferenca}")
                    print(f"   - Data cadastro: {data_cadastro}")
                    
                    # Verificar se deveria ter sido aceita
                    if dias_diferenca > 30:
                        print(f"   ⚠️  ATENÇÃO: Esta garantia tem {dias_diferenca} dias e foi aceita!")
                    elif dias_diferenca < 0:
                        print(f"   ⚠️  ATENÇÃO: Esta garantia tem data futura e foi aceita!")
                    else:
                        print(f"   ✅ Garantia válida ({dias_diferenca} dias)")
                        
                except Exception as e:
                    print(f"   ❌ Erro ao processar data: {e}")
                    
            else:
                print(f"❌ {lote}: NÃO ENCONTRADA (rejeitada corretamente)")
            
            print()
        
        # Contar total de garantias
        cursor.execute("SELECT COUNT(*) FROM garantias")
        total_garantias = cursor.fetchone()[0]
        print(f"📈 Total de garantias no banco: {total_garantias}")
        
        # Mostrar últimas 5 garantias
        print("\n📋 Últimas 5 garantias cadastradas:")
        cursor.execute("""
            SELECT id, lote_fabricacao, data_instalacao, data_cadastro
            FROM garantias 
            ORDER BY data_cadastro DESC 
            LIMIT 5
        """)
        
        ultimas = cursor.fetchall()
        for garantia in ultimas:
            try:
                data_inst = datetime.fromisoformat(garantia[2]).date()
                hoje = datetime.now().date()
                dias = (hoje - data_inst).days
                print(f"   - ID {garantia[0]}: {garantia[1]} ({dias} dias atrás)")
            except:
                print(f"   - ID {garantia[0]}: {garantia[1]} (data inválida)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    verificar_garantias()