# Scripts do Projeto

Esta pasta contém scripts organizados por categoria para facilitar a manutenção e desenvolvimento do projeto.

## Estrutura

### 📁 dev/
Scripts para desenvolvimento e debugging:
- Scripts de desenvolvimento local
- Ferramentas de debugging
- Scripts de setup do ambiente de desenvolvimento

### 📁 deploy/
Scripts para deploy e produção:
- Scripts de build
- Scripts de deploy
- Scripts de configuração de produção
- Scripts de migração

### 📁 utils/
Scripts utilitários e de manutenção:
- `maintenance.py` - Script de manutenção do banco de dados
- Scripts de backup
- Scripts de limpeza
- Ferramentas auxiliares

## Como usar

Todos os scripts devem ser executados a partir da raiz do projeto:

```bash
# Exemplo de execução
uv run scripts/utils/maintenance.py
```

## Convenções

- Use nomes descritivos para os scripts
- Adicione docstrings e comentários
- Inclua tratamento de erros adequado
- Use type hints
- Teste os scripts antes de commitar