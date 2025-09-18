#!/usr/bin/env python3
"""
Testes visuais para o componente de paginação
"""

import pytest
from fasthtml.common import *
from app.templates import pagination_component


def test_pagination_visual_layout():
    """Testa se o layout da paginação está organizado horizontalmente"""
    # Simular dados de paginação com múltiplas páginas
    component = pagination_component(
        current_page=2,
        total_pages=5,
        base_url="/admin/usuarios",
        page_size=50,
        total_records=250
    )
    
    # Verificar se o componente foi criado
    assert component is not None
    
    # Converter para string para análise
    html_str = str(component)
    
    # Verificar se contém as classes de layout horizontal
    assert "d-flex" in html_str
    assert "justify-content-center" in html_str
    assert "flex-wrap" in html_str
    
    # Verificar se contém a estrutura de rows para organização vertical
    assert html_str.count('<div class="row">') >= 2  # Pelo menos 2 rows
    
    print("✓ Layout horizontal verificado com sucesso")


def test_pagination_current_page_bold():
    """Testa se a página atual está destacada em negrito"""
    component = pagination_component(
        current_page=3,
        total_pages=5,
        base_url="/admin/usuarios",
        page_size=50,
        total_records=250
    )
    
    # Converter para string para análise
    html_str = str(component)
    
    # Verificar se contém o elemento Strong para negrito (pode ser renderizado de diferentes formas)
    assert "strong" in html_str.lower() or "font-bold" in html_str.lower()
    
    # Verificar se contém as classes de destaque
    assert "bg-primary" in html_str
    assert "text-white" in html_str
    
    # Verificar se a página atual (3) está presente
    assert ">3<" in html_str
    
    print("✓ Página atual em negrito verificada com sucesso")


def test_pagination_single_page_layout():
    """Testa o layout quando há apenas uma página"""
    component = pagination_component(
        current_page=1,
        total_pages=1,
        base_url="/admin/usuarios",
        page_size=50,
        total_records=10
    )
    
    # Verificar se o componente foi criado (não deve ser None)
    assert component is not None
    
    # Converter para string para análise
    html_str = str(component)
    
    # Verificar se contém informações básicas
    assert "registro" in html_str.lower()
    assert "text-center" in html_str
    
    print("✓ Layout de página única verificado com sucesso")


def test_pagination_responsive_classes():
    """Testa se as classes responsivas estão presentes"""
    component = pagination_component(
        current_page=1,
        total_pages=3,
        base_url="/admin/usuarios",
        page_size=50,
        total_records=150
    )
    
    html_str = str(component)
    
    # Verificar classes responsivas
    assert "flex-wrap" in html_str
    assert "mb-2" in html_str  # Margem bottom para espaçamento
    
    # Verificar se usa width=12 para ocupar toda a largura
    assert 'width="12"' in html_str
    
    print("✓ Classes responsivas verificadas com sucesso")


if __name__ == "__main__":
    test_pagination_visual_layout()
    test_pagination_current_page_bold()
    test_pagination_single_page_layout()
    test_pagination_responsive_classes()
    print("\n🎉 Todos os testes visuais passaram!")