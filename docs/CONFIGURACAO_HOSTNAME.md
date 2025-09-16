# Configuração do Hostname

Este documento explica como configurar o hostname da aplicação para diferentes ambientes.

## Variável de Ambiente HOSTNAME

A aplicação utiliza a variável de ambiente `HOSTNAME` para definir o domínio usado nos emails e URLs geradas pelo sistema.

### Configuração por Ambiente

#### Desenvolvimento Local
```bash
HOSTNAME=localhost:8000
```

#### Produção
```bash
HOSTNAME=garantia70mil.viemar.com.br
```

#### Staging/Homologação
```bash
HOSTNAME=staging.garantia70mil.viemar.com.br
```

## Como Configurar

### 1. Arquivo .env
Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e defina o HOSTNAME apropriado:

```bash
# Para desenvolvimento
HOSTNAME=localhost:8000

# Para produção
HOSTNAME=garantia70mil.viemar.com.br
```

### 2. Variável de Ambiente do Sistema
Alternativamente, você pode definir a variável diretamente no sistema:

#### Windows
```cmd
set HOSTNAME=garantia70mil.viemar.com.br
```

#### Linux/macOS
```bash
export HOSTNAME=garantia70mil.viemar.com.br
```

## Onde é Utilizado

O hostname configurado é usado nos seguintes locais:

1. **Emails de confirmação de cadastro**: Links para confirmar email
2. **Emails de ativação de garantia**: Links para consultar garantias
3. **Emails de redefinição de senha**: Links para redefinir senha
4. **URLs geradas pelo sistema**: Todas as URLs absolutas

## Exemplo de Email

Com `HOSTNAME=garantia70mil.viemar.com.br`, os emails conterão:

```
Para consultar suas garantias, acesse: http://garantia70mil.viemar.com.br/garantias
```

Com `HOSTNAME=localhost:8000` (desenvolvimento), os emails conterão:

```
Para consultar suas garantias, acesse: http://localhost:8000/garantias
```

## Importante

- **Não inclua** `http://` ou `https://` na variável HOSTNAME
- **Inclua a porta** apenas em desenvolvimento (ex: `localhost:8000`)
- **Em produção**, use apenas o domínio (ex: `garantia70mil.viemar.com.br`)
- A aplicação automaticamente adiciona `http://` nas URLs geradas

## Verificação

Para verificar se a configuração está correta, você pode:

1. Cadastrar um novo usuário e verificar o email de confirmação
2. Ativar uma garantia e verificar o email de ativação
3. Verificar os logs da aplicação para confirmar as URLs geradas