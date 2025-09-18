#!/usr/bin/env python3
"""
Templates e componentes visuais da aplicação
"""

from fasthtml.common import *
from monsterui.all import *
from typing import Optional, List, Dict, Any

# Definir Row como um Div com classe Bootstrap
Row = lambda *args, **kwargs: Div(*args, cls=f"row {kwargs.get('cls', '')}".strip(), **{k: v for k, v in kwargs.items() if k != 'cls'})

# Usar componentes MonsterUI (não precisamos redefinir, já estão disponíveis)

def base_layout(title: str, content, user: Optional[Dict[str, Any]] = None, show_nav: bool = True):
    """Layout base da aplicação usando MonsterUI NavBar responsivo"""
    
    # Criar links de navegação baseados no tipo de usuário
    nav_links = []
    user_info = None
    
    if user and show_nav:
        if user['tipo_usuario'] in ['admin', 'administrador']:
            nav_links = [
                A("Dashboard", href="/admin"),
                A("Usuários", href="/admin/usuarios"),
                A("Produtos", href="/admin/produtos"),
                A("Sincronizar ERP Tecnicon", href="/admin/produtos/sync"),
                A("Garantias", href="/admin/garantias"),
                A("Relatórios", href="/admin/relatorios"),
                A("Regulamento", href="/regulamento"),
                A("Contato", href="/contato"),
                A("Sair", href="/logout", cls="text-red-500")
            ]
        else:
            nav_links = [
                A("Meus Dados", href="/cliente/perfil"),
                A("Meus Veículos", href="/cliente/veiculos"),
                A("Garantias", href="/cliente/garantias"),
                A("Regulamento", href="/regulamento"),
                A("Contato", href="/contato"),
                A("Sair", href="/logout", cls="text-red-500")
            ]
        
        # Extrair apenas o primeiro nome do campo nome da tabela usuarios
        nome_completo = user.get('nome', '')
        primeiro_nome = nome_completo.split()[0] if nome_completo and nome_completo.strip() else ''
        user_info = Span(f"Olá, {primeiro_nome}", cls="text-sm text-gray-600") if primeiro_nome else None
    
    # Criar navbar usando MonsterUI
    navbar = None
    if show_nav and user:
        # Brand com logo
        brand = Div(
            Img(src="/static/g70k.png", alt="G70K", cls="h-16 w-auto mr-2"),
            cls="flex items-center"
        )
        
        # Adicionar informações do usuário aos links
        if user_info:
            nav_links.insert(0, user_info)
        
        navbar = NavBar(*nav_links, brand=brand, sticky=True)
    
    return Titled(title,
        Div(
            navbar,
            Main(
                Container(
                    content,
                    cls="main-container"
                ),
                cls="min-h-screen"
            ),
            footer_component(),
            # JavaScript para consulta automática de CEP
            Script("""
                async function consultarCEP(cep) {
                    // Limpar CEP (remover caracteres não numéricos)
                    const cepLimpo = cep.replace(/\D/g, '');
                    
                    // Validar se tem 8 dígitos
                    if (cepLimpo.length !== 8) {
                        return;
                    }
                    
                    try {
                        // Mostrar loading nos campos
                        const campos = ['endereco', 'bairro', 'cidade', 'uf'];
                        campos.forEach(campo => {
                            const elemento = document.getElementById(campo);
                            if (elemento) {
                                elemento.value = 'Carregando...';
                                elemento.disabled = true;
                            }
                        });
                        
                        // Fazer requisição para API
                        const response = await fetch(`/api/cep/${cepLimpo}`);
                        const result = await response.json();
                        
                        // Reabilitar campos
                        campos.forEach(campo => {
                            const elemento = document.getElementById(campo);
                            if (elemento) {
                                elemento.disabled = false;
                            }
                        });
                        
                        if (result.success && result.data) {
                            // Preencher campos com dados do CEP
                            const data = result.data;
                            
                            const enderecoEl = document.getElementById('endereco');
                            if (enderecoEl) enderecoEl.value = data.logradouro || '';
                            
                            const bairroEl = document.getElementById('bairro');
                            if (bairroEl) bairroEl.value = data.bairro || '';
                            
                            const cidadeEl = document.getElementById('cidade');
                            if (cidadeEl) cidadeEl.value = data.cidade || '';
                            
                            const ufEl = document.getElementById('uf');
                            if (ufEl) {
                                if (ufEl.tagName === 'SELECT') {
                                    // Para select, definir o valor selecionado
                                    ufEl.value = data.uf || '';
                                } else {
                                    // Para input text
                                    ufEl.value = data.uf || '';
                                }
                            }
                            
                            // Mostrar mensagem de sucesso
                            console.log('CEP consultado com sucesso:', data.cidade + '/' + data.uf);
                            
                        } else {
                            // Limpar campos em caso de erro
                            campos.forEach(campo => {
                                const elemento = document.getElementById(campo);
                                if (elemento && elemento.value === 'Carregando...') {
                                    elemento.value = '';
                                }
                            });
                            
                            // Mostrar erro
                            const erro = result.error || 'CEP não encontrado';
                            console.warn('Erro na consulta do CEP:', erro);
                            
                            // Opcional: mostrar alerta para o usuário
                            if (erro !== 'CEP deve ter exatamente 8 dígitos numéricos') {
                                alert('Erro: ' + erro);
                            }
                        }
                        
                    } catch (error) {
                        console.error('Erro na consulta do CEP:', error);
                        
                        // Reabilitar e limpar campos
                        const campos = ['endereco', 'bairro', 'cidade', 'uf'];
                        campos.forEach(campo => {
                            const elemento = document.getElementById(campo);
                            if (elemento) {
                                elemento.disabled = false;
                                if (elemento.value === 'Carregando...') {
                                    elemento.value = '';
                                }
                            }
                        });
                        
                        alert('Erro de conexão ao consultar CEP');
                    }
                }
                
                // Função para formatar CEP enquanto digita
                function formatarCEP(input) {
                    // Remove caracteres não numéricos
                    let valor = input.value.replace(/\D/g, '');
                    
                    // Limita a 8 dígitos
                    if (valor.length > 8) {
                        valor = valor.substring(0, 8);
                    }
                    
                    input.value = valor;
                }
                
                // Adicionar evento de formatação ao campo CEP
                document.addEventListener('DOMContentLoaded', function() {
                    const cepInput = document.getElementById('cep');
                    if (cepInput) {
                        cepInput.addEventListener('input', function() {
                            formatarCEP(this);
                        });
                    }
                });
            """)
        )
    )


