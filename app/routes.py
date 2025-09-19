#!/usr/bin/env python3
"""
Rotas principais da aplicação
"""

import logging
import re
from datetime import datetime
from fasthtml.common import *
from monsterui.all import *
from fastlite import Database
from app.auth import get_auth_manager, login_required, admin_required, get_current_user, SESSION_COOKIE_NAME
from app.templates import *
from models.usuario import Usuario
from models.produto import Produto
from models.veiculo import Veiculo
from models.garantia import Garantia
from app.cep_service import consultar_cep_sync

# Definir Row como um Div com classe Bootstrap
Row = lambda *args, **kwargs: Div(*args, cls=f"row {kwargs.get('cls', '')}".strip(), **{k: v for k, v in kwargs.items() if k != 'cls'})

logger = logging.getLogger(__name__)

def setup_routes(app, db: Database):
    """Configura todas as rotas da aplicação"""
    
    @app.get("/")
    def home(request):
        """Página inicial"""
        user = get_current_user(request)
        
        if user:
            if user['tipo_usuario'] in ['admin', 'administrador']:
                return RedirectResponse('/admin', status_code=302)
            else:
                return RedirectResponse('/cliente', status_code=302)
        
        # Página inicial para usuários não autenticados
        content = Container(
            Row(
                Col(
                    Div(
                        H1("Viemar - Garantia 70mil Km ou 2 anos", cls="display-4 text-center mb-4"),
                        P(
                            "Ative a garantia estendida dos seus produtos Viemar de forma rápida e segura.",
                            cls="lead text-center mb-4"
                        ),
                        Div(
                            A(
                                "Fazer Login",
                                href="/login",
                                cls="btn btn-primary btn-lg me-3"
                            ),
                            A(
                                "Criar Conta",
                                href="/cadastro",
                                cls="btn btn-outline-primary btn-lg"
                            ),
                            cls="text-center mb-4"
                        ),
                        Div(
                            A(
                                "Regulamento",
                                href="/regulamento",
                                cls="btn btn-link me-3"
                            ),
                            A(
                                "Contato",
                                href="/contato",
                                cls="btn btn-link"
                            ),
                            cls="text-center"
                        ),
                        cls="hero-section py-5"
                    ),
                    width=12
                )
            ),
            Row(
                Col(
                    card_component(
                        "Como funciona?",
                        Div(
                            P("1. Crie sua conta ou faça login"),
                            P("2. Cadastre seus veículos"),
                            P("3. Ative a garantia dos produtos instalados"),
                            P("4. Receba a confirmação por email")
                        )
                    ),
                    width=6
                ),
                Col(
                    card_component(
                        "Benefícios",
                        Div(
                            P("✓ Garantia de 70.000 km ou 2 anos"),
                            P("✓ Cobertura nacional"),
                            P("✓ Atendimento especializado"),
                            P("✓ Processo 100% digital")
                        )
                    ),
                    width=6
                )
            )
        )
        
        return base_layout("Bem-vindo", content, show_nav=False)
    
    @app.get("/login")
    def login_page(request):
        """Página de login"""
        user = get_current_user(request)
        if user:
            if user['tipo_usuario'] in ['admin', 'administrador']:
                return RedirectResponse('/admin', status_code=302)
            else:
                return RedirectResponse('/cliente', status_code=302)
        
        error = request.query_params.get('erro')
        email_value = request.query_params.get('email', '')
        error_message = None
        
        if error == 'credenciais_invalidas':
            error_message = "Email ou senha incorretos."
        elif error == 'email_nao_confirmado':
            error_message = "Você precisa confirmar seu email antes de fazer login."
        elif error == 'acesso_negado':
            error_message = "Acesso negado. Você precisa ser administrador."
        
        content = Container(
            Row(
                Col(
                    card_component(
                        "Entrar na sua conta",
                        login_form(error_message, email_value)
                    ),
                    width=6,
                    offset=3
                )
            ),
            cls="py-5"
        )
        
        return base_layout("Login", content, show_nav=False)
    
    @app.post("/login")
    async def login_submit(request):
        """Processa login"""
        form_data = await request.form()
        email = form_data.get('email', '').strip().lower()
        senha = form_data.get('senha', '')
        
        if not email or not senha:
            # Preservar email no redirecionamento
            from urllib.parse import quote
            return RedirectResponse(f'/login?erro=credenciais_invalidas&email={quote(email)}', status_code=302)
        
        # Autenticar usuário
        auth_manager = get_auth_manager()
        usuario = auth_manager.autenticar_usuario(email, senha)
        
        # Verificar se é erro de email não confirmado
        if isinstance(usuario, dict) and usuario.get('erro') == 'email_nao_confirmado':
            # Preservar email no redirecionamento
            from urllib.parse import quote
            return RedirectResponse(f'/login?erro=email_nao_confirmado&email={quote(email)}', status_code=302)
        
        if not usuario:
            # Preservar email no redirecionamento
            from urllib.parse import quote
            return RedirectResponse(f'/login?erro=credenciais_invalidas&email={quote(email)}', status_code=302)
        
        # Criar sessão
        session_id = auth_manager.criar_sessao(
            usuario['id'],
            usuario['email'],
            usuario['tipo_usuario']
        )
        
        # Redirecionar baseado no tipo de usuário
        if usuario['tipo_usuario'] in ['admin', 'administrador']:
            redirect_url = '/admin'
        else:
            redirect_url = '/cliente'
        
        response = RedirectResponse(redirect_url, status_code=302)
        response.set_cookie(
            SESSION_COOKIE_NAME,
            session_id,
            max_age=86400,  # 24 horas
            httponly=True,
            secure=False  # True em produção com HTTPS
        )
        
        return response
    
    @app.get("/logout")
    def logout(request):
        """Logout do usuário"""
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        
        if session_id:
            get_auth_manager().destruir_sessao(session_id)
        
        response = RedirectResponse('/', status_code=302)
        response.delete_cookie(SESSION_COOKIE_NAME)
        
        return response
    
    @app.get("/cadastro")
    def cadastro_page(request):
        """Página de cadastro"""
        user = get_current_user(request)
        if user:
            if user['tipo_usuario'] in ['admin', 'administrador']:
                return RedirectResponse('/admin', status_code=302)
            else:
                return RedirectResponse('/cliente', status_code=302)
        
        content = Container(
            Row(
                Col(
                    card_component(
                        "Criar nova conta",
                        cadastro_form()
                    ),
                    width=10,
                    offset=1
                )
            ),
            cls="py-5"
        )
        
        return base_layout("Cadastro", content, show_nav=False)
    
    @app.post("/cadastro")
    async def cadastro_submit(request):
        """Processa cadastro de novo cliente"""
        form_data = await request.form()
        
        # Extrair dados do formulário
        nome = form_data.get('nome', '').strip()
        email = form_data.get('email', '').strip().lower()
        confirmar_email = form_data.get('confirmar_email', '').strip().lower()
        senha = form_data.get('senha', '')
        confirmar_senha = form_data.get('confirmar_senha', '')
        cep = form_data.get('cep', '').strip()
        endereco = form_data.get('endereco', '').strip()
        bairro = form_data.get('bairro', '').strip()
        cidade = form_data.get('cidade', '').strip()
        uf = form_data.get('uf', '').strip()
        telefone = form_data.get('telefone', '').strip()
        cpf_cnpj = form_data.get('cpf_cnpj', '').strip()
        data_nascimento_str = form_data.get('data_nascimento', '').strip()
        
        errors = {}
        
        # Validação do nome
        if not nome:
            errors['nome'] = 'Nome completo é obrigatório'
        elif len(nome) < 3:
            errors['nome'] = 'Nome deve ter pelo menos 3 caracteres'
        
        # Validação do email
        if not email:
            errors['email'] = 'Email é obrigatório'
        elif '@' not in email or '.' not in email.split('@')[-1]:
            errors['email'] = 'Email deve ter um formato válido'
        
        # Validação da confirmação de email
        if not confirmar_email:
            errors['confirmar_email'] = 'Confirmação de email é obrigatória'
        elif email and confirmar_email and email != confirmar_email:
            errors['confirmar_email'] = 'Emails não conferem'
        
        # Validação da senha
        if not senha:
            errors['senha'] = 'Senha é obrigatória'
        elif len(senha) < 6:
            errors['senha'] = 'Senha deve ter pelo menos 6 caracteres'
        
        # Validação da confirmação de senha
        if not confirmar_senha:
            errors['confirmar_senha'] = 'Confirmação de senha é obrigatória'
        elif senha and confirmar_senha and senha != confirmar_senha:
            errors['confirmar_senha'] = 'Senhas não conferem'
        
        # Validação do CEP (opcional, mas se preenchido deve ser válido)
        # Conforme API ViaCEP: deve ter exatamente 8 dígitos numéricos
        if cep:
            # Remove caracteres não numéricos
            cep_clean = re.sub(r'[^\d]', '', cep)
            if not re.match(r'^\d{8}$', cep_clean):
                errors['cep'] = 'CEP deve ter exatamente 8 dígitos numéricos'
            else:
                # Atualiza o CEP para usar apenas números
                cep = cep_clean
        
        # Validação do telefone (opcional, mas se preenchido deve ser válido)
        if telefone and not re.match(r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$', telefone):
            errors['telefone'] = 'Telefone deve ter um formato válido'
        
        # Validação do CPF/CNPJ (opcional, mas se preenchido deve ser válido)
        if cpf_cnpj:
            # Remove caracteres especiais
            cpf_cnpj_clean = re.sub(r'[^\d]', '', cpf_cnpj)
            if len(cpf_cnpj_clean) not in [11, 14]:
                errors['cpf_cnpj'] = 'CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos'
        
        # Validação da data de nascimento (opcional)
        if data_nascimento_str:
            try:
                data_nasc = datetime.strptime(data_nascimento_str, '%Y-%m-%d')
                # Verificar se a data não é futura
                if data_nasc > datetime.now():
                    errors['data_nascimento'] = 'Data de nascimento não pode ser futura'
                # Verificar se a pessoa tem pelo menos 16 anos
                elif (datetime.now() - data_nasc).days < 16 * 365:
                    errors['data_nascimento'] = 'Idade mínima é 16 anos'
            except ValueError:
                errors['data_nascimento'] = 'Data de nascimento inválida'
        
        # Verificar se email já existe
        if not errors.get('email'):
            existing_user = db.execute(
                "SELECT id FROM usuarios WHERE email = ?",
                (email,)
            ).fetchone()
            
            if existing_user:
                errors['email'] = 'Este email já está cadastrado'
        
        if errors:
            # Preparar dados do formulário para preservar valores preenchidos
            form_values = {
                'nome': nome,
                'email': email,
                'confirmar_email': confirmar_email,
                'cep': cep,
                'endereco': endereco,
                'bairro': bairro,
                'cidade': cidade,
                'uf': uf,
                'telefone': telefone,
                'cpf_cnpj': cpf_cnpj,
                'data_nascimento': data_nascimento_str
            }
            
            # Retornar formulário com erros e valores preservados
            content = Container(
                Row(
                    Col(
                        alert_component(
                            "Corrija os erros abaixo:",
                            "danger"
                        ),
                        card_component(
                            "Criar nova conta",
                            cadastro_form(errors, form_values)
                        ),
                        width=10,
                        offset=1
                    )
                ),
                cls="py-5"
            )
            return base_layout("Cadastro", content, show_nav=False)
        
        try:
            logger.info(f"Iniciando cadastro para email: {email}")
            
            # Processar data de nascimento
            data_nascimento_str = form_data.get('data_nascimento', '').strip()
            data_nascimento = None
            if data_nascimento_str:
                try:
                    data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d')
                except ValueError:
                    pass  # Ignora data inválida
            
            logger.info(f"Criando objeto usuário...")
            # Criar usuário
            usuario = Usuario(
                email=email,
                senha_hash=Usuario.criar_hash_senha(senha),
                nome=nome,
                tipo_usuario='cliente',
                confirmado=False,  # Precisa confirmar email
                cep=form_data.get('cep', ''),
                endereco=form_data.get('endereco', ''),
                bairro=form_data.get('bairro', ''),
                cidade=form_data.get('cidade', ''),
                uf=form_data.get('uf', ''),
                telefone=form_data.get('telefone', ''),
                cpf_cnpj=form_data.get('cpf_cnpj', ''),
                data_nascimento=data_nascimento,
                data_cadastro=datetime.now(),
                token_confirmacao=Usuario.gerar_token_confirmacao()
            )
            
            logger.info(f"Inserindo usuário no banco: {usuario.email}")
            # Inserir no banco
            cursor = db.execute("""
                INSERT INTO usuarios (
                    email, senha_hash, nome, tipo_usuario, confirmado,
                    cep, endereco, bairro, cidade, uf, telefone, cpf_cnpj,
                    data_nascimento, data_cadastro, token_confirmacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usuario.email, usuario.senha_hash, usuario.nome, usuario.tipo_usuario,
                usuario.confirmado, usuario.cep, usuario.endereco, usuario.bairro,
                usuario.cidade, usuario.uf, usuario.telefone, usuario.cpf_cnpj,
                usuario.data_nascimento.strftime('%Y-%m-%d') if usuario.data_nascimento else None,
                usuario.data_cadastro.strftime('%Y-%m-%d %H:%M:%S'), usuario.token_confirmacao
            ))
            
            # Obter o ID do usuário inserido
            usuario_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            
            logger.info(f"Novo usuário cadastrado: {email} (ID: {usuario_id})")
            
            # Enviar email de confirmação de forma assíncrona
            try:
                from app.async_tasks import send_confirmation_email_async
                send_confirmation_email_async(
                    user_email=usuario.email,
                    user_name=usuario.nome,
                    confirmation_token=usuario.token_confirmacao
                )
                logger.info(f"Email de confirmação agendado para envio assíncrono: {usuario.email}")
                    
            except Exception as e:
                logger.error(f"Erro ao agendar envio de email de confirmação para {usuario.email}: {e}")
            
            # Redirecionar para página de sucesso
            return RedirectResponse('/cadastro/sucesso', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao cadastrar usuário {email}: {e}")
            
            content = Container(
                Row(
                    Col(
                        alert_component(
                            "Erro interno. Tente novamente mais tarde.",
                            "danger"
                        ),
                        card_component(
                            "Criar nova conta",
                            cadastro_form()
                        ),
                        width=10,
                        offset=1
                    )
                ),
                cls="py-5"
            )
            return base_layout("Cadastro", content, show_nav=False)
    
    @app.get("/cadastro/sucesso")
    def cadastro_sucesso(request):
        """Página de sucesso do cadastro"""
        content = Container(
            Row(
                Col(
                    card_component(
                        "Cadastro realizado com sucesso!",
                        Div(
                            P(
                                "Sua conta foi criada com sucesso. "
                                "Enviamos um email de confirmação para o endereço informado."
                            ),
                            P(
                                "Clique no link do email para ativar sua conta e fazer login."
                            ),
                            Div(
                                A(
                                    "Fazer Login",
                                    href="/login",
                                    cls="btn btn-primary"
                                ),
                                cls="mt-3"
                            )
                        )
                    ),
                    width=6,
                    offset=3
                )
            ),
            cls="py-5"
        )
        
        return base_layout("Cadastro realizado", content, show_nav=False)
    
    # Rotas do cliente
    def cliente_dashboard(request):
        """Dashboard do cliente"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        # Buscar estatísticas do cliente
        try:
            # Contar veículos
            veiculos_count = db.execute(
                "SELECT COUNT(*) FROM veiculos WHERE usuario_id = ? AND ativo = TRUE",
                (user['usuario_id'],)
            ).fetchone()[0]
            
            # Contar garantias ativas
            garantias_count = db.execute(
                "SELECT COUNT(*) FROM garantias WHERE usuario_id = ? AND ativo = TRUE",
                (user['usuario_id'],)
            ).fetchone()[0]
            
            # Últimas garantias
            ultimas_garantias = db.execute("""
                SELECT g.id, p.sku, p.descricao, v.marca, v.modelo, v.placa, 
                       g.data_cadastro, g.data_vencimento
                FROM garantias g
                JOIN produtos p ON g.produto_id = p.id
                JOIN veiculos v ON g.veiculo_id = v.id
                WHERE g.usuario_id = ? AND g.ativo = TRUE
                ORDER BY g.data_cadastro DESC
                LIMIT 5
            """, (user['usuario_id'],)).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do dashboard do cliente {user['usuario_id']}: {e}")
            veiculos_count = 0
            garantias_count = 0
            ultimas_garantias = []
        
        content = Container(
            Row(
                Col(
                    H2(f"Bem-vindo, {user['usuario_email']}!", cls="mb-4")
                )
            ),
            Row(
                Col(
                    card_component(
                        "Meus Veículos",
                        Div(
                            H3(str(veiculos_count), cls="display-6 text-primary"),
                            P("veículos cadastrados")
                        ),
                        A("Gerenciar veículos", href="/cliente/veiculos", cls="btn btn-primary")
                    ),
                    width=6
                ),
                Col(
                    card_component(
                        "Garantias",
                        Div(
                            H3(str(garantias_count), cls="display-6 text-success"),
                            P("garantias ativas")
                        ),
                        A("Ver garantias", href="/cliente/garantias", cls="btn btn-primary")
                    ),
                    width=6
                )
            ),
            Row(
                Col(
                    card_component(
                        "Últimas Garantias Ativadas",
                        table_component(
                            ["Produto", "Veículo", "Data de Ativação", "Vencimento"],
                            [
                                [
                                    f"{g[1]} - {g[2]}",
                                    f"{g[3]} {g[4]} ({g[5]})",
                                    datetime.fromisoformat(g[6]).strftime('%d/%m/%Y') if g[6] else 'N/A',
                                    datetime.fromisoformat(g[7]).strftime('%d/%m/%Y') if g[7] else 'N/A'
                                ] for g in ultimas_garantias
                            ]
                        ) if ultimas_garantias else P("Nenhuma garantia ativada ainda.", cls="text-muted"),
                        A("Ativar nova garantia", href="/cliente/garantias/nova", cls="btn btn-primary")
                    ),
                    width=12
                )
            )
        )
        
        return base_layout("Dashboard", content, user)
    
    # Aplicar decorador e registrar rota na ordem correta
    cliente_dashboard = login_required(cliente_dashboard)
    app.get("/cliente")(cliente_dashboard)
    
    # Rotas do administrador
    @app.get("/admin")
    @admin_required
    def admin_dashboard(request):
        """Dashboard do administrador"""
        user = request.state.usuario
        
        # Buscar estatísticas gerais
        try:
            stats = {
                'usuarios': db.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario = 'cliente'").fetchone()[0],
                'produtos': db.execute("SELECT COUNT(*) FROM produtos WHERE ativo = TRUE").fetchone()[0],
                'veiculos': db.execute("SELECT COUNT(*) FROM veiculos WHERE ativo = TRUE").fetchone()[0],
                'garantias': db.execute("SELECT COUNT(*) FROM garantias WHERE ativo = TRUE").fetchone()[0]
            }
            
            # Últimas ativações de garantia
            ultimas_ativacoes = db.execute("""
                SELECT u.nome, u.email, p.sku, p.descricao, g.data_cadastro
                FROM garantias g
                JOIN usuarios u ON g.usuario_id = u.id
                JOIN produtos p ON g.produto_id = p.id
                WHERE g.ativo = TRUE
                ORDER BY g.data_cadastro DESC
                LIMIT 10
            """).fetchall()
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do dashboard admin: {e}")
            stats = {'usuarios': 0, 'produtos': 0, 'veiculos': 0, 'garantias': 0}
            ultimas_ativacoes = []
        
        content = Container(
            Row(
                Col(
                    H2(f"Dashboard Administrativo", cls="mb-4")
                )
            ),
            Row(
                Col(
                    card_component(
                        "Clientes",
                        Div(
                            H3(str(stats['usuarios']), cls="display-6 text-info"),
                            P("clientes cadastrados")
                        ),
                        A("Gerenciar clientes", href="/admin/usuarios", cls="btn btn-info")
                    ),
                    width=3
                ),
                Col(
                    card_component(
                        "Produtos",
                        Div(
                            H3(str(stats['produtos']), cls="display-6 text-warning"),
                            P("produtos ativos")
                        ),
                        A("Gerenciar produtos", href="/admin/produtos", cls="btn btn-warning")
                    ),
                    width=3
                ),
                Col(
                    card_component(
                        "Veículos",
                        Div(
                            H3(str(stats['veiculos']), cls="display-6 text-secondary"),
                            P("veículos cadastrados")
                        )
                    ),
                    width=3
                ),
                Col(
                    card_component(
                        "Garantias",
                        Div(
                            H3(str(stats['garantias']), cls="display-6 text-success"),
                            P("garantias ativas")
                        ),
                        A("Ver garantias", href="/admin/garantias", cls="btn btn-primary")
                    ),
                    width=3
                )
            ),
            Row(
                Col(
                    card_component(
                        "Últimas Ativações de Garantia",
                        table_component(
                            ["Cliente", "Email", "Produto", "Data de Ativação"],
                            [
                                [
                                    a[0],
                                    a[1],
                                    f"{a[2]} - {a[3]}",
                                    datetime.fromisoformat(a[4]).strftime('%d/%m/%Y %H:%M') if a[4] else 'N/A'
                                ] for a in ultimas_ativacoes
                            ]
                        ) if ultimas_ativacoes else P("Nenhuma ativação recente.", cls="text-muted")
                    ),
                    width=12
                )
            )
        )
        
        return base_layout("Dashboard Admin", content, user)
    
    # Páginas institucionais
    @app.get("/sobre")
    def sobre_page(request):
        """Página sobre a empresa"""
        content = Container(
            Row(
                Col(
                    H1("Sobre a Viemar", cls="mb-4"),
                    P(
                        "A Viemar é uma empresa especializada em produtos automotivos de alta qualidade, "
                        "oferecendo garantia estendida de 70.000 km ou 2 anos para seus produtos.",
                        cls="lead"
                    ),
                    H3("Nossa Missão", cls="mt-4 mb-3"),
                    P(
                        "Proporcionar tranquilidade e segurança aos nossos clientes através de produtos "
                        "de qualidade superior e um sistema de garantia confiável e eficiente."
                    ),
                    H3("Nossos Valores", cls="mt-4 mb-3"),
                    Ul(
                        Li("Qualidade em primeiro lugar"),
                        Li("Atendimento personalizado"),
                        Li("Transparência nos processos"),
                        Li("Inovação constante"),
                        Li("Compromisso com o cliente")
                    ),
                    width=8,
                    offset=2
                )
            )
        )
        return base_layout("Sobre", content)
    
    @app.get("/regulamento")
    def regulamento_route(request):
        """Página de regulamento da garantia"""
        user = get_current_user(request)
        content = regulamento_page(user)
        return base_layout("Regulamento", content, user)
    
    @app.get("/contato")
    def contato_route(request):
        """Página de contato"""
        user = get_current_user(request)
        content = contato_page(user)
        return base_layout("Contato", content, user)
    
    @app.post("/contato")
    async def contato_submit(request):
        """Processa formulário de contato"""
        form_data = await request.form()
        
        # Aqui você pode processar o formulário (enviar email, salvar no banco, etc.)
        logger.info(f"Mensagem de contato recebida de {form_data.get('email')}")
        
        content = Container(
            Row(
                Col(
                    alert_component(
                        "Mensagem enviada com sucesso! Entraremos em contato em breve.",
                        "success"
                    ),
                    A("Voltar ao início", href="/", cls="btn btn-primary"),
                    width=6,
                    offset=3
                )
            )
        )
        return base_layout("Mensagem Enviada", content)
    
    @app.get("/admin/dashboard")
    @admin_required
    def admin_dashboard_redirect(request):
        """Redireciona para o dashboard admin"""
        return RedirectResponse('/admin', status_code=302)
    
    def cliente_dashboard_redirect(request):
        """Redireciona para o dashboard do cliente"""
        user = request.state.usuario
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        return RedirectResponse('/cliente', status_code=302)
    
    # Aplicar decorador e registrar rota na ordem correta
    cliente_dashboard_redirect = login_required(cliente_dashboard_redirect)
    app.get("/cliente/dashboard")(cliente_dashboard_redirect)
    
    @app.get("/cliente/perfil")
    @login_required
    def cliente_perfil(request):
        """Página de perfil do cliente"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        # Buscar dados completos do usuário
        try:
            usuario_completo = db.execute(
                "SELECT id, email, nome, telefone, data_cadastro FROM usuarios WHERE id = ?",
                (user['usuario_id'],)
            ).fetchone()
            
            if not usuario_completo:
                return RedirectResponse('/cliente', status_code=302)
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados do usuário {user['usuario_id']}: {e}")
            return RedirectResponse('/cliente', status_code=302)
        
        content = Container(
            Row(
                Col(
                    H2("Meu Perfil", cls="mb-4")
                )
            ),
            Row(
                Col(
                    card_component(
                        None,  # Remove título redundante
                        Form(
                            Div(
                                Label("Nome", for_="nome", cls="form-label"),
                                Input(
                                    type="text",
                                    id="nome",
                                    name="nome",
                                    value=usuario_completo[2] or "",
                                    cls="form-control",
                                    required=True
                                ),
                                cls="mb-3"
                            ),
                            Div(
                                Label("Email", for_="email", cls="form-label"),
                                Input(
                                    type="email",
                                    id="email",
                                    name="email",
                                    value=usuario_completo[1],
                                    cls="form-control",
                                    readonly=True
                                ),
                                Small("O email não pode ser alterado", cls="form-text text-muted"),
                                cls="mb-3"
                            ),
                            Div(
                                Label("Telefone", for_="telefone", cls="form-label"),
                                Input(
                                    type="tel",
                                    id="telefone",
                                    name="telefone",
                                    value=usuario_completo[3] or "",
                                    cls="form-control",
                                    placeholder="(11) 99999-9999"
                                ),
                                cls="mb-3"
                            ),
                            Div(
                                Button("Salvar Alterações", type="submit", cls="btn btn-primary me-2"),
                                A("Voltar", href="/cliente", cls="btn btn-secondary"),
                                cls="d-flex gap-2"
                            ),
                            method="post",
                            action="/cliente/perfil"
                        )
                    ),
                    width=8
                ),
                Col(
                    card_component(
                        "Informações da Conta",
                        Div(
                            P(f"Membro desde: {datetime.fromisoformat(usuario_completo[4]).strftime('%d/%m/%Y') if usuario_completo[4] else 'N/A'}"),
                            P(f"ID da conta: {usuario_completo[0]}"),
                            Hr(),
                            A("Alterar Senha", href="/cliente/alterar-senha", cls="btn btn-outline-warning btn-sm")
                        )
                    ),
                    width=4
                )
            )
        )
        
        return base_layout("Meu Perfil", content, user)
    
    async def cliente_perfil_update(request):
        """Atualiza perfil do cliente"""
        user = request.state.usuario
        
        if user['tipo_usuario'] != 'cliente':
            return RedirectResponse('/admin', status_code=302)
        
        form_data = await request.form()
        nome = form_data.get('nome', '').strip()
        telefone = form_data.get('telefone', '').strip()
        
        try:
            db.execute(
                "UPDATE usuarios SET nome = ?, telefone = ? WHERE id = ?",
                (nome, telefone, user['usuario_id'])
            )
            
            logger.info(f"Perfil atualizado para usuário {user['usuario_id']}")
            return RedirectResponse('/cliente/perfil?sucesso=atualizado', status_code=302)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil do usuário {user['usuario_id']}: {e}")
            return RedirectResponse('/cliente/perfil?erro=interno', status_code=302)
    
    # Aplicar decorador e registrar rota na ordem correta
    cliente_perfil_update = login_required(cliente_perfil_update)
    app.post("/cliente/perfil")(cliente_perfil_update)
    
    # Rota para confirmação de email
    @app.get("/confirmar-email")
    async def confirmar_email_route(request):
        """Confirma o email do usuário através do token"""
        token = request.query_params.get('token')
        
        if not token:
            content = Container(
                Row(
                    Col(
                        alert_component(
                            "Token de confirmação não fornecido.",
                            "danger"
                        ),
                        A("Voltar ao início", href="/", cls="btn btn-primary"),
                        width=6,
                        offset=3
                    )
                ),
                cls="py-5"
            )
            return base_layout("Erro na Confirmação", content, show_nav=False)
        
        try:
            # Buscar usuário pelo token
            result = db.execute(
                "SELECT id, nome, email FROM usuarios WHERE token_confirmacao = ? AND confirmado = FALSE",
                (token,)
            ).fetchone()
            
            if not result:
                content = Container(
                    Row(
                        Col(
                            alert_component(
                                "Token inválido ou já utilizado. O link pode ter expirado.",
                                "warning"
                            ),
                            A("Fazer login", href="/login", cls="btn btn-primary me-2"),
                            A("Voltar ao início", href="/", cls="btn btn-secondary"),
                            width=6,
                            offset=3
                        )
                    ),
                    cls="py-5"
                )
                return base_layout("Token Inválido", content, show_nav=False)
            
            usuario_id, nome, email = result
            
            # Confirmar o email
            from app.auth import confirmar_email
            if confirmar_email(usuario_id, token):
                logger.info(f"Email confirmado com sucesso para usuário: {email}")
                
                content = Container(
                    Row(
                        Col(
                            alert_component(
                                "Email confirmado com sucesso! Agora você pode fazer login.",
                                "success"
                            ),
                            H3(f"Bem-vindo, {nome}!", cls="text-center mb-4"),
                            P("Sua conta foi ativada com sucesso. Agora você pode acessar todas as funcionalidades do sistema.", cls="text-center mb-4"),
                            Div(
                                A("Fazer Login", href="/login", cls="btn btn-primary btn-lg me-2"),
                                A("Voltar ao início", href="/", cls="btn btn-secondary btn-lg"),
                                cls="text-center"
                            ),
                            width=8,
                            offset=2
                        )
                    ),
                    cls="py-5"
                )
                return base_layout("Email Confirmado", content, show_nav=False)
            else:
                content = Container(
                    Row(
                        Col(
                            alert_component(
                                "Erro interno ao confirmar email. Tente novamente mais tarde.",
                                "danger"
                            ),
                            A("Voltar ao início", href="/", cls="btn btn-primary"),
                            width=6,
                            offset=3
                        )
                    ),
                    cls="py-5"
                )
                return base_layout("Erro na Confirmação", content, show_nav=False)
                
        except Exception as e:
            logger.error(f"Erro ao confirmar email com token {token}: {e}")
            content = Container(
                Row(
                    Col(
                        alert_component(
                            "Erro interno. Tente novamente mais tarde.",
                            "danger"
                        ),
                        A("Voltar ao início", href="/", cls="btn btn-primary"),
                        width=6,
                        offset=3
                    )
                ),
                cls="py-5"
            )
            return base_layout("Erro na Confirmação", content, show_nav=False)
    
    # Endpoint para consulta de CEP via API ViaCEP
    @app.get("/api/cep/{cep}")
    def consultar_cep_api(cep: str):
        """
        Endpoint para consultar CEP via API ViaCEP.
        
        Args:
            cep: CEP com 8 dígitos numéricos
            
        Returns:
            JSON com dados do endereço ou erro
        """
        try:
            # Limpar CEP (remover caracteres não numéricos)
            cep_limpo = ''.join(filter(str.isdigit, cep))
            
            # Consultar CEP
            dados, erro = consultar_cep_sync(cep_limpo)
            
            if erro:
                logger.warning(f"Erro na consulta de CEP {cep}: {erro}")
                return {"success": False, "error": erro}
            
            logger.info(f"CEP {cep} consultado com sucesso via API")
            return {"success": True, "data": dados}
            
        except Exception as e:
            logger.error(f"Erro inesperado na consulta de CEP {cep}: {e}")
            return {"success": False, "error": "Erro interno do servidor"}

    logger.info("Rotas configuradas com sucesso")