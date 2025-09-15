#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar diretamente a função listar_veiculos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastlite import Database
from pathlib import Path

def test_listar_veiculos():
    """Testa a função listar_veiculos diretamente"""
    
    db_path = Path("viemar_garantia.db")
    
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        # Conectar ao banco usando fastlite
        db = Database(db_path)
        
        print("🔍 Testando função listar_veiculos...")
        
        # Simular usuário sergio@reis.com
        user = {
            'usuario_id': 2,
            'email': 'sergio@reis.com',
            'nome': 'Sergio Reis',
            'tipo_usuario': 'cliente'
        }
        
        print(f"👤 Usuário simulado: {user}")
        
        # Executar a mesma consulta da função listar_veiculos
        print("\n🔍 Executando consulta da função listar_veiculos:")
        
        veiculos = db.execute("""
            SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
            FROM veiculos 
            WHERE usuario_id = ? 
            ORDER BY data_cadastro DESC
        """, (user['usuario_id'],)).fetchall()
        
        print(f"✅ Consulta retornou {len(veiculos)} veículo(s):")
        
        for i, v in enumerate(veiculos, 1):
            print(f"   {i}. ID: {v[0]}, {v[1]} {v[2]} {v[3]}, Placa: {v[4]}, Ativo: {v[8]}")
        
        # Simular processamento dos dados para a tabela
        print("\n🔍 Simulando processamento para tabela HTML:")
        
        dados_tabela = []
        for v in veiculos:
            status = "Ativo" if v[8] else "Inativo"
            status_class = "success" if v[8] else "secondary"
            
            # Simular formatação da placa (função Veiculo.formatar_placa_estatico)
            placa_formatada = v[4]  # Assumindo que já está formatada
            if len(v[4]) == 7 and v[4].isalnum():
                placa_formatada = f"{v[4][:3]}-{v[4][3:]}"
            
            dados_tabela.append([
                f"{v[1]} {v[2]}",  # Marca Modelo
                str(v[3]),  # Ano
                placa_formatada,  # Placa formatada
                v[5] or "N/A",  # Cor
                f"Badge: {status} ({status_class})",
                f"Ações para ID {v[0]}"
            ])
        
        print(f"✅ Dados processados para tabela ({len(dados_tabela)} linhas):")
        for i, linha in enumerate(dados_tabela, 1):
            print(f"   {i}. {linha}")
        
        # Verificar se há algum problema específico
        print("\n🔍 Verificações adicionais:")
        
        # Verificar se todos os veículos estão ativos
        ativos = [v for v in veiculos if v[8] == 1]
        print(f"   - Veículos ativos: {len(ativos)}/{len(veiculos)}")
        
        # Verificar se há campos None/NULL problemáticos
        problematicos = []
        for v in veiculos:
            if not v[1] or not v[2] or not v[4]:  # marca, modelo, placa
                problematicos.append(v[0])
        
        if problematicos:
            print(f"   ⚠️ Veículos com campos problemáticos: {problematicos}")
        else:
            print(f"   ✅ Todos os veículos têm campos obrigatórios preenchidos")
        
        # Verificar ordenação
        print(f"   - Ordenação por data_cadastro DESC:")
        for i, v in enumerate(veiculos, 1):
            print(f"     {i}. ID {v[0]}: {v[7]}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao testar função: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    test_listar_veiculos()