def footer_component():
    """Componente de rodapé"""
    return Footer(
        Container(
            Row(
                Col(
                    P("© 2024 Viemar - Garantia G70K. Todos os direitos reservados.", 
                      cls="text-center text-muted mb-0")
                )
            )
        ),
        cls="bg-light py-3 mt-auto"
    )


def page_layout(title: str, content, user: Optional[Dict[str, Any]] = None):
    """Layout padrão para páginas internas"""
    return base_layout(title, content, user)


def form_group(label: str, input_element, error: Optional[str] = None, help_text: Optional[str] = None, required: bool = False):
    """Componente para grupo de formulário com label, input e erro"""
    # Se required=True, adicionar asterisco ao label
    label_text = f"{label} *" if required else label
    
    elements = [
        Label(label_text, cls="form-label"),
        input_element
    ]
    
    if error:
        elements.append(Div(error, cls="invalid-feedback d-block"))
    
    if help_text:
        elements.append(Small(help_text, cls="form-text text-muted"))
    
    return Div(*elements, cls="mb-3")


def alert_component(message: str, alert_type: str = "info"):
    """Componente de alerta usando MonsterUI"""
    alert_classes = {
        "success": "alert-success",
        "error": "alert-error", 
        "warning": "alert-warning",
        "info": "alert-info"
    }
    return Alert(message, cls=alert_classes.get(alert_type, "alert-info"))


def card_component(title: str, content, footer=None):
    """Componente de card usando MonsterUI"""
    card_content = [
        CardHeader(H3(title, cls="card-title")) if title else None,
        CardBody(content) if content else None,
        CardFooter(footer) if footer else None
    ]
    # Filtrar elementos None
    card_content = [item for item in card_content if item is not None]
    return Card(*card_content)


