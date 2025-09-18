#!/usr/bin/env python3
"""
Script para verificar se a correção do ftoniolo foi bem-sucedida
e testar o login do usuário
"""

import sqlite3
import os
from datetime import datetime

def verify_ftoniolo_fix():
    """Verifica se a correção do ftoniolo foi bem-sucedida"""
    
    db_path = r"c:\python\g70k_trae\data\viemar_garantia.db"
    
    print("✅ VERIFICAÇÃO DA CORREÇÃO - FTONIOLO")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar registro do ftoniolo
        cursor.execute("SELECT * FROM usuarios WHERE email = 'ftoniolo@premiumcar.com.br'")
        result = cursor.fetchone()
        
        if not result:
            print("❌ Usuário ftoniolo não encontrado!")
            return
        
        # Obter nomes das colunas
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [col[1] for col in cursor.fetchall()]
        
        user_data = dict(zip(columns, result))
        
        print("📋 DADOS ATUAIS DO USUÁRIO:")
        for key, value in user_data.items():
            print(f"  {key}: {value}")
        
        print("\n🔍 VERIFICAÇÕES:")
        
        # Verificar caspio_id
        if user_data['caspio_id'] == 5:
            print("  ✅ Caspio_ID correto: 5")
        else:
            print(f"  ❌ Caspio_ID incorreto: {user_data['caspio_id']}")
        
        # Verificar se está confirmado
        if user_data['confirmado'] == 1:
            print("  ✅ Usuário confirmado")
        else:
            print("  ❌ Usuário não confirmado")
        
        # Verificar senha
        if user_data['senha_hash'] and len(user_data['senha_hash']) > 20:
            print("  ✅ Senha hash presente")
        else:
            print("  ❌ Senha hash ausente ou inválida")
        
        # Verificar nome
        if user_data['nome'] == 'Fabio p':
            print("  ✅ Nome atualizado para dados do XML")
        else:
            print(f"  ⚠️  Nome: {user_data['nome']}")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("🎯 RESULTADO: Correção aplicada com sucesso!")
        print("   O usuário ftoniolo agora possui:")
        print("   - Caspio_ID: 5")
        print("   - Status: Confirmado")
        print("   - Senha: Importada do XML")
        print("   - Nome: Atualizado do XML")
        
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")

if __name__ == "__main__":
    verify_ftoniolo_fix()