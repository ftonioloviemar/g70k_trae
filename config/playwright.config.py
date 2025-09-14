#!/usr/bin/env python3
"""
Configuração do Playwright para testes E2E
"""

from playwright.sync_api import Playwright

# Configuração global do Playwright
PLAYWRIGHT_CONFIG = {
    'headless': True,  # Executar em modo headless por padrão
    'slow_mo': 100,    # Adicionar delay entre ações para estabilidade
    'timeout': 30000,  # Timeout de 30 segundos
    'viewport': {'width': 1280, 'height': 720},
    'ignore_https_errors': True,
    'screenshot': 'only-on-failure',
    'video': 'retain-on-failure'
}

# Configuração específica para diferentes navegadores
BROWSER_CONFIGS = {
    'chromium': {
        'args': [
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--no-sandbox'
        ]
    },
    'firefox': {
        'firefox_user_prefs': {
            'security.tls.insecure_fallback_hosts': 'localhost,127.0.0.1'
        }
    },
    'webkit': {}
}