def table_component(headers: List[str], rows: List[List[str]], table_id: str = None):
    """Componente de tabela responsiva usando MonsterUI"""
    if not headers or not rows:
        return Div("Nenhum dado disponível", cls="text-muted text-center p-3")
    
    # Criar cabeçalho da tabela
    thead = Thead(
        Tr(*[Th(header, scope="col") for header in headers])
    )
    
    # Criar corpo da tabela
    tbody_rows = []
    for row in rows:
        tbody_rows.append(
            Tr(*[Td(str(cell) if cell is not None else '') for cell in row])
        )
    
    tbody = Tbody(*tbody_rows)
    
    # Criar tabela completa
    table_attrs = {"cls": "table table-striped table-hover"}
    if table_id:
        table_attrs["id"] = table_id
    
    return Div(
        Table(thead, tbody, **table_attrs),
        cls="table-responsive"
    )

def login_form(error_message: Optional[str] = None, email_value: str = ""):
    """Formulário de login"""
    return Form(
        Div(
            form_group(
                "Email",
                Input(
                    type="email",
                    name="email",
                    cls="form-control",
                    placeholder="seu@email.com",
                    value=email_value,
                    required=True
                )
            ),
            form_group(
                "Senha",
                Input(
                    type="password",
                    name="senha",
                    cls="form-control",
                    placeholder="Sua senha",
                    required=True
                )
            ),
            Div(
                Button("Entrar", type="submit", cls="btn btn-primary w-100"),
                cls="d-grid"
            ),
            Div(
                A("Esqueci minha senha", href="/reset-senha", cls="text-decoration-none"),
                " | ",
                A("Criar conta", href="/cadastro", cls="text-decoration-none"),
                cls="text-center mt-3"
            ),
            alert_component(error_message, "error") if error_message else None,
            cls="p-4"
        ),
        method="post",
        action="/login"
    )

