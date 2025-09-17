#!/usr/bin/env python3
"""
Serviço de importação de dados do Caspio.

Este serviço é responsável por importar dados da aplicação antiga Caspio
mantendo compatibilidade com senhas e estrutura de dados.
"""

import xml.etree.ElementTree as ET
import json
import binascii
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class ImportStats:
    """Estatísticas de importação."""
    users_imported: int = 0
    users_skipped: int = 0
    vehicles_imported: int = 0
    vehicles_skipped: int = 0
    warranties_imported: int = 0
    warranties_skipped: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class CaspioImportService:
    """
    Serviço para importação de dados do Caspio.
    
    Este serviço importa dados da aplicação antiga Caspio mantendo
    compatibilidade com senhas e estrutura de dados existente.
    """
    
    def __init__(self, db_path: str, caspio_xml_path: str):
        """
        Inicializa o serviço de importação.
        
        Args:
            db_path: Caminho para o banco SQLite
            caspio_xml_path: Caminho para o arquivo XML do Caspio
        """
        self.db_path = db_path
        self.caspio_xml_path = caspio_xml_path
        self.stats = ImportStats()
        
    def _get_db_connection(self) -> sqlite3.Connection:
        """Obtém conexão com o banco de dados."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _decode_caspio_password(self, hex_password: str) -> Optional[str]:
        """
        Decodifica senha do Caspio em formato hexadecimal.
        
        Args:
            hex_password: Senha em formato hexadecimal do Caspio
            
        Returns:
            Hash da senha decodificada ou None se houver erro
        """
        try:
            if not hex_password or hex_password == 'None':
                return None
                
            # Remove prefixo 0x se existir
            if hex_password.startswith('0x'):
                hex_password = hex_password[2:]
            
            # Converte de hex para bytes e depois para string
            decoded_bytes = binascii.unhexlify(hex_password)
            decoded_str = decoded_bytes.decode('utf-8')
            
            # Parse do JSON
            password_data = json.loads(decoded_str)
            
            # Retorna o hash da senha
            return password_data.get('hash')
            
        except Exception as e:
            logger.warning(f"Erro ao decodificar senha: {e}")
            return None
    
    def _parse_caspio_date(self, date_str: str) -> Optional[str]:
        """
        Converte data do formato Caspio para formato SQLite.
        
        Args:
            date_str: Data no formato do Caspio
            
        Returns:
            Data no formato SQLite (YYYY-MM-DD) ou None
        """
        if not date_str or date_str == 'None':
            return None
            
        try:
            # Tenta diferentes formatos de data do Caspio
            formats = [
                '%m/%d/%Y %I:%M:%S %p',  # 11/9/2017 2:26:09 PM
                '%m/%d/%Y',              # 4/14/1962
                '%Y-%m-%d',              # 1962-04-14
                '%d/%m/%Y',              # 14/04/1962
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
            logger.warning(f"Formato de data não reconhecido: {date_str}")
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao converter data {date_str}: {e}")
            return None
    
    def _user_exists(self, conn: sqlite3.Connection, email: str, cpf_cnpj: str) -> bool:
        """
        Verifica se usuário já existe no banco.
        
        Args:
            conn: Conexão com o banco
            email: Email do usuário
            cpf_cnpj: CPF/CNPJ do usuário
            
        Returns:
            True se usuário já existe
        """
        cursor = conn.execute(
            "SELECT id FROM usuarios WHERE email = ? OR cpf_cnpj = ?",
            (email, cpf_cnpj)
        )
        return cursor.fetchone() is not None
    
    def _vehicle_exists(self, conn: sqlite3.Connection, user_id: int, placa: str) -> bool:
        """
        Verifica se veículo já existe no banco.
        
        Args:
            conn: Conexão com o banco
            user_id: ID do usuário
            placa: Placa do veículo
            
        Returns:
            True se veículo já existe
        """
        cursor = conn.execute(
            "SELECT id FROM veiculos WHERE usuario_id = ? AND placa = ?",
            (user_id, placa)
        )
        return cursor.fetchone() is not None
    
    def _get_user_id_by_caspio_id(self, conn: sqlite3.Connection, caspio_id: str) -> Optional[int]:
        """
        Obtém ID do usuário no sistema atual pelo ID do Caspio.
        
        Args:
            conn: Conexão com o banco
            caspio_id: ID do usuário no Caspio
            
        Returns:
            ID do usuário no sistema atual ou None
        """
        cursor = conn.execute(
            "SELECT id FROM usuarios WHERE caspio_id = ?",
            (caspio_id,)
        )
        row = cursor.fetchone()
        return row['id'] if row else None
    
    def import_users(self) -> int:
        """
        Importa usuários do Caspio.
        
        Returns:
            Número de usuários importados
        """
        logger.info("Iniciando importação de usuários do Caspio")
        
        try:
            tree = ET.parse(self.caspio_xml_path)
            root = tree.getroot()
            
            # Encontra a tabela CLIENTE
            cliente_table = None
            for table in root.findall('.//Table'):
                name_elem = table.find('Name')
                if name_elem is not None and name_elem.text == 'CLIENTE':
                    cliente_table = table
                    break
            
            if cliente_table is None:
                raise ValueError("Tabela CLIENTE não encontrada no XML")
            
            conn = self._get_db_connection()
            
            try:
                for row in cliente_table.findall('Row'):
                    try:
                        # Extrai dados do usuário
                        caspio_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
                        nome = row.find('NOME').text if row.find('NOME') is not None else None
                        email = row.find('EMAIL').text if row.find('EMAIL') is not None else None
                        cpf_cnpj = row.find('CPF_CNPJ').text if row.find('CPF_CNPJ') is not None else None
                        telefone = row.find('TELEFONE').text if row.find('TELEFONE') is not None else None
                        cep = row.find('CEP').text if row.find('CEP') is not None else None
                        endereco = row.find('ENDERECO').text if row.find('ENDERECO') is not None else None
                        bairro = row.find('BAIRRO').text if row.find('BAIRRO') is not None else None
                        cidade = row.find('CIDADE').text if row.find('CIDADE') is not None else None
                        uf = row.find('UF').text if row.find('UF') is not None else None
                        
                        # Processa senha
                        senha_elem = row.find('SENHA')
                        senha_hash = None
                        if senha_elem is not None and senha_elem.text:
                            senha_hash = self._decode_caspio_password(senha_elem.text)
                        
                        # Processa datas
                        data_nascimento = None
                        data_nasc_elem = row.find('DATA_NASCIMENTO')
                        if data_nasc_elem is not None and data_nasc_elem.text:
                            data_nascimento = self._parse_caspio_date(data_nasc_elem.text)
                        
                        data_cadastro = None
                        data_cad_elem = row.find('DATA_CADASTRO')
                        if data_cad_elem is not None and data_cad_elem.text:
                            data_cadastro = self._parse_caspio_date(data_cad_elem.text)
                        
                        # Validações básicas
                        if not email or not nome:
                            self.stats.users_skipped += 1
                            continue
                        
                        # Verifica se usuário já existe
                        if self._user_exists(conn, email, cpf_cnpj or ''):
                            self.stats.users_skipped += 1
                            continue
                        
                        # Insere usuário
                        cursor = conn.execute("""
                            INSERT INTO usuarios (
                                email, senha_hash, nome, cpf_cnpj, data_nascimento,
                                data_cadastro, confirmado, caspio_id, telefone,
                                cep, endereco, bairro, cidade, uf
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            email, senha_hash, nome, cpf_cnpj, data_nascimento,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), True, caspio_id,
                            telefone, cep, endereco, bairro, cidade, uf
                        ))
                        
                        self.stats.users_imported += 1
                        
                        if self.stats.users_imported % 100 == 0:
                            logger.info(f"Importados {self.stats.users_imported} usuários")
                    
                    except Exception as e:
                        error_msg = f"Erro ao importar usuário {caspio_id}: {e}"
                        logger.error(error_msg)
                        self.stats.errors.append(error_msg)
                        self.stats.users_skipped += 1
                
                conn.commit()
                
            finally:
                conn.close()
            
            logger.info(f"Importação de usuários concluída: {self.stats.users_imported} importados, {self.stats.users_skipped} ignorados")
            return self.stats.users_imported
            
        except Exception as e:
            error_msg = f"Erro na importação de usuários: {e}"
            logger.error(error_msg)
            self.stats.errors.append(error_msg)
            raise
    
    def import_vehicles(self) -> int:
        """
        Importa veículos do Caspio.
        
        Returns:
            Número de veículos importados
        """
        logger.info("Iniciando importação de veículos do Caspio")
        
        try:
            tree = ET.parse(self.caspio_xml_path)
            root = tree.getroot()
            
            # Encontra a tabela VEICULO
            veiculo_table = None
            for table in root.findall('.//Table'):
                name_elem = table.find('Name')
                if name_elem is not None and name_elem.text == 'VEICULO':
                    veiculo_table = table
                    break
            
            if veiculo_table is None:
                raise ValueError("Tabela VEICULO não encontrada no XML")
            
            conn = self._get_db_connection()
            
            try:
                for row in veiculo_table.findall('Row'):
                    try:
                        # Extrai dados do veículo
                        caspio_cliente_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
                        marca = row.find('MARCA').text if row.find('MARCA') is not None else None
                        modelo = row.find('MODELO').text if row.find('MODELO') is not None else None
                        ano_modelo = row.find('ANO_MODELO').text if row.find('ANO_MODELO') is not None else None
                        placa = row.find('PLACA').text if row.find('PLACA') is not None else None
                        
                        # Validações básicas
                        if not caspio_cliente_id or not marca or not modelo or not placa:
                            self.stats.vehicles_skipped += 1
                            continue
                        
                        # Encontra o usuário correspondente
                        user_id = self._get_user_id_by_caspio_id(conn, caspio_cliente_id)
                        if not user_id:
                            self.stats.vehicles_skipped += 1
                            continue
                        
                        # Verifica se veículo já existe
                        if self._vehicle_exists(conn, user_id, placa):
                            self.stats.vehicles_skipped += 1
                            continue
                        
                        # Processa ano/modelo - mantém como string ou None
                        processed_ano_modelo = None
                        if ano_modelo:
                            # Se contém '/', pega apenas o primeiro valor (ano)
                            if '/' in ano_modelo:
                                try:
                                    processed_ano_modelo = ano_modelo.split('/')[0].strip()
                                except:
                                    processed_ano_modelo = ano_modelo.strip()
                            else:
                                processed_ano_modelo = ano_modelo.strip()
                            
                            # Se ficou vazio após processamento, define como None
                            if not processed_ano_modelo:
                                processed_ano_modelo = None
                        
                        # Insere veículo
                        cursor = conn.execute("""
                            INSERT INTO veiculos (
                                usuario_id, marca, modelo, ano_modelo, placa, data_cadastro
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            user_id, marca, modelo, processed_ano_modelo, placa,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ))
                        
                        self.stats.vehicles_imported += 1
                        
                        if self.stats.vehicles_imported % 100 == 0:
                            logger.info(f"Importados {self.stats.vehicles_imported} veículos")
                    
                    except Exception as e:
                        error_msg = f"Erro ao importar veículo: {e}"
                        logger.error(error_msg)
                        self.stats.errors.append(error_msg)
                        self.stats.vehicles_skipped += 1
                
                conn.commit()
                
            finally:
                conn.close()
            
            logger.info(f"Importação de veículos concluída: {self.stats.vehicles_imported} importados, {self.stats.vehicles_skipped} ignorados")
            return self.stats.vehicles_imported
            
        except Exception as e:
            error_msg = f"Erro na importação de veículos: {e}"
            logger.error(error_msg)
            self.stats.errors.append(error_msg)
            raise
    
    def import_warranties(self) -> int:
        """
        Importa garantias da tabela PRODUTO_APLICADO do Caspio.

        Returns:
            Número de garantias importadas
        """
        logger.info("Iniciando importação de garantias da tabela PRODUTO_APLICADO do Caspio")
        
        try:
            tree = ET.parse(self.caspio_xml_path)
            root = tree.getroot()
            
            # Encontra a tabela PRODUTO_APLICADO
            produto_table = None
            for table in root.findall('.//Table'):
                name_elem = table.find('Name')
                if name_elem is not None and name_elem.text == 'PRODUTO_APLICADO':
                    produto_table = table
                    break
            
            if produto_table is None:
                raise ValueError("Tabela PRODUTO_APLICADO não encontrada no XML")
            
            conn = self._get_db_connection()
            
            try:
                for row in produto_table.findall('Row'):
                    try:
                        # Extrai dados da garantia da tabela PRODUTO_APLICADO
                        caspio_cliente_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
                        caspio_veiculo_id = row.find('ID_VEICULO').text if row.find('ID_VEICULO') is not None else None
                        referencia = row.find('REFERENCIA').text if row.find('REFERENCIA') is not None else None
                        lote = row.find('LOTE').text if row.find('LOTE') is not None else None
                        data_aplicacao = row.find('DATA_APLICACAO').text if row.find('DATA_APLICACAO') is not None else None
                        km_aplicacao = row.find('KM_APLICACAO').text if row.find('KM_APLICACAO') is not None else None
                        nome_oficina = row.find('NOME_OFICINA').text if row.find('NOME_OFICINA') is not None else None
                        nf_oficina = row.find('NF_OFICINA').text if row.find('NF_OFICINA') is not None else None
                        data_cadastro = row.find('DATA_CADASTRO').text if row.find('DATA_CADASTRO') is not None else None
                        
                        # Validações básicas
                        if not caspio_cliente_id or not referencia or not lote:
                            self.stats.warranties_skipped += 1
                            continue
                        
                        # Encontra o usuário correspondente pelo caspio_id
                        user_id = self._get_user_id_by_caspio_id(conn, caspio_cliente_id)
                        if not user_id:
                            self.stats.warranties_skipped += 1
                            continue
                        
                        # Encontra o veículo correspondente se ID_VEICULO estiver presente
                        vehicle_id = None
                        if caspio_veiculo_id:
                            cursor = conn.execute(
                                "SELECT id FROM veiculos WHERE caspio_veiculo_id = ?",
                                (caspio_veiculo_id,)
                            )
                            vehicle_row = cursor.fetchone()
                            if vehicle_row:
                                vehicle_id = vehicle_row['id']
                        
                        # Se não encontrou veículo pelo caspio_id, pega o primeiro veículo do usuário
                        if not vehicle_id:
                            cursor = conn.execute(
                                "SELECT id FROM veiculos WHERE usuario_id = ? LIMIT 1",
                                (user_id,)
                            )
                            vehicle_row = cursor.fetchone()
                            if vehicle_row:
                                vehicle_id = vehicle_row['id']
                        
                        # Se ainda não encontrou veículo, cria um veículo padrão
                        if not vehicle_id:
                            cursor = conn.execute("""
                                INSERT INTO veiculos (
                                    usuario_id, marca, modelo, ano_modelo, placa, cor,
                                    data_cadastro
                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                user_id, 'Não informado', 'Não informado', 2020, 'SEM-PLACA',
                                'Não informado', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            ))
                            vehicle_id = cursor.lastrowid
                        
                        # Processa data de aplicação
                        data_instalacao = self._parse_caspio_date(data_aplicacao) if data_aplicacao else None
                        if not data_instalacao:
                            data_instalacao = datetime.now().strftime('%Y-%m-%d')
                        
                        # Processa quilometragem
                        quilometragem = 0
                        if km_aplicacao:
                            try:
                                quilometragem = int(km_aplicacao.replace('.', '').replace(',', ''))
                            except ValueError:
                                quilometragem = 0
                        
                        # Busca ou cria produto baseado na referência
                        cursor = conn.execute(
                            "SELECT id FROM produtos WHERE sku = ?",
                            (referencia,)
                        )
                        produto_row = cursor.fetchone()
                        
                        if not produto_row:
                            # Cria produto se não existir
                            cursor = conn.execute(
                                "INSERT INTO produtos (sku, descricao, ativo) VALUES (?, ?, ?)",
                                (referencia, f"Produto {referencia} (importado do Caspio)", True)
                            )
                            produto_id = cursor.lastrowid
                        else:
                            produto_id = produto_row['id']
                        
                        # Verifica se garantia já existe
                        cursor = conn.execute(
                            "SELECT id FROM garantias WHERE usuario_id = ? AND lote_fabricacao = ? AND referencia_produto = ?",
                            (user_id, lote, referencia)
                        )
                        if cursor.fetchone():
                            self.stats.warranties_skipped += 1
                            continue
                        
                        # Insere garantia na tabela garantias
                        cursor = conn.execute("""
                            INSERT INTO garantias (
                                usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                data_instalacao, nota_fiscal, nome_estabelecimento, 
                                quilometragem, referencia_produto, lote_caspio, 
                                oficina_nome, oficina_nf, data_aplicacao_caspio,
                                km_aplicacao, data_cadastro, ativo
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            user_id, produto_id, vehicle_id, lote,
                            data_instalacao, nf_oficina or '', nome_oficina or '',
                            quilometragem, referencia, lote, nome_oficina, nf_oficina,
                            data_aplicacao, quilometragem,
                            self._parse_caspio_date(data_cadastro) or datetime.now().strftime('%Y-%m-%d'),
                            True
                        ))
                        
                        self.stats.warranties_imported += 1
                        
                        if self.stats.warranties_imported % 100 == 0:
                            logger.info(f"Importadas {self.stats.warranties_imported} garantias")
                    
                    except Exception as e:
                        error_msg = f"Erro ao importar garantia: {e}"
                        logger.error(error_msg)
                        self.stats.errors.append(error_msg)
                        self.stats.warranties_skipped += 1
                
                conn.commit()
                
            finally:
                conn.close()
            
            logger.info(f"Importação de garantias concluída: {self.stats.warranties_imported} importadas, {self.stats.warranties_skipped} ignoradas")
            return self.stats.warranties_imported
            
        except Exception as e:
            error_msg = f"Erro na importação de garantias: {e}"
            logger.error(error_msg)
            self.stats.errors.append(error_msg)
            raise
    
    def import_all(self) -> ImportStats:
        """
        Executa importação completa de todos os dados.
        
        Returns:
            Estatísticas da importação
        """
        logger.info("Iniciando importação completa do Caspio")
        
        try:
            # Importa usuários primeiro
            self.import_users()
            
            # Depois importa veículos (dependem dos usuários)
            self.import_vehicles()
            
            # Por último importa garantias (dependem dos usuários)
            self.import_warranties()
            
            logger.info("Importação completa concluída com sucesso")
            
        except Exception as e:
            logger.error(f"Erro na importação completa: {e}")
            raise
        
        return self.stats
    
    def get_import_summary(self) -> str:
        """
        Retorna resumo da importação.
        
        Returns:
            String com resumo da importação
        """
        summary = f"""
=== RESUMO DA IMPORTAÇÃO DO CASPIO ===

Usuários:
  - Importados: {self.stats.users_imported}
  - Ignorados: {self.stats.users_skipped}

Veículos:
  - Importados: {self.stats.vehicles_imported}
  - Ignorados: {self.stats.vehicles_skipped}

Garantias:
  - Importadas: {self.stats.warranties_imported}
  - Ignoradas: {self.stats.warranties_skipped}

Erros: {len(self.stats.errors)}
"""
        
        if self.stats.errors:
            summary += "\n\nErros encontrados:\n"
            for error in self.stats.errors[:10]:  # Mostra apenas os primeiros 10 erros
                summary += f"  - {error}\n"
            
            if len(self.stats.errors) > 10:
                summary += f"  ... e mais {len(self.stats.errors) - 10} erros\n"
        
        return summary
    
    def get_import_stats(self) -> Dict[str, Any]:
        """
        Retorna as estatísticas de importação em formato de dicionário.
        
        Returns:
            Dicionário com estatísticas de importação
        """
        return {
            'users_imported': self.stats.users_imported,
            'users_skipped': self.stats.users_skipped,
            'vehicles_imported': self.stats.vehicles_imported,
            'vehicles_skipped': self.stats.vehicles_skipped,
            'warranties_imported': self.stats.warranties_imported,
            'warranties_skipped': self.stats.warranties_skipped,
            'errors': self.stats.errors.copy()
        }