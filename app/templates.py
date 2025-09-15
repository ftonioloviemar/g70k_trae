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
                A("Minhas Garantias", href="/cliente/garantias"),
                A("Nova Garantia", href="/cliente/garantias/nova"),
                A("Regulamento", href="/regulamento"),
                A("Contato", href="/contato"),
                A("Sair", href="/logout", cls="text-red-500")
            ]
        
        user_info = Span(f"Olá, {user.get('nome', user.get('usuario_email', 'Usuário'))}", cls="text-sm text-gray-600")
    
    # Criar navbar usando MonsterUI
    navbar = None
    if show_nav and user:
        # Brand com logo
        brand = Div(
            Img(src="/static/viemar-logo-light.png", alt="Viemar", cls="h-8 w-auto mr-2"),
            Span("Viemar Garantia", cls="font-bold text-lg"),
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
                    cls="py-6"
                ),
                cls="min-h-screen"
            ),
            footer_component()
        )
    )


def footer_component():
    """Componente de rodapé usando MonsterUI"""
    return Footer(
        Container(
            P(
                "© 2024 Viemar - Garantia 70mil Km ou 2 anos. Todos os direitos reservados.",
                cls="text-center text-gray-600 text-sm"
            ),
            cls="text-center py-4"
        ),
        cls="bg-gray-50 border-t"
    )

def alert_component(message: str, alert_type: str = "info"):
    """Componente de alerta usando MonsterUI"""
    # Mapear tipos de alerta para classes Tailwind
    alert_classes = {
        "info": "bg-blue-50 border-blue-200 text-blue-800",
        "success": "bg-green-50 border-green-200 text-green-800",
        "warning": "bg-yellow-50 border-yellow-200 text-yellow-800",
        "danger": "bg-red-50 border-red-200 text-red-800",
        "error": "bg-red-50 border-red-200 text-red-800"
    }
    
    return Alert(
        message,
        cls=f"border rounded-lg p-4 {alert_classes.get(alert_type, alert_classes['info'])}"
    )

def card_component(title: str, content, actions=None):
    """Componente de card usando MonsterUI"""
    card_content = []
    
    if title:
        card_content.append(H3(title, cls="text-lg font-semibold mb-4"))
    
    card_content.append(content)
    
    if actions:
        card_content.append(
            Div(actions, cls="mt-4 flex gap-2")
        )
    
    return Card(
        *card_content,
        cls="p-6 mb-4"
    )

def form_group(label: str, input_field, help_text: str = None, required: bool = False, error: str = None):
    """Componente de grupo de formulário com destaque visual para erros"""
    label_text = label
    if required:
        label_text += " *"
    
    # Adicionar classe de erro ao campo se houver erro
    if error:
        # Tentar diferentes formas de adicionar a classe is-invalid
        if hasattr(input_field, 'attrs'):
            current_cls = input_field.attrs.get('cls', '')
            input_field.attrs['cls'] = f"{current_cls} is-invalid".strip()
        elif hasattr(input_field, 'cls'):
            current_cls = getattr(input_field, 'cls', '') or ''
            input_field.cls = f"{current_cls} is-invalid".strip()
        # Para elementos Select e outros tipos especiais
        elif hasattr(input_field, '__dict__'):
            if 'cls' in input_field.__dict__:
                current_cls = input_field.__dict__['cls'] or ''
                input_field.__dict__['cls'] = f"{current_cls} is-invalid".strip()
            else:
                input_field.__dict__['cls'] = "is-invalid"
    
    # Criar label com destaque visual se houver erro
    label_cls = "form-label"
    if error:
        label_cls += " text-danger fw-bold"
    
    components = [
        Label(label_text, cls=label_cls),
        input_field
    ]
    
    # Adicionar mensagem de erro se houver
    if error:
        components.append(
            Div(
                I(cls="fas fa-exclamation-triangle me-1"),
                error,
                cls="invalid-feedback d-block",
                style="font-weight: 500;"
            )
        )
    
    if help_text:
        components.append(
            Div(help_text, cls="form-text text-muted")
        )
    
    # Adicionar classe de erro ao container se houver erro
    container_cls = "mb-3"
    if error:
        container_cls += " has-validation"
    
    return Div(*components, cls=container_cls)

