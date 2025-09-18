#!/usr/bin/env python3
"""
Rotas administrativas
"""

import logging
import math
from datetime import datetime
from fasthtml.common import *
from monsterui.all import *
from fastlite import Database
from app.auth import admin_required, get_current_user
from app.templates import *
from models.usuario import Usuario
from models.produto import Produto

# Definir Row como um Div com classe Bootstrap
Row = lambda *args, **kwargs: Div(*args, cls=f"row {kwargs.get('cls', '')}".strip(), **{k: v for k, v in kwargs.items() if k != 'cls'})

logger = logging.getLogger(__name__)

def setup_admin_routes(app, db: Database):
    """Configura rotas administrativas"""
    
    # ===== GERENCIAMENTO DE USUÁRIOS =====
    
    @app.get("/admin/usuarios")
    @admin_required
    def listar_usuarios(request):
        """Lista todos os usuários com paginação"""
        user = request.state.usuario
        
        # Parâmetros de paginação
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('size', 50))
        except ValueError:
            page = 1
            page_size = 50
        
        # Validar parâmetros
        if page < 1:
            page = 1
        if page_size not in [25, 50, 100, 200]:
            page_size = 50
        
        # Calcular offset
        offset = (page - 1) * page_size
        
        # Verificar mensagens na query string
        sucesso = request.query_params.get('sucesso')
        erro = request.query_params.get('erro')
        
        alert_message = None
        alert_type = None
        
        if sucesso == 'email_reenviado':
            alert_message = "Email de confirmação reenviado com sucesso!"
            alert_type = "success"
        elif sucesso == 'cadastrado':
            alert_message = "Usuário cadastrado com sucesso!"
            alert_type = "success"
        elif sucesso == 'editado':
            alert_message = "Usuário editado com sucesso!"
            alert_type = "success"
        elif erro == 'usuario_nao_encontrado':
            alert_message = "Usuário não encontrado."
            alert_type = "danger"
        elif erro == 'falha_envio':
            alert_message = "Falha ao enviar email. Tente novamente mais tarde."
            alert_type = "danger"
        elif erro == 'interno':
            alert_message = "Erro interno. Tente novamente mais tarde."
            alert_type = "danger"
        elif request.query_params.get('info') == 'ja_confirmado':
            alert_message = "Este usuário já confirmou seu email."
            alert_type = "info"
        
        try:
            # Contar total de usuários
            total_usuarios = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
            
            # Buscar usuários com paginação
            usuarios = db.execute("""
                SELECT id, email, nome, tipo_usuario, confirmado, email_enviado, data_cadastro
                FROM usuarios 
                ORDER BY data_cadastro DESC
                LIMIT ? OFFSET ?
            """, (page_size, offset)).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {e}")
            usuarios = []
            total_usuarios = 0
        
        # Preparar dados para a tabela
        dados_tabela = []
        for u in usuarios:
            status_confirmacao = "Confirmado" if u[4] else "Pendente"
            status_conf_class = "success" if u[4] else "warning"
            
            # Status do email
            email_enviado = u[5] if len(u) > 5 else False
            status_email = "Enviado" if email_enviado else "Não enviado"
            status_email_class = "info" if email_enviado else "secondary"
            
            # Botões de ação baseados no tipo de usuário
            acoes_list = [
                A("Ver", href=f"/admin/usuarios/{u[0]}", cls="btn btn-sm btn-outline-info me-1")
            ]
            
            # Só mostrar editar/excluir para clientes
            if u[3] == 'cliente':  # tipo_usuario
                acoes_list.extend([
                    A("Editar", href=f"/admin/usuarios/{u[0]}/editar", cls="btn btn-sm btn-outline-primary me-1"),
                    # Botão de reenvio de email (só se não confirmado)
                    *([Form(
                        Button("📧", type="submit", cls="btn btn-sm btn-outline-success me-1", title="Reenviar email"),
                        method="post",
                        action=f"/admin/usuarios/{u[0]}/reenviar-email",
                        style="display: inline;"
                    )] if not u[4] else []),  # não confirmado
                    # Botão de exclusão
                    Form(
                        Button("🗑️", type="submit", cls="btn btn-sm btn-outline-danger", 
                               title="Excluir usuário",
                               onclick="return confirm('Tem certeza? Esta ação excluirá o usuário e todos os seus dados (veículos e garantias). Esta ação não pode ser desfeita!')"),
                        method="post",
                        action=f"/admin/usuarios/{u[0]}/excluir",
                        style="display: inline;"
                    )
                ])
            
            acoes = Div(*acoes_list, cls="btn-group")
            
            dados_tabela.append([
                u[2] or "N/A",  # Nome
                u[1],  # Email
                u[3].title(),  # Tipo
                Span(status_confirmacao, cls=f"badge bg-{status_conf_class}"),
                Span(status_email, cls=f"badge bg-{status_email_class}"),
                u[6] if isinstance(u[6], str) else (u[6].strftime('%d/%m/%Y') if u[6] else "N/A"),  # Data cadastro
                acoes
            ])
        
        content = Container(
            Row(
                Col(
                    Div(
                        H2("Gerenciar Usuários", cls="mb-3"),
                        A(
                            "Novo Usuário",
                            href="/admin/usuarios/novo",
                            cls="btn btn-primary mb-3"
                        ),
                        cls="d-flex justify-content-between align-items-center"
                    )
                )
            ),
            # Mostrar alerta se houver mensagem
            Row(
                Col(
                    Div(
                        alert_message,
                        cls=f"alert alert-{alert_type} alert-dismissible fade show",
                        role="alert",
                        **{
                            "data-bs-dismiss": "alert",
                            "aria-label": "Close"
                        }
                    ) if alert_message else None,
                    width=12
                )
            ) if alert_message else None,
            Row(
                Col(
                    card_component(
                        "Usuários Cadastrados",
                        Div(
                            table_component(
                                ["Nome", "Email", "Tipo", "Confirmação", "Email Enviado", "Cadastro", "Ações"],
                                dados_tabela
                            ) if usuarios else P("Nenhum usuário cadastrado ainda.", cls="text-muted text-center py-4"),
                            # Adicionar paginação
                            pagination_component(
                                current_page=page,
                                total_pages=math.ceil(total_usuarios / page_size) if total_usuarios > 0 else 1,
                                base_url="/admin/usuarios",
                                page_size=page_size,
                                total_records=total_usuarios
                            ) if total_usuarios > 0 else None
                        )
                    ),
                    width=12
                )
            )
        )
        
        return base_layout("Gerenciar Usuários", content, user)
    

    
    @app.get("/admin/usuarios/novo")
    @admin_required
    def novo_usuario_form(request):
        """Formulário para novo usuário"""
        try:
            logger.info("Acessando formulário de novo usuário")
            user = request.state.usuario
            
            # Verificar se há erros na query string
            error = request.query_params.get('erro')
            error_message = None
            
            if error == 'campos_obrigatorios':
                error_message = "Nome, email e senha são obrigatórios."
            elif error == 'senha_fraca':
                error_message = "A senha deve ter pelo menos 6 caracteres."
            elif error == 'email_existente':
                error_message = "Este email já está sendo usado por outro usuário."
            elif error == 'interno':
                error_message = "Erro interno. Tente novamente mais tarde."
        
            content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Usuários",
                            href="/admin/usuarios",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2("Cadastrar Novo Usuário", cls="mb-4")
                    )
                )
            ),
            Row(
                Col(
                    *([alert_component(error_message, "danger")] if error_message else []),
                    card_component(
                        None,  # Remove título redundante
                        Form(
                            form_group(
                                "Nome",
                                Input(
                                    type="text",
                                    name="nome",
                                    cls="form-control",
                                    placeholder="Nome completo",
                                    required=True
                                ),
                                None,
                                True,
                                error if error == 'campos_obrigatorios' else None
                            ),
                            form_group(
                                "Email",
                                Input(
                                    type="email",
                                    name="email",
                                    cls="form-control",
                                    placeholder="email@exemplo.com",
                                    required=True
                                ),
                                None,
                                True,
                                error if error in ['campos_obrigatorios', 'email_existente'] else None
                            ),
                            form_group(
                                "Senha",
                                Input(
                                    type="password",
                                    name="senha",
                                    cls="form-control",
                                    placeholder="Mínimo 6 caracteres",
                                    required=True
                                ),
                                None,
                                True,
                                error if error in ['campos_obrigatorios', 'senha_fraca'] else None
                            ),
                            Div(
                                Label("Tipo de Usuário", for_="tipo_usuario", cls="form-label"),
                                Select(
                                    Option("Cliente", value="cliente", selected=True),
                                    Option("Administrador", value="administrador"),
                                    id="tipo_usuario",
                                    name="tipo_usuario",
                                    cls="form-select"
                                ),
                                cls="mb-3"
                            ),
                            form_group(
                                "CPF/CNPJ",
                                Input(
                                    type="text",
                                    name="cpf_cnpj",
                                    cls="form-control",
                                    placeholder="CPF ou CNPJ (opcional)"
                                )
                            ),
                            form_group(
                                "Telefone",
                                Input(
                                    type="tel",
                                    name="telefone",
                                    cls="form-control",
                                    placeholder="(11) 99999-9999 (opcional)"
                                )
                            ),
                            Div(
                                Div(
                                    Input(
                                        type="checkbox",
                                        id="confirmado",
                                        name="confirmado",
                                        cls="form-check-input"
                                    ),
                                    Label("Email já confirmado", for_="confirmado", cls="form-check-label"),
                                    cls="form-check"
                                ),
                                cls="mb-3"
                            ),
                            Div(
                                Button(
                                    "Cadastrar Usuário",
                                    type="submit",
                                    cls="btn btn-primary me-2"
                                ),
                                A(
                                    "Cancelar",
                                    href="/admin/usuarios",
                                    cls="btn btn-secondary"
                                ),
                                cls="d-flex gap-2"
                            ),
                            method="post",
                            action="/admin/usuarios/novo"
                        )
                    ),
                    width=8,
                    offset=2
                )
            )
        )
        
            logger.info("Retornando layout do formulário de novo usuário")
            result = base_layout("Novo Usuário", content, user)
            logger.info(f"Layout criado: {type(result)}")
            return result
        except Exception as e:
            logger.error(f"Erro na função novo_usuario_form: {e}")
            logger.exception("Stack trace completo:")
            raise
    
    @app.post("/admin/usuarios/novo")
    @admin_required
    async def novo_usuario_submit(request):
        """Processa criação de novo usuário"""
        user = request.state.usuario
        form_data = await request.form()
        
        nome = form_data.get('nome', '').strip()
        email = form_data.get('email', '').strip().lower()
        senha = form_data.get('senha', '').strip()
        tipo_usuario = form_data.get('tipo_usuario', 'cliente')
        cpf_cnpj = form_data.get('cpf_cnpj', '').strip()
        telefone = form_data.get('telefone', '').strip()
        confirmado = bool(form_data.get('confirmado'))
        
        # Validações básicas
        if not nome or not email or not senha:
            return RedirectResponse('/admin/usuarios/novo?erro=campos_obrigatorios', status_code=302)
        
        if len(senha) < 6:
            return RedirectResponse('/admin/usuarios/novo?erro=senha_fraca', status_code=302)
        
        try:
            # Verificar se email já existe
            existing = db.execute(
                "SELECT id FROM usuarios WHERE email = ?",
                (email,)
            ).fetchone()
            
            if existing:
                return RedirectResponse('/admin/usuarios/novo?erro=email_existente', status_code=302)
            
            # Criar usuário
            usuario = Usuario(
                email=email,
                senha_hash=Usuario.criar_hash_senha(senha),
                nome=nome,
                tipo_usuario=tipo_usuario,
                confirmado=confirmado,
                cpf_cnpj=cpf_cnpj,
                telefone=telefone,
                data_cadastro=datetime.now(),
                token_confirmacao=Usuario.gerar_token_confirmacao() if not confirmado else None
            )
            
            # Inserir no banco
            db.execute("""
                INSERT INTO usuarios (
                    email, senha_hash, nome, tipo_usuario, confirmado,
                    cpf_cnpj, telefone, data_cadastro, token_confirmacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usuario.email, usuario.senha_hash, usuario.nome, usuario.tipo_usuario,
                usuario.confirmado, usuario.cpf_cnpj, usuario.telefone,
                usuario.data_cadastro.strftime('%Y-%m-%d %H:%M:%S'), usuario.token_confirmacao
            ))
            
            # Obter o ID do usuário inserido
            usuario_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            
            logger.info(f"Novo usuário criado pelo admin {user['usuario_id']}: {email} (ID: {usuario_id})")
            
            return RedirectResponse('/admin/usuarios?sucesso=cadastrado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return RedirectResponse('/admin/usuarios/novo?erro=interno', status_code=302)
    
    @app.get("/admin/usuarios/{usuario_id}")
    @admin_required
    def ver_usuario(request):
        """Ver detalhes do usuário"""
        user = request.state.usuario
        usuario_id = request.path_params['usuario_id']
        
        # Verificar mensagens na query string
        sucesso = request.query_params.get('sucesso')
        erro = request.query_params.get('erro')
        info = request.query_params.get('info')
        
        alert_message = None
        alert_type = None
        
        if sucesso == 'email_reenviado':
            alert_message = "Email de confirmação reenviado com sucesso!"
            alert_type = "success"
        elif erro == 'usuario_nao_encontrado':
            alert_message = "Usuário não encontrado."
            alert_type = "danger"
        elif erro == 'falha_envio':
            alert_message = "Falha ao enviar email. Tente novamente mais tarde."
            alert_type = "danger"
        elif erro == 'interno':
            alert_message = "Erro interno. Tente novamente mais tarde."
            alert_type = "danger"
        elif info == 'ja_confirmado':
            alert_message = "Este usuário já confirmou seu email."
            alert_type = "info"
        
        try:
            # Buscar usuário
            usuario = db.execute("""
                SELECT id, email, nome, tipo_usuario, confirmado, cep, endereco, bairro,
                       cidade, uf, telefone, cpf_cnpj, data_nascimento, data_cadastro
                FROM usuarios WHERE id = ?
            """, (usuario_id,)).fetchone()
            
            if not usuario:
                return RedirectResponse('/admin/usuarios?erro=nao_encontrado', status_code=302)
            
            # Buscar estatísticas do usuário
            stats = {
                'veiculos': db.execute(
                    "SELECT COUNT(*) FROM veiculos WHERE usuario_id = ? AND ativo = TRUE",
                    (usuario_id,)
                ).fetchone()[0],
                'garantias': db.execute(
                    "SELECT COUNT(*) FROM garantias WHERE usuario_id = ? AND ativo = TRUE",
                    (usuario_id,)
                ).fetchone()[0]
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário {usuario_id}: {e}")
            return RedirectResponse('/admin/usuarios?erro=interno', status_code=302)
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Usuários",
                            href="/admin/usuarios",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2(f"Usuário: {usuario[2] or usuario[1]}", cls="mb-4")
                    )
                )
            ),
            # Mostrar alerta se houver mensagem
            Row(
                Col(
                    Div(
                        alert_message,
                        cls=f"alert alert-{alert_type} alert-dismissible fade show",
                        role="alert",
                        **{
                            "data-bs-dismiss": "alert",
                            "aria-label": "Close"
                        }
                    ) if alert_message else None,
                    width=12
                )
            ) if alert_message else None,
            Row(
                Col(
                    card_component(
                        "Informações Pessoais",
                        Div(
                            P(f"Nome: {usuario[2] or 'N/A'}"),
                            P(f"Email: {usuario[1]}"),
                            P(f"Tipo: {usuario[3].title()}"),
                            P(f"Email Confirmado: {'Sim' if usuario[4] else 'Não'}"),
                            P(f"CPF/CNPJ: {usuario[11] or 'N/A'}"),
                            P(f"Telefone: {usuario[10] or 'N/A'}"),
                            P(f"Data de Nascimento: {datetime.fromisoformat(usuario[12]).strftime('%d/%m/%Y') if usuario[12] else 'N/A'}"),
                            P(f"Data de Cadastro: {datetime.fromisoformat(usuario[13]).strftime('%d/%m/%Y %H:%M') if usuario[13] else 'N/A'}")
                        )
                    ),
                    width=6
                ),
                Col(
                    card_component(
                        "Endereço",
                        Div(
                            P(f"CEP: {usuario[5] or 'N/A'}"),
                            P(f"Endereço: {usuario[6] or 'N/A'}"),
                            P(f"Bairro: {usuario[7] or 'N/A'}"),
                            P(f"Cidade: {usuario[8] or 'N/A'}"),
                            P(f"UF: {usuario[9] or 'N/A'}")
                        )
                    ),
                    width=6
                )
            ),
            Row(
                Col(
                    card_component(
                        "Estatísticas",
                        Div(
                            P(f"Veículos Cadastrados: {stats['veiculos']}"),
                            P(f"Garantias Ativas: {stats['garantias']}")
                        )
                    ),
                    width=6
                ),
                Col(
                    card_component(
                        "Ações",
                        Div(
                            A(
                                "Editar Usuário",
                                href=f"/admin/usuarios/{usuario[0]}/editar",
                                cls="btn btn-primary me-2 mb-2"
                            ),
                            A(
                                "Resetar Senha",
                                href=f"/admin/usuarios/{usuario[0]}/reset-senha",
                                cls="btn btn-warning me-2 mb-2"
                            ),
                            # Botão de reenvio de email apenas para usuários não confirmados
                            A(
                                "Reenviar Email",
                                href=f"/admin/usuarios/{usuario[0]}/reenviar-email",
                                cls="btn btn-info mb-2"
                            ) if not usuario[4] else None  # usuario[4] é o campo 'confirmado'
                        )
                    ),
                    width=6
                )
            )
        )
        
        return base_layout(f"Usuário: {usuario[2] or usuario[1]}", content, user)
    
    @app.get("/admin/usuarios/{usuario_id}/editar")
    @admin_required
    def editar_usuario_form(request):
        """Formulário para editar usuário"""
        user = request.state.usuario
        usuario_id = request.path_params['usuario_id']
        
        # Verificar se há erros na query string
        error = request.query_params.get('erro')
        error_message = None
        
        if error == 'campos_obrigatorios':
            error_message = "Nome e email são obrigatórios."
        elif error == 'email_existente':
            error_message = "Este email já está sendo usado por outro usuário."
        elif error == 'interno':
            error_message = "Erro interno. Tente novamente mais tarde."
        
        try:
            # Buscar usuário
            usuario = db.execute("""
                SELECT id, email, nome, tipo_usuario, confirmado, cep, endereco, bairro, 
                       cidade, uf, telefone, cpf_cnpj, data_nascimento, data_cadastro
                FROM usuarios 
                WHERE id = ?
            """, (usuario_id,)).fetchone()
            
            if not usuario:
                return RedirectResponse('/admin/usuarios?erro=nao_encontrado', status_code=302)
                
        except Exception as e:
            logger.error(f"Erro ao buscar usuário {usuario_id}: {e}")
            return RedirectResponse('/admin/usuarios?erro=interno', status_code=302)
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Usuários",
                            href="/admin/usuarios",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2(f"Editar Usuário: {usuario[2] or usuario[1]}", cls="mb-4")
                    )
                )
            ),
            Row(
                Col(
                    *([alert_component(error_message, "danger")] if error_message else []),
                    card_component(
                        "Dados do Usuário",
                        Form(
                            form_group(
                                "Nome", 
                                Input(
                                    name="nome", 
                                    type="text",
                                    value=usuario[2] or "",
                                    placeholder="Nome completo", 
                                    cls="form-control",
                                    required=True
                                ),
                                required=True,
                                error=error if error == 'campos_obrigatorios' else None
                            ),
                            form_group(
                                "Email", 
                                Input(
                                    name="email", 
                                    type="email",
                                    value=usuario[1],
                                    placeholder="email@exemplo.com", 
                                    cls="form-control",
                                    required=True
                                ),
                                required=True,
                                error=error if error in ['campos_obrigatorios', 'email_existente'] else None
                            ),
                            Div(
                                Label("Tipo de Usuário", for_="tipo_usuario", cls="form-label"),
                                Select(
                                    Option("Cliente", value="cliente", selected=(usuario[3] == "cliente")),
                                    Option("Administrador", value="administrador", selected=(usuario[3] == "administrador")),
                                    id="tipo_usuario",
                                    name="tipo_usuario",
                                    cls="form-select"
                                ),
                                cls="mb-3"
                            ),
                            form_group(
                                "CPF/CNPJ", 
                                Input(
                                    name="cpf_cnpj", 
                                    type="text",
                                    value=usuario[11] or "",
                                    placeholder="CPF ou CNPJ (opcional)",
                                    cls="form-control"
                                )
                            ),
                            form_group(
                                "Telefone", 
                                Input(
                                    name="telefone", 
                                    type="tel",
                                    value=usuario[10] or "",
                                    placeholder="(11) 99999-9999 (opcional)",
                                    cls="form-control"
                                )
                            ),
                            form_group(
                                "CEP", 
                                Input(
                                    name="cep", 
                                    type="text",
                                    value=usuario[5] or "",
                                    placeholder="00000-000 (opcional)",
                                    cls="form-control"
                                )
                            ),
                            form_group(
                                "Endereço", 
                                Input(
                                    name="endereco", 
                                    type="text",
                                    value=usuario[6] or "",
                                    placeholder="Rua, número (opcional)",
                                    cls="form-control"
                                )
                            ),
                            form_group(
                                "Bairro", 
                                Input(
                                    name="bairro", 
                                    type="text",
                                    value=usuario[7] or "",
                                    placeholder="Bairro (opcional)",
                                    cls="form-control"
                                )
                            ),
                            Row(
                                Col(
                                    form_group(
                                        "Cidade", 
                                        Input(
                                            name="cidade", 
                                            type="text",
                                            value=usuario[8] or "",
                                            placeholder="Cidade (opcional)",
                                            cls="form-control"
                                        )
                                    ),
                                    width=8
                                ),
                                Col(
                                    form_group(
                                        "UF", 
                                        Input(
                                            name="uf", 
                                            type="text",
                                            value=usuario[9] or "",
                                            placeholder="SP",
                                            maxlength="2",
                                            cls="form-control"
                                        )
                                    ),
                                    width=4
                                )
                            ),
                            Div(
                                Label(
                                    Span("Email confirmado", cls="label-text mr-3"),
                                    Input(
                                        type="checkbox",
                                        id="confirmado",
                                        name="confirmado",
                                        checked=usuario[4],
                                        cls="toggle toggle-primary"
                                    ),
                                    cls="label cursor-pointer justify-start gap-3"
                                ),
                                cls="mb-3"
                            ),
                            Div(
                                Button(
                                    "Salvar Alterações",
                                    type="submit",
                                    cls="btn btn-primary me-2"
                                ),
                                A(
                                    "Cancelar",
                                    href="/admin/usuarios",
                                    cls="btn btn-secondary"
                                ),
                                cls="d-flex gap-2"
                            ),
                            method="post",
                            action=f"/admin/usuarios/{usuario[0]}/editar"
                        )
                    ),
                    width=8,
                    offset=2
                )
            )
        )
        
        return base_layout(f"Editar Usuário: {usuario[2] or usuario[1]}", content, user)
    
    @app.post("/admin/usuarios/{usuario_id}/editar")
    @admin_required
    async def editar_usuario_submit(request):
        """Processa edição de usuário"""
        user = request.state.usuario
        usuario_id = request.path_params['usuario_id']
        
        try:
            # Verificar se usuário existe
            usuario_existe = db.execute(
                "SELECT id FROM usuarios WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            
            if not usuario_existe:
                return RedirectResponse('/admin/usuarios?erro=nao_encontrado', status_code=302)
            
            # Processar dados do formulário
            form_data = await request.form()
            nome = form_data.get('nome', '').strip()
            email = form_data.get('email', '').strip().lower()
            tipo_usuario = form_data.get('tipo_usuario', 'cliente')
            cpf_cnpj = form_data.get('cpf_cnpj', '').strip()
            telefone = form_data.get('telefone', '').strip()
            cep = form_data.get('cep', '').strip()
            endereco = form_data.get('endereco', '').strip()
            bairro = form_data.get('bairro', '').strip()
            cidade = form_data.get('cidade', '').strip()
            uf = form_data.get('uf', '').strip().upper()
            confirmado = 'confirmado' in form_data
            
            # Validações básicas
            if not nome or not email:
                return RedirectResponse(f'/admin/usuarios/{usuario_id}/editar?erro=campos_obrigatorios', status_code=302)
            
            # Verificar se email já existe em outro usuário
            email_existente = db.execute(
                "SELECT id FROM usuarios WHERE email = ? AND id != ?",
                (email, usuario_id)
            ).fetchone()
            
            if email_existente:
                return RedirectResponse(f'/admin/usuarios/{usuario_id}/editar?erro=email_existente', status_code=302)
            
            # Atualizar usuário
            db.execute("""
                UPDATE usuarios 
                SET nome = ?, email = ?, tipo_usuario = ?, confirmado = ?,
                    cpf_cnpj = ?, telefone = ?, cep = ?, endereco = ?, 
                    bairro = ?, cidade = ?, uf = ?
                WHERE id = ?
            """, (
                nome, email, tipo_usuario, confirmado,
                cpf_cnpj or None, telefone or None, cep or None, 
                endereco or None, bairro or None, cidade or None, 
                uf or None, usuario_id
            ))
            
            logger.info(f"Usuário {usuario_id} editado pelo admin {user['usuario_id']}")
            
            return RedirectResponse('/admin/usuarios?sucesso=editado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao editar usuário {usuario_id}: {e}")
            return RedirectResponse(f'/admin/usuarios/{usuario_id}/editar?erro=interno', status_code=302)
    

    
    # ===== GERENCIAMENTO DE PRODUTOS =====
    
    @app.get("/admin/produtos")
    @admin_required
    def listar_produtos(request):
        """Lista todos os produtos"""
        user = request.state.usuario
        
        try:
            # Buscar produtos
            produtos = db.execute("""
                SELECT id, sku, descricao, ativo, data_cadastro
                FROM produtos 
                ORDER BY sku
            """).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {e}")
            produtos = []
        
        # Preparar dados para a tabela
        dados_tabela = []
        for p in produtos:
            status = "Ativo" if p[3] else "Inativo"
            status_class = "success" if p[3] else "secondary"
            
            acoes = Div(
                A("Editar", href=f"/admin/produtos/{p[0]}/editar", cls="btn btn-sm btn-outline-primary me-1"),
                A("Desativar" if p[3] else "Ativar", 
                  href=f"/admin/produtos/{p[0]}/toggle", 
                  cls=f"btn btn-sm btn-outline-{'danger' if p[3] else 'success'}"),
                cls="btn-group"
            )
            
            dados_tabela.append([
                p[1],  # SKU
                p[2],  # Descrição
                Span(status, cls=f"badge bg-{status_class}"),
                datetime.fromisoformat(p[4]).strftime('%d/%m/%Y') if p[4] else "N/A",  # Data cadastro
                acoes
            ])
        
        content = Container(
            Row(
                Col(
                    Div(
                        H2("Gerenciar Produtos", cls="mb-3"),
                        A(
                            "Novo Produto",
                            href="/admin/produtos/novo",
                            cls="btn btn-primary mb-3"
                        ),
                        cls="d-flex justify-content-between align-items-center"
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        "Produtos Cadastrados",
                        table_component(
                            ["SKU", "Descrição", "Status", "Cadastro", "Ações"],
                            dados_tabela
                        ) if produtos else P("Nenhum produto cadastrado ainda.", cls="text-muted text-center py-4")
                    ),
                    width=12
                )
            )
        )
        
        return base_layout("Gerenciar Produtos", content, user)
    
    @app.get("/admin/produtos/novo")
    @admin_required
    def novo_produto_form(request):
        """Formulário para novo produto"""
        user = request.state.usuario
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Produtos",
                            href="/admin/produtos",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2("Cadastrar Novo Produto", cls="mb-4")
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        "Dados do Produto",
                        produto_form(action="/admin/produtos/novo")
                    ),
                    width=6,
                    offset=3
                )
            )
        )
        
        return base_layout("Novo Produto", content, user)
    
    @app.post("/admin/produtos/novo")
    @admin_required
    async def criar_produto(request):
        """Cria novo produto"""
        user = request.state.usuario
        
        form_data = await request.form()
        
        # Validar dados
        sku = form_data.get('sku', '').strip().upper()
        descricao = form_data.get('descricao', '').strip()
        
        errors = {}
        
        if not sku:
            errors['sku'] = 'SKU é obrigatório'
        elif len(sku) < 3:
            errors['sku'] = 'SKU deve ter pelo menos 3 caracteres'
        
        if not descricao:
            errors['descricao'] = 'Descrição é obrigatória'
        
        # Verificar se SKU já existe
        if not errors.get('sku'):
            sku_existente = db.execute(
                "SELECT id FROM produtos WHERE sku = ?",
                (sku,)
            ).fetchone()
            
            if sku_existente:
                errors['sku'] = 'Este SKU já está cadastrado'
        
        if errors:
            # Retornar formulário com erros
            form_data_dict = {
                'sku': sku,
                'descricao': descricao
            }
            
            content = Container(
                Row(
                    Col(
                        Div(
                            A(
                                "← Voltar para Produtos",
                                href="/admin/produtos",
                                cls="btn btn-outline-secondary mb-3"
                            ),
                            H2("Cadastrar Novo Produto", cls="mb-4")
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
                            "Dados do Produto",
                            produto_form(
                                produto=form_data_dict,
                                errors=errors,
                                action="/admin/produtos/novo"
                            )
                        ),
                        width=6,
                        offset=3
                    )
                )
            )
            return base_layout("Novo Produto", content, user)
        
        try:
            # Criar produto
            produto = Produto(
                sku=sku,
                descricao=descricao,
                ativo=True,
                data_cadastro=datetime.now()
            )
            
            # Inserir no banco
            db.execute("""
                INSERT INTO produtos (sku, descricao, ativo, data_cadastro)
                VALUES (?, ?, ?, ?)
            """, (
                produto.sku, produto.descricao, produto.ativo, produto.data_cadastro.strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            # Obter o ID do produto inserido
            produto_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            
            logger.info(f"Novo produto cadastrado: {sku} (ID: {produto_id}) pelo admin {user['usuario_id']}")
            
            return RedirectResponse('/admin/produtos?sucesso=cadastrado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao cadastrar produto: {e}")
            return RedirectResponse('/admin/produtos?erro=interno', status_code=302)
    
    @app.get("/admin/produtos/{produto_id}/toggle")
    @admin_required
    def toggle_produto(request):
        """Ativa/desativa produto"""
        user = request.state.usuario
        produto_id = request.path_params['produto_id']
        
        try:
            # Buscar status atual
            produto = db.execute(
                "SELECT ativo FROM produtos WHERE id = ?",
                (produto_id,)
            ).fetchone()
            
            if not produto:
                return RedirectResponse('/admin/produtos?erro=nao_encontrado', status_code=302)
            
            # Alternar status
            novo_status = not produto[0]
            
            db.execute(
                "UPDATE produtos SET ativo = ? WHERE id = ?",
                (novo_status, produto_id)
            )
            
            action = "ativado" if novo_status else "desativado"
            logger.info(f"Produto {produto_id} {action} pelo admin {user['usuario_id']}")
            
            return RedirectResponse(f'/admin/produtos?sucesso={action}', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao alterar status do produto {produto_id}: {e}")
            return RedirectResponse('/admin/produtos?erro=interno', status_code=302)
    
    @app.get("/admin/produtos/{produto_id}/editar")
    @admin_required
    def editar_produto_form(request):
        """Formulário para editar produto"""
        user = request.state.usuario
        produto_id = request.path_params['produto_id']
        
        try:
            # Buscar produto
            produto = db.execute(
                "SELECT id, sku, descricao, ativo FROM produtos WHERE id = ?",
                (produto_id,)
            ).fetchone()
            
            if not produto:
                return RedirectResponse('/admin/produtos?erro=nao_encontrado', status_code=302)
            
            # Converter para dict
            produto_dict = {
                'id': produto[0],
                'sku': produto[1],
                'descricao': produto[2],
                'ativo': produto[3]
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar produto {produto_id}: {e}")
            return RedirectResponse('/admin/produtos?erro=interno', status_code=302)
        
        content = Container(
            Row(
                Col(
                    Div(
                        A(
                            "← Voltar para Produtos",
                            href="/admin/produtos",
                            cls="btn btn-outline-secondary mb-3"
                        ),
                        H2("Editar Produto", cls="mb-4")
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        None,  # Remove título redundante
                        produto_form(
                            produto=produto_dict,
                            is_edit=True,
                            action=f"/admin/produtos/{produto_id}/editar"
                        )
                    ),
                    width=6,
                    offset=3
                )
            )
        )
        
        return base_layout("Editar Produto", content, user)
    
    @app.post("/admin/produtos/{produto_id}/editar")
    @admin_required
    async def editar_produto_submit(request):
        """Processa edição de produto"""
        user = request.state.usuario
        produto_id = request.path_params['produto_id']
        
        try:
            # Verificar se produto existe
            produto_existe = db.execute(
                "SELECT id FROM produtos WHERE id = ?",
                (produto_id,)
            ).fetchone()
            
            if not produto_existe:
                return RedirectResponse('/admin/produtos?erro=nao_encontrado', status_code=302)
            
            # Processar dados do formulário
            form_data = await request.form()
            sku = form_data.get('sku', '').strip().upper()
            descricao = form_data.get('descricao', '').strip()
            ativo = 'ativo' in form_data
            
            # Buscar produto atual
            produto_atual = db.execute(
                "SELECT id, sku, descricao, ativo FROM produtos WHERE id = ?",
                (produto_id,)
            ).fetchone()
            
            if not produto_atual:
                return RedirectResponse('/admin/produtos?erro=nao_encontrado', status_code=302)
            
            # Validações
            errors = {}
            
            if not sku:
                errors['sku'] = 'SKU é obrigatório'
            elif len(sku) < 3:
                errors['sku'] = 'SKU deve ter pelo menos 3 caracteres'
            
            if not descricao:
                errors['descricao'] = 'Descrição é obrigatória'
            
            # Verificar se SKU já existe em outro produto
            if not errors.get('sku'):
                sku_existente = db.execute(
                    "SELECT id FROM produtos WHERE sku = ? AND id != ?",
                    (sku, produto_id)
                ).fetchone()
                
                if sku_existente:
                    errors['sku'] = 'Este SKU já está cadastrado em outro produto'
            
            if errors:
                # Retornar formulário com erros
                produto_dict = {
                    'id': produto_atual[0],
                    'sku': sku,
                    'descricao': descricao,
                    'ativo': ativo
                }
                
                content = Container(
                    Row(
                        Col(
                            Div(
                                A(
                                    "← Voltar para Produtos",
                                    href="/admin/produtos",
                                    cls="btn btn-outline-secondary mb-3"
                                ),
                                H2("Editar Produto", cls="mb-4")
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
                                "Dados do Produto",
                                produto_form(
                                    produto=produto_dict,
                                    is_edit=True,
                                    errors=errors,
                                    action=f"/admin/produtos/{produto_id}/editar"
                                )
                            ),
                            width=6,
                            offset=3
                        )
                    )
                )
                return base_layout("Editar Produto", content, user)
            
            # Atualizar produto
            db.execute(
                """UPDATE produtos 
                   SET sku = ?, descricao = ?, ativo = ?, data_atualizacao = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (sku, descricao, ativo, produto_id)
            )
            
            logger.info(f"Produto {produto_id} editado pelo admin {user['usuario_id']}")
            
            return RedirectResponse('/admin/produtos?sucesso=editado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao editar produto {produto_id}: {e}")
            return RedirectResponse(f'/admin/produtos/{produto_id}/editar?erro=interno', status_code=302)
    
    # ===== VISUALIZAÇÃO DE GARANTIAS =====
    
    @app.get("/admin/garantias")
    @admin_required
    def listar_garantias_admin(request):
        """Lista todas as garantias (visão administrativa) com paginação"""
        user = request.state.usuario
        
        # Parâmetros de paginação
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('size', 50))  # Mudando de 'page_size' para 'size'
        
        # Validar parâmetros
        if page < 1:
            page = 1
        if page_size not in [25, 50, 100, 200]:
            page_size = 50
        
        # Calcular offset
        offset = (page - 1) * page_size
        
        try:
            # Contar total de garantias
            total_garantias = db.execute("SELECT COUNT(*) FROM garantias").fetchone()[0]
            
            # Buscar garantias com dados relacionados (com paginação)
            garantias = db.execute("""
                SELECT g.id, u.nome, u.email, p.sku, p.descricao, v.marca, v.modelo, v.placa,
                       g.lote_fabricacao, g.data_instalacao, g.data_cadastro, g.data_vencimento, g.ativo
                FROM garantias g
                JOIN usuarios u ON g.usuario_id = u.id
                JOIN produtos p ON g.produto_id = p.id
                JOIN veiculos v ON g.veiculo_id = v.id
                ORDER BY g.data_cadastro DESC
                LIMIT ? OFFSET ?
            """, (page_size, offset)).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar garantias: {e}")
            garantias = []
            total_garantias = 0
        
        # Preparar dados para a tabela
        dados_tabela = []
        for g in garantias:
            # Verificar se está vencida
            try:
                vencida = g[11] and datetime.fromisoformat(g[11]).date() < datetime.now().date() if g[11] else False
            except (ValueError, TypeError):
                vencida = False
            
            if not g[12]:  # Inativa
                status = "Inativa"
                status_class = "secondary"
            elif vencida:
                status = "Vencida"
                status_class = "danger"
            else:
                status = "Ativa"
                status_class = "success"
            
            dados_tabela.append([
                f"#{g[0]}",  # ID
                g[1] or g[2],  # Nome ou email
                f"{g[3]} - {g[4]}",  # SKU - Descrição
                f"{g[5]} {g[6]} ({g[7]})",  # Marca Modelo (Placa)
                datetime.fromisoformat(g[9]).strftime('%d/%m/%Y') if g[9] else "N/A",  # Data instalação
                datetime.fromisoformat(g[11]).strftime('%d/%m/%Y') if g[11] else "N/A",  # Data vencimento
                Span(status, cls=f"badge bg-{status_class}")
            ])
        
        # Calcular total de páginas
        total_pages = math.ceil(total_garantias / page_size) if total_garantias > 0 else 1
        
        content = Container(
            Row(
                Col(
                    H2("Todas as Garantias", cls="mb-4")
                )
            ),
            Row(
                Col(
                    card_component(
                        "Garantias Cadastradas",
                        Div(
                            table_component(
                                ["ID", "Cliente", "Produto", "Veículo", "Instalação", "Vencimento", "Status"],
                                dados_tabela
                            ) if garantias else P("Nenhuma garantia cadastrada ainda.", cls="text-muted text-center py-4"),
                            pagination_component(
                                current_page=page,
                                total_pages=total_pages,
                                base_url="/admin/garantias",
                                page_size=page_size,
                                total_records=total_garantias
                            ) if total_garantias > 0 else None
                        )
                    ),
                    width=12
                )
            )
        )
        
        return base_layout("Todas as Garantias", content, user)
    
    @app.get("/admin/garantias/{garantia_id}")
    @admin_required
    def visualizar_garantia_admin(request):
        """Visualizar detalhes de uma garantia específica (visão administrativa)"""
        user = request.state.usuario
        garantia_id = request.path_params['garantia_id']
        
        try:
            # Buscar garantia com dados relacionados
            garantia = db.execute("""
                SELECT g.id, g.lote_fabricacao, g.data_instalacao, g.nota_fiscal,
                       g.nome_estabelecimento, g.quilometragem, g.data_cadastro,
                       g.data_vencimento, g.ativo, g.observacoes,
                       p.sku, p.descricao as produto_descricao,
                       v.marca, v.modelo, v.ano_modelo, v.placa,
                       u.nome as cliente_nome, u.email as cliente_email
                FROM garantias g
                JOIN produtos p ON g.produto_id = p.id
                JOIN veiculos v ON g.veiculo_id = v.id
                JOIN usuarios u ON g.usuario_id = u.id
                WHERE g.id = ?
            """, (garantia_id,)).fetchone()
            
            if not garantia:
                return RedirectResponse('/admin/garantias?erro=nao_encontrada', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao buscar garantia {garantia_id}: {e}")
            return RedirectResponse('/admin/garantias?erro=interno', status_code=302)
        
        # Verificar status da garantia
        try:
            vencida = garantia[7] and datetime.fromisoformat(garantia[7]).date() < datetime.now().date() if garantia[7] else False
        except (ValueError, TypeError):
            vencida = False
        
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
                            href="/admin/garantias",
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
                                H5("Cliente"),
                                P(f"{garantia[16]} ({garantia[17]})", cls="mb-3"),
                                
                                H5("Produto"),
                                P(f"{garantia[10]} - {garantia[11]}", cls="mb-3"),
                                
                                H5("Veículo"),
                                P(f"{garantia[12]} {garantia[13]} {garantia[14]} - {garantia[15]}", cls="mb-3"),
                                
                                H5("Lote de Fabricação"),
                                P(garantia[1] or "Não informado", cls="mb-3"),
                                
                                H5("Data de Instalação"),
                                P(datetime.fromisoformat(garantia[2]).strftime('%d/%m/%Y') if garantia[2] else "Não informada", cls="mb-3"),
                                
                                H5("Quilometragem"),
                                P(f"{garantia[5]:,} km" if garantia[5] else "Não informada", cls="mb-3"),
                                
                                H5("Nota Fiscal"),
                                P(garantia[3] or "Não informada", cls="mb-3"),
                                
                                H5("Estabelecimento"),
                                P(garantia[4] or "Não informado", cls="mb-3"),
                                
                                H5("Data de Cadastro"),
                                P(datetime.fromisoformat(garantia[6]).strftime('%d/%m/%Y %H:%M') if garantia[6] else "Não informada", cls="mb-3"),
                                
                                H5("Data de Vencimento"),
                                P(datetime.fromisoformat(garantia[7]).strftime('%d/%m/%Y') if garantia[7] else "Não informada", cls="mb-3"),
                                
                                H5("Observações") if garantia[9] else None,
                                P(garantia[9], cls="mb-3") if garantia[9] else None
                            )
                        )
                    ),
                    width=8,
                    offset=2
                )
            )
        )
        
        return base_layout(f"Garantia #{garantia[0]}", content, user)
    
    # ===== RELATÓRIOS =====
    
    @app.get("/admin/relatorios")
    @admin_required
    def relatorios_admin(request):
        """Página de relatórios administrativos"""
        user = request.state.usuario
        
        try:
            # Estatísticas básicas
            total_usuarios = db.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario = 'cliente'").fetchone()[0]
            total_produtos = db.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1").fetchone()[0]
            total_garantias = db.execute("SELECT COUNT(*) FROM garantias").fetchone()[0]
            garantias_ativas = db.execute("SELECT COUNT(*) FROM garantias WHERE status = 'ativa'").fetchone()[0]
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            total_usuarios = total_produtos = total_garantias = garantias_ativas = 0
        
        content = Container(
            Row(
                Col(
                    H2("Relatórios", cls="mb-4")
                )
            ),
            Row(
                Col(
                    Card(
                        CardBody(
                            H5("Estatísticas Gerais", cls="card-title"),
                            Row(
                                Col(
                                    Card(
                                        CardBody(
                                            H3(str(total_usuarios), cls="text-primary"),
                                            P("Usuários Cadastrados", cls="text-muted")
                                        ),
                                        cls="text-center"
                                    ),
                                    width=3
                                ),
                                Col(
                                    Card(
                                        CardBody(
                                            H3(str(total_produtos), cls="text-success"),
                                            P("Produtos Ativos", cls="text-muted")
                                        ),
                                        cls="text-center"
                                    ),
                                    width=3
                                ),
                                Col(
                                    Card(
                                        CardBody(
                                            H3(str(total_garantias), cls="text-info"),
                                            P("Total de Garantias", cls="text-muted")
                                        ),
                                        cls="text-center"
                                    ),
                                    width=3
                                ),
                                Col(
                                    Card(
                                        CardBody(
                                            H3(str(garantias_ativas), cls="text-warning"),
                                            P("Garantias Ativas", cls="text-muted")
                                        ),
                                        cls="text-center"
                                    ),
                                    width=3
                                )
                            )
                        )
                    ),
                    width=12
                )
            )
        )
        
        return base_layout("Relatórios", content, user)
    
    # ===== REENVIO DE EMAIL DE CONFIRMAÇÃO =====
    
    @app.post("/admin/usuarios/{usuario_id}/reenviar-email")
    @admin_required
    async def reenviar_email_confirmacao(request):
        """Reenvia email de confirmação para o usuário"""
        user = request.state.usuario
        usuario_id = request.path_params['usuario_id']
        
        try:
            # Buscar usuário
            usuario = db.execute(
                "SELECT id, email, nome, confirmado, token_confirmacao FROM usuarios WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            
            if not usuario:
                logger.warning(f"Tentativa de reenviar email para usuário inexistente: {usuario_id}")
                return RedirectResponse('/admin/usuarios?erro=usuario_nao_encontrado', status_code=302)
            
            # Verificar se usuário já está confirmado
            if usuario[3]:  # confirmado
                logger.info(f"Tentativa de reenviar email para usuário já confirmado: {usuario[1]}")
                return RedirectResponse('/admin/usuarios?info=ja_confirmado', status_code=302)
            
            # Gerar novo token se necessário
            token_confirmacao = usuario[4] or Usuario.gerar_token_confirmacao()
            
            if not usuario[4]:  # Se não tinha token, atualizar no banco
                db.execute(
                    "UPDATE usuarios SET token_confirmacao = ? WHERE id = ?",
                    (token_confirmacao, usuario_id)
                )
            
            # Enviar email de confirmação de forma assíncrona
            try:
                from app.async_tasks import send_confirmation_email_async
                send_confirmation_email_async(
                    user_email=usuario[1],  # email
                    user_name=usuario[2] or usuario[1],  # nome ou email como fallback
                    confirmation_token=token_confirmacao
                )
                
                # Marcar email como enviado (agendado)
                db.execute(
                    "UPDATE usuarios SET email_enviado = TRUE WHERE id = ?",
                    (usuario_id,)
                )
                
                logger.info(f"Email de confirmação agendado para reenvio assíncrono: {usuario[1]} pelo admin {user['email']}")
                return RedirectResponse('/admin/usuarios?sucesso=email_reenviado', status_code=302)
                
            except Exception as e:
                logger.error(f"Erro ao agendar reenvio de email de confirmação para {usuario[1]}: {e}")
                return RedirectResponse('/admin/usuarios?erro=falha_envio', status_code=302)
                
        except Exception as e:
            logger.error(f"Erro ao reenviar email de confirmação para usuário {usuario_id}: {e}")
            return RedirectResponse('/admin/usuarios?erro=interno', status_code=302)
    
    # ===== EXCLUSÃO DE USUÁRIO =====
    
    @app.post("/admin/usuarios/{usuario_id}/excluir")
    @admin_required
    async def excluir_usuario(request):
        """Exclui usuário e todos os dados relacionados (cascata)"""
        user = request.state.usuario
        usuario_id = request.path_params['usuario_id']
        
        try:
            # Verificar se o usuário existe
            usuario = db.execute(
                "SELECT id, email, nome, tipo_usuario FROM usuarios WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            
            if not usuario:
                logger.warning(f"Tentativa de excluir usuário inexistente: {usuario_id}")
                return RedirectResponse('/admin/usuarios?erro=usuario_nao_encontrado', status_code=302)
            
            # Não permitir exclusão de administradores
            if usuario[3] == 'administrador':
                logger.warning(f"Tentativa de excluir administrador: {usuario[1]} por {user['email']}")
                return RedirectResponse('/admin/usuarios?erro=nao_pode_excluir_admin', status_code=302)
            
            # Não permitir auto-exclusão
            if int(usuario_id) == user['usuario_id']:
                logger.warning(f"Tentativa de auto-exclusão: {user['email']}")
                return RedirectResponse('/admin/usuarios?erro=nao_pode_excluir_proprio', status_code=302)
            
            # Iniciar transação para exclusão em cascata
            db.execute("BEGIN TRANSACTION")
            
            try:
                # 1. Excluir garantias do usuário
                garantias_result = db.execute(
                    "DELETE FROM garantias WHERE usuario_id = ?",
                    (usuario_id,)
                )
                garantias_excluidas = garantias_result.rowcount if hasattr(garantias_result, 'rowcount') else 0
                
                # 2. Excluir veículos do usuário
                veiculos_result = db.execute(
                    "DELETE FROM veiculos WHERE usuario_id = ?",
                    (usuario_id,)
                )
                veiculos_excluidos = veiculos_result.rowcount if hasattr(veiculos_result, 'rowcount') else 0
                
                # 3. Excluir o usuário
                db.execute(
                    "DELETE FROM usuarios WHERE id = ?",
                    (usuario_id,)
                )
                
                # Confirmar transação
                db.execute("COMMIT")
                
                logger.info(
                    f"Usuário excluído com sucesso: {usuario[1]} (ID: {usuario_id}) "
                    f"por {user['email']}. Garantias: {garantias_excluidas}, "
                    f"Veículos: {veiculos_excluidos}"
                )
                
                return RedirectResponse('/admin/usuarios?sucesso=usuario_excluido', status_code=302)
                
            except Exception as e:
                # Reverter transação em caso de erro
                db.execute("ROLLBACK")
                raise e
                
        except Exception as e:
            logger.error(f"Erro ao excluir usuário {usuario_id}: {e}")
            return RedirectResponse('/admin/usuarios?erro=erro_exclusao', status_code=302)
    
    # ===== REENVIO DE EMAIL =====
    
    @app.post("/admin/usuarios/{usuario_id}/reenviar-email")
    @admin_required
    async def reenviar_email_confirmacao(request):
        """Reenvia email de confirmação para o usuário"""
        user = request.state.usuario
        usuario_id = request.path_params['usuario_id']
        
        try:
            # Buscar usuário
            usuario = db.execute(
                "SELECT id, email, nome, confirmado, token_confirmacao FROM usuarios WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            
            if not usuario:
                return RedirectResponse('/admin/usuarios?erro=usuario_nao_encontrado', status_code=302)
            
            # Verificar se já está confirmado
            if usuario[3]:  # confirmado
                return RedirectResponse(f'/admin/usuarios/{usuario_id}?erro=ja_confirmado', status_code=302)
            
            # Importar serviço de email
            from app.email_service import EmailService
            email_service = EmailService()
            
            # Gerar novo token se necessário
            token = usuario[4] if usuario[4] else Usuario.gerar_token_confirmacao()
            
            if not usuario[4]:  # Se não tinha token, atualizar no banco
                db.execute(
                    "UPDATE usuarios SET token_confirmacao = ? WHERE id = ?",
                    (token, usuario_id)
                )
            
            # Enviar email de forma assíncrona
            try:
                from app.async_tasks import send_confirmation_email_async
                send_confirmation_email_async(
                    user_email=usuario[1],
                    user_name=usuario[2],
                    confirmation_token=token
                )
                
                # Marcar como email enviado (agendado)
                db.execute(
                    "UPDATE usuarios SET email_enviado = TRUE WHERE id = ?",
                    (usuario_id,)
                )
                
                logger.info(f"Email de confirmação agendado para reenvio assíncrono: {usuario[1]} por {user['email']}")
                return RedirectResponse(f'/admin/usuarios/{usuario_id}?sucesso=email_reenviado', status_code=302)
                
            except Exception as e:
                logger.error(f"Erro ao agendar reenvio de email para {usuario[1]}: {e}")
                return RedirectResponse(f'/admin/usuarios/{usuario_id}?erro=falha_envio', status_code=302)
                
        except Exception as e:
            logger.error(f"Erro ao reenviar email para usuário {usuario_id}: {e}")
            return RedirectResponse(f'/admin/usuarios/{usuario_id}?erro=erro_interno', status_code=302)
    
    # ===== RESET DE SENHA =====
    
    @app.get("/admin/usuarios/{usuario_id}/reset-senha")
    @admin_required
    def reset_senha_form(request):
        """Formulário para resetar senha do usuário"""
        user = request.state.usuario
        usuario_id = request.path_params['usuario_id']
        
        try:
            # Buscar usuário
            usuario = db.execute(
                "SELECT id, email, nome, tipo_usuario FROM usuarios WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            
            if not usuario:
                return RedirectResponse('/admin/usuarios?erro=nao_encontrado', status_code=302)
            
            # Não permitir reset de senha de administradores por outros admins
            if usuario[3] == 'administrador' and user['usuario_id'] != int(usuario_id):
                return RedirectResponse('/admin/usuarios?erro=nao_pode_alterar_admin', status_code=302)
            
            # Formulário de reset de senha
            form = Form(
                Div(
                    Label("Nova Senha:", **{"for": "nova_senha"}),
                    Input(
                        type="password",
                        name="nova_senha",
                        id="nova_senha",
                        cls="form-control",
                        required=True,
                        minlength="6"
                    ),
                    cls="mb-3"
                ),
                Div(
                    Label("Confirmar Nova Senha:", **{"for": "confirmar_senha"}),
                    Input(
                        type="password",
                        name="confirmar_senha",
                        id="confirmar_senha",
                        cls="form-control",
                        required=True,
                        minlength="6"
                    ),
                    cls="mb-3"
                ),
                Div(
                    Button("Resetar Senha", type="submit", cls="btn btn-danger me-2"),
                    A("Cancelar", href=f"/admin/usuarios/{usuario_id}", cls="btn btn-secondary"),
                    cls="d-flex gap-2"
                ),
                method="post",
                action=f"/admin/usuarios/{usuario_id}/reset-senha"
            )
            
            content = Container(
                Row(
                    Col(
                        Div(
                            A(
                                "← Voltar para Usuário",
                                href=f"/admin/usuarios/{usuario_id}",
                                cls="btn btn-outline-secondary mb-3"
                            ),
                            H2(f"Resetar Senha - {usuario[2] or usuario[1]}", cls="mb-4")
                        )
                    )
                ),
                Row(
                    Col(
                        card_component(
                            "Nova Senha",
                            form
                        ),
                        width=6,
                        offset=3
                    )
                )
            )
            
            return base_layout("Resetar Senha", content, user)
            
        except Exception as e:
            logger.error(f"Erro ao carregar formulário de reset de senha para usuário {usuario_id}: {e}")
            return RedirectResponse('/admin/usuarios?erro=interno', status_code=302)
    
    @app.post("/admin/usuarios/{usuario_id}/reset-senha")
    @admin_required
    async def reset_senha_submit(request):
        """Processa reset de senha do usuário"""
        user = request.state.usuario
        usuario_id = request.path_params['usuario_id']
        
        try:
            # Buscar usuário
            usuario = db.execute(
                "SELECT id, email, nome, tipo_usuario FROM usuarios WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            
            if not usuario:
                return RedirectResponse('/admin/usuarios?erro=nao_encontrado', status_code=302)
            
            # Não permitir reset de senha de administradores por outros admins
            if usuario[3] == 'administrador' and user['usuario_id'] != int(usuario_id):
                return RedirectResponse('/admin/usuarios?erro=nao_pode_alterar_admin', status_code=302)
            
            # Processar dados do formulário
            form_data = await request.form()
            nova_senha = form_data.get('nova_senha', '').strip()
            confirmar_senha = form_data.get('confirmar_senha', '').strip()
            
            # Validações
            if not nova_senha or not confirmar_senha:
                return RedirectResponse(f'/admin/usuarios/{usuario_id}/reset-senha?erro=campos_obrigatorios', status_code=302)
            
            if len(nova_senha) < 6:
                return RedirectResponse(f'/admin/usuarios/{usuario_id}/reset-senha?erro=senha_muito_curta', status_code=302)
            
            if nova_senha != confirmar_senha:
                return RedirectResponse(f'/admin/usuarios/{usuario_id}/reset-senha?erro=senhas_diferentes', status_code=302)
            
            # Importar função de hash de senha
            from app.auth import hash_password
            
            # Gerar hash da nova senha
            senha_hash = hash_password(nova_senha)
            
            # Atualizar senha no banco
            db.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (senha_hash, usuario_id)
            )
            
            logger.info(f"Senha resetada para usuário {usuario[1]} (ID: {usuario_id}) pelo admin {user['email']}")
            
            return RedirectResponse(f'/admin/usuarios/{usuario_id}?sucesso=senha_resetada', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao resetar senha do usuário {usuario_id}: {e}")
            return RedirectResponse(f'/admin/usuarios/{usuario_id}/reset-senha?erro=interno', status_code=302)
    
    # ===== SINCRONIZAÇÃO COM ERP TECNICON =====
    
    @app.get("/admin/produtos/sync")
    @admin_required
    def sync_produtos_page(request):
        """Página de sincronização de produtos com ERP"""
        user = request.state.usuario
        
        # Verificar mensagens na query string
        sucesso = request.query_params.get('sucesso')
        erro = request.query_params.get('erro')
        
        alert_message = None
        alert_type = None
        
        if sucesso == 'sync_concluida':
            # Recuperar estatísticas da sincronização
            total = request.query_params.get('total', '0')
            inseridos = request.query_params.get('inseridos', '0')
            atualizados = request.query_params.get('atualizados', '0')
            inalterados = request.query_params.get('inalterados', '0')
            erros = request.query_params.get('erros', '0')
            
            alert_message = f"Sincronização concluída! Total ERP: {total}, Inseridos: {inseridos}, Atualizados: {atualizados}, Inalterados: {inalterados}, Erros: {erros}"
            alert_type = "success"
        elif erro == 'conexao_firebird':
            alert_message = "Erro ao conectar com o ERP Tecnicon. Verifique as configurações."
            alert_type = "danger"
        elif erro == 'sync_falhou':
            # Capturar erro detalhado dos logs se disponível
            erro_detalhe = request.query_params.get('erro_detalhe', '')
            if erro_detalhe:
                alert_message = f"Falha durante a sincronização: {erro_detalhe}"
            else:
                alert_message = "Falha durante a sincronização. Verifique os logs para mais detalhes."
            alert_type = "danger"
        elif erro == 'teste_conexao_falhou':
            # Capturar erro detalhado dos logs se disponível
            erro_detalhe = request.query_params.get('erro_detalhe', '')
            if erro_detalhe:
                alert_message = f"Teste de conexão com Firebird falhou: {erro_detalhe}"
            else:
                alert_message = "Teste de conexão com Firebird falhou. Verifique as configurações."
            alert_type = "danger"
        elif sucesso == 'teste_conexao_ok':
            alert_message = "Conexão com Firebird testada com sucesso!"
            alert_type = "success"
        
        content = Container(
            Row(
                Col(
                    H1("Sincronização de Produtos ERP Tecnicon", cls="mb-4"),
                    
                    # Alert de feedback
                    Alert(
                        alert_message,
                        variant=alert_type,
                        cls="mb-4"
                    ) if alert_message else None,
                    
                    Card(
                        CardHeader(
                            H4("Sincronização com ERP Tecnicon", cls="mb-0")
                        ),
                        CardBody(
                            P("Esta funcionalidade sincroniza os produtos do ERP Tecnicon com o sistema de garantias."),
                            P("A sincronização irá:"),
                            Ul(
                                Li("Buscar produtos ativos do grupo 48 e subgrupos específicos"),
                                Li("Inserir novos produtos que não existem no sistema"),
                                Li("Atualizar produtos existentes com descrições diferentes"),
                                Li("Manter produtos inalterados quando não há diferenças")
                            ),
                            Hr(),
                            Div(
                                Button(
                                    "Testar Conexão",
                                    type="button",
                                    cls="btn btn-outline-primary me-3",
                                    onclick="testarConexaoFirebird()"
                                ),
                                Button(
                                    "Atualizar Produtos do ERP",
                                    type="button",
                                    cls="btn btn-primary",
                                    onclick="sincronizarProdutos()",
                                    id="btnSincronizar"
                                ),
                                cls="d-flex gap-2"
                            )
                        )
                    ),
                    
                    # Área de status
                    Div(
                        id="statusSincronizacao",
                        cls="mt-4"
                    ),
                    
                    # Script JavaScript
                    Script("""
                        function testarConexaoFirebird() {
                            const statusDiv = document.getElementById('statusSincronizacao');
                            statusDiv.innerHTML = '<div class="alert alert-info">Testando conexão com ERP Tecnicon...</div>';
                            
                            fetch('/admin/produtos/test-firebird', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    window.location.href = '/admin/produtos/sync?sucesso=teste_conexao_ok';
                                } else {
                                    const errorDetail = encodeURIComponent(data.error || 'Erro desconhecido');
                                    window.location.href = '/admin/produtos/sync?erro=teste_conexao_falhou&erro_detalhe=' + errorDetail;
                                }
                            })
                            .catch(error => {
                                console.error('Erro:', error);
                                const errorDetail = encodeURIComponent(error.message || 'Erro de conexão');
                                window.location.href = '/admin/produtos/sync?erro=teste_conexao_falhou&erro_detalhe=' + errorDetail;
                            });
                        }
                        
                        function sincronizarProdutos() {
                            const btnSincronizar = document.getElementById('btnSincronizar');
                            const statusDiv = document.getElementById('statusSincronizacao');
                            
                            btnSincronizar.disabled = true;
                            btnSincronizar.innerHTML = 'Sincronizando...';
                            statusDiv.innerHTML = '<div class="alert alert-info">Sincronizando produtos com ERP Tecnicon...</div>';
                            
                            fetch('/admin/produtos/sync-execute', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    const stats = data.stats;
                                    const params = new URLSearchParams({
                                        sucesso: 'sync_concluida',
                                        total: stats.total_erp,
                                        inseridos: stats.inseridos,
                                        atualizados: stats.atualizados,
                                        inalterados: stats.inalterados,
                                        erros: stats.erros
                                    });
                                    window.location.href = '/admin/produtos/sync?' + params.toString();
                                } else {
                                    const errorDetail = encodeURIComponent(data.error || 'Erro desconhecido');
                                    window.location.href = '/admin/produtos/sync?erro=sync_falhou&erro_detalhe=' + errorDetail;
                                }
                            })
                            .catch(error => {
                                console.error('Erro:', error);
                                const errorDetail = encodeURIComponent(error.message || 'Erro de conexão');
                                window.location.href = '/admin/produtos/sync?erro=sync_falhou&erro_detalhe=' + errorDetail;
                            })
                            .finally(() => {
                                btnSincronizar.disabled = false;
                                btnSincronizar.innerHTML = 'Atualizar Produtos do ERP';
                            });
                        }
                    """)
                )
            )
        )
        
        return base_layout("Sincronização de Produtos ERP Tecnicon", content, user)
    
    @app.post("/admin/produtos/test-firebird")
    @admin_required
    def test_firebird_connection(request):
        """Testa conexão com ERP Tecnicon"""
        try:
            from app.services import get_firebird_service
            from app.config import Config
            
            config = Config()
            firebird_service = get_firebird_service(config)
            
            success = firebird_service.test_connection()
            
            return {"success": success}
            
        except Exception as e:
            logger.error(f"Erro ao testar conexão Firebird: {e}")
            return {"success": False, "error": str(e)}
    
    @app.post("/admin/produtos/sync-execute")
    @admin_required
    def execute_produtos_sync(request):
        """Executa sincronização de produtos com ERP"""
        try:
            from app.services import get_firebird_service
            from app.config import Config
            
            config = Config()
            firebird_service = get_firebird_service(config)
            
            # Executar sincronização
            stats = firebird_service.sync_produtos(db)
            
            logger.info(f"Sincronização de produtos concluída: {stats}")
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Erro durante sincronização de produtos: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    logger.info("Rotas administrativas configuradas com sucesso")