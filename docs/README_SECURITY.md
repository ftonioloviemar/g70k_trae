# Guia de Segurança - Sistema Viemar Garantia 70k

## ⚠️ IMPORTANTE - ANTES DE PUBLICAR EM PRODUÇÃO

### 1. Variáveis de Ambiente Obrigatórias

Antes de executar o sistema em produção, você DEVE configurar as seguintes variáveis de ambiente:

```bash
# Configurações de Segurança (OBRIGATÓRIAS)
export SECRET_KEY="sua-chave-secreta-super-forte-aqui-min-32-chars"
export ADMIN_EMAIL="seu-admin@viemar.com.br"
export ADMIN_PASSWORD="sua-senha-super-segura-aqui"

# Configurações de Email (se usar funcionalidade de email)
export SMTP_USERNAME="seu-email@domain.com"
export SMTP_PASSWORD="sua-senha-de-app-aqui"

# Configurações Opcionais
export DEBUG="False"
export HOST="0.0.0.0"
export PORT="8000"
```

### 2. Geração de SECRET_KEY Segura

Para gerar uma SECRET_KEY segura, use:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Ou no terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Checklist de Segurança

- [ ] ✅ SECRET_KEY definida como variável de ambiente (não hardcoded)
- [ ] ✅ ADMIN_EMAIL e ADMIN_PASSWORD definidos como variáveis de ambiente
- [ ] ✅ DEBUG=False em produção
- [ ] ✅ Senhas de email usando App Passwords (não senha principal)
- [ ] ✅ Banco de dados com permissões adequadas
- [ ] ✅ Logs não contêm informações sensíveis
- [ ] ✅ HTTPS configurado (recomendado)
- [ ] ✅ Firewall configurado adequadamente

### 4. Arquivos que NÃO devem ir para o repositório público

- `.env` (já está no .gitignore)
- `data/viemar_garantia.db*` (dados reais)
- `logs/*` (podem conter informações sensíveis)
- Qualquer arquivo com credenciais reais

### 5. Configuração para Desenvolvimento

Para desenvolvimento local, copie `.env.example` para `.env` e configure:

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações de desenvolvimento
```

### 6. Configuração para Produção

**NUNCA** use as credenciais de exemplo em produção. Sempre:

1. Use variáveis de ambiente do sistema
2. Use senhas fortes e únicas
3. Configure HTTPS
4. Monitore logs de segurança
5. Mantenha o sistema atualizado

### 7. Contato de Segurança

Em caso de problemas de segurança, entre em contato com a equipe de TI da Viemar.

---

**⚠️ LEMBRE-SE: Este sistema gerencia dados sensíveis de garantias de veículos. A segurança é fundamental!**