def login_form(error_message: str = None):
    """Formulário de login"""
    form_content = [
        form_group(
            "E-mail",
            Input(
                type="email",
                name="email",
                cls="form-control",
                placeholder="seu@email.com",
                required=True
            ),
            required=True
        ),
        form_group(
            "Senha",
            Input(
                type="password",
                name="senha",
                cls="form-control",
                placeholder="Sua senha",
                required=True
            ),
            required=True
        ),
        Div(
            Button(
                "Entrar",
                type="submit",
                cls="btn btn-primary w-100"
            ),
            cls="d-grid"
        ),
        Div(
            A("Esqueci minha senha", href="/esqueci-senha", cls="text-decoration-none"),
            " | ",
            A("Criar conta", href="/cadastro", cls="text-decoration-none"),
            cls="text-center mt-3"
        )
    ]
    
    if error_message:
        form_content.insert(0, alert_component(error_message, "danger"))
    
    return Form(
        *form_content,
        method="post",
        action="/login"
    )

def cadastro_form(errors: Dict[str, str] = None):
    """Formulário de cadastro de cliente"""
    errors = errors or {}
    
    return Form(
        Row(
            Col(
                form_group(
                    "Nome completo",
                    Input(
                        type="text",
                        name="nome",
                        cls="form-control",
                        placeholder="Seu nome completo",
                        required=True
                    ),
                    required=True,
                    error=errors.get('nome')
                ),
                width=12
            )
        ),
        Row(
            Col(
                form_group(
                    "E-mail",
                    Input(
                        type="email",
                        name="email",
                        cls="form-control",
                        placeholder="seu@email.com",
                        required=True
                    ),
                    required=True,
                    error=errors.get('email')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Confirme o e-mail",
                    Input(
                        type="email",
                        name="confirmar_email",
                        cls="form-control",
                        placeholder="seu@email.com",
                        required=True
                    ),
                    required=True,
                    error=errors.get('confirmar_email')
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
                        cls="form-control",
                        placeholder="00000-000",
                        maxlength="9"
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
                        cls="form-control",
                        placeholder="Rua, número"
                    ),
                    error=errors.get('endereco')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Bairro",
                    Input(
                        type="text",
                        name="bairro",
                        cls="form-control",
                        placeholder="Bairro"
                    ),
                    error=errors.get('bairro')
                ),
                width=3
            )
        ),
        Row(
            Col(
                form_group(
                    "Cidade",
                    Input(
                        type="text",
                        name="cidade",
                        cls="form-control",
                        placeholder="Cidade"
                    ),
                    error=errors.get('cidade')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Estado (UF)",
                    Select(
                        Option("Selecione...", value=""),
                        Option("AC", value="AC"),
                        Option("AL", value="AL"),
                        Option("AP", value="AP"),
                        Option("AM", value="AM"),
                        Option("BA", value="BA"),
                        Option("CE", value="CE"),
                        Option("DF", value="DF"),
                        Option("ES", value="ES"),
                        Option("GO", value="GO"),
                        Option("MA", value="MA"),
                        Option("MT", value="MT"),
                        Option("MS", value="MS"),
                        Option("MG", value="MG"),
                        Option("PA", value="PA"),
                        Option("PB", value="PB"),
                        Option("PR", value="PR"),
                        Option("PE", value="PE"),
                        Option("PI", value="PI"),
                        Option("RJ", value="RJ"),
                        Option("RN", value="RN"),
                        Option("RS", value="RS"),
                        Option("RO", value="RO"),
                        Option("RR", value="RR"),
                        Option("SC", value="SC"),
                        Option("SP", value="SP"),
                        Option("SE", value="SE"),
                        Option("TO", value="TO"),
                        name="uf",
                        cls="form-select"
                    ),
                    error=errors.get('uf')
                ),
                width=3
            ),
            Col(
                form_group(
                    "Telefone",
                    Input(
                        type="tel",
                        name="telefone",
                        cls="form-control",
                        placeholder="(00) 00000-0000"
                    ),
                    error=errors.get('telefone')
                ),
                width=3
            )
        ),
        Row(
            Col(
                form_group(
                    "CPF/CNPJ",
                    Input(
                        type="text",
                        name="cpf_cnpj",
                        cls="form-control",
                        placeholder="000.000.000-00"
                    ),
                    error=errors.get('cpf_cnpj')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Data de nascimento",
                    Input(
                        type="date",
                        name="data_nascimento",
                        cls="form-control"
                    ),
                    error=errors.get('data_nascimento')
                ),
                width=6
            )
        ),
        Row(
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
                    "Mínimo 6 caracteres",
                    required=True,
                    error=errors.get('senha')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Confirme a senha",
                    Input(
                        type="password",
                        name="confirmar_senha",
                        cls="form-control",
                        placeholder="Confirme sua senha",
                        required=True
                    ),
                    required=True,
                    error=errors.get('confirmar_senha')
                ),
                width=6
            )
        ),
        Div(
            Button(
                "Criar conta",
                type="submit",
                cls="btn btn-primary btn-lg"
            ),
            A(
                "Já tenho conta",
                href="/login",
                cls="btn btn-link"
            ),
            cls="d-flex justify-content-between align-items-center mt-4"
        ),
        method="post",
        action="/cadastro"
    )

