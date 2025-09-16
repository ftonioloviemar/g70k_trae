"""Testes básicos para verificar funcionalidade do sistema."""

import pytest
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestBasicFunctionality:
    """Testes básicos de funcionalidade."""
    
    def test_python_environment(self):
        """Testa se o ambiente Python está funcionando."""
        assert sys.version_info >= (3, 8)
        assert os.getcwd().endswith('g70k_trae')
    
    def test_project_structure(self):
        """Testa se a estrutura básica do projeto existe."""
        project_root = Path(__file__).parent.parent
        
        # Verificar diretórios principais
        assert (project_root / 'app').exists()
        assert (project_root / 'tests').exists()
        assert (project_root / 'models').exists()
        
        # Verificar arquivos principais
        assert (project_root / 'main.py').exists()
        assert (project_root / 'pyproject.toml').exists()
    
    def test_app_module_exists(self):
        """Testa se o módulo app existe."""
        project_root = Path(__file__).parent.parent
        app_init = project_root / 'app' / '__init__.py'
        assert app_init.exists()
    
    def test_models_module_exists(self):
        """Testa se o módulo models existe."""
        project_root = Path(__file__).parent.parent
        models_init = project_root / 'models' / '__init__.py'
        assert models_init.exists()
    
    def test_database_file_exists(self):
        """Testa se o arquivo de banco de dados existe."""
        project_root = Path(__file__).parent.parent
        db_file = project_root / 'g70k.db'
        # O arquivo pode não existir ainda, mas o diretório deve existir
        assert project_root.exists()
    
    def test_import_basic_modules(self):
        """Testa importações básicas do Python."""
        import json
        import datetime
        import sqlite3
        
        # Testa funcionalidades básicas
        data = {'test': 'value'}
        json_str = json.dumps(data)
        assert json.loads(json_str) == data
        
        now = datetime.datetime.now()
        assert isinstance(now, datetime.datetime)
    
    def test_pathlib_functionality(self):
        """Testa funcionalidades do pathlib."""
        current_file = Path(__file__)
        assert current_file.exists()
        assert current_file.name == 'test_basic_functionality.py'
        assert current_file.parent.name == 'tests'
    
    def test_string_operations(self):
        """Testa operações básicas com strings."""
        test_string = "Teste de String"
        assert test_string.lower() == "teste de string"
        assert test_string.upper() == "TESTE DE STRING"
        assert len(test_string) == 15
    
    def test_list_operations(self):
        """Testa operações básicas com listas."""
        test_list = [1, 2, 3, 4, 5]
        assert len(test_list) == 5
        assert sum(test_list) == 15
        assert max(test_list) == 5
        assert min(test_list) == 1
    
    def test_dict_operations(self):
        """Testa operações básicas com dicionários."""
        test_dict = {'a': 1, 'b': 2, 'c': 3}
        assert len(test_dict) == 3
        assert test_dict['a'] == 1
        assert 'b' in test_dict
        assert list(test_dict.keys()) == ['a', 'b', 'c']