def cadastro_form(errors: Dict = None, form_data: Dict = None):
    """Formulário de cadastro de usuário"""
    if errors is None:
        errors = {}
    if form_data is None:
        form_data = {}
    
    return Form(
        Div(
            Row(
                Col(
                    form_group(
                        "Nome Completo",
                        Input(
                            type="text",
                            name="nome",
                            cls="form-control",
                            placeholder="João da Silva",
                            value=form_data.get('nome', ''),
                            required=True
                        ),
                        error=errors.get('nome')
                    ),
                    width=12
                ),
                Col(
                    form_group(
                        "Email",
                        Input(
                            type="email",
                            name="email",
                            cls="form-control",
                            placeholder="joao@email.com",
                            value=form_data.get('email', ''),
                            required=True
                        ),
                        error=errors.get('email')
                    ),
                    width=12
                ),
                Col(
                    form_group(
                        "Telefone",
                        Input(
                            type="tel",
                            name="telefone",
                            cls="form-control",
                            placeholder="(11) 99999-9999",
                            value=form_data.get('telefone', ''),
                            required=True
                        ),
                        error=errors.get('telefone')
                    ),
                    width=6
                ),
                Col(
                    form_group(
                        "CPF/CNPJ",
                        Input(
                            type="text",
                            name="cpf_cnpj",
                            cls="form-control",
                            placeholder="000.000.000-00",
                            value=form_data.get('cpf_cnpj', ''),
                            required=True
                        ),
                        error=errors.get('cpf_cnpj')
                    ),
                    width=6
                ),
                Col(
                    form_group(
                        "CEP",
                        Input(
                            type="text",
                            name="cep",
                            id="cep",
                            cls="form-control",
                            placeholder="00000-000",
                            value=form_data.get('cep', ''),
                            required=True,
                            maxlength="8",
                            onblur="consultarCEP(this.value)",
                            **{"data-cep": "true"}
                        ),
                        error=errors.get('cep')
                    ),
                    width=4
                ),
                Col(
                    form_group(
                        "Logradouro",
                        Input(
                            type="text",
                            name="endereco",
                            id="endereco",
                            cls="form-control",
                            placeholder="Rua das Flores, 123",
                            value=form_data.get('endereco', ''),
                            required=True,
                            **{"data-endereco": "true"}
                        ),
                        error=errors.get('endereco')
                    ),
                    width=8
                ),
                Col(
                    form_group(
                        "Bairro",
                        Input(
                            type="text",
                            name="bairro",
                            id="bairro",
                            cls="form-control",
                            placeholder="Centro",
                            value=form_data.get('bairro', ''),
                            required=True,
                            **{"data-bairro": "true"}
                        ),
                        error=errors.get('bairro')
                    ),
                    width=4
                ),
                Col(
                    form_group(
                        "Cidade",
                        Input(
                            type="text",
                            name="cidade",
                            id="cidade",
                            cls="form-control",
                            placeholder="São Paulo",
                            value=form_data.get('cidade', ''),
                            required=True,
                            **{"data-cidade": "true"}
                        ),
                        error=errors.get('cidade')
                    ),
                    width=6
                ),
                Col(
                    form_group(
                        "UF",
                        Input(
                            type="text",
                            name="uf",
                            id="uf",
                            cls="form-control",
                            placeholder="SP",
                            value=form_data.get('uf', ''),
                            required=True,
                            maxlength="2",
                            **{"data-uf": "true"}
                        ),
                        error=errors.get('uf')
                    ),
                    width=2
                ),
                Col(
                    form_group(
                        "Data de Nascimento",
                        Input(
                            type="date",
                            name="data_nascimento",
                            cls="form-control",
                            value=form_data.get('data_nascimento', ''),
                            required=True
                        ),
                        error=errors.get('data_nascimento')
                    ),
                    width=6
                ),
                Col(
                    form_group(
                        "Senha",
                        Input(
                            type="password",
                            name="senha",
                            cls="form-control",
                            placeholder="Mínimo 6 caracteres",
                            required=True,
                            minlength="6"
                        ),
                        error=errors.get('senha')
                    ),
                    width=6
                ),
                Col(
                    form_group(
                        "Confirmar Senha",
                        Input(
                            type="password",
                            name="confirmar_senha",
                            cls="form-control",
                            placeholder="Repita a senha",
                            required=True,
                            minlength="6"
                        ),
                        error=errors.get('confirmar_senha')
                    ),
                    width=6
                )
            ),
            Div(
                Button("Criar Conta", type="submit", cls="btn btn-primary w-100"),
                cls="d-grid mt-3"
            ),
            Div(
                "Já tem uma conta? ",
                A("Faça login", href="/login", cls="text-decoration-none"),
                cls="text-center mt-3"
            ),
            cls="p-4"
        ),
        method="post",
        action="/cadastro"
    )


def dashboard_page(user: Dict[str, Any]):
    """Página do dashboard"""
    if user['tipo_usuario'] in ['admin', 'administrador']:
        return admin_dashboard()
    else:
        return cliente_dashboard(user)


def admin_dashboard():
    """Dashboard do administrador"""
    return Div(
        H1("Dashboard Administrativo", cls="mb-4"),
        Row(
            Col(
                Card(
                    CardBody(
                        H5("Usuários", cls="card-title"),
                        P("Gerenciar usuários do sistema", cls="card-text"),
                        A("Acessar", href="/admin/usuarios", cls="btn btn-primary")
                    )
                ),
                width=4
            ),
            Col(
                Card(
                    CardBody(
                        H5("Produtos", cls="card-title"),
                        P("Gerenciar produtos e sincronização", cls="card-text"),
                        A("Acessar", href="/admin/produtos", cls="btn btn-primary")
                    )
                ),
                width=4
            ),
            Col(
                Card(
                    CardBody(
                        H5("Garantias", cls="card-title"),
                        P("Visualizar e gerenciar garantias", cls="card-text"),
                        A("Acessar", href="/admin/garantias", cls="btn btn-primary")
                    )
                ),
                width=4
            )
        )
    )


