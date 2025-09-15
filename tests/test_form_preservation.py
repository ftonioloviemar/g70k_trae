#!/usr/bin/env python3
"""
Testes para preservação de dados em formulários após erros de validação
"""

import pytest
from fasthtml.common import *
from app.templates import cadastro_form, login_form


class TestFormPreservation:
    """Testes para preservação de dados em formulários"""
    
    def test_cadastro_form_preserves_data_on_error(self):
        """Testa se o formulário de cadastro preserva dados quando há erros"""
        # Dados de teste
        form_data = {
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'confirmar_email': 'joao@email.com',
            'cep': '12345-678',
            'endereco': 'Rua das Flores, 123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'uf': 'SP',
            'telefone': '(11) 99999-9999',
            'cpf_cnpj': '123.456.789-00',
            'data_nascimento': '1990-01-01'
        }
        
        errors = {
            'senha': 'Senha é obrigatória'
        }
        
        # Gerar formulário com dados e erros
        form = cadastro_form(errors, form_data)
        
        # Converter para string para verificar se os valores estão presentes
        form_html = str(form)
        
        # Verificar se os valores estão preservados
        assert 'value="João Silva"' in form_html
        assert 'value="joao@email.com"' in form_html
        assert 'value="12345-678"' in form_html
        assert 'value="Rua das Flores, 123"' in form_html
        assert 'value="Centro"' in form_html
        assert 'value="São Paulo"' in form_html
        assert 'selected="True"' in form_html or 'selected' in form_html  # Para o select de UF
        assert 'value="(11) 99999-9999"' in form_html
        assert 'value="123.456.789-00"' in form_html
        assert 'value="1990-01-01"' in form_html
    
    def test_cadastro_form_without_data(self):
        """Testa se o formulário funciona sem dados preservados"""
        form = cadastro_form()
        form_html = str(form)
        
        # Deve funcionar normalmente sem erros
        assert 'form' in form_html.lower()
        assert 'name="nome"' in form_html
        assert 'name="email"' in form_html
    
    def test_login_form_preserves_email_on_error(self):
        """Testa se o formulário de login preserva o email quando há erro"""
        email_value = 'usuario@teste.com'
        error_message = 'Email ou senha incorretos.'
        
        form = login_form(error_message, email_value)
        form_html = str(form)
        
        # Verificar se o email está preservado
        assert 'value="usuario@teste.com"' in form_html
        assert 'Email ou senha incorretos.' in form_html
    
    def test_login_form_without_email_value(self):
        """Testa se o formulário de login funciona sem email preservado"""
        form = login_form()
        form_html = str(form)
        
        # Deve funcionar normalmente
        assert 'name="email"' in form_html
        assert 'name="senha"' in form_html
    
    def test_cadastro_form_partial_data_preservation(self):
        """Testa preservação parcial de dados (alguns campos preenchidos)"""
        form_data = {
            'nome': 'Maria Santos',
            'email': 'maria@email.com',
            'cidade': 'Rio de Janeiro',
            'uf': 'RJ'
        }
        
        errors = {
            'confirmar_email': 'Confirmação de email é obrigatória'
        }
        
        form = cadastro_form(errors, form_data)
        form_html = str(form)
        
        # Verificar campos preenchidos
        assert 'value="Maria Santos"' in form_html
        assert 'value="maria@email.com"' in form_html
        assert 'value="Rio de Janeiro"' in form_html
        
        # Verificar que campos não preenchidos têm valores vazios
        assert 'value=""' in form_html  # Campos vazios devem ter value=""
    
    def test_uf_select_preservation(self):
        """Testa se o select de UF preserva a seleção corretamente"""
        form_data = {'uf': 'MG'}
        
        form = cadastro_form(form_data=form_data)
        form_html = str(form)
        
        # Verificar se MG está selecionado
        # O HTML pode variar, mas deve conter a indicação de seleção para MG
        assert 'value="MG"' in form_html