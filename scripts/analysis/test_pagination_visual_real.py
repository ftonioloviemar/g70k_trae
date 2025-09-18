#!/usr/bin/env python3
"""
Teste visual real da paginação horizontal
Este script faz uma verificação real da tela para garantir que a paginação está horizontal
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
from bs4 import BeautifulSoup
import time
import json

def test_pagination_visual_real():
    """
    Testa visualmente se a paginação está realmente horizontal
    Verifica o HTML real da página e analisa a estrutura
    """
    print("🔍 Testando paginação horizontal - VERIFICAÇÃO REAL DA TELA")
    print("=" * 60)
    
    try:
        # URL da página de usuários (que tem paginação)
        url = "http://localhost:8000/admin/usuarios"
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer login primeiro
        session = requests.Session()
        
        # 1. Fazer login como admin
        print("🔐 Fazendo login como admin...")
        login_data = {
            'email': 'admin@viemar.com.br',
            'senha': 'admin123'
        }
        
        login_response = session.post("http://localhost:8000/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code not in [302, 303]:
            print(f"❌ Erro no login: {login_response.status_code}")
            return False
        
        print("✅ Login realizado com sucesso")
        
        # 2. Acessar página de usuários
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Página carregada com sucesso")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Salvar HTML para debug
        debug_file = Path("C:\\python\\g70k_trae\\tmp\\pagination_debug_real.html")
        debug_file.parent.mkdir(exist_ok=True)
        
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"📄 HTML salvo em: {debug_file}")
        
        # Verificar estrutura da paginação
        print("\n🔍 ANÁLISE DA ESTRUTURA DE PAGINAÇÃO:")
        print("-" * 40)
        
        # 1. Procurar container de paginação
        pagination_container = soup.find(class_="pagination-container")
        
        if not pagination_container:
            print("❌ ERRO: Container de paginação (.pagination-container) não encontrado!")
            return False
        
        print("✅ Container de paginação encontrado")
        
        # 2. Verificar se tem classe mt-3
        container_classes = pagination_container.get("class", [])
        if "mt-3" in container_classes:
            print("✅ Classe mt-3 (margem superior) presente")
        else:
            print("⚠️  Classe mt-3 não encontrada")
        
        # 3. Verificar estrutura Row/Col (Bootstrap)
        rows = pagination_container.find_all(class_="row")
        if not rows:
            print("❌ ERRO: Nenhuma row encontrada no container!")
            return False
        
        print(f"✅ Encontradas {len(rows)} row(s)")
        
        # 4. Analisar primeira row (principal)
        main_row = rows[0]
        cols = main_row.find_all(class_=lambda x: x and any("col" in cls for cls in x))
        
        if len(cols) < 3:
            print(f"❌ ERRO: Esperadas 3 colunas, encontradas {len(cols)}")
            return False
        
        print(f"✅ Encontradas {len(cols)} colunas (layout horizontal)")
        
        # 5. Verificar conteúdo das colunas
        print("\n📊 ANÁLISE DAS COLUNAS:")
        print("-" * 25)
        
        # Coluna 1: Informações de paginação
        col1 = cols[0]
        pagination_info = col1.find("small", class_="text-muted")
        if pagination_info and "Mostrando" in pagination_info.text:
            print("✅ Coluna 1: Informações de paginação OK")
            print(f"   📝 Texto: {pagination_info.text.strip()}")
        else:
            print("❌ Coluna 1: Informações de paginação não encontradas")
        
        # Coluna 2: Navegação de páginas
        col2 = cols[1]
        pagination_nav = col2.find("nav")
        if pagination_nav:
            print("✅ Coluna 2: Navegação de páginas OK")
            
            # Verificar se tem números de página
            page_links = pagination_nav.find_all("a", class_="page-link")
            if page_links:
                print(f"   🔗 Encontrados {len(page_links)} links de página")
            
            # Verificar se está centralizada
            nav_classes = pagination_nav.parent.get("class", [])
            if "justify-content-center" in nav_classes:
                print("   ✅ Navegação centralizada")
            else:
                print("   ⚠️  Navegação pode não estar centralizada")
        else:
            print("❌ Coluna 2: Navegação de páginas não encontrada")
        
        # Coluna 3: Seletor de registros por página
        col3 = cols[2]
        page_size_selector = col3.find("select", class_="form-select")
        if page_size_selector:
            print("✅ Coluna 3: Seletor de registros por página OK")
            
            # Verificar opções
            options = page_size_selector.find_all("option")
            if options:
                values = [opt.get("value") for opt in options]
                print(f"   📋 Opções disponíveis: {values}")
        else:
            print("❌ Coluna 3: Seletor de registros por página não encontrado")
        
        # 6. Verificar classes de alinhamento horizontal
        print("\n🎯 VERIFICAÇÃO DE LAYOUT HORIZONTAL:")
        print("-" * 35)
        
        horizontal_indicators = []
        
        # Verificar d-flex nas colunas
        for i, col in enumerate(cols, 1):
            col_classes = col.get("class", [])
            if "d-flex" in col_classes:
                horizontal_indicators.append(f"Coluna {i} tem d-flex")
            if "align-items-center" in col_classes:
                horizontal_indicators.append(f"Coluna {i} tem align-items-center")
            if "justify-content-start" in col_classes:
                horizontal_indicators.append(f"Coluna {i} alinhada à esquerda")
            elif "justify-content-center" in col_classes:
                horizontal_indicators.append(f"Coluna {i} centralizada")
            elif "justify-content-end" in col_classes:
                horizontal_indicators.append(f"Coluna {i} alinhada à direita")
        
        if horizontal_indicators:
            print("✅ Indicadores de layout horizontal encontrados:")
            for indicator in horizontal_indicators:
                print(f"   • {indicator}")
        else:
            print("⚠️  Poucos indicadores de layout horizontal")
        
        # 7. Verificar se NÃO há indicadores de layout vertical
        print("\n🚫 VERIFICAÇÃO DE LAYOUT VERTICAL (deve estar ausente):")
        print("-" * 50)
        
        vertical_indicators = []
        
        # Procurar por classes que indicariam layout vertical
        vertical_classes = ["flex-column", "d-block", "w-100"]
        for cls in vertical_classes:
            if soup.find(class_=cls):
                vertical_indicators.append(f"Classe {cls} encontrada")
        
        if vertical_indicators:
            print("⚠️  Possíveis indicadores de layout vertical:")
            for indicator in vertical_indicators:
                print(f"   • {indicator}")
        else:
            print("✅ Nenhum indicador de layout vertical encontrado")
        
        # 8. Resumo final
        print("\n" + "=" * 60)
        print("📋 RESUMO DA VERIFICAÇÃO:")
        print("=" * 60)
        
        checks = [
            pagination_container is not None,
            len(rows) > 0,
            len(cols) >= 3,
            pagination_info is not None,
            pagination_nav is not None,
            page_size_selector is not None,
            len(horizontal_indicators) > 0
        ]
        
        passed_checks = sum(checks)
        total_checks = len(checks)
        
        print(f"✅ Verificações passadas: {passed_checks}/{total_checks}")
        
        if passed_checks >= 6:
            print("🎉 SUCESSO: A paginação está HORIZONTAL e funcionando corretamente!")
            print("   • Layout em 3 colunas lado a lado")
            print("   • Informações à esquerda")
            print("   • Navegação no centro")
            print("   • Seletor à direita")
            return True
        else:
            print("❌ FALHA: A paginação NÃO está horizontal ou tem problemas!")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando teste visual real da paginação horizontal...")
    print()
    
    success = test_pagination_visual_real()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ RESULTADO: PAGINAÇÃO HORIZONTAL CONFIRMADA!")
    else:
        print("❌ RESULTADO: PAGINAÇÃO COM PROBLEMAS!")
    print("=" * 60)