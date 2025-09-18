#!/usr/bin/env python3
"""
Análise completa da importação do Caspio XML.

Este script analisa todos os dados do XML do Caspio e compara com o que foi
importado no banco de dados, identificando registros faltantes ou inconsistências.
"""

import xml.etree.ElementTree as ET
import sqlite3
import json
import binascii
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass

@dataclass
class ImportAnalysis:
    """Resultado da análise de importação."""
    xml_users: int = 0
    db_users: int = 0
    missing_users: List[Dict] = None
    xml_vehicles: int = 0
    db_vehicles: int = 0
    missing_vehicles: List[Dict] = None
    xml_warranties: int = 0
    db_warranties: int = 0
    missing_warranties: List[Dict] = None
    inconsistencies: List[str] = None
    
    def __post_init__(self):
        if self.missing_users is None:
            self.missing_users = []
        if self.missing_vehicles is None:
            self.missing_vehicles = []
        if self.missing_warranties is None:
            self.missing_warranties = []
        if self.inconsistencies is None:
            self.inconsistencies = []

class CaspioImportAnalyzer:
    """Analisador completo da importação do Caspio."""
    
    def __init__(self, db_path: str, xml_path: str):
        """
        Inicializa o analisador.
        
        Args:
            db_path: Caminho para o banco SQLite
            xml_path: Caminho para o arquivo XML do Caspio
        """
        self.db_path = db_path
        self.xml_path = xml_path
        self.analysis = ImportAnalysis()
    
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
            
        except Exception:
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
                    
            return None
            
        except Exception:
            return None
    
    def analyze_users(self) -> None:
        """Analisa importação de usuários."""
        print("=== ANALISANDO USUÁRIOS ===")
        
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
            print("❌ Tabela CLIENTE não encontrada no XML")
            return
        
        # Coleta dados do XML
        xml_users = {}
        valid_xml_users = 0
        
        for row in cliente_table.findall('Row'):
            caspio_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
            nome = row.find('NOME').text if row.find('NOME') is not None else None
            email = row.find('EMAIL').text if row.find('EMAIL') is not None else None
            cpf_cnpj = row.find('CPF_CNPJ').text if row.find('CPF_CNPJ') is not None else None
            
            if email and nome:  # Critério básico para usuário válido
                valid_xml_users += 1
                xml_users[email] = {
                    'caspio_id': caspio_id,
                    'nome': nome,
                    'email': email,
                    'cpf_cnpj': cpf_cnpj
                }
        
        self.analysis.xml_users = valid_xml_users
        print(f"📊 Usuários válidos no XML: {valid_xml_users}")
        
        # Coleta dados do banco
        conn = self._get_db_connection()
        try:
            cursor = conn.execute("SELECT email, nome, caspio_id, cpf_cnpj FROM usuarios")
            db_users = {}
            for row in cursor.fetchall():
                db_users[row['email']] = {
                    'nome': row['nome'],
                    'email': row['email'],
                    'caspio_id': row['caspio_id'],
                    'cpf_cnpj': row['cpf_cnpj']
                }
            
            self.analysis.db_users = len(db_users)
            print(f"📊 Usuários no banco: {len(db_users)}")
            
            # Identifica usuários faltantes
            missing_count = 0
            for email, xml_user in xml_users.items():
                if email not in db_users:
                    self.analysis.missing_users.append(xml_user)
                    missing_count += 1
            
            print(f"❌ Usuários faltantes: {missing_count}")
            
            # Mostra alguns exemplos de usuários faltantes
            if missing_count > 0:
                print("\n🔍 Exemplos de usuários faltantes:")
                for i, user in enumerate(self.analysis.missing_users[:5]):
                    print(f"  {i+1}. {user['nome']} ({user['email']}) - Caspio ID: {user['caspio_id']}")
                
                if missing_count > 5:
                    print(f"  ... e mais {missing_count - 5} usuários")
            
            # Verifica inconsistências nos dados existentes
            inconsistencies = 0
            for email, xml_user in xml_users.items():
                if email in db_users:
                    db_user = db_users[email]
                    
                    # Verifica caspio_id
                    if xml_user['caspio_id'] != db_user['caspio_id']:
                        inconsistency = f"Usuário {email}: Caspio ID diferente (XML: {xml_user['caspio_id']}, DB: {db_user['caspio_id']})"
                        self.analysis.inconsistencies.append(inconsistency)
                        inconsistencies += 1
                    
                    # Verifica nome (pode ter pequenas diferenças)
                    if xml_user['nome'] != db_user['nome']:
                        inconsistency = f"Usuário {email}: Nome diferente (XML: '{xml_user['nome']}', DB: '{db_user['nome']}')"
                        self.analysis.inconsistencies.append(inconsistency)
                        inconsistencies += 1
            
            if inconsistencies > 0:
                print(f"⚠️  Inconsistências encontradas: {inconsistencies}")
                print("\n🔍 Exemplos de inconsistências:")
                for i, inconsistency in enumerate(self.analysis.inconsistencies[:3]):
                    print(f"  {i+1}. {inconsistency}")
                
                if inconsistencies > 3:
                    print(f"  ... e mais {inconsistencies - 3} inconsistências")
        
        finally:
            conn.close()
    
    def analyze_vehicles(self) -> None:
        """Analisa importação de veículos."""
        print("\n=== ANALISANDO VEÍCULOS ===")
        
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
            print("❌ Tabela VEICULO não encontrada no XML")
            return
        
        # Coleta dados do XML
        xml_vehicles = {}
        valid_xml_vehicles = 0
        
        for row in veiculo_table.findall('Row'):
            caspio_cliente_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
            marca = row.find('MARCA').text if row.find('MARCA') is not None else None
            modelo = row.find('MODELO').text if row.find('MODELO') is not None else None
            placa = row.find('PLACA').text if row.find('PLACA') is not None else None
            
            if caspio_cliente_id and marca and modelo and placa:
                valid_xml_vehicles += 1
                key = f"{caspio_cliente_id}_{placa}"
                xml_vehicles[key] = {
                    'caspio_cliente_id': caspio_cliente_id,
                    'marca': marca,
                    'modelo': modelo,
                    'placa': placa
                }
        
        self.analysis.xml_vehicles = valid_xml_vehicles
        print(f"📊 Veículos válidos no XML: {valid_xml_vehicles}")
        
        # Coleta dados do banco
        conn = self._get_db_connection()
        try:
            cursor = conn.execute("""
                SELECT v.marca, v.modelo, v.placa, u.caspio_id
                FROM veiculos v
                JOIN usuarios u ON v.usuario_id = u.id
                WHERE u.caspio_id IS NOT NULL
            """)
            
            db_vehicles = {}
            for row in cursor.fetchall():
                key = f"{row['caspio_id']}_{row['placa']}"
                db_vehicles[key] = {
                    'caspio_cliente_id': row['caspio_id'],
                    'marca': row['marca'],
                    'modelo': row['modelo'],
                    'placa': row['placa']
                }
            
            self.analysis.db_vehicles = len(db_vehicles)
            print(f"📊 Veículos no banco (com caspio_id): {len(db_vehicles)}")
            
            # Identifica veículos faltantes
            missing_count = 0
            for key, xml_vehicle in xml_vehicles.items():
                if key not in db_vehicles:
                    self.analysis.missing_vehicles.append(xml_vehicle)
                    missing_count += 1
            
            print(f"❌ Veículos faltantes: {missing_count}")
            
            # Mostra alguns exemplos
            if missing_count > 0:
                print("\n🔍 Exemplos de veículos faltantes:")
                for i, vehicle in enumerate(self.analysis.missing_vehicles[:5]):
                    print(f"  {i+1}. {vehicle['marca']} {vehicle['modelo']} ({vehicle['placa']}) - Cliente: {vehicle['caspio_cliente_id']}")
                
                if missing_count > 5:
                    print(f"  ... e mais {missing_count - 5} veículos")
        
        finally:
            conn.close()
    
    def analyze_warranties(self) -> None:
        """Analisa importação de garantias."""
        print("\n=== ANALISANDO GARANTIAS ===")
        
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
            print("❌ Tabela PRODUTO_APLICADO não encontrada no XML")
            return
        
        # Coleta dados do XML
        xml_warranties = {}
        valid_xml_warranties = 0
        
        for row in produto_table.findall('Row'):
            caspio_cliente_id = row.find('ID_CLIENTE').text if row.find('ID_CLIENTE') is not None else None
            referencia = row.find('REFERENCIA').text if row.find('REFERENCIA') is not None else None
            lote = row.find('LOTE').text if row.find('LOTE') is not None else None
            
            if caspio_cliente_id and referencia and lote:
                valid_xml_warranties += 1
                key = f"{caspio_cliente_id}_{referencia}_{lote}"
                xml_warranties[key] = {
                    'caspio_cliente_id': caspio_cliente_id,
                    'referencia': referencia,
                    'lote': lote
                }
        
        self.analysis.xml_warranties = valid_xml_warranties
        print(f"📊 Garantias válidas no XML: {valid_xml_warranties}")
        
        # Coleta dados do banco
        conn = self._get_db_connection()
        try:
            cursor = conn.execute("""
                SELECT g.referencia_produto, g.lote_fabricacao, u.caspio_id
                FROM garantias g
                JOIN usuarios u ON g.usuario_id = u.id
                WHERE u.caspio_id IS NOT NULL
            """)
            
            db_warranties = {}
            for row in cursor.fetchall():
                key = f"{row['caspio_id']}_{row['referencia_produto']}_{row['lote_fabricacao']}"
                db_warranties[key] = {
                    'caspio_cliente_id': row['caspio_id'],
                    'referencia': row['referencia_produto'],
                    'lote': row['lote_fabricacao']
                }
            
            self.analysis.db_warranties = len(db_warranties)
            print(f"📊 Garantias no banco (com caspio_id): {len(db_warranties)}")
            
            # Identifica garantias faltantes
            missing_count = 0
            for key, xml_warranty in xml_warranties.items():
                if key not in db_warranties:
                    self.analysis.missing_warranties.append(xml_warranty)
                    missing_count += 1
            
            print(f"❌ Garantias faltantes: {missing_count}")
            
            # Mostra alguns exemplos
            if missing_count > 0:
                print("\n🔍 Exemplos de garantias faltantes:")
                for i, warranty in enumerate(self.analysis.missing_warranties[:5]):
                    print(f"  {i+1}. Ref: {warranty['referencia']}, Lote: {warranty['lote']} - Cliente: {warranty['caspio_cliente_id']}")
                
                if missing_count > 5:
                    print(f"  ... e mais {missing_count - 5} garantias")
        
        finally:
            conn.close()
    
    def generate_report(self) -> str:
        """Gera relatório completo da análise."""
        report = f"""
=== RELATÓRIO COMPLETO DE ANÁLISE DA IMPORTAÇÃO CASPIO ===

USUÁRIOS:
  - XML: {self.analysis.xml_users}
  - Banco: {self.analysis.db_users}
  - Faltantes: {len(self.analysis.missing_users)}
  - Taxa de importação: {(self.analysis.db_users / self.analysis.xml_users * 100):.1f}%

VEÍCULOS:
  - XML: {self.analysis.xml_vehicles}
  - Banco: {self.analysis.db_vehicles}
  - Faltantes: {len(self.analysis.missing_vehicles)}
  - Taxa de importação: {(self.analysis.db_vehicles / self.analysis.xml_vehicles * 100):.1f}%

GARANTIAS:
  - XML: {self.analysis.xml_warranties}
  - Banco: {self.analysis.db_warranties}
  - Faltantes: {len(self.analysis.missing_warranties)}
  - Taxa de importação: {(self.analysis.db_warranties / self.analysis.xml_warranties * 100):.1f}%

INCONSISTÊNCIAS: {len(self.analysis.inconsistencies)}

RESUMO:
  - Total de registros no XML: {self.analysis.xml_users + self.analysis.xml_vehicles + self.analysis.xml_warranties}
  - Total de registros no banco: {self.analysis.db_users + self.analysis.db_vehicles + self.analysis.db_warranties}
  - Total de registros faltantes: {len(self.analysis.missing_users) + len(self.analysis.missing_vehicles) + len(self.analysis.missing_warranties)}
"""
        
        return report
    
    def run_complete_analysis(self) -> None:
        """Executa análise completa."""
        print("🔍 INICIANDO ANÁLISE COMPLETA DA IMPORTAÇÃO CASPIO")
        print("=" * 60)
        
        self.analyze_users()
        self.analyze_vehicles()
        self.analyze_warranties()
        
        print("\n" + "=" * 60)
        print(self.generate_report())
        
        # Salva relatório em arquivo
        report_path = Path("caspio_import_analysis_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())
        
        print(f"\n📄 Relatório salvo em: {report_path}")

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
    
    analyzer = CaspioImportAnalyzer(db_path, xml_path)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()