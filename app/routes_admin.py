#!/usr/bin/env python3
"""
Rotas administrativas
"""

import logging
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
        """Lista todos os usuários"""
        user = request.state.usuario
        
        try:
            # Buscar usuários
            usuarios = db.execute("""
                SELECT id, email, nome, tipo_usuario, confirmado, data_cadastro
                FROM usuarios 
                ORDER BY data_cadastro DESC
            """).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {e}")
            usuarios = []
        
        # Preparar dados para a tabela
        dados_tabela = []
        for u in usuarios:
            status_confirmacao = "Confirmado" if u[4] else "Pendente"
            status_conf_class = "success" if u[4] else "warning"
            
            acoes = Div(
                A("Ver", href=f"/admin/usuarios/{u[0]}", cls="btn btn-sm btn-outline-info me-1"),
                A("Editar", href=f"/admin/usuarios/{u[0]}/editar", cls="btn btn-sm btn-outline-primary me-1"),
                cls="btn-group"
            )
            
            dados_tabela.append([
                u[2] or "N/A",  # Nome
                u[1],  # Email
                u[3].title(),  # Tipo
                Span(status_confirmacao, cls=f"badge bg-{status_conf_class}"),
                u[5] if isinstance(u[5], str) else (u[5].strftime('%d/%m/%Y') if u[5] else "N/A"),  # Data cadastro
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
                            cls="btn btn-success mb-3"
                        ),
                        cls="d-flex justify-content-between align-items-center"
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        "Usuários Cadastrados",
                        Div(
                            table_component(
                                ["Nome", "Email", "Tipo", "Confirmação", "Cadastro", "Ações"],
                                dados_tabela
                            ) if usuarios else P("Nenhum usuário cadastrado ainda.", cls="text-muted text-center py-4")
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
                        "Dados do Usuário",
                        Form(
                            form_group(
                                "Nome", "nome", "text", 
                                placeholder="Nome completo", 
                                required=True,
                                error=error if error == 'campos_obrigatorios' else None
                            ),
                            form_group(
                                "Email", "email", "email", 
                                placeholder="email@exemplo.com", 
                                required=True,
                                error=error if error in ['campos_obrigatorios', 'email_existente'] else None
                            ),
                            form_group(
                                "Senha", "senha", "password", 
                                placeholder="Mínimo 6 caracteres", 
                                required=True,
                                error=error if error in ['campos_obrigatorios', 'senha_fraca'] else None
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
                                "CPF/CNPJ", "cpf_cnpj", "text", 
                                placeholder="CPF ou CNPJ (opcional)"
                            ),
                            form_group(
                                "Telefone", "telefone", "tel", 
                                placeholder="(11) 99999-9999 (opcional)"
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
                                    cls="btn btn-success me-2"
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
                usuario.data_cadastro.isoformat(), usuario.token_confirmacao
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
                                cls="btn btn-warning mb-2"
                            )
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
                                "Nome", "nome", "text", 
                                value=usuario[2] or "",
                                placeholder="Nome completo", 
                                required=True,
                                error=error if error == 'campos_obrigatorios' else None
                            ),
                            form_group(
                                "Email", "email", "email", 
                                value=usuario[1],
                                placeholder="email@exemplo.com", 
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
                                "CPF/CNPJ", "cpf_cnpj", "text", 
                                value=usuario[11] or "",
                                placeholder="CPF ou CNPJ (opcional)"
                            ),
                            form_group(
                                "Telefone", "telefone", "tel", 
                                value=usuario[10] or "",
                                placeholder="(11) 99999-9999 (opcional)"
                            ),
                            form_group(
                                "CEP", "cep", "text", 
                                value=usuario[5] or "",
                                placeholder="00000-000 (opcional)"
                            ),
                            form_group(
                                "Endereço", "endereco", "text", 
                                value=usuario[6] or "",
                                placeholder="Rua, número (opcional)"
                            ),
                            form_group(
                                "Bairro", "bairro", "text", 
                                value=usuario[7] or "",
                                placeholder="Bairro (opcional)"
                            ),
                            Row(
                                Col(
                                    form_group(
                                        "Cidade", "cidade", "text", 
                                        value=usuario[8] or "",
                                        placeholder="Cidade (opcional)"
                                    ),
                                    width=8
                                ),
                                Col(
                                    form_group(
                                        "UF", "uf", "text", 
                                        value=usuario[9] or "",
                                        placeholder="SP",
                                        maxlength="2"
                                    ),
                                    width=4
                                )
                            ),
                            Div(
                                Div(
                                    Input(
                                        type="checkbox",
                                        id="confirmado",
                                        name="confirmado",
                                        checked=usuario[4],
                                        cls="form-check-input"
                                    ),
                                    Label("Email confirmado", for_="confirmado", cls="form-check-label"),
                                    cls="form-check"
                                ),
                                cls="mb-3"
                            ),
                            Div(
                                Button(
                                    "Salvar Alterações",
                                    type="submit",
                                    cls="btn btn-success me-2"
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
                            cls="btn btn-success mb-3"
                        ),
                        cls="d-flex justify-content-between align-items-center"
                    )
                )
            ),
            Row(
                Col(
                    card_component(
                        "Produtos Cadastrados",
                        Div(
                            table_component(
                                ["SKU", "Descrição", "Status", "Cadastro", "Ações"],
                                dados_tabela
                            ) if produtos else P("Nenhum produto cadastrado ainda.", cls="text-muted text-center py-4")
                        )
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
                produto.sku, produto.descricao, produto.ativo, produto.data_cadastro.isoformat()
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
                        "Dados do Produto",
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
        """Lista todas as garantias (visão administrativa)"""
        user = request.state.usuario
        
        try:
            # Buscar garantias com dados relacionados
            garantias = db.execute("""
                SELECT g.id, u.nome, u.email, p.sku, p.descricao, v.marca, v.modelo, v.placa,
                       g.lote_fabricacao, g.data_instalacao, g.data_cadastro, g.data_vencimento, g.ativo
                FROM garantias g
                JOIN usuarios u ON g.usuario_id = u.id
                JOIN produtos p ON g.produto_id = p.id
                JOIN veiculos v ON g.veiculo_id = v.id
                ORDER BY g.data_cadastro DESC
            """).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar garantias: {e}")
            garantias = []
        
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
                            ) if garantias else P("Nenhuma garantia cadastrada ainda.", cls="text-muted text-center py-4")
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
    
    logger.info("Rotas administrativas configuradas com sucesso")