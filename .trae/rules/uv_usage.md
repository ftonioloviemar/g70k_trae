# Regras de Uso do UV

## Comando UV - Regra Obrigatória

**SEMPRE** execute comandos usando:
- `uv run xxx.py` 
- `uv run pytest xxx`

**NUNCA** use:
- `uv run python xxx`

### Exemplos Corretos:
```bash
# Executar arquivo Python
uv run main.py
uv run debug_auth.py

# Executar testes
uv run pytest tests/
uv run pytest tests/test_database.py -v
```

### Exemplos Incorretos:
```bash
# NÃO USAR
uv run python main.py
uv run python -c "print('test')"
```

### Justificativa:
Esta regra garante consistência no uso do UV e evita problemas de execução no ambiente virtual.