def veiculo_form(veiculo: Dict[str, Any] = None, is_edit: bool = False, errors: Dict[str, str] = None, veiculo_id: str = None):
    """Formulário de cadastro/edição de veículo"""
    veiculo = veiculo or {}
    errors = errors or {}
    
    # Definir action baseado no contexto
    if is_edit and veiculo_id:
        action = f"/cliente/veiculos/{veiculo_id}"
    else:
        action = "/cliente/veiculos"
    
    return Form(
        Row(
            Col(
                form_group(
                    "Marca",
                    Input(
                        type="text",
                        name="marca",
                        cls="form-control",
                        placeholder="Ex: Volkswagen",
                        value=veiculo.get('marca', ''),
                        required=True
                    ),
                    required=True,
                    error=errors.get('marca')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Modelo",
                    Input(
                        type="text",
                        name="modelo",
                        cls="form-control",
                        placeholder="Ex: Gol",
                        value=veiculo.get('modelo', ''),
                        required=True
                    ),
                    required=True,
                    error=errors.get('modelo')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "Ano/Modelo",
                    Input(
                        type="text",
                        name="ano_modelo",
                        cls="form-control",
                        placeholder="Ex: 2020/2021",
                        value=veiculo.get('ano_modelo', ''),
                        required=True
                    ),
                    required=True,
                    error=errors.get('ano_modelo')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Placa",
                    Input(
                        type="text",
                        name="placa",
                        cls="form-control",
                        placeholder="ABC-1234 ou ABC1D23",
                        value=veiculo.get('placa', ''),
                        required=True,
                        maxlength="8"
                    ),
                    "Formato antigo (ABC-1234) ou Mercosul (ABC1D23)",
                    required=True,
                    error=errors.get('placa')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "Cor",
                    Input(
                        type="text",
                        name="cor",
                        cls="form-control",
                        placeholder="Ex: Branco",
                        value=veiculo.get('cor', '')
                    ),
                    error=errors.get('cor')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Chassi",
                    Input(
                        type="text",
                        name="chassi",
                        cls="form-control",
                        placeholder="Ex: 9BWZZZ377VT004251",
                        value=veiculo.get('chassi', ''),
                        maxlength="17"
                    ),
                    "Opcional - 17 caracteres",
                    error=errors.get('chassi')
                ),
                width=6
            )
        ),
        Div(
            Button(
                "Atualizar veículo" if is_edit else "Salvar veículo",
                type="submit",
                cls="btn btn-primary"
            ),
            A(
                "Cancelar",
                href="/cliente/veiculos",
                cls="btn btn-secondary ms-2"
            ),
            cls="mt-3"
        ),
        method="post",
        action=action
    )

