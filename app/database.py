#!/usr/bin/env python3
"""
Inicialização e configuração do banco de dados SQLite
"""

import logging
from datetime import datetime
from fastlite import Database
from models.usuario import Usuario
from models.produto import Produto
from models.veiculo import Veiculo
from models.garantia import Garantia
from app.date_utils import format_datetime_iso

logger = logging.getLogger(__name__)

def init_database(db: Database):
    """Inicializa o banco de dados com as tabelas necessárias"""
    
    logger.info("Inicializando banco de dados...")
    
    # Criar tabela de usuários
    db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            nome TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL DEFAULT 'cliente',
            confirmado BOOLEAN DEFAULT FALSE,
            email_enviado BOOLEAN DEFAULT FALSE,
            cep TEXT,
            endereco TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT,
            telefone TEXT,
            cpf_cnpj TEXT,
            data_nascimento DATETIME,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            token_confirmacao TEXT,
            token_reset_senha TEXT,
            CONSTRAINT chk_tipo_usuario CHECK (tipo_usuario IN ('cliente', 'administrador'))
        )
    """)
    
    # Adicionar coluna email_enviado se não existir (para bancos existentes)
    try:
        db.execute("ALTER TABLE usuarios ADD COLUMN email_enviado BOOLEAN DEFAULT FALSE")
        logger.info("Coluna email_enviado adicionada à tabela usuarios")
    except Exception:
        # Coluna já existe, ignorar erro
        pass
    
    # Criar tabela de produtos
    db.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            descricao TEXT,
            ativo BOOLEAN DEFAULT TRUE,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao DATETIME
        )
    """)
    
    # Criar tabela de veículos
    db.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            ano_modelo TEXT,
            placa TEXT NOT NULL,
            chassi TEXT,
            cor TEXT,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao DATETIME,
            ativo BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)
    
    # Criar tabela de garantias
    db.execute("""
        CREATE TABLE IF NOT EXISTS garantias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            veiculo_id INTEGER NOT NULL,
            lote_fabricacao TEXT NOT NULL,
            data_instalacao DATETIME NOT NULL,
            nota_fiscal TEXT NOT NULL,
            nome_estabelecimento TEXT NOT NULL,
            quilometragem INTEGER NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_vencimento DATETIME,
            ativo BOOLEAN DEFAULT TRUE,
            observacoes TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
        )
    """)
    
    # Criar índices para melhor performance
    db.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios (email)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios (tipo_usuario)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_produtos_sku ON produtos (sku)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_veiculos_usuario ON veiculos (usuario_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_garantias_usuario ON garantias (usuario_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_garantias_produto ON garantias (produto_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_garantias_veiculo ON garantias (veiculo_id)")
    
    # Criar usuário administrador padrão se não existir
    criar_admin_padrao(db)
    
    logger.info("Banco de dados inicializado com sucesso")

def criar_admin_padrao(db: Database):
    """Cria o usuário administrador padrão se não existir"""
    
    admin_email = 'ftoniolo@viemar.com.br'
    
    # Verificar se o admin já existe
    admin_existente = db.execute(
        "SELECT id FROM usuarios WHERE email = ? AND tipo_usuario = 'administrador'",
        (admin_email,)
    ).fetchone()
    
    if not admin_existente:
        # Criar usuário administrador
        admin = Usuario(
            email=admin_email,
            senha_hash=Usuario.criar_hash_senha('abc123'),
            nome='Administrador Viemar',
            tipo_usuario='administrador',
            confirmado=True,
            data_cadastro=datetime.now()
        )
        
        db.execute("""
            INSERT INTO usuarios (
                email, senha_hash, nome, tipo_usuario, confirmado, data_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            admin.email,
            admin.senha_hash,
            admin.nome,
            admin.tipo_usuario,
            admin.confirmado,
            format_datetime_iso(admin.data_cadastro) if admin.data_cadastro else None
        ))
        
        logger.info(f"Usuário administrador criado: {admin_email}")
    else:
        logger.info("Usuário administrador já existe")

def migrar_dados_caspio(db: Database, dados_caspio: dict):
    """Migra dados da aplicação antiga do Caspio"""
    
    logger.info("Iniciando migração de dados do Caspio...")
    
    # Migrar clientes para usuários
    if 'clientes' in dados_caspio:
        for cliente_data in dados_caspio['clientes']:
            try:
                # Converter cliente para usuário
                usuario = Usuario(
                    email=cliente_data.get('EMAIL', ''),
                    senha_hash=Usuario.migrar_senha_caspio(cliente_data.get('SENHA', '')),
                    nome=cliente_data.get('NOME', ''),
                    tipo_usuario='cliente',
                    confirmado=cliente_data.get('EMAIL_CONFIRMADO', False),
                    cep=cliente_data.get('CEP', ''),
                    endereco=cliente_data.get('ENDERECO', ''),
                    bairro=cliente_data.get('BAIRRO', ''),
                    cidade=cliente_data.get('CIDADE', ''),
                    uf=cliente_data.get('UF', ''),
                    telefone=cliente_data.get('TELEFONE', ''),
                    cpf_cnpj=str(cliente_data.get('CPF_CNPJ', '')),
                    data_nascimento=cliente_data.get('DATA_NASCIMENTO'),
                    data_cadastro=cliente_data.get('DATA_CADASTRO')
                )
                
                # Inserir no banco
                db.execute("""
                    INSERT OR IGNORE INTO usuarios (
                        email, senha_hash, nome, tipo_usuario, confirmado,
                        cep, endereco, bairro, cidade, uf, telefone, cpf_cnpj,
                        data_nascimento, data_cadastro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    usuario.email, usuario.senha_hash, usuario.nome, usuario.tipo_usuario,
                    usuario.confirmado, usuario.cep, usuario.endereco, usuario.bairro,
                    usuario.cidade, usuario.uf, usuario.telefone, usuario.cpf_cnpj,
                    usuario.data_nascimento, usuario.data_cadastro
                ))
                
            except Exception as e:
                logger.error(f"Erro ao migrar cliente {cliente_data.get('EMAIL', 'N/A')}: {e}")
    
    # Migrar produtos válidos
    if 'produtos_validos' in dados_caspio:
        for produto_data in dados_caspio['produtos_validos']:
            try:
                produto = Produto(
                    sku=produto_data.get('SKU', ''),
                    descricao=produto_data.get('DESCRICAO', ''),
                    ativo=produto_data.get('ATIVO', True),
                    data_cadastro=produto_data.get('DATA_CADASTRO')
                )
                
                db.execute("""
                    INSERT OR IGNORE INTO produtos (sku, descricao, ativo, data_cadastro)
                    VALUES (?, ?, ?, ?)
                """, (produto.sku, produto.descricao, produto.ativo, produto.data_cadastro))
                
            except Exception as e:
                logger.error(f"Erro ao migrar produto {produto_data.get('SKU', 'N/A')}: {e}")
    
    logger.info("Migração de dados do Caspio concluída")

def get_database_stats(db: Database) -> dict:
    """Retorna estatísticas do banco de dados"""
    
    stats = {}
    
    # Contar registros em cada tabela
    tabelas = ['usuarios', 'produtos', 'veiculos', 'garantias']
    
    for tabela in tabelas:
        try:
            result = db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()
            stats[f'total_{tabela}'] = result[0] if result else 0
        except Exception as e:
            logger.error(f"Erro ao contar registros da tabela {tabela}: {e}")
            stats[f'total_{tabela}'] = 0
    
    # Estatísticas específicas
    try:
        # Usuários por tipo
        result = db.execute("""
            SELECT tipo_usuario, COUNT(*) 
            FROM usuarios 
            GROUP BY tipo_usuario
        """).fetchall()
        stats['usuarios_por_tipo'] = {row[0]: row[1] for row in result}
        
        # Garantias ativas
        result = db.execute("""
            SELECT COUNT(*) FROM garantias WHERE ativo = TRUE
        """).fetchone()
        stats['garantias_ativas'] = result[0] if result else 0
        
        # Produtos ativos
        result = db.execute("""
            SELECT COUNT(*) FROM produtos WHERE ativo = TRUE
        """).fetchone()
        stats['produtos_ativos'] = result[0] if result else 0
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {e}")
    
    return stats