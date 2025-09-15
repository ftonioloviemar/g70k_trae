#!/usr/bin/env python3
"""
Script para diagnosticar problemas com chaves estrangeiras na tabela veículos
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def diagnose_foreign_keys():
    """Diagnostica problemas com chaves estrangeiras"""
    
    # Caminho do banco de dados
    db_path = Path("viemar_garantia.db")
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 DIAGNÓSTICO DE CHAVES ESTRANGEIRAS\n")
        print("=" * 60)
        
        # 1. Verificar estrutura da tabela usuarios
        print("\n📋 1. ESTRUTURA DA TABELA USUARIOS:")
        cursor.execute("PRAGMA table_info(usuarios)")
        usuarios_schema = cursor.fetchall()
        for col in usuarios_schema:
            print(f"  {col[1]} {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]})")
        
        # 2. Verificar estrutura da tabela veiculos
        print("\n📋 2. ESTRUTURA DA TABELA VEICULOS:")
        cursor.execute("PRAGMA table_info(veiculos)")
        veiculos_schema = cursor.fetchall()
        for col in veiculos_schema:
            print(f"  {col[1]} {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]})")
        
        # 3. Verificar chaves estrangeiras
        print("\n🔗 3. CHAVES ESTRANGEIRAS DA TABELA VEICULOS:")
        cursor.execute("PRAGMA foreign_key_list(veiculos)")
        foreign_keys = cursor.fetchall()
        if foreign_keys:
            for fk in foreign_keys:
                print(f"  Coluna: {fk[3]} -> Tabela: {fk[2]}.{fk[4]}")
        else:
            print("  ❌ Nenhuma chave estrangeira encontrada!")
        
        # 4. Verificar se foreign keys estão habilitadas
        print("\n⚙️ 4. STATUS DAS FOREIGN KEYS:")
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"  Foreign Keys habilitadas: {'✅ Sim' if fk_status else '❌ Não'}")
        
        # 5. Listar todos os usuários
        print("\n👥 5. USUÁRIOS NO BANCO:")
        cursor.execute("SELECT id, email, nome, tipo_usuario, confirmado FROM usuarios ORDER BY id")
        usuarios = cursor.fetchall()
        if usuarios:
            for user in usuarios:
                status = "✅ Confirmado" if user[4] else "❌ Não confirmado"
                print(f"  ID: {user[0]} | Email: {user[1]} | Nome: {user[2]} | Tipo: {user[3]} | {status}")
        else:
            print("  ❌ Nenhum usuário encontrado!")
        
        # 6. Listar todos os veículos
        print("\n🚗 6. VEÍCULOS NO BANCO:")
        cursor.execute("""
            SELECT v.id, v.usuario_id, v.marca, v.modelo, v.placa, v.ativo, u.email
            FROM veiculos v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            ORDER BY v.id
        """)
        veiculos = cursor.fetchall()
        if veiculos:
            for veiculo in veiculos:
                status = "✅ Ativo" if veiculo[5] else "❌ Inativo"
                email = veiculo[6] if veiculo[6] else "❌ USUÁRIO NÃO ENCONTRADO"
                print(f"  ID: {veiculo[0]} | Usuario ID: {veiculo[1]} | {veiculo[2]} {veiculo[3]} | Placa: {veiculo[4]} | {status} | Email: {email}")
        else:
            print("  ❌ Nenhum veículo encontrado!")
        
        # 7. Verificar veículos órfãos (sem usuário válido)
        print("\n🔍 7. VEÍCULOS ÓRFÃOS (sem usuário válido):")
        cursor.execute("""
            SELECT v.id, v.usuario_id, v.marca, v.modelo, v.placa
            FROM veiculos v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE u.id IS NULL
        """)
        orfaos = cursor.fetchall()
        if orfaos:
            print("  ❌ ENCONTRADOS VEÍCULOS ÓRFÃOS:")
            for orfao in orfaos:
                print(f"    Veículo ID: {orfao[0]} | Usuario ID inexistente: {orfao[1]} | {orfao[2]} {orfao[3]} | Placa: {orfao[4]}")
        else:
            print("  ✅ Nenhum veículo órfão encontrado")
        
        # 8. Verificar veículos do sergio@reis.com especificamente
        print("\n🎯 8. VEÍCULOS DO SERGIO@REIS.COM:")
        cursor.execute("""
            SELECT u.id, u.email, u.confirmado
            FROM usuarios u
            WHERE u.email = 'sergio@reis.com'
        """)
        sergio_user = cursor.fetchone()
        
        if sergio_user:
            sergio_id, sergio_email, confirmado = sergio_user
            status = "✅ Confirmado" if confirmado else "❌ Não confirmado"
            print(f"  Usuário encontrado: ID {sergio_id} | {sergio_email} | {status}")
            
            # Buscar veículos do Sergio
            cursor.execute("""
                SELECT id, marca, modelo, placa, ativo, data_cadastro
                FROM veiculos
                WHERE usuario_id = ?
                ORDER BY data_cadastro DESC
            """, (sergio_id,))
            sergio_veiculos = cursor.fetchall()
            
            if sergio_veiculos:
                print(f"  ✅ Encontrados {len(sergio_veiculos)} veículo(s):")
                for veiculo in sergio_veiculos:
                    status = "✅ Ativo" if veiculo[4] else "❌ Inativo"
                    print(f"    ID: {veiculo[0]} | {veiculo[1]} {veiculo[2]} | Placa: {veiculo[3]} | {status} | Cadastro: {veiculo[5]}")
            else:
                print("  ❌ Nenhum veículo encontrado para sergio@reis.com")
        else:
            print("  ❌ Usuário sergio@reis.com não encontrado!")
        
        # 9. Testar integridade referencial
        print("\n🧪 9. TESTE DE INTEGRIDADE REFERENCIAL:")
        cursor.execute("PRAGMA foreign_key_check")
        integrity_errors = cursor.fetchall()
        if integrity_errors:
            print("  ❌ ERROS DE INTEGRIDADE ENCONTRADOS:")
            for error in integrity_errors:
                print(f"    Tabela: {error[0]} | Linha: {error[1]} | Referência: {error[2]} | FK: {error[3]}")
        else:
            print("  ✅ Integridade referencial OK")
        
        # 10. Verificar se há problemas com tipos de dados
        print("\n🔢 10. VERIFICAÇÃO DE TIPOS DE DADOS:")
        cursor.execute("""
            SELECT v.id, v.usuario_id, typeof(v.usuario_id) as tipo_usuario_id,
                   u.id as user_real_id, typeof(u.id) as tipo_user_id
            FROM veiculos v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            LIMIT 5
        """)
        tipo_dados = cursor.fetchall()
        if tipo_dados:
            print("  Amostra de tipos de dados:")
            for row in tipo_dados:
                print(f"    Veículo ID: {row[0]} | usuario_id: {row[1]} ({row[2]}) | user.id: {row[3]} ({row[4] if row[4] else 'NULL'})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def fix_foreign_key_issues():
    """Corrige problemas com chaves estrangeiras"""
    
    db_path = Path("viemar_garantia.db")
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔧 CORRIGINDO PROBLEMAS DE CHAVES ESTRANGEIRAS...\n")
        
        # 1. Habilitar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        print("✅ Foreign keys habilitadas")
        
        # 2. Verificar e corrigir veículos órfãos
        cursor.execute("""
            SELECT v.id, v.usuario_id, v.marca, v.modelo, v.placa
            FROM veiculos v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE u.id IS NULL
        """)
        orfaos = cursor.fetchall()
        
        if orfaos:
            print(f"❌ Encontrados {len(orfaos)} veículos órfãos. Removendo...")
            for orfao in orfaos:
                cursor.execute("DELETE FROM veiculos WHERE id = ?", (orfao[0],))
                print(f"  Removido: Veículo ID {orfao[0]} (usuario_id inexistente: {orfao[1]})")
        else:
            print("✅ Nenhum veículo órfão encontrado")
        
        # 3. Verificar se sergio@reis.com existe
        cursor.execute("SELECT id FROM usuarios WHERE email = 'sergio@reis.com'")
        sergio = cursor.fetchone()
        
        if not sergio:
            print("❌ Usuário sergio@reis.com não encontrado. Será criado pelo script fix_user_credentials.py")
        else:
            print(f"✅ Usuário sergio@reis.com encontrado (ID: {sergio[0]})")
        
        conn.commit()
        print("\n✅ Correções aplicadas com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir problemas: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE CHAVES ESTRANGEIRAS - TABELA VEÍCULOS\n")
    
    # Executar diagnóstico
    success = diagnose_foreign_keys()
    
    if success:
        print("\n" + "=" * 60)
        resposta = input("\n🤔 Deseja tentar corrigir os problemas encontrados? (s/N): ")
        
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            fix_foreign_key_issues()
        else:
            print("\n📝 Para corrigir manualmente, execute:")
            print("   1. uv run fix_user_credentials.py")
            print("   2. Verifique se os usuários existem antes de cadastrar veículos")
    
    print("\n✨ Diagnóstico concluído!")