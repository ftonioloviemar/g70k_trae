#!/usr/bin/env python3
"""Script para criar usuário de teste não confirmado"""

import bcrypt
from fastlite import Database
from app.database import init_database

def main():
    # Inicializar banco
    db = Database('g70k.db')
    init_database(db)
    
    # Remover usuário se existir
    db.execute('DELETE FROM usuarios WHERE email = ?', ('naoconfirmado@teste.com',))
    
    # Criar usuário não confirmado
    senha_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.execute(
        'INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, confirmado) VALUES (?, ?, ?, ?, ?)',
        ('Usuario Nao Confirmado', 'naoconfirmado@teste.com', senha_hash, 'cliente', False)
    )
    
    print('Usuário de teste criado:')
    print('Email: naoconfirmado@teste.com')
    print('Senha: 123456')
    print('Confirmado: False')
    
    # Verificar se foi criado
    user = db.execute('SELECT id, nome, email, confirmado FROM usuarios WHERE email = ?', ('naoconfirmado@teste.com',)).fetchone()
    if user:
        print(f'Usuário encontrado no banco: ID={user[0]}, Nome={user[1]}, Email={user[2]}, Confirmado={user[3]}')
    else:
        print('ERRO: Usuário não foi criado!')
    
    db.close()

if __name__ == '__main__':
    main()