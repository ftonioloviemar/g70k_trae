#!/usr/bin/env python3
"""
Serviço de integração com ERP Tecnicon
"""

import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

try:
    import firebird.driver as fb
except ImportError:
    raise ImportError("firebird-driver não está instalado. Execute: uv add firebird-driver")

from ..config import Config
# Removido import incorreto de get_db
from models.produto import Produto

logger = logging.getLogger(__name__)

class FirebirdService:
    """
    Serviço para conectar e sincronizar dados com o ERP Tecnicon
    """
    
    def __init__(self, config: Config):
        """
        Inicializa o serviço com as configurações do Firebird
        
        Args:
            config: Instância da configuração da aplicação
        """
        self.config = config
        self._connection_string = self._build_connection_string()
        
    def _build_connection_string(self) -> str:
        """
        Constrói a string de conexão com o Firebird
        
        Returns:
            String de conexão formatada
        """
        return (
            f"firebird://{self.config.FIREBIRD_USER}:{self.config.FIREBIRD_PASSWORD}@"
            f"{self.config.FIREBIRD_HOST}/{self.config.FIREBIRD_DATABASE}"
            f"?role={self.config.FIREBIRD_ROLE}&charset={self.config.FIREBIRD_CHARSET}"
        )
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para conexão com Firebird
        
        Yields:
            Conexão ativa com o Firebird
        """
        connection = None
        try:
            logger.info("Conectando ao ERP Tecnicon...")
            # Usar string de conexão completa ou configurar servidor
            dsn = f"{self.config.FIREBIRD_HOST}:{self.config.FIREBIRD_DATABASE}"
            
            # Configurações de conexão com tratamento de charset
            connection_params = {
                'database': dsn,
                'user': self.config.FIREBIRD_USER,
                'password': self.config.FIREBIRD_PASSWORD,
                'role': self.config.FIREBIRD_ROLE,
                'charset': 'ISO8859_1'  # Encoding correto para Firebird
            }
            
            logger.info(f"Conectando com charset: {self.config.FIREBIRD_CHARSET}")
            connection = fb.connect(**connection_params)
            logger.info("Conexão com Firebird estabelecida com sucesso")
            yield connection
        except Exception as e:
            logger.error(f"Erro ao conectar com Firebird: {e}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                    logger.info("Conexão com Firebird fechada")
                except Exception as e:
                    logger.error(f"Erro ao fechar conexão com Firebird: {e}")
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o Firebird
        
        Returns:
            True se a conexão foi bem-sucedida, False caso contrário
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM RDB$DATABASE")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Teste de conexão falhou: {e}")
            return False
    
    def get_produtos_erp(self) -> List[Dict[str, Any]]:
        """
        Busca produtos do ERP Tecnicon
        
        Returns:
            Lista de dicionários com os dados dos produtos
        """
        query = """
        SELECT 
            PRODUTO.REF_FORNECE, 
            PRODUTO.DESCRICAO 
        FROM 
            PRODUTO 
        WHERE 
            PRODUTO.CGRUPO = 48 
            AND PRODUTO.ATIVO = 'S' 
            AND PRODUTO.CSUBGRUPO IN (11938, 48, 17, 116, 12836)
        """
        
        produtos = []
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                for row in cursor.fetchall():
                    try:
                        # Garantir que os dados sejam tratados como UTF-8
                        sku = row[0].strip() if row[0] else ''
                        descricao = row[1].strip() if row[1] else ''
                        
                        # Se os dados vierem como bytes, decodificar com ISO8859_1
                        if isinstance(sku, bytes):
                            sku = sku.decode('iso8859-1', errors='replace')
                        if isinstance(descricao, bytes):
                            descricao = descricao.decode('iso8859-1', errors='replace')
                        
                        produto = {
                            'sku': sku,
                            'descricao': descricao
                        }
                        produtos.append(produto)
                    except UnicodeDecodeError as e:
                        logger.warning(f"Erro de encoding no produto {row}: {e}")
                        # Tentar com latin-1 como fallback
                        try:
                            sku = row[0].decode('latin-1') if isinstance(row[0], bytes) else str(row[0]).strip()
                            descricao = row[1].decode('latin-1') if isinstance(row[1], bytes) else str(row[1]).strip()
                            produto = {
                                'sku': sku,
                                'descricao': descricao
                            }
                            produtos.append(produto)
                        except Exception as fallback_error:
                            logger.error(f"Erro ao processar produto com fallback {row}: {fallback_error}")
                            continue
                    
                logger.info(f"Encontrados {len(produtos)} produtos no ERP")
                return produtos
                
        except Exception as e:
            logger.error(f"Erro ao buscar produtos do ERP: {e}")
            raise
    
    def sync_produtos(self, db) -> Dict[str, int]:
        """
        Sincroniza produtos do ERP com o sistema local
        
        Args:
            db: Instância do banco de dados SQLite
            
        Returns:
            Dicionário com estatísticas da sincronização
        """
        stats = {
            'total_erp': 0,
            'inseridos': 0,
            'atualizados': 0,
            'inalterados': 0,
            'erros': 0
        }
        
        try:
            # Busca produtos do ERP
            produtos_erp = self.get_produtos_erp()
            stats['total_erp'] = len(produtos_erp)
            
            if not produtos_erp:
                logger.warning("Nenhum produto encontrado no ERP")
                return stats
            
            # Usa o banco de dados passado como parâmetro
            
            for produto_erp in produtos_erp:
                try:
                    sku = produto_erp['sku']
                    descricao = produto_erp['descricao']
                    
                    if not sku or not descricao:
                        logger.warning(f"Produto com dados incompletos ignorado: {produto_erp}")
                        stats['erros'] += 1
                        continue
                    
                    # Verifica se o produto já existe
                    produto_existente = db.execute(
                        "SELECT id, descricao FROM produtos WHERE sku = ?",
                        (sku,)
                    ).fetchone()
                    
                    if produto_existente:
                        # Produto existe - verifica se precisa atualizar
                        # produto_existente é uma tupla: (id, descricao)
                        descricao_existente = produto_existente[1] if len(produto_existente) > 1 else ''
                        if descricao_existente != descricao:
                            db.execute(
                                "UPDATE produtos SET descricao = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE sku = ?",
                                (descricao, sku)
                            )
                            stats['atualizados'] += 1
                            logger.info(f"Produto atualizado: {sku} - {descricao}")
                        else:
                            stats['inalterados'] += 1
                    else:
                        # Produto não existe - insere novo
                        db.execute(
                            "INSERT INTO produtos (sku, descricao, data_cadastro, data_atualizacao) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                            (sku, descricao)
                        )
                        stats['inseridos'] += 1
                        logger.info(f"Produto inserido: {sku} - {descricao}")
                        
                except Exception as e:
                    logger.error(f"Erro ao processar produto {produto_erp}: {e}")
                    stats['erros'] += 1
            
            # As alterações são commitadas automaticamente pelo fastlite
            
            logger.info(f"Sincronização concluída: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Erro durante sincronização: {e}")
            stats['erros'] += 1
            raise

# Instância global do serviço
_firebird_service: Optional[FirebirdService] = None

def get_firebird_service(config: Optional[Config] = None) -> FirebirdService:
    """
    Retorna a instância do serviço Firebird (singleton)
    
    Args:
        config: Configuração da aplicação (opcional)
        
    Returns:
        Instância do FirebirdService
    """
    global _firebird_service
    
    if _firebird_service is None:
        if config is None:
            from ..config import Config
            config = Config()
        _firebird_service = FirebirdService(config)
    
    return _firebird_service