def garantia_form(produtos: List[Dict], veiculos: List[Dict], garantia: Dict[str, Any] = None, errors: Dict[str, str] = None):
    """Formulário de ativação de garantia"""
    garantia = garantia or {}
    errors = errors or {}
    
    # Opções de produto com valor selecionado preservado
    produto_options = [Option("Selecione um produto...", value="")]
    produto_selecionado = garantia.get('produto_id', '')
    for produto in produtos:
        is_selected = str(produto['id']) == str(produto_selecionado)
        produto_options.append(
            Option(
                f"{produto['sku']} - {produto['descricao']}", 
                value=produto['id'],
                selected=is_selected
            )
        )
    
    # Opções de veículo com valor selecionado preservado
    veiculo_options = [Option("Selecione um veículo...", value="")]
    veiculo_selecionado = garantia.get('veiculo_id', '')
    for veiculo in veiculos:
        is_selected = str(veiculo['id']) == str(veiculo_selecionado)
        veiculo_options.append(
            Option(
                f"{veiculo['marca']} {veiculo['modelo']} - {veiculo['placa']}", 
                value=veiculo['id'],
                selected=is_selected
            )
        )
    
    return Form(
        Row(
            Col(
                form_group(
                    "Produto",
                    Select(
                        *produto_options,
                        name="produto_id",
                        cls="form-select",
                        required=True
                    ),
                    required=True,
                    error=errors.get('produto_id')
                ),
                width=12
            )
        ),
        Row(
            Col(
                form_group(
                    "Lote de fabricação",
                    Input(
                        type="text",
                        name="lote_fabricacao",
                        cls="form-control",
                        placeholder="Mínimo 5 caracteres",
                        value=garantia.get('lote_fabricacao', ''),
                        required=True,
                        minlength="5"
                    ),
                    "Código do lote de fabricação (mínimo 5 caracteres)",
                    required=True,
                    error=errors.get('lote_fabricacao')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Data de instalação",
                    Input(
                        type="date",
                        name="data_instalacao",
                        cls="form-control",
                        value=garantia.get('data_instalacao', ''),
                        required=True
                    ),
                    required=True,
                    error=errors.get('data_instalacao')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "Nota fiscal",
                    Input(
                        type="text",
                        name="nota_fiscal",
                        cls="form-control",
                        placeholder="Número da nota fiscal",
                        value=garantia.get('nota_fiscal', ''),
                        required=True
                    ),
                    required=True,
                    error=errors.get('nota_fiscal')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Nome do estabelecimento",
                    Input(
                        type="text",
                        name="nome_estabelecimento",
                        cls="form-control",
                        placeholder="Local da instalação",
                        value=garantia.get('nome_estabelecimento', ''),
                        required=True
                    ),
                    required=True,
                    error=errors.get('nome_estabelecimento')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "Quilometragem",
                    Input(
                        type="number",
                        name="quilometragem",
                        cls="form-control",
                        placeholder="Km atual do veículo",
                        value=garantia.get('quilometragem', ''),
                        required=True,
                        min="0"
                    ),
                    required=True,
                    error=errors.get('quilometragem')
                ),
                width=6
            ),
            Col(
                form_group(
                    "Veículo",
                    Select(
                        *veiculo_options,
                        name="veiculo_id",
                        cls="form-select",
                        required=True
                    ),
                    required=True,
                    error=errors.get('veiculo_id')
                ),
                width=6
            )
        ),
        Row(
            Col(
                form_group(
                    "Observações",
                    Textarea(
                        garantia.get('observacoes', ''),
                        name="observacoes",
                        cls="form-control",
                        rows="3",
                        placeholder="Observações adicionais (opcional)"
                    ),
                    error=errors.get('observacoes')
                ),
                width=12
            )
        ),
        Div(
            Button(
                "Ativar garantia",
                type="submit",
                cls="btn btn-success btn-lg"
            ),
            A(
                "Cancelar",
                href="/cliente/garantias",
                cls="btn btn-secondary ms-2"
            ),
            cls="mt-3"
        ),
        method="post"
    )

