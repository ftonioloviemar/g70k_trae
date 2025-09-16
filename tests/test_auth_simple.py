import pytest
import tempfile
import os
import bcrypt
from fastlite import Database
from app.database import init_database
from app.auth import AuthManager


class TestAuthSimple:
    """Testes simples para verificar a funcionalidade de autenticação"""
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Configura banco de teste"""
        # Criar banco temporário
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            self.db_path = tmp.name
        
        self.db = Database(self.db_path)
        init_database(self.db)
        
        # Criar AuthManager
        self.auth_manager = AuthManager(self.db)
        
        yield
        
        # Limpar
        self.db.close()
        os.unlink(self.db_path)
    
    def test_usuario_nao_confirmado_retorna_erro(self):
        """Testa se usuário não confirmado retorna erro específico"""
        # Criar usuário não confirmado
        senha_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.db.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, confirmado) VALUES (?, ?, ?, ?, ?)",
            ('Usuario Teste', 'teste@email.com', senha_hash, 'cliente', False)
        )
        
        # Tentar autenticar
        resultado = self.auth_manager.autenticar_usuario('teste@email.com', '123456')
        
        # Verificar se retorna erro específico
        assert isinstance(resultado, dict)
        assert resultado.get('erro') == 'email_nao_confirmado'
        print(f"Resultado da autenticação: {resultado}")
    
    def test_usuario_confirmado_autentica_com_sucesso(self):
        """Testa se usuário confirmado autentica normalmente"""
        # Criar usuário confirmado
        senha_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.db.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, confirmado) VALUES (?, ?, ?, ?, ?)",
            ('Usuario Confirmado', 'confirmado@email.com', senha_hash, 'cliente', True)
        )
        
        # Tentar autenticar
        resultado = self.auth_manager.autenticar_usuario('confirmado@email.com', '123456')
        
        # Verificar se retorna dados do usuário
        assert isinstance(resultado, dict)
        assert 'id' in resultado
        assert resultado['email'] == 'confirmado@email.com'
        assert 'erro' not in resultado
        print(f"Resultado da autenticação: {resultado}")
    
    def test_credenciais_invalidas_retorna_none(self):
        """Testa se credenciais inválidas retornam None"""
        # Tentar autenticar com email inexistente
        resultado = self.auth_manager.autenticar_usuario('inexistente@email.com', '123456')
        
        # Deve retornar None
        assert resultado is None
        print(f"Resultado da autenticação: {resultado}")