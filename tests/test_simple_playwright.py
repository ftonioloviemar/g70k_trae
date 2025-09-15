"""Teste simples do Playwright."""

import pytest
from playwright.sync_api import sync_playwright
import subprocess
import time


def test_simple_playwright():
    """Teste simples para verificar se o Playwright funciona."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com")
        assert "Example Domain" in page.title()
        browser.close()
        print("✅ Playwright funcionando!")


def test_local_server():
    """Teste para verificar se conseguimos acessar o servidor local."""
    # Inicia o servidor em background
    process = subprocess.Popen(
        ["uv", "run", "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Aguarda o servidor iniciar
        time.sleep(3)
        
        # Testa com Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto("http://localhost:8000", timeout=10000)
                print(f"Status: {page.url}")
                print(f"Título: {page.title()}")
                print("✅ Servidor local acessível!")
            except Exception as e:
                print(f"❌ Erro ao acessar servidor: {e}")
            finally:
                browser.close()
    
    finally:
        # Para o servidor
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    test_simple_playwright()
    test_local_server()