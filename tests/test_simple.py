#!/usr/bin/env python3
"""
Teste simples para verificar se o pytest está funcionando
"""

import pytest

def test_simple_addition():
    """Teste simples de adição"""
    assert 2 + 2 == 4

def test_simple_string():
    """Teste simples de string"""
    assert "hello" + " world" == "hello world"

def test_simple_list():
    """Teste simples de lista"""
    lista = [1, 2, 3]
    lista.append(4)
    assert len(lista) == 4
    assert lista[-1] == 4

if __name__ == "__main__":
    pytest.main([__file__])