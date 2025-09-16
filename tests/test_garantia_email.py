#!/usr/bin/env python3
"""
Testes para verificar o envio de email ao cadastrar garantia
"""

import pytest
from unittest.mock import patch, MagicMock
from fasthtml.common import *
from pathlib import Path
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.email_service import EmailService, send_warranty_activation_email
from models.garantia import Garantia
from fastlite import Database


class TestGarantiaEmail:
    """Testes para envio de email de garantia"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.db_path = Path(__file__).parent.parent / 'data' / 'viemar_garantia.db'
        self.db = Database(self.db_path)
        
    def test_send_warranty_activation_email_success(self):
        """Testa envio bem-sucedido de email de ativação de garantia"""
        with patch('app.email_service.send_email') as mock_send:
            mock_send.return_value = True
            
            result = send_warranty_activation_email(
                user_email="test@example.com",
                user_name="Usuário Teste",
                produto_nome="Filtro de Combustível",
                veiculo_info="Honda Civic (ABC-1234)",
                data_vencimento="16/09/2026"
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Verificar argumentos da chamada
            args, kwargs = mock_send.call_args
            assert args[0] == "test@example.com"
            assert "Garantia Ativada - Filtro de Combustível" in args[1]
            assert "Usuário Teste" in args[2]
            assert "Honda Civic (ABC-1234)" in args[2]
            assert "16/09/2026" in args[2]
    
    def test_send_warranty_activation_email_failure(self):
        """Testa falha no envio de email de ativação de garantia"""
        with patch('app.email_service.send_email') as mock_send:
            mock_send.return_value = False
            
            result = send_warranty_activation_email(
                user_email="test@example.com",
                user_name="Usuário Teste",
                produto_nome="Filtro de Combustível",
                veiculo_info="Honda Civic (ABC-1234)",
                data_vencimento="16/09/2026"
            )
            
            assert result is False
            mock_send.assert_called_once()
    
    def test_email_service_initialization(self):
        """Testa inicialização do serviço de email"""
        email_service = EmailService()
        assert email_service is not None
        assert hasattr(email_service, 'send_email')
        assert hasattr(email_service, 'send_warranty_activation_email')
    
    def test_garantia_creation_with_email(self):
        """Testa criação de garantia com envio de email"""
        # Buscar dados de teste existentes
        user = self.db.execute('SELECT id, nome, email FROM usuarios WHERE email = ?', ['ftoniolo@gmail.com']).fetchone()
        if not user:
            pytest.skip("Usuário ftoniolo@gmail.com não encontrado para teste")
            
        user_id, user_nome, user_email = user
        
        # Buscar veículo do usuário
        veiculo = self.db.execute('SELECT id FROM veiculos WHERE usuario_id = ? AND ativo = TRUE LIMIT 1', [user_id]).fetchone()
        if not veiculo:
            pytest.skip("Nenhum veículo encontrado para o usuário")
            
        veiculo_id = veiculo[0]
        
        # Buscar produto
        produto = self.db.execute('SELECT id FROM produtos WHERE ativo = TRUE LIMIT 1').fetchone()
        if not produto:
            pytest.skip("Nenhum produto encontrado")
            
        produto_id = produto[0]
        
        # Mock do envio de email
        with patch('app.email_service.send_warranty_activation_email') as mock_email:
            mock_email.return_value = True
            
            # Criar garantia
            garantia = Garantia(
                usuario_id=user_id,
                produto_id=produto_id,
                veiculo_id=veiculo_id,
                lote_fabricacao="TESTE123",
                data_instalacao="2024-09-16",
                quilometragem_instalacao=50000
            )
            
            # Inserir no banco (simulando o processo da aplicação)
            garantia_id = self.db.execute("""
                INSERT INTO garantias (usuario_id, produto_id, veiculo_id, lote_fabricacao, 
                                     data_instalacao, quilometragem_instalacao, data_vencimento, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?, DATE(?, '+2 years'), DATETIME('now'))
            """, (
                garantia.usuario_id,
                garantia.produto_id, 
                garantia.veiculo_id,
                garantia.lote_fabricacao,
                garantia.data_instalacao,
                garantia.quilometragem_instalacao,
                garantia.data_instalacao
            )).lastrowid
            
            # Simular envio de email (como na função criar_garantia)
            dados_email = self.db.execute("""
                SELECT u.nome, u.email, p.descricao as produto_nome,
                       (v.marca || ' ' || v.modelo || ' (' || v.placa || ')') as veiculo_info,
                       g.data_vencimento
                FROM garantias g
                JOIN usuarios u ON g.usuario_id = u.id
                JOIN produtos p ON g.produto_id = p.id
                JOIN veiculos v ON g.veiculo_id = v.id
                WHERE g.id = ?
            """, (garantia_id,)).fetchone()
            
            if dados_email:
                nome, email, produto_nome, veiculo_info, data_vencimento = dados_email
                
                # Chamar função de envio de email
                email_enviado = send_warranty_activation_email(
                    user_email=email,
                    user_name=nome,
                    produto_nome=produto_nome,
                    veiculo_info=veiculo_info,
                    data_vencimento=data_vencimento
                )
                
                # Verificar se o email foi "enviado"
                assert email_enviado is True
                mock_email.assert_called_once()
                
                # Verificar argumentos
                args, kwargs = mock_email.call_args
                assert kwargs['user_email'] == user_email
                assert kwargs['user_name'] == user_nome
            
            # Limpar dados de teste
            self.db.execute('DELETE FROM garantias WHERE id = ?', (garantia_id,))
    
    def test_email_content_format(self):
        """Testa formatação do conteúdo do email"""
        with patch('app.email_service.send_email') as mock_send:
            mock_send.return_value = True
            
            send_warranty_activation_email(
                user_email="ftoniolo@gmail.com",
                user_name="Francisco Toniolo",
                produto_nome="Filtro de Combustível Viemar Premium",
                veiculo_info="Honda Civic (IUY4321)",
                data_vencimento="16/09/2026"
            )
            
            # Verificar se foi chamado
            mock_send.assert_called_once()
            
            # Verificar conteúdo do email
            args, kwargs = mock_send.call_args
            email_body = args[2]
            
            assert "Francisco Toniolo" in email_body
            assert "Filtro de Combustível Viemar Premium" in email_body
            assert "Honda Civic (IUY4321)" in email_body
            assert "16/09/2026" in email_body
            assert "Sua garantia foi ativada com sucesso!" in email_body
            assert "Guarde este email como comprovante" in email_body


if __name__ == "__main__":
    pytest.main([__file__, "-v"])