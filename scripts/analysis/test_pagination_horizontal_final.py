#!/usr/bin/env python3
"""
Teste final para verificar se a paginação está horizontal
"""

import requests
from bs4 import BeautifulSoup
import sys
import os

def test_pagination_horizontal_final():
    """Testa se a paginação está realmente horizontal"""
    
    print("🔍 Testando paginação horizontal...")
    
    try:
        # Fazer login primeiro
        session = requests.Session()
        
        print("🔐 Fazendo login...")
        login_response = session.post(
            "http://localhost:8000/login",
            data={
                "email": "ftoniolo@viemar.com.br",
                "password": "abc123"
            },
            allow_redirects=False
        )
        
        if login_response.status_code not in [302, 303]:
            print(f"❌ Falha no login. Status: {login_response.status_code}")
            return False
            
        print("✅ Login realizado com sucesso")
        
        # Acessar página de usuários
        print("📄 Acessando página de usuários...")
        response = session.get("http://localhost:8000/admin/usuarios")
        
        if response.status_code != 200:
            print(f"❌ Falha ao carregar página. Status: {response.status_code}")
            return False
            
        print("✅ Página carregada com sucesso")
        
        # Analisar HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Salvar HTML para debug
        with open("C:\\python\\g70k_trae\\tmp\\pagination_horizontal_final.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("📄 HTML salvo em tmp/pagination_horizontal_final.html")
        
        # Verificar se existe o container de paginação
        pagination_container = soup.find(class_="pagination-container")
        
        if not pagination_container:
            print("❌ Container de paginação (.pagination-container) não encontrado")
            return False
            
        print("✅ Container de paginação encontrado")
        
        # Verificar se tem a classe mt-3
        container_classes = pagination_container.get("class", [])
        if "mt-3" in container_classes:
            print("✅ Classe mt-3 encontrada no container")
        else:
            print("⚠️  Classe mt-3 não encontrada no container")
        
        # Verificar estrutura de row única (horizontal)
        rows = pagination_container.find_all(class_="row")
        if not rows:
            print("❌ Nenhuma row encontrada no container de paginação")
            return False
            
        if len(rows) > 1:
            print(f"❌ Múltiplas rows encontradas ({len(rows)}). Isso indica layout vertical!")
            return False
            
        print(f"✅ Apenas 1 row encontrada (layout horizontal)")
        
        # Verificar colunas na row
        main_row = rows[0]
        cols = main_row.find_all(lambda tag: tag.name == 'div' and tag.get('class') and any('col' in cls for cls in tag.get('class', [])))
        
        if len(cols) != 3:
            print(f"❌ Esperadas 3 colunas, encontradas {len(cols)}")
            return False
            
        print(f"✅ 3 colunas encontradas (layout horizontal correto)")
        
        # Verificar conteúdo das colunas
        col_contents = []
        for i, col in enumerate(cols):
            col_classes = col.get("class", [])
            
            # Verificar se tem width=4 (ou col-4)
            has_width_4 = any('col-4' in cls or 'col-md-4' in cls for cls in col_classes)
            if not has_width_4:
                # Verificar se tem width como atributo
                width = col.get('width')
                if width == '4':
                    has_width_4 = True
            
            if has_width_4:
                print(f"✅ Coluna {i+1} tem largura 4 (1/3 da tela)")
            else:
                print(f"⚠️  Coluna {i+1} não tem largura 4 definida")
            
            # Verificar conteúdo
            if col.find(class_="text-muted"):
                col_contents.append("info")
                print(f"✅ Coluna {i+1} contém informações de paginação")
            elif col.find("nav"):
                col_contents.append("nav")
                print(f"✅ Coluna {i+1} contém navegação de páginas")
            elif col.find("select"):
                col_contents.append("selector")
                print(f"✅ Coluna {i+1} contém seletor de registros por página")
            else:
                col_contents.append("unknown")
                print(f"⚠️  Coluna {i+1} tem conteúdo não identificado")
        
        # Verificar se temos os 3 elementos esperados
        expected_contents = {"info", "nav", "selector"}
        found_contents = set(col_contents)
        
        if expected_contents.issubset(found_contents):
            print("✅ Todos os elementos de paginação encontrados")
        else:
            missing = expected_contents - found_contents
            print(f"⚠️  Elementos faltando: {missing}")
        
        # Verificar classes de alinhamento horizontal
        horizontal_classes = ["d-flex", "justify-content-center", "justify-content-start", "justify-content-end"]
        found_horizontal = False
        
        for col in cols:
            col_classes = col.get("class", [])
            if any(hc in col_classes for hc in horizontal_classes):
                found_horizontal = True
                break
        
        if found_horizontal:
            print("✅ Classes de alinhamento horizontal encontradas")
        else:
            print("⚠️  Classes de alinhamento horizontal não encontradas")
        
        # Verificar se NÃO tem indicadores de layout vertical
        vertical_indicators = pagination_container.find_all(class_=lambda x: x and any(
            indicator in str(x) for indicator in ["flex-column", "d-block", "w-100 mb-"]
        ))
        
        if not vertical_indicators:
            print("✅ Nenhum indicador de layout vertical encontrado")
        else:
            print(f"⚠️  {len(vertical_indicators)} indicadores de layout vertical encontrados")
        
        print("\n" + "="*50)
        print("📊 RESUMO DA ANÁLISE:")
        print("="*50)
        print(f"✅ Container de paginação: {'SIM' if pagination_container else 'NÃO'}")
        print(f"✅ Layout horizontal (1 row): {'SIM' if len(rows) == 1 else 'NÃO'}")
        print(f"✅ 3 colunas lado a lado: {'SIM' if len(cols) == 3 else 'NÃO'}")
        print(f"✅ Elementos completos: {'SIM' if expected_contents.issubset(found_contents) else 'NÃO'}")
        print(f"✅ Classes horizontais: {'SIM' if found_horizontal else 'NÃO'}")
        print(f"✅ Sem layout vertical: {'SIM' if not vertical_indicators else 'NÃO'}")
        
        # Resultado final
        is_horizontal = (
            pagination_container and 
            len(rows) == 1 and 
            len(cols) == 3 and 
            expected_contents.issubset(found_contents) and
            not vertical_indicators
        )
        
        if is_horizontal:
            print("\n🎉 SUCESSO: A paginação está HORIZONTAL!")
            return True
        else:
            print("\n❌ FALHA: A paginação NÃO está horizontal!")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Certifique-se de que o servidor está rodando em http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    success = test_pagination_horizontal_final()
    sys.exit(0 if success else 1)