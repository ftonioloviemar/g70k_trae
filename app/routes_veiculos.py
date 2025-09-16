#!/usr/bin/env python3
"""
Rotas para gerenciamento de veículos
"""

import logging
from datetime import datetime
from fasthtml.common import *
from monsterui.all import *
from fastlite import Database
from app.auth import login_required, get_current_user
from app.templates import *
from models.veiculo import Veiculo
from models.usuario import Usuario

# Definir Row como um Div com classe Bootstrap
Row = lambda *args, **kwargs: Div(*args, cls=f"row {kwargs.get('cls', '')}".strip(), **{k: v for k, v in kwargs.items() if k != 'cls'})

logger = logging.getLogger(__name__)

def setup_veiculo_routes(app, db: Database):
    """Configura rotas de veículos"""
    
    def listar_veiculos(request):
        """Lista veículos do cliente"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        try:
            # Buscar veículos do usuário
            veiculos = db.execute("""
                SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
                FROM veiculos 
                WHERE usuario_id = ? 
                ORDER BY data_cadastro DESC
            """, (user['usuario_id'],)).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar veículos do usuário {user['usuario_id']}: {e}")
            veiculos = []
        
        # Preparar dados para a tabela
        dados_tabela = []
        for v in veiculos:
            status = "Ativo" if v[8] else "Inativo"
            status_class = "success" if v[8] else "secondary"
            
            acoes = Div(
                A("Editar", href=f"/cliente/veiculos/{v[0]}/editar", cls="btn btn-sm btn-outline-primary me-1"),
                A("Nova Garantia", href=f"/cliente/garantias/nova?veiculo_id={v[0]}", cls="btn btn-sm btn-outline-primary me-1"),
                A("Desativar" if v[8] else "Ativar", 
                  href=f"/cliente/veiculos/{v[0]}/toggle", 
                  cls=f"btn btn-sm btn-outline-{'danger' if v[8] else 'primary'}"),
                cls="btn-group"
            )
            
            dados_tabela.append([
                f"{v[1]} {v[2]}",  # Marca Modelo
                str(v[3]),  # Ano
                Veiculo.formatar_placa_estatico(v[4]),  # Placa formatada
                v[5] or "N/A",  # Cor
                Span(status, cls=f"badge bg-{status_class}"),
                acoes
            ])
        
        content = Container(
            Row(
                Col(
                    Div(
                        H2("Meus Veículos", cls="mb-3"),
                        A(
                            "Cadastrar Novo Veículo",
                            href="/cliente/veiculos/novo",
                            cls="btn btn-primary mb-3"
                        ),
                        cls="d-flex justify-content-between align-items-center"
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        None,  # Remove título redundante
                        table_component(
                            ["Veículo", "Ano", "Placa", "Cor", "Status", "Ações"],
                            dados_tabela
                        ) if veiculos else P("Nenhum veículo cadastrado ainda.", cls="text-muted text-center py-4")
                    ),
                    width=12
                )
            )
        )
        
        return base_layout("Meus Veículos", content, user)
    
    def novo_veiculo_form(request):
        """Formulário para novo veículo"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Veículos",
                            href="/cliente/veiculos",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2("Cadastrar Novo Veículo", cls="mb-4")
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        "Dados do Veículo",
                        veiculo_form()
                    ),
                    width=8,
                    offset=2
                )
            )
        )
        
        return base_layout("Novo Veículo", content, user)
    
    async def criar_veiculo(request):
        """Cria novo veículo"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        # Acessar dados do formulário
        form_data = await request.form()
        
        # Validar dados
        marca = form_data.get('marca', '').strip()
        modelo = form_data.get('modelo', '').strip()
        ano_modelo = form_data.get('ano_modelo', '').strip()
        placa = form_data.get('placa', '').strip().upper()
        cor = form_data.get('cor', '').strip()
        chassi = form_data.get('chassi', '').strip().upper()
        
        errors = {}
        
        # Validação de marca
        if not marca:
            errors['marca'] = 'A marca do veículo é obrigatória'
        elif len(marca) < 2:
            errors['marca'] = 'A marca deve ter pelo menos 2 caracteres'
        elif len(marca) > 50:
            errors['marca'] = 'A marca não pode ter mais de 50 caracteres'
        
        # Validação de modelo
        if not modelo:
            errors['modelo'] = 'O modelo do veículo é obrigatório'
        elif len(modelo) < 2:
            errors['modelo'] = 'O modelo deve ter pelo menos 2 caracteres'
        elif len(modelo) > 50:
            errors['modelo'] = 'O modelo não pode ter mais de 50 caracteres'
        
        # Validação de ano/modelo
        if not ano_modelo:
            errors['ano_modelo'] = 'O ano/modelo é obrigatório'
        else:
            try:
                # Extrair o primeiro ano se estiver no formato 2020/2021
                primeiro_ano = ano_modelo.split('/')[0].strip()
                ano_int = int(primeiro_ano)
                ano_atual = datetime.now().year
                if ano_int < 1900:
                    errors['ano_modelo'] = 'Ano não pode ser anterior a 1900'
                elif ano_int > ano_atual + 1:
                    errors['ano_modelo'] = f'Ano não pode ser posterior a {ano_atual + 1}'
            except ValueError:
                errors['ano_modelo'] = 'Formato de ano inválido. Use: 2020 ou 2020/2021'
        
        # Validação de placa
        if not placa:
            errors['placa'] = 'A placa do veículo é obrigatória'
        elif not Veiculo.validar_placa(placa):
            errors['placa'] = 'Formato inválido. Use: ABC1234 (antigo) ou ABC1D23 (Mercosul)'
        
        # Validação de cor (opcional)
        if cor and len(cor) > 30:
            errors['cor'] = 'A cor não pode ter mais de 30 caracteres'
        
        # Validação de chassi (opcional)
        if chassi:
            import re
            if len(chassi) != 17:
                errors['chassi'] = 'O chassi deve ter exatamente 17 caracteres'
            elif not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', chassi):
                errors['chassi'] = 'Chassi contém caracteres inválidos (não use I, O ou Q)'
        
        # Verificar se placa já existe
        if not errors.get('placa'):
            placa_existente = db.execute(
                "SELECT id FROM veiculos WHERE placa = ? AND ativo = TRUE",
                (placa,)
            ).fetchone()
            
            if placa_existente:
                errors['placa'] = 'Esta placa já está cadastrada no sistema'
        
        # Verificar se chassi já existe (se fornecido)
        if chassi and not errors.get('chassi'):
            chassi_existente = db.execute(
                "SELECT id FROM veiculos WHERE chassi = ? AND chassi != '' AND ativo = TRUE",
                (chassi,)
            ).fetchone()
            
            if chassi_existente:
                errors['chassi'] = 'Este chassi já está cadastrado no sistema'
        
        if errors:
            # Retornar formulário com erros
            content = Container(
                Row(
                    Col(
                        Div(
                            A(
                                "← Voltar para Veículos",
                                href="/cliente/veiculos",
                                cls="btn btn-outline-secondary mb-3"
                            ),
                            H2("Cadastrar Novo Veículo", cls="mb-4")
                        )
                    )
                ),
                Row(
                    Col(
                        alert_component(
                            "Corrija os erros abaixo:",
                            "danger"
                        ),
                        card_component(
                            "Dados do Veículo",
                            veiculo_form(form_data, is_edit=False, errors=errors)
                        ),
                        width=8,
                        offset=2
                    )
                )
            )
            return base_layout("Novo Veículo", content, user)
        
        try:
            # Criar veículo
            veiculo = Veiculo(
                usuario_id=user['usuario_id'],
                marca=marca,
                modelo=modelo,
                ano_modelo=ano_modelo,
                placa=placa,
                cor=cor,
                chassi=chassi,
                data_cadastro=datetime.now(),
                ativo=True
            )
            
            # Inserir no banco
            db.execute("""
                INSERT INTO veiculos (
                    usuario_id, marca, modelo, ano_modelo, placa, cor, chassi, data_cadastro, ativo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                veiculo.usuario_id, veiculo.marca, veiculo.modelo, veiculo.ano_modelo,
                veiculo.placa, veiculo.cor, veiculo.chassi, veiculo.data_cadastro.strftime('%Y-%m-%d %H:%M:%S'), veiculo.ativo
            ))
            
            # Obter o ID do veículo inserido
            veiculo_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            
            logger.info(f"Novo veículo cadastrado: {placa} (ID: {veiculo_id}) pelo usuário {user['usuario_id']}")
            
            return RedirectResponse('/cliente/veiculos?sucesso=cadastrado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao cadastrar veículo para usuário {user['usuario_id']}: {e}")
            
            content = Container(
                Row(
                    Col(
                        Div(
                            A(
                                "← Voltar para Veículos",
                                href="/cliente/veiculos",
                                cls="btn btn-outline-secondary mb-3"
                            ),
                            H2("Cadastrar Novo Veículo", cls="mb-4")
                        )
                    )
                ),
                Row(
                    Col(
                        alert_component(
                            "Erro interno. Tente novamente mais tarde.",
                            "danger"
                        ),
                        card_component(
                            "Dados do Veículo",
                            veiculo_form()
                        ),
                        width=8,
                        offset=2
                    )
                )
            )
            return base_layout("Novo Veículo", content, user)
    
    def editar_veiculo_form(request):
        """Formulário para editar veículo"""
        user = request.state.usuario
        veiculo_id = request.path_params['veiculo_id']
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        try:
            # Buscar veículo
            veiculo = db.execute("""
                SELECT id, marca, modelo, ano_modelo, placa, cor, chassi, ativo
                FROM veiculos 
                WHERE id = ? AND usuario_id = ?
            """, (veiculo_id, user['usuario_id'])).fetchone()
            
            if not veiculo:
                return RedirectResponse('/cliente/veiculos?erro=nao_encontrado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao buscar veículo {veiculo_id} do usuário {user['usuario_id']}: {e}")
            return RedirectResponse('/cliente/veiculos?erro=interno', status_code=302)
        
        # Preparar dados do formulário
        form_data = {
            'marca': veiculo[1],
            'modelo': veiculo[2],
            'ano_modelo': str(veiculo[3]),
            'placa': veiculo[4],
            'cor': veiculo[5] or '',
            'chassi': veiculo[6] or ''
        }
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Veículos",
                            href="/cliente/veiculos",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2(f"Editar Veículo - {veiculo[4]}", cls="mb-4")
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        "Dados do Veículo",
                        veiculo_form(form_data, is_edit=True, veiculo_id=veiculo_id)
                    ),
                    width=8,
                    offset=2
                )
            )
        )
        
        return base_layout("Editar Veículo", content, user)
    
    async def atualizar_veiculo(request):
        """Atualiza dados do veículo"""
        user = request.state.usuario
        veiculo_id = request.path_params['veiculo_id']
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        # Verificar se veículo pertence ao usuário
        try:
            veiculo_atual = db.execute(
                "SELECT placa FROM veiculos WHERE id = ? AND usuario_id = ?",
                (veiculo_id, user['usuario_id'])
            ).fetchone()
            
            if not veiculo_atual:
                return RedirectResponse('/cliente/veiculos?erro=nao_encontrado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao verificar veículo {veiculo_id}: {e}")
            return RedirectResponse('/cliente/veiculos?erro=interno', status_code=302)
        
        # Acessar dados do formulário
        form_data = await request.form()
        
        # Validar dados
        marca = form_data.get('marca', '').strip()
        modelo = form_data.get('modelo', '').strip()
        ano = form_data.get('ano_modelo', '').strip()
        placa = form_data.get('placa', '').strip().upper()
        cor = form_data.get('cor', '').strip()
        chassi = form_data.get('chassi', '').strip().upper()
        
        errors = {}
        
        if not marca:
            errors['marca'] = 'Marca é obrigatória'
        
        if not modelo:
            errors['modelo'] = 'Modelo é obrigatório'
        
        if not ano:
            errors['ano_modelo'] = 'Ano é obrigatório'
        else:
            try:
                # Extrair o primeiro ano se estiver no formato 2020/2021
                primeiro_ano = ano.split('/')[0].strip()
                ano_int = int(primeiro_ano)
                if ano_int < 1900 or ano_int > datetime.now().year + 1:
                    errors['ano_modelo'] = 'Ano inválido'
            except ValueError:
                errors['ano_modelo'] = 'Ano deve ser um número válido (ex: 2020 ou 2020/2021)'
        
        if not placa:
            errors['placa'] = 'Placa é obrigatória'
        elif not Veiculo.validar_placa(placa):
            errors['placa'] = 'Formato de placa inválido (ABC1234 ou ABC1D23)'
        
        # Verificar se placa já existe (exceto o próprio veículo)
        if not errors.get('placa') and placa.replace('-', '').replace(' ', '') != veiculo_atual[0].replace('-', '').replace(' ', ''):
            placa_existente = db.execute(
                "SELECT id FROM veiculos WHERE placa = ? AND ativo = TRUE AND id != ?",
                (placa, veiculo_id)
            ).fetchone()
            
            if placa_existente:
                errors['placa'] = 'Esta placa já está cadastrada'
        
        if errors:
            # Retornar formulário com erros
            content = Container(
                Row(
                    Col(
                        Div(
                            A(
                                "← Voltar para Veículos",
                                href="/cliente/veiculos",
                                cls="btn btn-outline-secondary mb-3"
                            ),
                            H2(f"Editar Veículo - {veiculo_atual[0]}", cls="mb-4")
                        )
                    )
                ),
                Row(
                    Col(
                        alert_component(
                            "Corrija os erros abaixo:",
                            "danger"
                        ),
                        card_component(
                            "Dados do Veículo",
                            veiculo_form(form_data, is_edit=True, errors=errors, veiculo_id=veiculo_id)
                        ),
                        width=8,
                        offset=2
                    )
                )
            )
            return base_layout("Editar Veículo", content, user)
        
        try:
            # Atualizar veículo
            db.execute("""
                UPDATE veiculos 
                SET marca = ?, modelo = ?, ano_modelo = ?, placa = ?, cor = ?, chassi = ?
                WHERE id = ? AND usuario_id = ?
            """, (
                marca, modelo, ano, placa, cor, chassi, veiculo_id, user['usuario_id']
            ))
            
            logger.info(f"Veículo {veiculo_id} atualizado pelo usuário {user['usuario_id']}")
            return RedirectResponse('/cliente/veiculos?sucesso=atualizado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar veículo {veiculo_id}: {str(e)}")
            return RedirectResponse('/cliente/veiculos?erro=atualizacao', status_code=302)

            
            logger.info(f"Veículo {veiculo_id} atualizado pelo usuário {user['usuario_id']}")
            
            return RedirectResponse('/cliente/veiculos?sucesso=atualizado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar veículo {veiculo_id}: {e}")
            return RedirectResponse('/cliente/veiculos?erro=interno', status_code=302)
    
    def toggle_veiculo(request):
        """Ativa/desativa veículo"""
        user = request.state.usuario
        veiculo_id = request.path_params['veiculo_id']
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        try:
            # Buscar status atual
            veiculo = db.execute(
                "SELECT ativo FROM veiculos WHERE id = ? AND usuario_id = ?",
                (veiculo_id, user['usuario_id'])
            ).fetchone()
            
            if not veiculo:
                return RedirectResponse('/cliente/veiculos?erro=nao_encontrado', status_code=302)
            
            # Alternar status
            novo_status = not veiculo[0]
            
            db.execute(
                "UPDATE veiculos SET ativo = ? WHERE id = ? AND usuario_id = ?",
                (novo_status, veiculo_id, user['usuario_id'])
            )
            
            action = "ativado" if novo_status else "desativado"
            logger.info(f"Veículo {veiculo_id} {action} pelo usuário {user['usuario_id']}")
            
            return RedirectResponse(f'/cliente/veiculos?sucesso={action}', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao alterar status do veículo {veiculo_id}: {str(e)}")
            return RedirectResponse('/cliente/veiculos?erro=toggle', status_code=302)

    # Aplicar decoradores e registrar rotas na ordem correta
    listar_veiculos = login_required(listar_veiculos)
    app.get("/cliente/veiculos")(listar_veiculos)
    
    novo_veiculo_form = login_required(novo_veiculo_form)
    app.get("/cliente/veiculos/novo")(novo_veiculo_form)
    
    criar_veiculo = login_required(criar_veiculo)
    app.post("/cliente/veiculos")(criar_veiculo)
    
    editar_veiculo_form = login_required(editar_veiculo_form)
    app.get("/cliente/veiculos/{veiculo_id}/editar")(editar_veiculo_form)
    
    atualizar_veiculo = login_required(atualizar_veiculo)
    app.post("/cliente/veiculos/{veiculo_id}")(atualizar_veiculo)
    
    toggle_veiculo = login_required(toggle_veiculo)
    app.get("/cliente/veiculos/{veiculo_id}/toggle")(toggle_veiculo)

    logger.info("Rotas de veículos configuradas com sucesso")