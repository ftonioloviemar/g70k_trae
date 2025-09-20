#!/usr/bin/env python3
"""
Rotas para gerenciamento de garantias
"""

import logging
from datetime import datetime
from fasthtml.common import *
from monsterui.all import *
from fastlite import Database
from app.auth import login_required, get_current_user
from app.templates import *
from app.filter_component import filter_component
from app.email_service import send_warranty_activation_email
from models.garantia import Garantia

# Definir Row como um Div com classe Bootstrap
Row = lambda *args, **kwargs: Div(*args, cls=f"row {kwargs.get('cls', '')}".strip(), **{k: v for k, v in kwargs.items() if k != 'cls'})

logger = logging.getLogger(__name__)

from app.date_utils import format_date_br, format_datetime_br_short, format_date_iso, format_datetime_iso

def _format_date(date_value):
    """Formata uma data para exibição"""
    return format_date_br(date_value)

def _format_datetime(datetime_value):
    """Formata um datetime para exibição"""
    return format_datetime_br_short(datetime_value)

def setup_garantia_routes(app, db: Database):
    """Configura rotas de garantias"""
    
    def listar_garantias(request):
        """Lista garantias do cliente com filtros"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        # Obter parâmetros de filtro
        filtros = {
            'produto_sku': request.query_params.get('produto_sku', '').strip(),
            'produto_descricao': request.query_params.get('produto_descricao', '').strip(),
            'veiculo_marca': request.query_params.get('veiculo_marca', '').strip(),
            'veiculo_modelo': request.query_params.get('veiculo_modelo', '').strip(),
            'veiculo_placa': request.query_params.get('veiculo_placa', '').strip(),
            'lote_fabricacao': request.query_params.get('lote_fabricacao', '').strip(),
            'ativo': request.query_params.get('ativo', '').strip()
        }
        
        # Construir query com filtros
        where_conditions = ["g.usuario_id = ?"]
        params = [user['usuario_id']]
        
        if filtros['produto_sku']:
            where_conditions.append("p.sku LIKE ?")
            params.append(f"%{filtros['produto_sku']}%")
        
        if filtros['produto_descricao']:
            where_conditions.append("p.descricao LIKE ?")
            params.append(f"%{filtros['produto_descricao']}%")
        
        if filtros['veiculo_marca']:
            where_conditions.append("v.marca LIKE ?")
            params.append(f"%{filtros['veiculo_marca']}%")
        
        if filtros['veiculo_modelo']:
            where_conditions.append("v.modelo LIKE ?")
            params.append(f"%{filtros['veiculo_modelo']}%")
        
        if filtros['veiculo_placa']:
            where_conditions.append("v.placa LIKE ?")
            params.append(f"%{filtros['veiculo_placa']}%")
        
        if filtros['lote_fabricacao']:
            where_conditions.append("g.lote_fabricacao LIKE ?")
            params.append(f"%{filtros['lote_fabricacao']}%")
        
        if filtros['ativo']:
            ativo_bool = filtros['ativo'] == 'true'
            where_conditions.append("g.ativo = ?")
            params.append(ativo_bool)
        
        where_clause = " WHERE " + " AND ".join(where_conditions)
        
        try:
            # Buscar garantias do usuário com filtros
            select_query = f"""
                SELECT g.id, p.sku, p.descricao, v.marca, v.modelo, v.placa,
                       g.lote_fabricacao, g.data_instalacao, g.data_cadastro, 
                       g.data_vencimento, g.ativo, g.nota_fiscal, g.nome_estabelecimento,
                       g.quilometragem, g.observacoes
                FROM garantias g
                JOIN produtos p ON g.produto_id = p.id
                JOIN veiculos v ON g.veiculo_id = v.id
                {where_clause}
                ORDER BY g.data_cadastro DESC
            """
            garantias = db.execute(select_query, params).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar garantias do usuário {user['usuario_id']}: {e}")
            garantias = []
        
        # Preparar dados para a tabela
        dados_tabela = []
        for g in garantias:
            # Verificar se está vencida
            try:
                if g[9]:
                    if isinstance(g[9], str):
                        data_vencimento = datetime.strptime(g[9], '%Y-%m-%d').date()
                    else:
                        data_vencimento = g[9]
                    vencida = data_vencimento < datetime.now().date()
                else:
                    vencida = False
            except:
                vencida = False
            
            if not g[10]:  # Inativa
                status = "Inativa"
                status_class = "secondary"
            elif vencida:
                status = "Vencida"
                status_class = "danger"
            else:
                status = "Ativa"
                status_class = "success"
            
            acoes = Div(
                A("Ver", href=f"/cliente/garantias/{g[0]}", cls="btn btn-sm btn-outline-info me-1"),
                A("Desativar" if g[10] else "Ativar", 
                  href=f"/cliente/garantias/{g[0]}/toggle", 
                  cls=f"btn btn-sm btn-outline-{'danger' if g[10] else 'success'}"),
                cls="btn-group"
            )
            
            # Formatar datas
            try:
                data_instalacao_str = format_date_br(g[7])
            except:
                data_instalacao_str = "N/A"
            
            try:
                data_vencimento_str = format_date_br(g[9])
            except:
                data_vencimento_str = "N/A"
            
            dados_tabela.append([
                f"{g[1]} - {g[2]}",  # SKU - Descrição
                f"{g[3]} {g[4]} ({g[5]})",  # Marca Modelo (Placa)
                g[6] or "N/A",  # Lote
                data_instalacao_str,  # Data instalação
                data_vencimento_str,  # Data vencimento
                Span(status, cls=f"badge bg-{status_class}"),
                acoes
            ])
        
        # Definir campos de filtro para garantias do cliente
        filter_fields = [
            {'name': 'produto_sku', 'label': 'SKU do Produto', 'type': 'text'},
            {'name': 'produto_descricao', 'label': 'Descrição do Produto', 'type': 'text'},
            {'name': 'veiculo_marca', 'label': 'Marca do Veículo', 'type': 'text'},
            {'name': 'veiculo_modelo', 'label': 'Modelo do Veículo', 'type': 'text'},
            {'name': 'veiculo_placa', 'label': 'Placa do Veículo', 'type': 'text'},
            {'name': 'lote_fabricacao', 'label': 'Lote de Fabricação', 'type': 'text'},
            {'name': 'ativo', 'label': 'Status', 'type': 'select', 'options': [
                {'value': 'true', 'label': 'Ativa'},
                {'value': 'false', 'label': 'Inativa'}
            ]}
        ]
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "Ativar Nova Garantia",
                            href="/cliente/garantias/nova",
                            cls="btn btn-primary mb-3"
                        ),
                        cls="d-flex justify-content-between align-items-center"
                    )
                )
            ),
            # Componente de filtro
            filter_component(
                fields=filter_fields,
                current_filters=filtros,
                action_url="/cliente/garantias"
            ),
            Row(
                Col(
                    card_component(
                        None,  # Remove título redundante
                        table_component(
                            ["Produto", "Veículo", "Lote", "Instalação", "Vencimento", "Status", "Ações"],
                            dados_tabela
                        ) if garantias else P("Nenhuma garantia ativada ainda.", cls="text-muted text-center py-4")
                    ),
                    width=12
                )
            )
        )
        
        return base_layout("Minhas Garantias", content, user)
    
    def nova_garantia_form(request):
        """Formulário para nova garantia"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        # Capturar veiculo_id da query string se fornecido
        veiculo_id_selecionado = request.query_params.get('veiculo_id')
        
        try:
            # Buscar produtos ativos
            produtos_result = db.execute(
                "SELECT id, sku, descricao FROM produtos WHERE ativo = TRUE ORDER BY sku"
            ).fetchall()
            
            # Converter produtos para lista de dicionários
            produtos = []
            for row in produtos_result:
                produtos.append({
                    'id': row[0],
                    'sku': row[1],
                    'descricao': row[2]
                })
            
            # Buscar veículos ativos do usuário
            logger.info(f"Buscando veículos para usuário ID: {user['usuario_id']}")
            veiculos_result = db.execute("""
                SELECT id, marca, modelo, placa 
                FROM veiculos 
                WHERE usuario_id = ? AND ativo = TRUE 
                ORDER BY marca, modelo
            """, (user['usuario_id'],)).fetchall()
            
            # Converter veículos para lista de dicionários
            veiculos = []
            for row in veiculos_result:
                veiculos.append({
                    'id': row[0],
                    'marca': row[1],
                    'modelo': row[2],
                    'placa': row[3]
                })

            logger.info(f"Veículos encontrados: {len(veiculos)} - {veiculos}")
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados para nova garantia: {e}")
            produtos = []
            veiculos = []
        
        if not veiculos:
            # Redirecionar para cadastro de veículo se não tiver nenhum
            content = Container(
                Row(
                    Col(
                        alert_component(
                            "Você precisa cadastrar pelo menos um veículo antes de ativar uma garantia.",
                            "warning"
                        ),
                        card_component(
                            "Cadastrar Veículo",
                            Div(
                                P("Para ativar uma garantia, você precisa ter pelo menos um veículo cadastrado."),
                                A(
                                    "Cadastrar Veículo",
                                    href="/cliente/veiculos/novo",
                                    cls="btn btn-primary"
                                )
                            )
                        ),
                        width=6,
                        offset=3
                    )
                )
            )
            return base_layout("Nova Garantia", content, user)
        
        # Preparar dados iniciais do formulário se veiculo_id foi fornecido
        form_data = {}
        if veiculo_id_selecionado:
            form_data['veiculo_id'] = veiculo_id_selecionado
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Garantias",
                            href="/cliente/garantias",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2("Ativar Nova Garantia", cls="mb-4")
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        "Dados da Garantia",
                        garantia_form(produtos=produtos, veiculos=veiculos, garantia=form_data)
                    ),
                    width=10,
                    offset=1
                )
            )
        )
        
        return base_layout("Nova Garantia", content, user)
    
    async def criar_garantia(request):
        """Cria nova garantia"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        # Acessar dados do formulário de forma assíncrona
        form_data = await request.form()
        
        # Validar dados
        produto_id = form_data.get('produto_id', '').strip()
        veiculo_id = form_data.get('veiculo_id', '').strip()
        lote_fabricacao = form_data.get('lote_fabricacao', '').strip()
        data_instalacao = form_data.get('data_instalacao', '').strip()
        nota_fiscal = form_data.get('nota_fiscal', '').strip()
        nome_estabelecimento = form_data.get('nome_estabelecimento', '').strip()
        quilometragem = form_data.get('quilometragem', '').strip()
        observacoes = form_data.get('observacoes', '').strip()
        
        errors = {}        
        logger.info(f"Dados recebidos: produto_id={produto_id}, veiculo_id={veiculo_id}, lote_fabricacao={lote_fabricacao}, data_instalacao={data_instalacao}")
        
        # Validar produto
        if not produto_id:
            errors['produto_id'] = 'Produto é obrigatório'
        else:
            try:
                produto = db.execute(
                    "SELECT id FROM produtos WHERE id = ? AND ativo = TRUE",
                    (produto_id,)
                ).fetchone()
                if not produto:
                    errors['produto_id'] = 'Produto inválido'
            except:
                errors['produto_id'] = 'Produto inválido'
        
        # Validar veículo
        if not veiculo_id:
            errors['veiculo_id'] = 'Veículo é obrigatório'
        else:
            try:
                veiculo = db.execute(
                    "SELECT id FROM veiculos WHERE id = ? AND usuario_id = ? AND ativo = TRUE",
                    (veiculo_id, user['usuario_id'])
                ).fetchone()
                if not veiculo:
                    errors['veiculo_id'] = 'Veículo inválido'
            except:
                errors['veiculo_id'] = 'Veículo inválido'
        
        # Validar lote de fabricação
        if not lote_fabricacao:
            errors['lote_fabricacao'] = 'Lote de fabricação é obrigatório'
        elif not Garantia.validar_lote_fabricacao(lote_fabricacao):
            errors['lote_fabricacao'] = 'Formato de lote inválido (deve ter pelo menos 3 caracteres)'
        
        # Validar data de instalação
        data_instalacao_obj = None
        if not data_instalacao:
            errors['data_instalacao'] = 'Data de instalação é obrigatória'
        else:
            try:
                data_instalacao_obj = datetime.strptime(data_instalacao, '%Y-%m-%d')
                data_hoje = datetime.now().date()
                data_instalacao_date = data_instalacao_obj.date()
                
                if data_instalacao_date > data_hoje:
                    errors['data_instalacao'] = 'Data de instalação não pode ser futura'
                elif (data_hoje - data_instalacao_date).days > 30:
                    errors['data_instalacao'] = 'Data de instalação não pode ser superior a 30 dias'
            except ValueError:
                errors['data_instalacao'] = 'Data de instalação inválida'
        
        # Validar quilometragem
        quilometragem_int = None
        if quilometragem:
            try:
                quilometragem_int = int(quilometragem)
                if quilometragem_int < 0:
                    errors['quilometragem'] = 'Quilometragem não pode ser negativa'
            except ValueError:
                errors['quilometragem'] = 'Quilometragem deve ser um número'
        
        # Verificar se já existe garantia para este produto/veículo
        if not errors.get('produto_id') and not errors.get('veiculo_id'):
            garantia_existente = db.execute("""
                SELECT id FROM garantias 
                WHERE produto_id = ? AND veiculo_id = ? AND ativo = TRUE
            """, (produto_id, veiculo_id)).fetchone()
            
            if garantia_existente:
                errors['produto_id'] = 'Já existe uma garantia ativa para este produto neste veículo'
        
        if errors:
            logger.warning(f"Erros de validação encontrados: {errors}")
            # Buscar dados para reexibir o formulário
            try:
                produtos_result = db.execute(
                    "SELECT id, sku, descricao FROM produtos WHERE ativo = TRUE ORDER BY sku"
                ).fetchall()
                
                # Converter para lista de dicionários
                produtos = []
                for row in produtos_result:
                    produtos.append({
                        'id': row[0],
                        'sku': row[1],
                        'descricao': row[2]
                    })
                
                veiculos_result = db.execute("""
                    SELECT id, marca, modelo, placa 
                    FROM veiculos 
                    WHERE usuario_id = ? AND ativo = TRUE 
                    ORDER BY marca, modelo
                """, (user['usuario_id'],)).fetchall()
                
                # Converter para lista de dicionários
                veiculos = []
                for row in veiculos_result:
                    veiculos.append({
                        'id': row[0],
                        'marca': row[1],
                        'modelo': row[2],
                        'placa': row[3]
                    })
            except:
                produtos = []
                veiculos = []
            
            content = Container(
                Row(
                    Col(
                        Div(
                            A(
                                "← Voltar para Garantias",
                                href="/cliente/garantias",
                                cls="btn btn-outline-secondary mb-3"
                            ),
                            H2("Ativar Nova Garantia", cls="mb-4")
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
                            "Dados da Garantia",
                            garantia_form(produtos, veiculos, {
                                'produto_id': produto_id,
                                'veiculo_id': veiculo_id,
                                'lote_fabricacao': lote_fabricacao,
                                'data_instalacao': data_instalacao,
                                'nota_fiscal': nota_fiscal,
                                'nome_estabelecimento': nome_estabelecimento,
                                'quilometragem': quilometragem,
                                'observacoes': observacoes
                            }, errors)
                        ),
                        width=10,
                        offset=1
                    )
                )
            )
            return base_layout("Nova Garantia", content, user)
        
        try:
            # Criar garantia
            garantia = Garantia(
                usuario_id=user['usuario_id'],
                produto_id=int(produto_id),
                veiculo_id=int(veiculo_id),
                lote_fabricacao=lote_fabricacao,
                data_instalacao=data_instalacao_obj,
                nota_fiscal=nota_fiscal or None,
                nome_estabelecimento=nome_estabelecimento or None,
                quilometragem=quilometragem_int,
                data_cadastro=datetime.now(),
                ativo=True,
                observacoes=observacoes or None
            )
            
            # A data de vencimento é calculada automaticamente no __post_init__
            
            # Inserir no banco
            db.execute("""
                INSERT INTO garantias (
                    usuario_id, produto_id, veiculo_id, lote_fabricacao, data_instalacao,
                    nota_fiscal, nome_estabelecimento, quilometragem, data_cadastro,
                    data_vencimento, ativo, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                garantia.usuario_id, garantia.produto_id, garantia.veiculo_id,
                garantia.lote_fabricacao, format_date_iso(garantia.data_instalacao),
                garantia.nota_fiscal, garantia.nome_estabelecimento, garantia.quilometragem,
                format_datetime_iso(garantia.data_cadastro), format_date_iso(garantia.data_vencimento),
                garantia.ativo, garantia.observacoes
            ))
            
            garantia_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            
            logger.info(f"Nova garantia ativada: ID {garantia_id} pelo usuário {user['usuario_id']}")
            
            # Enviar email de confirmação de garantia ativada de forma assíncrona
            try:
                # Buscar dados para o email
                dados_email = db.execute("""
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
                    # Extrair dados da tupla
                    nome, email, produto_nome, veiculo_info, data_vencimento = dados_email
                    
                    # Formatar data de vencimento
                    data_vencimento_formatada = _format_date(data_vencimento)
                    
                    # Enviar email de forma assíncrona
                    from app.async_tasks import send_warranty_activation_email_async
                    send_warranty_activation_email_async(
                        user_email=email,
                        user_name=nome,
                        produto_nome=produto_nome,
                        veiculo_info=veiculo_info,
                        data_vencimento=data_vencimento_formatada
                    )
                    
                    logger.info(f"Email de garantia ativada agendado para envio assíncrono: {email}")
                else:
                    logger.error(f"Não foi possível buscar dados para envio de email da garantia {garantia_id}")
                    
            except Exception as e:
                logger.error(f"Erro ao agendar envio de email de garantia ativada: {e}")
            
            return RedirectResponse('/cliente/garantias?sucesso=ativada', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao ativar garantia para usuário {user['usuario_id']}: {e}")
            
            # Buscar dados para reexibir o formulário
            try:
                produtos_raw = db.execute(
                    "SELECT id, sku, descricao FROM produtos WHERE ativo = TRUE ORDER BY sku"
                ).fetchall()
                produtos = [{'id': p[0], 'sku': p[1], 'descricao': p[2]} for p in produtos_raw]
                
                veiculos_raw = db.execute("""
                    SELECT id, marca, modelo, placa 
                    FROM veiculos 
                    WHERE usuario_id = ? AND ativo = TRUE 
                    ORDER BY marca, modelo
                """, (user['usuario_id'],)).fetchall()
                veiculos = [{'id': v[0], 'marca': v[1], 'modelo': v[2], 'placa': v[3]} for v in veiculos_raw]
            except:
                produtos = []
                veiculos = []
            
            content = Container(
                Row(
                    Col(
                        Div(
                            A(
                                "← Voltar para Garantias",
                                href="/cliente/garantias",
                                cls="btn btn-outline-secondary mb-3"
                            ),
                            H2("Ativar Nova Garantia", cls="mb-4")
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
                            "Dados da Garantia",
                            garantia_form(produtos, veiculos, {
                                'produto_id': produto_id,
                                'veiculo_id': veiculo_id,
                                'lote_fabricacao': lote_fabricacao,
                                'data_instalacao': data_instalacao,
                                'nota_fiscal': nota_fiscal,
                                'nome_estabelecimento': nome_estabelecimento,
                                'quilometragem': quilometragem,
                                'observacoes': observacoes
                            })
                        ),
                        width=10,
                        offset=1
                    )
                )
            )
            return base_layout("Nova Garantia", content, user)
    
    def ver_garantia(request):
        """Visualizar detalhes da garantia"""
        user = request.state.usuario
        garantia_id = request.path_params['garantia_id']
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        try:
            # Buscar garantia com dados relacionados
            garantia = db.execute("""
                SELECT g.id, g.lote_fabricacao, g.data_instalacao, g.nota_fiscal,
                       g.nome_estabelecimento, g.quilometragem, g.data_cadastro,
                       g.data_vencimento, g.ativo, g.observacoes,
                       p.sku, p.descricao as produto_descricao,
                       v.marca, v.modelo, v.ano_modelo, v.placa, v.cor
                FROM garantias g
                JOIN produtos p ON g.produto_id = p.id
                JOIN veiculos v ON g.veiculo_id = v.id
                WHERE g.id = ? AND g.usuario_id = ?
            """, (garantia_id, user['usuario_id'])).fetchone()
            
            if not garantia:
                return RedirectResponse('/cliente/garantias?erro=nao_encontrada', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao buscar garantia {garantia_id} do usuário {user['usuario_id']}: {e}")
            return RedirectResponse('/cliente/garantias?erro=interno', status_code=302)
        
        # Verificar status da garantia
        data_vencimento = None
        if garantia[7]:
            if isinstance(garantia[7], str):
                try:
                    data_vencimento = datetime.strptime(garantia[7], '%Y-%m-%d').date()
                except ValueError:
                    data_vencimento = None
            else:
                data_vencimento = garantia[7]
        
        vencida = data_vencimento and data_vencimento < datetime.now().date() if data_vencimento else False
        
        if not garantia[8]:  # Inativa
            status = "Inativa"
            status_class = "secondary"
        elif vencida:
            status = "Vencida"
            status_class = "danger"
        else:
            status = "Ativa"
            status_class = "success"
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Garantias",
                            href="/cliente/garantias",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2(f"Garantia #{garantia[0]}", cls="mb-4")
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        "Informações da Garantia",
                        Div(
                            Div(
                                Span(status, cls=f"badge bg-{status_class} fs-6 mb-3")
                            ),
                            Div(
                                H5("Produto"),
                                P(f"{garantia[10]} - {garantia[11]}", cls="mb-3"),
                                
                                H5("Veículo"),
                                P(f"{garantia[12]} {garantia[13]} {garantia[14]} - {garantia[15]}", cls="mb-3"),
                                P(f"Cor: {garantia[16] or 'N/A'}", cls="text-muted mb-3"),
                                
                                H5("Detalhes da Garantia"),
                                P(f"Lote de Fabricação: {garantia[1]}"),
                                P(f"Data de Instalação: {_format_date(garantia[2]) if garantia[2] else 'N/A'}"),
                                P(f"Data de Cadastro: {_format_datetime(garantia[6]) if garantia[6] else 'N/A'}"),
                                P(f"Data de Vencimento: {_format_date(data_vencimento) if data_vencimento else 'N/A'}"),
                                
                                H5("Informações Adicionais", cls="mt-4"),
                                P(f"Nota Fiscal: {garantia[3] or 'N/A'}"),
                                P(f"Estabelecimento: {garantia[4] or 'N/A'}"),
                                P(f"Quilometragem: {garantia[5]:,} km" if garantia[5] else "Quilometragem: N/A"),
                                
                                (Div(
                                    H5("Observações", cls="mt-4"),
                                    P(garantia[9], cls="text-muted")
                                ) if garantia[9] else ""),
                                
                                Div(
                                    A(
                                        "Desativar Garantia" if garantia[8] else "Ativar Garantia",
                                        href=f"/cliente/garantias/{garantia[0]}/toggle",
                                        cls=f"btn btn-{'danger' if garantia[8] else 'success'} mt-3"
                                    ),
                                    cls="mt-4"
                                )
                            )
                        )
                    ),
                    width=8,
                    offset=2
                )
            )
        )
        
        return base_layout(f"Garantia #{garantia[0]}", content, user)
    
    def toggle_garantia(request):
        """Ativa/desativa garantia"""
        user = request.state.usuario
        garantia_id = request.path_params['garantia_id']
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        try:
            # Buscar status atual
            garantia = db.execute(
                "SELECT ativo FROM garantias WHERE id = ? AND usuario_id = ?",
                (garantia_id, user['usuario_id'])
            ).fetchone()
            
            if not garantia:
                return RedirectResponse('/cliente/garantias?erro=nao_encontrada', status_code=302)
            
            # Alternar status
            novo_status = not garantia[0]
            
            db.execute(
                "UPDATE garantias SET ativo = ? WHERE id = ? AND usuario_id = ?",
                (novo_status, garantia_id, user['usuario_id'])
            )
            
            action = "ativada" if novo_status else "desativada"
            
            logger.info(f"Garantia {garantia_id} {action} pelo usuário {user['usuario_id']}")
            
            return RedirectResponse(f'/cliente/garantias?sucesso={action}', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao alterar status da garantia {garantia_id}: {e}")
            return RedirectResponse('/cliente/garantias?erro=interno', status_code=302)

    # Registrar rotas
    listar_garantias = login_required(listar_garantias)
    app.get("/cliente/garantias")(listar_garantias)
    
    nova_garantia_form = login_required(nova_garantia_form)
    app.get("/cliente/garantias/nova")(nova_garantia_form)
    
    ver_garantia = login_required(ver_garantia)
    app.get("/cliente/garantias/{garantia_id}")(ver_garantia)
    
    toggle_garantia = login_required(toggle_garantia)
    app.get("/cliente/garantias/{garantia_id}/toggle")(toggle_garantia)
    
    criar_garantia = login_required(criar_garantia)
    app.post("/cliente/garantias/nova")(criar_garantia)
    
    logger.info("Rotas de garantias configuradas com sucesso")