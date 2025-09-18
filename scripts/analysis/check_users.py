#!/usr/bin/env python3
"""Script para verificar usuários no banco de dados G70K"""

import sqlite3
import os

def check_users():
    """Verifica usuários específicos no banco de dados"""
    db_path = r'c:\python\g70k_trae\data\viemar_garantia.db'
    
    if not os.path.exists(db_path):
        print('Banco de dados não encontrado!')
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Procurar por ftoniolo
        cursor = conn.execute('SELECT * FROM usuarios WHERE email LIKE ?', ('%ftoniolo%',))
        ftoniolo_users = cursor.fetchall()
        
        print('Usuários com "ftoniolo" no email:')
        if ftoniolo_users:
            for user in ftoniolo_users:
                print(f'  ID: {user["id"]}, Email: {user["email"]}, Caspio ID: {user["caspio_id"]}, Nome: {user["nome"]}')
        else:
            print('  Nenhum usuário encontrado')
        
        # Procurar por premiumcar
        cursor = conn.execute('SELECT * FROM usuarios WHERE email LIKE ?', ('%premiumcar%',))
        premiumcar_users = cursor.fetchall()
        
        print('\nUsuários com "premiumcar" no email:')
        if premiumcar_users:
            for user in premiumcar_users:
                print(f'  ID: {user["id"]}, Email: {user["email"]}, Caspio ID: {user["caspio_id"]}, Nome: {user["nome"]}')
        else:
            print('  Nenhum usuário encontrado')
            
        # Estatísticas gerais
        cursor = conn.execute('SELECT COUNT(*) as total FROM usuarios')
        total_users = cursor.fetchone()['total']
        
        cursor = conn.execute('SELECT COUNT(*) as total FROM usuarios WHERE caspio_id IS NOT NULL')
        caspio_users = cursor.fetchone()['total']
        
        print(f'\nEstatísticas:')
        print(f'  Total de usuários: {total_users}')
        print(f'  Usuários do Caspio: {caspio_users}')
        print(f'  Percentual do Caspio: {(caspio_users/total_users*100):.1f}%')
        
    finally:
        conn.close()

if __name__ == '__main__':
    check_users()