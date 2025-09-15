#!/usr/bin/env python3
"""
Script para verificar e corrigir credenciais dos usuários padrão
"""

import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime

def fix_user_credentials():
    """Verifica e corrige as credenciais dos usuários padrão"""
    
    # Caminho do banco de dados
    db_path = Path("viemar_garantia.db")
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando usuários padrão...\n")
        
        # Usuários padrão e suas senhas
        usuarios_padrao = [
            {
                'email': 'ftoniolo@viemar.com.br',
                'senha': 'abc123',
                'nome': 'Administrador Viemar',
                'tipo': 'administrador'
            },
            {
                'email': 'sergio@reis.com',
                'senha': '123456',
                'nome': 'Sergio Reis',
                'tipo': 'cliente'
            }
        ]
        
        for usuario_info in usuarios_padrao:
            email = usuario_info['email']
            senha = usuario_info['senha']
            nome = usuario_info['nome']
            tipo = usuario_info['tipo']
            
            print(f"📧 Verificando usuário: {email}")
            
            # Verificar se o usuário existe
            cursor.execute(
                "SELECT id, email, nome, tipo_usuario, confirmado FROM usuarios WHERE email = ?",
                (email,)
            )
            user = cursor.fetchone()
            
            if user:
                user_id, user_email, user_nome, user_tipo, confirmado = user
                print(f"  ✅ Usuário encontrado: {user_email} (ID: {user_id})")
                print(f"  📝 Nome: {user_nome}")
                print(f"  👤 Tipo: {user_tipo}")
                print(f"  ✔️ Confirmado: {'Sim' if confirmado else 'Não'}")
                
                # Gerar nova senha hash
                senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
                
                # Atualizar a senha e confirmar o usuário
                cursor.execute(
                    "UPDATE usuarios SET senha_hash = ?, confirmado = TRUE WHERE id = ?",
                    (senha_hash.decode('utf-8'), user_id)
                )
                
                print(f"  🔑 Senha atualizada para: {senha}")
                print(f"  ✅ Usuário confirmado")
                
            else:
                print(f"  ❌ Usuário não encontrado, criando...")
                
                # Criar o usuário
                senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
                
                cursor.execute("""
                    INSERT INTO usuarios (
                        email, senha_hash, nome, tipo_usuario, confirmado, data_cadastro
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    email,
                    senha_hash.decode('utf-8'),
                    nome,
                    tipo,
                    True,
                    datetime.now().isoformat()
                ))
                
                print(f"  ✅ Usuário criado com sucesso")
                print(f"  📝 Nome: {nome}")
                print(f"  👤 Tipo: {tipo}")
                print(f"  🔑 Senha: {senha}")
            
            print()
        
        conn.commit()
        
        print("🎉 Credenciais verificadas e corrigidas com sucesso!\n")
        
        # Mostrar resumo das credenciais
        print("📋 CREDENCIAIS ATUALIZADAS:")
        print("=" * 50)
        for usuario_info in usuarios_padrao:
            print(f"Email: {usuario_info['email']}")
            print(f"Senha: {usuario_info['senha']}")
            print(f"Tipo: {usuario_info['tipo']}")
            print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir credenciais: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def verificar_login(email: str, senha: str):
    """Testa o login de um usuário"""
    
    db_path = Path("viemar_garantia.db")
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar usuário
        cursor.execute(
            "SELECT id, email, senha_hash, confirmado FROM usuarios WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuário {email} não encontrado")
            return False
        
        user_id, user_email, senha_hash, confirmado = user
        
        if not confirmado:
            print(f"❌ Usuário {email} não confirmado")
            return False
        
        # Verificar senha
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
            print(f"✅ Login bem-sucedido para {email}")
            return True
        else:
            print(f"❌ Senha incorreta para {email}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar login: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔧 Corrigindo credenciais dos usuários padrão...\n")
    
    success = fix_user_credentials()
    
    if success:
        print("\n🧪 Testando logins...\n")
        
        # Testar logins
        verificar_login('ftoniolo@viemar.com.br', 'abc123')
        verificar_login('sergio@reis.com', '123456')
        
        print("\n✨ Processo concluído!")
    else:
        print("\n❌ Falha ao corrigir credenciais")