def cliente_dashboard(user: Dict[str, Any]):
    """Dashboard do cliente"""
    return Div(
        H1(f"Bem-vindo, {user.get('nome', 'Cliente')}!", cls="mb-4"),
        Row(
            Col(
                Card(
                    CardBody(
                        H5("Meus Dados", cls="card-title"),
                        P("Visualizar e editar informações pessoais", cls="card-text"),
                        A("Acessar", href="/cliente/perfil", cls="btn btn-primary")
                    )
                ),
                width=6
            ),
            Col(
                Card(
                    CardBody(
                        H5("Meus Veículos", cls="card-title"),
                        P("Gerenciar veículos cadastrados", cls="card-text"),
                        A("Acessar", href="/cliente/veiculos", cls="btn btn-primary")
                    )
                ),
                width=6
            )
        ),
        Row(
            Col(
                Card(
                    CardBody(
                        H5("Garantias", cls="card-title"),
                        P("Visualizar garantias ativas", cls="card-text"),
                        A("Acessar", href="/cliente/garantias", cls="btn btn-primary")
                    )
                ),
                width=6
            ),
            Col(
                Card(
                    CardBody(
                        H5("Regulamento", cls="card-title"),
                        P("Consultar termos e condições", cls="card-text"),
                        A("Acessar", href="/regulamento", cls="btn btn-primary")
                    )
                ),
                width=6
            )
        )
    )


def usuarios_page():
    """Página de gerenciamento de usuários"""
    return Div(
        H1("Gerenciamento de Usuários", cls="mb-4"),
        Div(
            A("Novo Usuário", href="/admin/usuarios/novo", cls="btn btn-success mb-3"),
            Div(id="usuarios-list", cls="table-responsive")
        )
    )


def produtos_page():
    """Página de gerenciamento de produtos"""
    return Div(
        H1("Gerenciamento de Produtos", cls="mb-4"),
        Div(
            A("Novo Produto", href="/admin/produtos/novo", cls="btn btn-success mb-3"),
            A("Sincronizar ERP", href="/admin/produtos/sync", cls="btn btn-info mb-3 ms-2"),
            Div(id="produtos-list", cls="table-responsive")
        )
    )


def servicos_page():
    """Página de gerenciamento de serviços"""
    return Div(
        H1("Gerenciamento de Serviços", cls="mb-4"),
        Div(
            A("Novo Serviço", href="/admin/servicos/novo", cls="btn btn-success mb-3"),
            Div(id="servicos-list", cls="table-responsive")
        )
    )


def garantias_page():
    """Página de gerenciamento de garantias"""
    return Div(
        H1("Gerenciamento de Garantias", cls="mb-4"),
        Div(
            A("Nova Garantia", href="/admin/garantias/nova", cls="btn btn-success mb-3"),
            Div(id="garantias-list", cls="table-responsive")
        )
    )


def relatorios_page():
    """Página de relatórios"""
    return Div(
        H1("Relatórios", cls="mb-4"),
        Row(
            Col(
                Card(
                    CardBody(
                        H5("Relatório de Usuários", cls="card-title"),
                        P("Relatório completo de usuários cadastrados", cls="card-text"),
                        A("Gerar", href="/admin/relatorios/usuarios", cls="btn btn-primary")
                    )
                ),
                width=4
            ),
            Col(
                Card(
                    CardBody(
                        H5("Relatório de Produtos", cls="card-title"),
                        P("Relatório de produtos e estoque", cls="card-text"),
                        A("Gerar", href="/admin/relatorios/produtos", cls="btn btn-primary")
                    )
                ),
                width=4
            ),
            Col(
                Card(
                    CardBody(
                        H5("Relatório de Garantias", cls="card-title"),
                        P("Relatório de garantias ativas e vencidas", cls="card-text"),
                        A("Gerar", href="/admin/relatorios/garantias", cls="btn btn-primary")
                    )
                ),
                width=4
            )
        )
    )


