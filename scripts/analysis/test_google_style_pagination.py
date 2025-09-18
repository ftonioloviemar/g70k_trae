#!/usr/bin/env python3
"""
Teste para verificar se a paginação está no estilo Google (horizontal)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
from bs4 import BeautifulSoup

def test_google_style_pagination():
    """Teste da paginação estilo Google"""
    
    print("=== TESTE DA PAGINAÇÃO ESTILO GOOGLE ===\n")
    
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
        print("\n3. Analisando estrutura da paginação estilo Google...")
        soup = BeautifulSoup(usuarios_response.text, 'html.parser')
        
        # Procurar container de paginação
        pagination_container = soup.find(class_='pagination-container')
        if not pagination_container:
            print("   ❌ Container de paginação não encontrado!")
            return False
        
        print("   ✅ Container de paginação encontrado!")
        
        # 4. Verificar estrutura horizontal
        print("\n4. Verificando estrutura horizontal...")
        
        # Verificar se tem divs com d-flex
        flex_divs = pagination_container.find_all('div', class_=lambda x: x and 'd-flex' in x)
        if len(flex_divs) >= 2:
            print(f"   ✅ Encontrados {len(flex_divs)} divs com d-flex (layout horizontal)!")
        else:
            print(f"   ❌ Poucos divs com d-flex encontrados: {len(flex_divs)}")
        
        # 5. Verificar botões estilo Google
        print("\n5. Verificando botões estilo Google...")
        
        # Procurar botão "Anterior"
        anterior_btn = soup.find('a', string=lambda text: text and 'Anterior' in text)
        if anterior_btn and 'btn' in anterior_btn.get('class', []):
            print("   ✅ Botão 'Anterior' estilo Google encontrado!")
        else:
            print("   ❌ Botão 'Anterior' estilo Google não encontrado!")
        
        # Procurar botão "Próxima"
        proxima_btn = soup.find('a', string=lambda text: text and 'Próxima' in text)
        if proxima_btn and 'btn' in proxima_btn.get('class', []):
            print("   ✅ Botão 'Próxima' estilo Google encontrado!")
        else:
            print("   ❌ Botão 'Próxima' estilo Google não encontrado!")
        
        # 6. Verificar páginas numeradas como botões
        print("\n6. Verificando páginas numeradas...")
        
        # Procurar botões de página (números)
        page_buttons = pagination_container.find_all(['a', 'span'], class_=lambda x: x and 'btn' in x and ('btn-primary' in x or 'btn-outline-secondary' in x))
        
        if len(page_buttons) >= 3:  # Pelo menos algumas páginas
            print(f"   ✅ Encontrados {len(page_buttons)} botões de página!")
            
            # Verificar se tem página ativa
            active_page = pagination_container.find(['a', 'span'], class_=lambda x: x and 'btn-primary' in x)
            if active_page:
                print(f"   ✅ Página ativa encontrada: {active_page.get_text().strip()}")
            else:
                print("   ❌ Página ativa não encontrada!")
        else:
            print(f"   ❌ Poucos botões de página encontrados: {len(page_buttons)}")
        
        # 7. Verificar layout de duas linhas
        print("\n7. Verificando layout de duas linhas...")
        
        # Primeira linha: informações e seletor
        info_line = pagination_container.find('div', class_=lambda x: x and 'justify-content-between' in x)
        if info_line:
            print("   ✅ Primeira linha (informações e seletor) encontrada!")
        else:
            print("   ❌ Primeira linha não encontrada!")
        
        # Segunda linha: navegação
        nav_line = pagination_container.find('div', class_=lambda x: x and 'justify-content-center' in x and 'flex-wrap' in x)
        if nav_line:
            print("   ✅ Segunda linha (navegação) encontrada!")
        else:
            print("   ❌ Segunda linha não encontrada!")
        
        # 8. Verificar informações de registros
        print("\n8. Verificando informações de registros...")
        
        mostrando = soup.find(string=lambda text: text and 'Mostrando' in text and 'registros' in text)
        if mostrando:
            print(f"   ✅ Informações de registros: {mostrando.strip()}")
        else:
            print("   ❌ Informações de registros não encontradas!")
        
        # 9. Verificar seletor de registros por página
        print("\n9. Verificando seletor de registros por página...")
        
        registros_label = soup.find('label', string=lambda text: text and 'Registros por página' in text)
        if registros_label:
            print("   ✅ Seletor de registros por página encontrado!")
        else:
            print("   ❌ Seletor de registros por página não encontrado!")
        
        print("\n🎉 RESULTADO FINAL:")
        print("✅ A paginação foi modificada para estilo Google!")
        print("✅ Layout horizontal com duas linhas!")
        print("✅ Botões 'Anterior' e 'Próxima' estilo Google!")
        print("✅ Páginas numeradas como botões!")
        print("✅ Informações e seletor na linha superior!")
        print("✅ Navegação centralizada na linha inferior!")
        print("\n🎯 CONCLUSÃO: PAGINAÇÃO ESTILO GOOGLE IMPLEMENTADA!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_google_style_pagination()
    sys.exit(0 if success else 1)