def table_component(headers: List[str], rows: List[List], actions: List[str] = None):
    """Componente de tabela responsiva"""
    
    header_cells = [Th(header) for header in headers]
    if actions:
        header_cells.append(Th("Ações"))
    
    table_rows = []
    for row in rows:
        cells = [Td(str(cell)) for cell in row]
        if actions:
            action_buttons = []
            for action in actions:
                if action == "editar":
                    action_buttons.append(
                        A("Editar", href="#", cls="btn btn-sm btn-outline-primary me-1")
                    )
                elif action == "excluir":
                    action_buttons.append(
                        A("Excluir", href="#", cls="btn btn-sm btn-outline-danger")
                    )
            cells.append(Td(*action_buttons))
        table_rows.append(Tr(*cells))
    
    # Envolver a tabela em um container responsivo
    return Div(
        Table(
            Thead(Tr(*header_cells)),
            Tbody(*table_rows),
            cls="table table-striped table-hover mb-0"
        ),
        cls="table-responsive"
    )

def produto_form(produto: Dict[str, Any] = None, is_edit: bool = False, errors: Dict[str, str] = None, action: str = None):
    """Formulário de cadastro/edição de produto"""
    produto = produto or {}
    errors = errors or {}
    
    form_content = [
        form_group(
            "SKU",
            Input(
                type="text",
                name="sku",
                cls="form-control",
                placeholder="Ex: VIE001",
                value=produto.get('sku', ''),
                required=True
            ),
            "Código único do produto (mínimo 3 caracteres)",
            required=True,
            error=errors.get('sku')
        ),
        form_group(
            "Descrição",
            Textarea(
                produto.get('descricao', ''),
                name="descricao",
                cls="form-control",
                rows="3",
                placeholder="Descrição detalhada do produto",
                required=True
            ),
            "Descrição completa do produto",
            required=True,
            error=errors.get('descricao')
        )
    ]
    
    # Adicionar checkbox de ativo apenas na edição
    if is_edit:
        form_content.append(
            Div(
                Div(
                    Input(
                        type="checkbox",
                        name="ativo",
                        id="ativo",
                        cls="form-check-input",
                        checked=produto.get('ativo', True)
                    ),
                    Label("Produto ativo", for_="ativo", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            )
        )
    
    # Botões de ação
    form_content.append(
        Div(
            Button(
                "Salvar Alterações" if is_edit else "Cadastrar Produto",
                type="submit",
                cls="btn btn-success" if not is_edit else "btn btn-primary"
            ),
            A(
                "Cancelar",
                href="/admin/produtos",
                cls="btn btn-secondary ms-2"
            ),
            cls="d-flex gap-2"
        )
    )
    
    form_attrs = {"method": "post"}
    if action:
        form_attrs["action"] = action

def regulamento_page(user: Optional[Dict[str, Any]] = None):
    """Página de Regulamento da Garantia 70mil Km"""
    content = Container(
        Row(
            Col(
                Card(
                    CardHeader(
                        H1("Garantia Viemar 70 mil Km ou 2 anos", cls="h3 mb-0 text-primary")
                    ),
                    CardBody(
                        Div(
                            P("A Viemar oferece ao mercado de reposição uma garantia de até 70 mil Km ou 2 anos para articulações axiais, terminais de direção, pivôs de suspensão e pinças de freios.", cls="lead mb-4"),
                            
                            Alert(
                                Strong("Importante: "),
                                "Para ter direito à Garantia 70 mil Km ou 2 anos, o consumidor é obrigado a preencher o Termo de Garantia Contratual, disponível no website da Viemar, obedecendo ao prazo de até 30 (trinta) dias após a emissão da Nota Fiscal e/ou do Cupom Fiscal.",
                                cls="alert-warning"
                            ),
                            
                            H3("Perguntas Frequentes", cls="mt-5 mb-4 text-primary"),
                            
                            Div(
                                Div(
                                    H5("A garantia 70 mil Km ou 2 anos vale para todos os produtos fabricados pela Viemar?", cls="text-dark mb-2"),
                                    P("Não. É válida para articulações axiais, terminais de direção, pivôs de suspensão e pinças de freios.", cls="text-muted mb-4")
                                ),
                                
                                Div(
                                    H5("Qual é o prazo que eu tenho para me inscrever para ter direito à garantia 70 mil Km ou 2 anos?", cls="text-dark mb-2"),
                                    P("O consumidor tem o prazo de até 30 dias a partir da emissão da nota ou do cupom fiscal para se cadastrar no site e ter o direito a solicitar a garantia.", cls="text-muted mb-4")
                                ),
                                
                                Div(
                                    H5("O que é preciso fazer para se cadastrar no site?", cls="text-dark mb-2"),
                                    P("Basta criar uma conta de usuário, cadastrar pelo menos um veículo e, por fim, cadastrar as suas peças para ativar a garantia.", cls="text-muted mb-4")
                                ),
                                
                                Div(
                                    H5("Que documentos precisa?", cls="text-dark mb-2"),
                                    P("Você precisa ter em mãos a nota ou cupom fiscal, seus dados de identificação, do veículo e os dados da peça (referência/código do produto e lote).", cls="text-muted mb-4")
                                ),
                                
                                Div(
                                    H5("A garantia 70 mil Km ou 2 anos vale para os produtos fabricados a partir de quando?", cls="text-dark mb-2"),
                                    P("A garantia 70 mil Km ou 2 anos vale para articulações axiais, terminais de direção, pivôs de suspensão e pinças de freios fabricados a partir de janeiro de 2015.", cls="text-muted mb-4")
                                ),
                                
                                Div(
                                    H5("Como eu sei que a peça foi fabricada a partir de janeiro de 2015?", cls="text-dark mb-2"),
                                    P("As peças Viemar são identificadas por lote de fabricação e os dois últimos números do lote referem-se ao ano da fabricação. Se os dois últimos números forem 15, 16, 17, 18 e assim por diante, significa que estão cobertas pela garantia 70 mil Km ou dois anos.", cls="text-muted mb-4")
                                ),
                                
                                Div(
                                    H5("Como eu sei que o meu cadastro deu certo?", cls="text-dark mb-2"),
                                    P("Ao se cadastrar, você cria login e senha e o sistema envia um e-mail de confirmação para o endereço eletrônico informado.", cls="text-muted mb-4")
                                ),
                                
                                Div(
                                    H5("Posso cadastrar mais de uma peça por vez? E mais de um veículo?", cls="text-dark mb-2"),
                                    P("Sim. No seu login (perfil), você pode cadastrar quantas peças e veículos forem precisos.", cls="text-muted mb-4")
                                ),
                                
                                Div(
                                    H5("Como eu faço para requerer a garantia 70 mil Km ou 2 anos?", cls="text-dark mb-2"),
                                    P("A solicitação de garantia 70 mil Km ou 2 anos obedece aos mesmos padrões da garantia legal. Basta entrar em contato com a Viemar, através do Serviço de Atendimento ao Cliente (SAC) ou encaminhar junto ao seu distribuidor.", cls="text-muted mb-4")
                                ),
                                
                                cls="mb-5"
                            ),
                            
                            Alert(
                                Strong("Atenção: "),
                                "Se você não se cadastrar no site, mas mesmo assim tiver a Nota Fiscal do produto, não poderá solicitar a garantia 70 mil Km ou 2 anos depois de passado o prazo legal de 90 dias. A garantia 70 mil Km ou 2 anos é só para quem fez o registro no site.",
                                cls="alert-danger"
                            ),
                            
                            Div(
                                A(
                                    "Cadastrar Garantia",
                                    href="/cliente/garantias/nova" if user else "/cadastro",
                                    cls="btn btn-primary btn-lg me-3"
                                ),
                                A(
                                    "Entrar em Contato",
                                    href="/contato",
                                    cls="btn btn-outline-primary btn-lg"
                                ),
                                cls="text-center mt-5"
                            )
                        )
                    )
                ),
                width=10,
                offset=1
            )
        )
    )
    
    return base_layout("Regulamento da Garantia", content, user)

def contato_page(user: Optional[Dict[str, Any]] = None):
    """Página de Contato da Viemar"""
    content = Container(
        Row(
            Col(
                Card(
                    CardHeader(
                        H1("Entre em Contato", cls="h3 mb-0 text-primary")
                    ),
                    CardBody(
                        Div(
                            P("Entre em contato conosco para esclarecer dúvidas sobre a Garantia 70mil Km ou 2 anos da Viemar.", cls="lead mb-5"),
                            
                            Row(
                                Col(
                                    Card(
                                        CardBody(
                                            Div(
                                                I(cls="fas fa-phone fa-2x text-primary mb-3"),
                                                H4("Telefone", cls="h5 mb-2"),
                                                P("SAC: 0800 608 0188", cls="mb-1"),
                                P("Horário: Segunda a Sexta, 8h às 17h", cls="text-muted small")
                                            ),
                                            cls="text-center"
                                        )
                                    ),
                                    width=6,
                                    cls="mb-4"
                                ),
                                Col(
                                    Card(
                                        CardBody(
                                            Div(
                                                I(cls="fas fa-envelope fa-2x text-primary mb-3"),
                                                H4("E-mail", cls="h5 mb-2"),
                                                P("sac@viemar.com", cls="mb-1"),
                                                P("Resposta em até 24 horas", cls="text-muted small")
                                            ),
                                            cls="text-center"
                                        )
                                    ),
                                    width=6,
                                    cls="mb-4"
                                )
                            ),
                            
                            Row(
                                Col(
                                    Card(
                                        CardBody(
                                            Div(
                                                I(cls="fas fa-map-marker-alt fa-2x text-primary mb-3"),
                                                H4("Endereço", cls="h5 mb-2"),
                                                P("Viemar Automotive", cls="mb-1"),
                                P("Rodovia RS-118, 9393, Km 30", cls="mb-1"),
                                P("Viamão/RS", cls="mb-1"),
                                P("CEP: 94420-400", cls="text-muted small")
                                            ),
                                            cls="text-center"
                                        )
                                    ),
                                    width=6,
                                    cls="mb-4"
                                ),
                                Col(
                                    Card(
                                        CardBody(
                                            Div(
                                                I(cls="fas fa-clock fa-2x text-primary mb-3"),
                                                H4("Horário de Funcionamento", cls="h5 mb-2"),
                                                P("Segunda a Sexta: 8h às 17h", cls="mb-1"),
                                P("Sábado e Domingo: Fechado", cls="text-muted small")
                                            ),
                                            cls="text-center"
                                        )
                                    ),
                                    width=6,
                                    cls="mb-4"
                                )
                            ),
                            
                            Alert(
                Strong("Redes Sociais: "),
                "Siga a Viemar nas redes sociais para ficar por dentro das novidades e promoções.",
                cls="alert-info mt-4"
            ),
            
            Row(
                Col(
                    Div(
                        A(
                            I(cls="fab fa-instagram fa-2x text-primary me-2"),
                            "Instagram",
                            href="https://www.instagram.com/viemarautomotive/",
                            target="_blank",
                            cls="btn btn-outline-primary me-3 mb-2"
                        ),
                        A(
                            I(cls="fab fa-facebook fa-2x text-primary me-2"),
                            "Facebook",
                            href="https://www.facebook.com/Viemarautomotive/?locale=pt_BR",
                            target="_blank",
                            cls="btn btn-outline-primary me-3 mb-2"
                        ),
                        A(
                            I(cls="fab fa-youtube fa-2x text-primary me-2"),
                            "YouTube",
                            href="https://www.youtube.com/@ViemarAutomotive",
                            target="_blank",
                            cls="btn btn-outline-primary mb-2"
                        ),
                        cls="text-center"
                    ),
                    width=12
                )
            ),
                            
                            Div(
                                A(
                                    I(cls="fab fa-facebook fa-2x me-3"),
                                    href="#",
                                    cls="text-primary"
                                ),
                                A(
                                    I(cls="fab fa-instagram fa-2x me-3"),
                                    href="#",
                                    cls="text-primary"
                                ),
                                A(
                                    I(cls="fab fa-linkedin fa-2x"),
                                    href="#",
                                    cls="text-primary"
                                ),
                                cls="text-center mt-4 mb-4"
                            ),
                            
                            Div(
                                A(
                                    "Ver Regulamento",
                                    href="/regulamento",
                                    cls="btn btn-outline-primary btn-lg me-3"
                                ),
                                A(
                                    "Cadastrar Garantia",
                                    href="/cliente/garantias/nova" if user else "/cadastro",
                                    cls="btn btn-primary btn-lg"
                                ),
                                cls="text-center mt-5"
                            )
                        )
                    )
                ),
                width=10,
                offset=1
            )
        )
    )
    
    return base_layout("Contato", content, user)
    
    return Form(
        *form_content,
        **form_attrs
    )