def contato_page():
    """Página de contato"""
    return Div(
        H1("Contato", cls="mb-4"),
        Row(
            Col(
                Card(
                    CardBody(
                        H5("Informações de Contato", cls="card-title"),
                        P("Entre em contato conosco através dos canais abaixo:", cls="card-text"),
                        Hr(),
                        P(Strong("Telefone: "), "(11) 1234-5678"),
                        P(Strong("Email: "), "contato@viemar.com.br"),
                        P(Strong("Endereço: "), "Rua Exemplo, 123 - São Paulo/SP")
                    )
                ),
                width=6
            ),
            Col(
                Card(
                    CardBody(
                        H5("Envie uma Mensagem", cls="card-title"),
                        Form(
                            form_group("Nome", Input(type="text", name="nome", cls="form-control", required=True)),
                            form_group("Email", Input(type="email", name="email", cls="form-control", required=True)),
                            form_group("Assunto", Input(type="text", name="assunto", cls="form-control", required=True)),
                            form_group("Mensagem", Textarea(name="mensagem", cls="form-control", rows="5", required=True)),
                            Button("Enviar", type="submit", cls="btn btn-primary"),
                            method="post",
                            action="/contato"
                        )
                    )
                ),
                width=6
            )
        )
    )


def form_usuario(form_data: Dict = None, errors: Dict = None):
    """Formulário de usuário"""
    if form_data is None:
        form_data = {}
    if errors is None:
        errors = {}
    
    return Form(
        Row(
            Col(
                form_group(
                    "Nome Completo",
                    Input(
                        type="text",
                        name="nome",
                        cls="form-control",
                        placeholder="João da Silva",
                        value=form_data.get('nome', ''),
                        required=True
                    ),
                    error=errors.get('nome')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Email",
                    Input(
                        type="email",
                        name="email",
                        cls="form-control",
                        placeholder="joao@email.com",
                        value=form_data.get('email', ''),
                        required=True
                    ),
                    error=errors.get('email')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "CPF",
                    Input(
                        type="text",
                        name="cpf",
                        cls="form-control",
                        placeholder="000.000.000-00",
                        value=form_data.get('cpf', ''),
                        required=True
                    ),
                    error=errors.get('cpf')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Telefone",
                    Input(
                        type="tel",
                        name="telefone",
                        cls="form-control",
                        placeholder="(11) 99999-9999",
                        value=form_data.get('telefone', '')
                    ),
                    error=errors.get('telefone')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "CEP",
                    Input(
                        type="text",
                        name="cep",
                        id="cep",
                        cls="form-control",
                        placeholder="00000000 (8 dígitos)",
                        value=form_data.get('cep', ''),
                        maxlength="8",
                        pattern="[0-9]{8}",
                        title="Digite apenas 8 dígitos numéricos",
                        onblur="consultarCEP(this.value)"
                    ),
                    error=errors.get('cep')
                ),
                width=3
            ),
            Col(
                form_group(
                    "Endereço",
                    Input(
                        type="text",
                        name="endereco",
                        id="endereco",
                        cls="form-control",
                        placeholder="Rua Leopoldo Schultz, 321",
                        value=form_data.get('endereco', '')
                    ),
                    error=errors.get('endereco')
                ),
                width=9
            )
        ),
        Row(
            Col(
                form_group(
                    "Bairro",
                    Input(
                        type="text",
                        name="bairro",
                        id="bairro",
                        cls="form-control",
                        placeholder="Parque da matriz",
                        value=form_data.get('bairro', '')
                    ),
                    error=errors.get('bairro')
                ),
                width=4
            ),
            Col(
                form_group(
                    "Cidade",
                    Input(
                        type="text",
                        name="cidade",
                        id="cidade",
                        cls="form-control",
                        placeholder="Cachoeirinha",
                        value=form_data.get('cidade', '')
                    ),
                    error=errors.get('cidade')
                ),
                width=6
            ),
            Col(
                form_group(
                    "UF",
                    Select(
                        Option("Selecione...", value="", selected=(not form_data.get('uf'))),
                        Option("AC", value="AC", selected=(form_data.get('uf') == 'AC')),
                        Option("AL", value="AL", selected=(form_data.get('uf') == 'AL')),
                        Option("AP", value="AP", selected=(form_data.get('uf') == 'AP')),
                        Option("AM", value="AM", selected=(form_data.get('uf') == 'AM')),
                        Option("BA", value="BA", selected=(form_data.get('uf') == 'BA')),
                        Option("CE", value="CE", selected=(form_data.get('uf') == 'CE')),
                        Option("DF", value="DF", selected=(form_data.get('uf') == 'DF')),
                        Option("ES", value="ES", selected=(form_data.get('uf') == 'ES')),
                        Option("GO", value="GO", selected=(form_data.get('uf') == 'GO')),
                        Option("MA", value="MA", selected=(form_data.get('uf') == 'MA')),
                        Option("MT", value="MT", selected=(form_data.get('uf') == 'MT')),
                        Option("MS", value="MS", selected=(form_data.get('uf') == 'MS')),
                        Option("MG", value="MG", selected=(form_data.get('uf') == 'MG')),
                        Option("PA", value="PA", selected=(form_data.get('uf') == 'PA')),
                        Option("PB", value="PB", selected=(form_data.get('uf') == 'PB')),
                        Option("PR", value="PR", selected=(form_data.get('uf') == 'PR')),
                        Option("PE", value="PE", selected=(form_data.get('uf') == 'PE')),
                        Option("PI", value="PI", selected=(form_data.get('uf') == 'PI')),
                        Option("RJ", value="RJ", selected=(form_data.get('uf') == 'RJ')),
                        Option("RN", value="RN", selected=(form_data.get('uf') == 'RN')),
                        Option("RS", value="RS", selected=(form_data.get('uf') == 'RS')),
                        Option("RO", value="RO", selected=(form_data.get('uf') == 'RO')),
                        Option("RR", value="RR", selected=(form_data.get('uf') == 'RR')),
                        Option("SC", value="SC", selected=(form_data.get('uf') == 'SC')),
                        Option("SP", value="SP", selected=(form_data.get('uf') == 'SP')),
                        Option("SE", value="SE", selected=(form_data.get('uf') == 'SE')),
                        Option("TO", value="TO", selected=(form_data.get('uf') == 'TO')),
                        name="uf",
                        id="uf",
                        cls="form-select"
                    ),
                    error=errors.get('uf')
                ),
                width=2
            )
        ),
        Row(
            Col(
                form_group(
                    "Tipo de Usuário",
                    Select(
                        Option("Cliente", value="cliente", selected=(form_data.get('tipo_usuario') == 'cliente')),
                        Option("Administrador", value="admin", selected=(form_data.get('tipo_usuario') == 'admin')),
                        name="tipo_usuario",
                        cls="form-select",
                        required=True
                    ),
                    error=errors.get('tipo_usuario')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Senha",
                    Input(
                        type="password",
                        name="senha",
                        cls="form-control",
                        placeholder="Digite a senha",
                        required=True
                    ),
                    error=errors.get('senha')
                ),
                width=6
            )
        ),
        Div(
            Button("Salvar", type="submit", cls="btn btn-primary me-2"),
            A("Cancelar", href="/admin/usuarios", cls="btn btn-secondary"),
            cls="mt-3"
        ),
        method="post"
    )


