#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a resposta HTML completa da página de veículos
"""

import requests
import re
from bs4 import BeautifulSoup

def main():
    base_url = "http://localhost:8000"
    
    print("🔍 Testando resposta HTML completa da página de veículos...")
    
    try:
        # Criar sessão
        session = requests.Session()
        
        print("\n1. Verificando servidor...")
        response = session.get(base_url)
        if response.status_code != 200:
            print(f"❌ Servidor não está respondendo: {response.status_code}")
            return
        print("✅ Servidor está rodando")
        
        print("\n2. Fazendo login...")
        login_data = {
            'email': 'sergio@reis.com',
            'senha': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code != 200 or '/cliente' not in login_response.url:
            print(f"❌ Login falhou: {login_response.status_code}, URL: {login_response.url}")
            print(f"Conteúdo: {login_response.text[:500]}")
            return
        
        print("✅ Login realizado com sucesso")
        
        print("\n3. Acessando página de veículos...")
        veiculos_response = session.get(f"{base_url}/cliente/veiculos")
        
        if veiculos_response.status_code != 200:
            print(f"❌ Erro ao acessar página de veículos: {veiculos_response.status_code}")
            return
        
        print("✅ Página de veículos acessada com sucesso")
        
        # Analisar HTML completo
        html_content = veiculos_response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("\n4. Analisando conteúdo HTML...")
        
        # Procurar por tabelas
        tables = soup.find_all('table')
        print(f"   - Tabelas encontradas: {len(tables)}")
        
        if tables:
            for i, table in enumerate(tables, 1):
                print(f"\n   📋 Tabela {i}:")
                
                # Procurar cabeçalhos
                headers = table.find_all('th')
                if headers:
                    header_texts = [th.get_text(strip=True) for th in headers]
                    print(f"      Cabeçalhos: {header_texts}")
                
                # Procurar linhas de dados
                rows = table.find_all('tr')
                data_rows = [row for row in rows if row.find_all('td')]
                
                print(f"      Linhas de dados: {len(data_rows)}")
                
                for j, row in enumerate(data_rows, 1):
                    cells = row.find_all('td')
                    cell_texts = [td.get_text(strip=True) for td in cells]
                    print(f"        Linha {j}: {cell_texts}")
        
        # Procurar por mensagens específicas
        print("\n5. Procurando por mensagens específicas...")
        
        if "Nenhum veículo cadastrado" in html_content:
            print("   ⚠️ Mensagem 'Nenhum veículo cadastrado' encontrada")
        else:
            print("   ✅ Mensagem 'Nenhum veículo cadastrado' NÃO encontrada")
        
        # Procurar por marcas de veículos
        marcas = ['Toyota', 'Honda', 'Volkswagen', 'Ford', 'Chevrolet']
        marcas_encontradas = []
        
        for marca in marcas:
            if marca in html_content:
                marcas_encontradas.append(marca)
        
        print(f"   - Marcas encontradas: {marcas_encontradas}")
        
        # Procurar por placas
        placas = ['ABC1234', 'ABC-1234', 'DEF5678', 'DEF-5678', 'GHI9012', 'GHI-9012', 'JKL3456', 'JKL-3456', 'MNO7890', 'MNO-7890']
        placas_encontradas = []
        
        for placa in placas:
            if placa in html_content:
                placas_encontradas.append(placa)
        
        print(f"   - Placas encontradas: {placas_encontradas}")
        
        # Procurar por IDs de veículos nos links
        print("\n6. Procurando por links de ações dos veículos...")
        
        links_editar = soup.find_all('a', href=re.compile(r'/cliente/veiculos/\d+/editar'))
        links_toggle = soup.find_all('a', href=re.compile(r'/cliente/veiculos/\d+/toggle'))
        
        print(f"   - Links de editar encontrados: {len(links_editar)}")
        for link in links_editar:
            print(f"     {link.get('href')}")
        
        print(f"   - Links de toggle encontrados: {len(links_toggle)}")
        for link in links_toggle:
            print(f"     {link.get('href')}")
        
        # Salvar HTML para análise manual se necessário
        print("\n7. Salvando HTML para análise...")
        with open('debug_veiculos_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("   ✅ HTML salvo em 'debug_veiculos_page.html'")
        
        # Verificar se há JavaScript que pode estar afetando a renderização
        scripts = soup.find_all('script')
        print(f"\n8. Scripts JavaScript encontrados: {len(scripts)}")
        
        for i, script in enumerate(scripts, 1):
            if script.string and ('veiculo' in script.string.lower() or 'table' in script.string.lower()):
                print(f"   Script {i} (relevante): {script.string[:200]}...")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()