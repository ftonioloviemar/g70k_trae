#!/usr/bin/env python3
"""
Script para importação completa e correção dos dados do Caspio.

Este script corrige a importação do Caspio, garantindo que todos os dados
do XML sejam corretamente importados para o banco de dados G70K.
"""

import xml.etree.ElementTree as ET
import sqlite3
import json
import binascii
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteCaspioImporter:
    """Importador completo e corretor dos dados do Caspio."""
    
    def __init__(self, db_path: str, xml_path: str):
        """
        Inicializa o importador.
        
        Args:
            db_path: Caminho para o banco SQLite
            xml_path: Caminho para o arquivo XML do Caspio
        """
        self.db_path = db_path
        self.xml_path = xml_path
        self.stats = {
            'users_imported': 0,
            'users_updated': 0,
            'vehicles_imported': 0,
            'warranties_imported': 0,
            'errors': []
        }
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """Obtém conexão com o banco de dados."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _decode_caspio_password(self, hex_password: str) -> Optional[str]:
        """Decodifica senha do Caspio."""
        try:
            if not hex_password or hex_password == 'None':
                return None
                
            if hex_password.startswith('0x'):
                hex_password = hex_password[2:]
            
            decoded_bytes = binascii.unhexlify(hex_password)
            decoded_str = decoded_bytes.decode('utf-8')
            password_data = json.loads(decoded_str)
            
            return password_data.get('hash')
            
        except Exception as e:
            logger.warning(f"Erro ao decodificar senha: {e}")
            return None
    
    def _parse_caspio_date(self, date_str: str) -> Optional[str]:
        """Converte data do formato Caspio para formato SQLite."""
        if not date_str or date_str == 'None':
            return None
            
        try:
            formats = [
                '%m/%d/%Y %I:%M:%S %p',
                '%m/%d/%Y',
                '%Y-%m-%d',
                '%d/%m/%Y',
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
    
    def import_missing_users(self) -> int:
        """Importa usuários faltantes do XML."""
        logger.info("Iniciando importação de usuários faltantes")
        
        # Parse do XML
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        
        # Encontra tabela CLIENTE
        cliente_table = None
        for table in root.findall('.//Table'):
            name_elem = table.find('Name')
            if name_elem is not None and name_elem.text == 'CLIENTE':
                cliente_table = table
                break
        
        if cliente_table is None:
            raise ValueError("Tabela CLIENTE não encontrada no XML")
        
        conn = self._get_db_connection()
        imported_count = 0
        updated_count = 0
        
        try:
            # Obtém usuários existentes
            cursor = conn.execute("SELECT email, caspio_id FROM usuarios")
            existing_users = {row['email']: row['caspio_id'] for row in cursor.fetchall()}
            
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
                        continue
                    
                    # Verifica se usuário existe
                    if email in existing_users:
                        # Usuário existe - verifica se precisa atualizar caspio_id
                        if existing_users[email] is None and caspio_id:
                            logger.info(f"Atualizando caspio_id para usuário existente: {email}")
                            conn.execute(
                                "UPDATE usuarios SET caspio_id = ? WHERE email = ?",
                                (caspio_id, email)
                            )
                            updated_count += 1
                        continue
                    
                    # Usuário não existe - importa
                    logger.info(f"Importando usuário faltante: {email} (Caspio ID: {caspio_id})")
                    
                    # Processa email confirmado
                    email_confirmado = True  # Assume confirmado por padrão
                    email_conf_elem = row.find('EMAIL_CONFIRMADO')
                    if email_conf_elem is not None and email_conf_elem.text:
                        email_confirmado = email_conf_elem.text.lower() in ['true', '1', 'sim', 'yes']
                    
                    cursor = conn.execute("""
                        INSERT INTO usuarios (
                            email, senha_hash, nome, cpf_cnpj, data_nascimento,
                            data_cadastro, confirmado, caspio_id, telefone,
                            cep, endereco, bairro, cidade, uf
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        email, senha_hash, nome, cpf_cnpj, data_nascimento,
                        data_cadastro or datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                        email_confirmado, caspio_id,
                        telefone, cep, endereco, bairro, cidade, uf
                    ))
                    
                    imported_count += 1
                    
                    if imported_count % 50 == 0:
                        logger.info(f"Importados {imported_count} usuários faltantes")
                
                except Exception as e:
                    error_msg = f"Erro ao importar usuário {caspio_id}: {e}"
                    logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
            
            conn.commit()
            
        finally:
            conn.close()
        
        self.stats['users_imported'] = imported_count
        self.stats['users_updated'] = updated_count
        logger.info(f"Usuários faltantes importados: {imported_count}, atualizados: {updated_count}")
        return imported_count
    
    def import_missing_vehicles(self) -> int:
        """Importa veículos faltantes do XML."""
        logger.info("Iniciando importação de veículos faltantes")
        
        # Parse do XML
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        
        # Encontra tabela VEICULO
        veiculo_table = None
        for table in root.findall('.//Table'):
            name_elem = table.find('Name')
            if name_elem is not None and name_elem.text == 'VEICULO':
                veiculo_table = table
                break
        
        if veiculo_table is None:
            raise ValueError("Tabela VEICULO não encontrada no XML")
        
        conn = self._get_db_connection()
        imported_count = 0
        
        try:
            # Obtém mapeamento caspio_id -> user_id
            cursor = conn.execute("SELECT id, caspio_id FROM usuarios WHERE caspio_id IS NOT NULL")
            caspio_to_user = {row['caspio_id']: row['id'] for row in cursor.fetchall()}
            
            # Obtém veículos existentes
            cursor = conn.execute("SELECT usuario_id, placa FROM veiculos")
            existing_vehicles = {(row['usuario_id'], row['placa']) for row in cursor.fetchall()}
            
            for row in veiculo_table.findall('Row'):
                try:
                    # Extrai dados do veículo
                    caspio_cliente_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
                    marca = row.find('MARCA').text if row.find('MARCA') is not None else None
                    modelo = row.find('MODELO').text if row.find('MODELO') is not None else None
                    ano_modelo = row.find('ANO_MODELO').text if row.find('ANO_MODELO') is not None else None
                    placa = row.find('PLACA').text if row.find('PLACA') is not None else None
                    cor = row.find('COR').text if row.find('COR') is not None else None
                    
                    # Validações básicas
                    if not caspio_cliente_id or not marca or not modelo or not placa:
                        continue
                    
                    # Encontra o usuário correspondente
                    if caspio_cliente_id not in caspio_to_user:
                        continue  # Usuário não existe
                    
                    user_id = caspio_to_user[caspio_cliente_id]
                    
                    # Verifica se veículo já existe
                    if (user_id, placa) in existing_vehicles:
                        continue
                    
                    # Processa ano/modelo
                    processed_ano_modelo = None
                    if ano_modelo:
                        if '/' in ano_modelo:
                            try:
                                processed_ano_modelo = ano_modelo.split('/')[0].strip()
                            except:
                                processed_ano_modelo = ano_modelo.strip()
                        else:
                            processed_ano_modelo = ano_modelo.strip()
                        
                        if not processed_ano_modelo:
                            processed_ano_modelo = None
                    
                    logger.info(f"Importando veículo faltante: {marca} {modelo} ({placa}) - Cliente: {caspio_cliente_id}")
                    
                    # Insere veículo
                    cursor = conn.execute("""
                        INSERT INTO veiculos (
                            usuario_id, marca, modelo, ano_modelo, placa, cor, data_cadastro
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id, marca, modelo, processed_ano_modelo, placa, cor,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    
                    imported_count += 1
                    
                    if imported_count % 50 == 0:
                        logger.info(f"Importados {imported_count} veículos faltantes")
                
                except Exception as e:
                    error_msg = f"Erro ao importar veículo: {e}"
                    logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
            
            conn.commit()
            
        finally:
            conn.close()
        
        self.stats['vehicles_imported'] = imported_count
        logger.info(f"Veículos faltantes importados: {imported_count}")
        return imported_count
    
    def import_missing_warranties(self) -> int:
        """Importa garantias faltantes do XML."""
        logger.info("Iniciando importação de garantias faltantes")
        
        # Parse do XML
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        
        # Encontra tabela PRODUTO_APLICADO
        produto_table = None
        for table in root.findall('.//Table'):
            name_elem = table.find('Name')
            if name_elem is not None and name_elem.text == 'PRODUTO_APLICADO':
                produto_table = table
                break
        
        if produto_table is None:
            raise ValueError("Tabela PRODUTO_APLICADO não encontrada no XML")
        
        conn = self._get_db_connection()
        imported_count = 0
        
        try:
            # Obtém mapeamento caspio_id -> user_id
            cursor = conn.execute("SELECT id, caspio_id FROM usuarios WHERE caspio_id IS NOT NULL")
            caspio_to_user = {row['caspio_id']: row['id'] for row in cursor.fetchall()}
            
            # Obtém garantias existentes
            cursor = conn.execute("SELECT usuario_id, referencia_produto, lote_fabricacao FROM garantias")
            existing_warranties = {(row['usuario_id'], row['referencia_produto'], row['lote_fabricacao']) for row in cursor.fetchall()}
            
            for row in produto_table.findall('Row'):
                try:
                    # Extrai dados da garantia
                    caspio_cliente_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
                    referencia = row.find('REFERENCIA').text if row.find('REFERENCIA') is not None else None
                    lote = row.find('LOTE').text if row.find('LOTE') is not None else None
                    data_aplicacao = row.find('DATA_APLICACAO').text if row.find('DATA_APLICACAO') is not None else None
                    km_aplicacao = row.find('KM_APLICACAO').text if row.find('KM_APLICACAO') is not None else None
                    nome_oficina = row.find('NOME_OFICINA').text if row.find('NOME_OFICINA') is not None else None
                    nf_oficina = row.find('NF_OFICINA').text if row.find('NF_OFICINA') is not None else None
                    
                    # Validações básicas
                    if not caspio_cliente_id or not referencia or not lote:
                        continue
                    
                    # Encontra o usuário correspondente
                    if caspio_cliente_id not in caspio_to_user:
                        continue  # Usuário não existe
                    
                    user_id = caspio_to_user[caspio_cliente_id]
                    
                    # Verifica se garantia já existe
                    if (user_id, referencia, lote) in existing_warranties:
                        continue
                    
                    # Encontra ou cria veículo para o usuário
                    cursor = conn.execute(
                        "SELECT id FROM veiculos WHERE usuario_id = ? LIMIT 1",
                        (user_id,)
                    )
                    vehicle_row = cursor.fetchone()
                    
                    if not vehicle_row:
                        # Cria veículo padrão se não existir
                        cursor = conn.execute("""
                            INSERT INTO veiculos (
                                usuario_id, marca, modelo, ano_modelo, placa, cor, data_cadastro
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            user_id, 'Não informado', 'Não informado', 2020, 'SEM-PLACA',
                            'Não informado', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ))
                        vehicle_id = cursor.lastrowid
                    else:
                        vehicle_id = vehicle_row['id']
                    
                    # Busca ou cria produto
                    cursor = conn.execute("SELECT id FROM produtos WHERE sku = ?", (referencia,))
                    produto_row = cursor.fetchone()
                    
                    if not produto_row:
                        cursor = conn.execute(
                            "INSERT INTO produtos (sku, descricao, ativo) VALUES (?, ?, ?)",
                            (referencia, f"Produto {referencia} (importado do Caspio)", True)
                        )
                        produto_id = cursor.lastrowid
                    else:
                        produto_id = produto_row['id']
                    
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
                    
                    logger.info(f"Importando garantia faltante: Ref {referencia}, Lote {lote} - Cliente: {caspio_cliente_id}")
                    
                    # Insere garantia
                    cursor = conn.execute("""
                        INSERT INTO garantias (
                            usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                            data_instalacao, nota_fiscal, nome_estabelecimento, 
                            quilometragem, referencia_produto, data_cadastro, ativo
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id, produto_id, vehicle_id, lote,
                        data_instalacao, nf_oficina or '', nome_oficina or '',
                        quilometragem, referencia,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), True
                    ))
                    
                    imported_count += 1
                    
                    if imported_count % 50 == 0:
                        logger.info(f"Importadas {imported_count} garantias faltantes")
                
                except Exception as e:
                    error_msg = f"Erro ao importar garantia: {e}"
                    logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
            
            conn.commit()
            
        finally:
            conn.close()
        
        self.stats['warranties_imported'] = imported_count
        logger.info(f"Garantias faltantes importadas: {imported_count}")
        return imported_count
    
    def run_complete_import(self) -> Dict[str, Any]:
        """Executa importação completa de todos os dados faltantes."""
        logger.info("Iniciando importação completa de dados faltantes do Caspio")
        
        try:
            # 1. Importa usuários faltantes primeiro
            self.import_missing_users()
            
            # 2. Importa veículos faltantes (dependem dos usuários)
            self.import_missing_vehicles()
            
            # 3. Importa garantias faltantes (dependem dos usuários e veículos)
            self.import_missing_warranties()
            
            logger.info("Importação completa concluída com sucesso")
            
        except Exception as e:
            error_msg = f"Erro na importação completa: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            raise
        
        return self.stats
    
    def get_summary(self) -> str:
        """Retorna resumo da importação."""
        summary = f"""
=== RESUMO DA IMPORTAÇÃO COMPLETA CASPIO ===

Usuários:
  - Importados: {self.stats['users_imported']}
  - Atualizados: {self.stats['users_updated']}

Veículos:
  - Importados: {self.stats['vehicles_imported']}

Garantias:
  - Importadas: {self.stats['warranties_imported']}

Erros: {len(self.stats['errors'])}
"""
        
        if self.stats['errors']:
            summary += "\n\nErros encontrados:\n"
            for error in self.stats['errors'][:5]:
                summary += f"  - {error}\n"
            
            if len(self.stats['errors']) > 5:
                summary += f"  ... e mais {len(self.stats['errors']) - 5} erros\n"
        
        return summary

def main():
    """Função principal."""
    db_path = "data/viemar_garantia.db"
    xml_path = "docs/context/caspio_viemar/Tables_2025-Sep-08_1152.xml"
    
    if not Path(db_path).exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    if not Path(xml_path).exists():
        print(f"❌ Arquivo XML não encontrado: {xml_path}")
        return
    
    importer = CompleteCaspioImporter(db_path, xml_path)
    
    print("🚀 Iniciando importação completa dos dados faltantes do Caspio...")
    stats = importer.run_complete_import()
    
    print(importer.get_summary())
    
    # Salva log detalhado
    log_path = Path("complete_import_log.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(importer.get_summary())
        if stats['errors']:
            f.write("\n\nErros detalhados:\n")
            for error in stats['errors']:
                f.write(f"  - {error}\n")
    
    print(f"\n📄 Log detalhado salvo em: {log_path}")

if __name__ == "__main__":
    main()