def form_produto(form_data: Dict = None, errors: Dict = None):
    """Formulário de produto"""
    if form_data is None:
        form_data = {}
    if errors is None:
        errors = {}
    
    return Form(
        Row(
            Col(
                form_group(
                    "Código",
                    Input(
                        type="text",
                        name="codigo",
                        cls="form-control",
                        placeholder="PRD001",
                        value=form_data.get('codigo', ''),
                        required=True
                    ),
                    error=errors.get('codigo')
                ),
                width=4
            ),
            Col(
                form_group(
                    "Nome",
                    Input(
                        type="text",
                        name="nome",
                        cls="form-control",
                        placeholder="Nome do produto",
                        value=form_data.get('nome', ''),
                        required=True
                    ),
                    error=errors.get('nome')
                ),
                width=8
            )
        ),
        Row(
            Col(
                form_group(
                    "Descrição",
                    Textarea(
                        name="descricao",
                        cls="form-control",
                        placeholder="Descrição detalhada do produto",
                        rows="3",
                        value=form_data.get('descricao', '')
                    ),
                    error=errors.get('descricao')
                ),
                width=12
            )
        ),
        Row(
            Col(
                form_group(
                    "Categoria",
                    Input(
                        type="text",
                        name="categoria",
                        cls="form-control",
                        placeholder="Categoria do produto",
                        value=form_data.get('categoria', '')
                    ),
                    error=errors.get('categoria')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Preço",
                    Input(
                        type="number",
                        name="preco",
                        cls="form-control",
                        placeholder="0.00",
                        step="0.01",
                        value=form_data.get('preco', '')
                    ),
                    error=errors.get('preco')
                ),
                width=6
            )
        ),
        Div(
            Button("Salvar", type="submit", cls="btn btn-primary me-2"),
            A("Cancelar", href="/admin/produtos", cls="btn btn-secondary"),
            cls="mt-3"
        ),
        method="post"
    )


