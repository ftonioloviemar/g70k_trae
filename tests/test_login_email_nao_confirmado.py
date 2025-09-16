"""Testes para verificar mensagem de erro quando usuário não confirmou email"""

import pytest
import tempfile
import os
import bcrypt
import requests
from fastlite import Database
from app.database import init_database
from app.auth import AuthManager


class TestLoginEmailNaoConfirmado:
    """Testes para login com email não confirmado"""
    
    @pytest.fixture(autouse=True)
    def setup_test_user(self):
        """Cria usuário de teste não confirmado"""
        # Criar banco temporário
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            self.db_path = tmp.name
        
        self.db = Database(self.db_path)
        init_database(self.db)
        
        # Criar usuário não confirmado
        senha_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.db.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, confirmado) VALUES (?, ?, ?, ?, ?)",
            ('Usuario Nao Confirmado', 'naoconfirmado@teste.com', senha_hash, 'cliente', False)
        )
        
        # Criar AuthManager com o banco de teste
        self.auth_manager = AuthManager(self.db)
        
        yield
        
        # Limpar após teste
        self.db.close()
        os.unlink(self.db_path)
    
    def test_auth_manager_retorna_erro_email_nao_confirmado(self):
        """Testa se AuthManager retorna erro específico para email não confirmado"""
        # Tentar autenticar usuário não confirmado
        resultado = self.auth_manager.autenticar_usuario('naoconfirmado@teste.com', '123456')
        
        # Deve retornar dict com erro
        assert isinstance(resultado, dict)
        assert resultado.get('erro') == 'email_nao_confirmado'
    
    def test_auth_manager_credenciais_invalidas(self):
        """Testa se AuthManager retorna None para credenciais inválidas"""
        # Tentar autenticar com senha errada
        resultado = self.auth_manager.autenticar_usuario('naoconfirmado@teste.com', 'senha_errada')
        
        # Deve retornar None
        assert resultado is None
        
        # Tentar autenticar com email inexistente
        resultado = self.auth_manager.autenticar_usuario('inexistente@teste.com', '123456')
        
        # Deve retornar None
        assert resultado is None
    
    def test_login_web_email_nao_confirmado(self):
        """Testa se a rota de login redireciona com erro correto para email não confirmado"""
        base_url = "http://localhost:8000"
        
        # Tentar fazer login com usuário não confirmado
        response = requests.post(f'{base_url}/login', data={
            'email': 'naoconfirmado@teste.com',
            'senha': '123456'
        }, allow_redirects=False)
        
        # Deve redirecionar
        assert response.status_code == 302
        
        # Verificar URL de redirecionamento
        location = response.headers.get('location')
        assert 'erro=email_nao_confirmado' in location
        assert 'email=naoconfirmado%40teste.com' in location
    
    def test_login_web_credenciais_invalidas(self):
        """Testa se a rota de login redireciona com erro correto para credenciais inválidas"""
        base_url = "http://localhost:8000"
        
        # Tentar fazer login com senha errada
        response = requests.post(f'{base_url}/login', data={
            'email': 'naoconfirmado@teste.com',
            'senha': 'senha_errada'
        }, allow_redirects=False)
        
        # Deve redirecionar
        assert response.status_code == 302
        
        # Verificar URL de redirecionamento
        location = response.headers.get('location')
        assert 'erro=credenciais_invalidas' in location
        assert 'email=naoconfirmado%40teste.com' in location
    
    def test_pagina_login_mostra_mensagem_email_nao_confirmado(self):
        """Testa se a página de login mostra a mensagem correta para email não confirmado"""
        base_url = "http://localhost:8000"
        
        # Acessar página de login com erro de email não confirmado
        response = requests.get(f'{base_url}/login?erro=email_nao_confirmado&email=naoconfirmado@teste.com')
        
        assert response.status_code == 200
        
        # Verificar se a mensagem está presente
        content = response.text
        assert 'Você precisa confirmar seu email antes de fazer login' in content
        
        # Verificar se o email foi preservado
        assert 'value="naoconfirmado@teste.com"' in content
    
    def test_pagina_login_mostra_mensagem_credenciais_invalidas(self):
        """Testa se a página de login mostra a mensagem correta para credenciais inválidas"""
        base_url = "http://localhost:8000"
        
        # Acessar página de login com erro de credenciais inválidas
        response = requests.get(f'{base_url}/login?erro=credenciais_invalidas&email=teste@exemplo.com')
        
        assert response.status_code == 200
        
        # Verificar se a mensagem está presente
        content = response.text
        assert 'Email ou senha incorretos' in content
        
        # Verificar se o email foi preservado
        assert 'value="teste@exemplo.com"' in content