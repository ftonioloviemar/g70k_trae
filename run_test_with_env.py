#!/usr/bin/env python3
"""
Script para executar o teste de encoding do Firebird com variáveis de ambiente.
"""

import os
import subprocess
import sys
from pathlib import Path

def load_env_file(env_file: str) -> None:
    """Carrega variáveis de ambiente de um arquivo .env"""
    if not os.path.exists(env_file):
        print(f"Arquivo {env_file} não encontrado")
        return
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
                print(f"Definindo {key}={value}")

def main():
    """Função principal"""
    # Carregar variáveis de ambiente do arquivo .env.test
    env_file = Path(__file__).parent / '.env.test'
    print(f"Carregando variáveis de ambiente de {env_file}")
    load_env_file(str(env_file))
    
    # Executar o teste
    test_file = Path(__file__).parent / 'tests' / 'test_firebird_encoding_fix.py'
    print(f"\nExecutando teste: {test_file}")
    
    try:
        # Executar sem capturar output para evitar problemas de encoding
        result = subprocess.run([sys.executable, str(test_file)])
        
        print(f"\n=== EXIT CODE: {result.returncode} ===")
        
        return result.returncode
        
    except Exception as e:
        print(f"Erro ao executar teste: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())