# Estrutura do Projeto Viemar Garantia

Este documento descreve a organização e estrutura do projeto seguindo as melhores práticas de desenvolvimento Python.

## 📁 Estrutura de Diretórios

```
g70k_trae/
├── 📁 app/                    # Código principal da aplicação
│   ├── auth.py               # Sistema de autenticação
│   ├── config.py             # Configurações da aplicação
│   ├── database.py           # Conexão e operações de banco
│   ├── email_service.py      # Serviço de envio de emails
│   ├── logger.py             # Sistema de logging
│   ├── routes*.py            # Rotas da aplicação
│   └── templates.py          # Templates FastHTML
│
├── 📁 models/                 # Modelos de dados
│   ├── garantia.py           # Modelo de garantias
│   ├── produto.py            # Modelo de produtos
│   ├── usuario.py            # Modelo de usuários
│   └── veiculo.py            # Modelo de veículos
│
├── 📁 tests/                  # Testes automatizados
│   ├── conftest.py           # Configurações do pytest
│   ├── test_database.py      # Testes de banco de dados
│   ├── test_e2e_garantias.py # Testes end-to-end
│   ├── test_models.py        # Testes de modelos
│   └── test_routes.py        # Testes de rotas
│
├── 📁 config/                 # Arquivos de configuração
│   └── playwright.config.py  # Configuração do Playwright
│
├── 📁 scripts/                # Scripts organizados por categoria
│   ├── 📁 dev/               # Scripts de desenvolvimento
│   ├── 📁 deploy/            # Scripts de deploy
│   ├── 📁 utils/             # Scripts utilitários
│   │   └── maintenance.py    # Manutenção do banco
│   └── README.md             # Documentação dos scripts
│
├── 📁 docs/                   # Documentação do projeto
│   ├── 📁 context/           # Contexto e especificações
│   └── ESTRUTURA_PROJETO.md  # Este arquivo
│
├── 📁 data/                   # Arquivos de banco de dados
│   ├── README.md             # Documentação dos dados
│   ├── g70k.db               # Banco principal
│   ├── viemar.db             # Banco Viemar
│   └── viemar_garantia.db*   # Banco de garantias
│
├── 📁 static/                 # Arquivos estáticos (CSS, JS, imagens)
│   └── style.css             # Estilos da aplicação
│
├── 📁 templates/              # Templates HTML (se necessário)
│
├── 📁 uploads/                # Arquivos enviados pelos usuários
│   └── .gitkeep              # Mantém pasta no repositório
│
├── 📁 logs/                   # Logs da aplicação
│   └── *.log                 # Arquivos de log rotativos
│
├── 📁 build/                  # Artefatos de build (ignorado no git)
│
├── main.py                    # Ponto de entrada da aplicação
├── pyproject.toml             # Configuração do projeto e dependências
├── uv.lock                    # Lock file do uv
├── .gitignore                 # Arquivos ignorados pelo git
└── README.md                  # Documentação principal
```

## 🎯 Benefícios da Organização

### 1. **Separação de Responsabilidades**
- Código da aplicação em `app/`
- Modelos de dados em `models/`
- Testes organizados em `tests/`
- Configurações centralizadas em `config/`

### 2. **Facilidade de Manutenção**
- Scripts organizados por categoria em `scripts/`
- Documentação centralizada em `docs/`
- Logs e dados em pastas específicas

### 3. **Segurança**
- Dados sensíveis em `data/` (pode ser ignorado em produção)
- Uploads isolados em `uploads/`
- Configurações de ambiente separadas

### 4. **Desenvolvimento**
- Configurações de teste no `pyproject.toml`
- Scripts de desenvolvimento organizados
- Estrutura compatível com ferramentas modernas (uv, pytest, etc.)

## 🔧 Ferramentas e Configurações

### Gerenciamento de Dependências
- **uv**: Gerenciador de pacotes e ambientes virtuais
- **pyproject.toml**: Configuração centralizada do projeto

### Testes
- **pytest**: Framework de testes
- **pytest-cov**: Cobertura de código
- **playwright**: Testes end-to-end

### Qualidade de Código
- **Type hints**: Tipagem estática
- **Docstrings**: Documentação de código
- **Logging**: Sistema de logs rotativos

## 📝 Convenções

1. **Nomes de arquivos**: snake_case
2. **Nomes de classes**: PascalCase
3. **Nomes de funções**: snake_case
4. **Constantes**: UPPER_CASE
5. **Documentação**: Português brasileiro
6. **Commits**: Mensagens descritivas em português

## 🚀 Como Executar

```bash
# Ativar ambiente virtual
uv venv

# Instalar dependências
uv sync

# Executar aplicação
uv run main.py

# Executar testes
uv run pytest

# Executar testes com cobertura
uv run pytest --cov
```

## 📚 Próximos Passos

1. Implementar CI/CD
2. Adicionar mais testes de integração
3. Configurar ambiente de produção
4. Implementar monitoramento
5. Adicionar documentação da API