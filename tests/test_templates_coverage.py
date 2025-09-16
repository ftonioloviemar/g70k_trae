#!/usr/bin/env python3
"""
Testes para melhorar cobertura do módulo templates
"""

import pytest
from fasthtml.common import *
from app.templates import (
    base_layout, footer_component, alert_component, card_component,
    form_group, login_form, cadastro_form
)

class TestTemplates:
    """Testes para os templates da aplicação"""
    
    def test_base_layout_basic(self):
        """Testa layout base básico"""
        content = Div("Conteúdo de teste")
        result = base_layout("Título Teste", content)
        
        assert result is not None
        # Verificar se é um elemento HTML válido
        assert hasattr(result, 'tag')
    
    def test_base_layout_with_user(self):
        """Testa layout base com usuário logado"""
        content = Div("Conteúdo de teste")
        user_data = {
            'nome': 'Usuário Teste',
            'email': 'teste@example.com',
            'tipo_usuario': 'cliente'
        }
        
        result = base_template("Título Teste", content, user=user_data)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_base_template_admin_user(self):
        """Testa template base com usuário administrador"""
        content = Div("Conteúdo de teste")
        admin_user = {
            'nome': 'Admin Teste',
            'email': 'admin@example.com',
            'tipo_usuario': 'administrador'
        }
        
        result = base_template("Admin Panel", content, user=admin_user)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_login_template_basic(self):
        """Testa template de login básico"""
        result = login_template()
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_login_template_with_error(self):
        """Testa template de login com erro"""
        result = login_template(erro="Credenciais inválidas")
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_login_template_with_email(self):
        """Testa template de login com email preenchido"""
        result = login_template(email="teste@example.com")
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_cadastro_template_basic(self):
        """Testa template de cadastro básico"""
        result = cadastro_template()
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_cadastro_template_with_error(self):
        """Testa template de cadastro com erro"""
        result = cadastro_template(erro="Email já cadastrado")
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_cadastro_template_with_form_data(self):
        """Testa template de cadastro com dados do formulário"""
        form_data = {
            'nome': 'Teste Usuario',
            'email': 'teste@example.com',
            'telefone': '11999999999'
        }
        
        result = cadastro_template(form_data=form_data)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_dashboard_template_basic(self):
        """Testa template de dashboard básico"""
        user_data = {
            'nome': 'Usuário Teste',
            'email': 'teste@example.com'
        }
        
        result = dashboard_template(user=user_data)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_dashboard_template_with_stats(self):
        """Testa template de dashboard com estatísticas"""
        user_data = {
            'nome': 'Usuário Teste',
            'email': 'teste@example.com'
        }
        
        stats = {
            'total_veiculos': 5,
            'total_garantias': 3,
            'garantias_ativas': 2
        }
        
        result = dashboard_template(user=user_data, stats=stats)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_admin_template_basic(self):
        """Testa template de administração básico"""
        admin_user = {
            'nome': 'Admin Teste',
            'email': 'admin@example.com',
            'tipo_usuario': 'administrador'
        }
        
        content = Div("Conteúdo administrativo")
        result = admin_template("Painel Admin", content, user=admin_user)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_veiculos_template_empty(self):
        """Testa template de veículos sem dados"""
        user_data = {
            'nome': 'Usuário Teste',
            'email': 'teste@example.com'
        }
        
        result = veiculos_template(user=user_data, veiculos=[])
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_veiculos_template_with_data(self):
        """Testa template de veículos com dados"""
        user_data = {
            'nome': 'Usuário Teste',
            'email': 'teste@example.com'
        }
        
        veiculos = [
            {
                'id': 1,
                'marca': 'Toyota',
                'modelo': 'Corolla',
                'ano_modelo': 2020,
                'placa': 'ABC1234'
            },
            {
                'id': 2,
                'marca': 'Honda',
                'modelo': 'Civic',
                'ano_modelo': 2021,
                'placa': 'XYZ5678'
            }
        ]
        
        result = veiculos_template(user=user_data, veiculos=veiculos)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_garantias_template_empty(self):
        """Testa template de garantias sem dados"""
        user_data = {
            'nome': 'Usuário Teste',
            'email': 'teste@example.com'
        }
        
        result = garantias_template(user=user_data, garantias=[])
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_garantias_template_with_data(self):
        """Testa template de garantias com dados"""
        user_data = {
            'nome': 'Usuário Teste',
            'email': 'teste@example.com'
        }
        
        garantias = [
            {
                'id': 1,
                'veiculo_marca': 'Toyota',
                'veiculo_modelo': 'Corolla',
                'produto_nome': 'Garantia Estendida',
                'data_inicio': '2024-01-01',
                'data_fim': '2025-01-01',
                'status': 'ativa'
            }
        ]
        
        result = garantias_template(user=user_data, garantias=garantias)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_error_template_basic(self):
        """Testa template de erro básico"""
        result = error_template("Erro de teste", "Descrição do erro")
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_error_template_with_code(self):
        """Testa template de erro com código"""
        result = error_template("Erro 404", "Página não encontrada", error_code=404)
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_success_template_basic(self):
        """Testa template de sucesso básico"""
        result = success_template("Operação realizada", "Dados salvos com sucesso")
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_success_template_with_redirect(self):
        """Testa template de sucesso com redirecionamento"""
        result = success_template(
            "Cadastro realizado", 
            "Usuário criado com sucesso",
            redirect_url="/dashboard",
            redirect_text="Ir para Dashboard"
        )
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_confirmation_template_basic(self):
        """Testa template de confirmação básico"""
        result = confirmation_template(
            "Confirmar ação",
            "Deseja realmente excluir este item?",
            "/delete/1"
        )
        
        assert result is not None
        assert hasattr(result, 'tag')
    
    def test_confirmation_template_with_cancel(self):
        """Testa template de confirmação com cancelamento"""
        result = confirmation_template(
            "Confirmar exclusão",
            "Esta ação não pode ser desfeita",
            "/delete/1",
            cancel_url="/dashboard"
        )
        
        assert result is not None
        assert hasattr(result, 'tag')