def form_servico(form_data: Dict = None, errors: Dict = None):
    """Formulário de serviço"""
    if form_data is None:
        form_data = {}
    if errors is None:
        errors = {}
    
    return Form(
        Row(
            Col(
                form_group(
                    "Código",
                    Input(
                        type="text",
                        name="codigo",
                        cls="form-control",
                        placeholder="SRV001",
                        value=form_data.get('codigo', ''),
                        required=True
                    ),
                    error=errors.get('codigo')
                ),
                width=4
            ),
            Col(
                form_group(
                    "Nome",
                    Input(
                        type="text",
                        name="nome",
                        cls="form-control",
                        placeholder="Nome do serviço",
                        value=form_data.get('nome', ''),
                        required=True
                    ),
                    error=errors.get('nome')
                ),
                width=8
            )
        ),
        Row(
            Col(
                form_group(
                    "Descrição",
                    Textarea(
                        name="descricao",
                        cls="form-control",
                        placeholder="Descrição detalhada do serviço",
                        rows="3",
                        value=form_data.get('descricao', '')
                    ),
                    error=errors.get('descricao')
                ),
                width=12
            )
        ),
        Row(
            Col(
                form_group(
                    "Categoria",
                    Input(
                        type="text",
                        name="categoria",
                        cls="form-control",
                        placeholder="Categoria do serviço",
                        value=form_data.get('categoria', '')
                    ),
                    error=errors.get('categoria')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Preço",
                    Input(
                        type="number",
                        name="preco",
                        cls="form-control",
                        placeholder="0.00",
                        step="0.01",
                        value=form_data.get('preco', '')
                    ),
                    error=errors.get('preco')
                ),
                width=6
            )
        ),
        Div(
            Button("Salvar", type="submit", cls="btn btn-primary me-2"),
            A("Cancelar", href="/admin/servicos", cls="btn btn-secondary"),
            cls="mt-3"
        ),
        method="post"
    )


def form_garantia(form_data: Dict = None, errors: Dict = None):
    """Formulário de garantia"""
    if form_data is None:
        form_data = {}
    if errors is None:
        errors = {}
    
    return Form(
        Row(
            Col(
                form_group(
                    "Cliente",
                    Select(
                        Option("Selecione um cliente...", value="", selected=(not form_data.get('cliente_id'))),
                        # As opções serão preenchidas dinamicamente
                        name="cliente_id",
                        cls="form-select",
                        required=True
                    ),
                    error=errors.get('cliente_id')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Produto/Serviço",
                    Select(
                        Option("Selecione um produto/serviço...", value="", selected=(not form_data.get('produto_id'))),
                        # As opções serão preenchidas dinamicamente
                        name="produto_id",
                        cls="form-select",
                        required=True
                    ),
                    error=errors.get('produto_id')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "Data de Compra",
                    Input(
                        type="date",
                        name="data_compra",
                        cls="form-control",
                        value=form_data.get('data_compra', ''),
                        required=True
                    ),
                    error=errors.get('data_compra')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Período de Garantia (meses)",
                    Input(
                        type="number",
                        name="periodo_garantia",
                        cls="form-control",
                        placeholder="12",
                        min="1",
                        value=form_data.get('periodo_garantia', ''),
                        required=True
                    ),
                    error=errors.get('periodo_garantia')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "Observações",
                    Textarea(
                        name="observacoes",
                        cls="form-control",
                        placeholder="Observações sobre a garantia",
                        rows="3",
                        value=form_data.get('observacoes', '')
                    ),
                    error=errors.get('observacoes')
                ),
                width=12
            )
        ),
        Div(
            Button("Salvar", type="submit", cls="btn btn-primary me-2"),
            A("Cancelar", href="/admin/garantias", cls="btn btn-secondary"),
            cls="mt-3"
        ),
        method="post"
    )