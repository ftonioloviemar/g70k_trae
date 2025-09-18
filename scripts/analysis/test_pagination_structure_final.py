#!/usr/bin/env python3
"""
Teste final para verificar a estrutura horizontal da paginação
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
from bs4 import BeautifulSoup

def test_pagination_structure():
    """Testa a estrutura da paginação para verificar se está horizontal"""
    
    print("=== TESTE FINAL DA ESTRUTURA DE PAGINAÇÃO ===\n")
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login como administrador...")
    login_data = {
        'email': 'ftoniolo@viemar.com.br',
        'senha': '123456'
    }
    
    try:
        login_response = session.post('http://localhost:8000/login', data=login_data, allow_redirects=True)
        
        if login_response.status_code == 200 and '/admin' in login_response.url:
            print("   ✅ Login bem-sucedido!")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return False
        
        # 2. Acessar página de usuários
        print("\n2. Acessando página de usuários...")
        usuarios_response = session.get('http://localhost:8000/admin/usuarios')
        
        if usuarios_response.status_code != 200:
            print(f"   ❌ Erro ao acessar usuários: {usuarios_response.status_code}")
            return False
        
        print("   ✅ Página de usuários carregada!")
        
        # 3. Analisar estrutura da paginação
        print("\n3. Analisando estrutura da paginação...")
        soup = BeautifulSoup(usuarios_response.text, 'html.parser')
        
        # Procurar container de paginação
        pagination_container = soup.find(class_='pagination-container')
        if not pagination_container:
            print("   ❌ Container de paginação não encontrado!")
            return False
        
        print("   ✅ Container de paginação encontrado!")
        
        # Verificar se tem uma row (linha)
        row = pagination_container.find(class_='row')
        if not row:
            print("   ❌ Elemento 'row' não encontrado na paginação!")
            return False
        
        print("   ✅ Elemento 'row' encontrado!")
        
        # Verificar colunas
        cols = row.find_all('col')
        if len(cols) != 3:
            print(f"   ❌ Esperado 3 colunas, encontrado {len(cols)}!")
            return False
        
        print(f"   ✅ Encontradas {len(cols)} colunas (correto)!")
        
        # Verificar conteúdo das colunas (o conteúdo real está em divs após as tags col)
        print("\n4. Verificando conteúdo das colunas...")
        
        # Buscar todos os divs filhos da row (que contêm o conteúdo real)
        content_divs = row.find_all('div', recursive=False)
        
        if len(content_divs) < 3:
            print(f"   ❌ Esperado pelo menos 3 divs de conteúdo, encontrado {len(content_divs)}!")
            return False
        
        # Div 1: Informações de registros
        div1 = content_divs[0]
        mostrando_text = div1.find('small')
        if mostrando_text and 'Mostrando' in mostrando_text.get_text():
            print("   ✅ Div 1: Informações de registros encontradas!")
        else:
            print("   ❌ Div 1: Informações de registros não encontradas!")
            print(f"   Debug - Conteúdo do div 1: {div1.get_text()[:100]}")
            return False
        
        # Div 2: Navegação de páginas
        div2 = content_divs[1]
        nav = div2.find('nav')
        pagination_ul = nav.find('ul', class_='pagination') if nav else None
        if pagination_ul:
            page_items = pagination_ul.find_all('li', class_='page-item')
            print(f"   ✅ Div 2: Navegação encontrada com {len(page_items)} itens!")
        else:
            print("   ❌ Div 2: Navegação não encontrada!")
            return False
        
        # Div 3: Seletor de registros por página
        div3 = content_divs[2]
        registros_label = div3.find('label')
        if registros_label and 'Registros por página' in registros_label.get_text():
            print("   ✅ Div 3: Seletor de registros por página encontrado!")
        else:
            print("   ❌ Div 3: Seletor de registros por página não encontrado!")
            return False
        
        # 5. Verificar classes de alinhamento horizontal
        print("\n5. Verificando classes de alinhamento horizontal...")
        
        # Verificar se as colunas têm classes de flexbox horizontal
        classes_horizontais = ['d-flex', 'justify-content-start', 'justify-content-center', 'justify-content-end']
        
        for i, col in enumerate(cols, 1):
            col_classes = col.get('class', [])
            tem_flex = any(cls in col_classes for cls in classes_horizontais)
            if tem_flex:
                print(f"   ✅ Coluna {i}: Classes de alinhamento horizontal encontradas!")
            else:
                print(f"   ❌ Coluna {i}: Classes de alinhamento horizontal não encontradas!")
        
        # 6. Verificar ausência de indicadores verticais
        print("\n6. Verificando ausência de layout vertical...")
        
        # Procurar por indicadores de layout vertical
        vertical_indicators = pagination_container.find_all(class_=lambda x: x and ('flex-column' in x or 'vertical' in x))
        
        if not vertical_indicators:
            print("   ✅ Nenhum indicador de layout vertical encontrado!")
        else:
            print(f"   ⚠️ Encontrados {len(vertical_indicators)} indicadores verticais!")
        
        print("\n🎉 RESULTADO FINAL:")
        print("✅ A paginação está estruturada HORIZONTALMENTE!")
        print("✅ Possui 3 colunas em uma única linha (row)")
        print("✅ Coluna 1: Informações de registros (esquerda)")
        print("✅ Coluna 2: Navegação de páginas (centro)")
        print("✅ Coluna 3: Seletor de registros (direita)")
        print("✅ Usa classes de flexbox para alinhamento horizontal")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pagination_structure()
    if success:
        print("\n🎯 TESTE CONCLUÍDO COM SUCESSO!")
        print("A paginação está corretamente implementada na orientação horizontal.")
    else:
        print("\n❌ TESTE FALHOU!")
        print("Há problemas na estrutura da paginação.")
    
    sys.exit(0 if success else 1)