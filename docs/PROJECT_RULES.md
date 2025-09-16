# Regras do Projeto

## Estrutura de Arquivos

### ❌ PROIBIDO: Criar novos arquivos na raiz

**REGRA IMPORTANTE**: Nunca criar novos arquivos na raiz do projeto sem aprovação explícita do desenvolvedor principal.

### ✅ Estrutura de pastas aprovada:

- `/app/` - Código principal da aplicação
- `/config/` - Arquivos de configuração
- `/data/` - Bancos de dados e arquivos de dados
- `/docs/` - Documentação do projeto
- `/models/` - Modelos de dados
- `/scripts/` - Scripts utilitários
- `/static/` - Arquivos estáticos (CSS, JS, imagens)
- `/templates/` - Templates HTML
- `/tests/` - Todos os arquivos de teste
- `/uploads/` - Arquivos enviados pelos usuários

### Arquivos permitidos na raiz:

- `main.py` - Arquivo principal da aplicação
- `pyproject.toml` - Configuração do projeto Python
- `uv.lock` - Lock file do uv
- `README.md` - Documentação principal
- `.env.example` - Exemplo de variáveis de ambiente
- `.gitignore` - Arquivos ignorados pelo Git
- `.python-version` - Versão do Python
- `viemar_garantia.db` - Banco de dados principal (temporário)

### Antes de criar qualquer arquivo na raiz:

1. ❓ Pergunte: "Este arquivo realmente precisa estar na raiz?"
2. 🤔 Considere: "Existe uma pasta mais apropriada?"
3. ✋ **PARE**: Solicite aprovação explícita antes de criar

### Exemplos de arquivos que NÃO devem ficar na raiz:

- ❌ Arquivos de teste (`test_*.py`)
- ❌ Scripts de debug (`debug_*.py`)
- ❌ Documentação específica (`*.md` exceto README.md)
- ❌ Arquivos de configuração específicos
- ❌ Bancos de dados adicionais
- ❌ Arquivos temporários

---

**Esta regra existe para manter o projeto organizado e facilitar a manutenção.**