# Testes da API Brasil

Este diretório contém scripts de teste para o pacote `api-brasil`, que permite integração com diversos serviços da [API Brasil](https://apibrasil.com.br).

## Arquivos de Teste

### 1. `teste_apibrasil_placa.py`
Teste específico para consulta de dados de veículos por placa.

**Funcionalidades:**
- Consulta dados de veículos pela placa
- Tratamento de erros e respostas
- Formatação clara dos resultados

### 2. `teste_apibrasil_completo.py`
Teste completo com múltiplas APIs disponíveis.

**Funcionalidades:**
- API de Veículos (consulta por placa)
- API de CNPJ (consulta de empresas)
- API de CPF (validação de CPF)
- API de CEP (geolocalização)

## Como Usar

### 1. Instalação
```bash
# Instalar o pacote api-brasil
uv add api-brasil
```

### 2. Configuração
1. Acesse [https://apibrasil.com.br](https://apibrasil.com.br)
2. Crie uma conta gratuita
3. Acesse a área de **Credenciais**
4. Copie seu `bearer_token` e `device_token`

### 3. Configurar os Tokens
Edite os arquivos de teste e substitua:
```python
bearrer_token = "your_bearer_token_here"  # Seu token real aqui
device_token = "your_device_token_here"   # Seu device token aqui
```

### 4. Executar os Testes

**Teste de Veículos:**
```bash
uv run tests/teste_apibrasil_placa.py
```

**Teste Completo:**
```bash
uv run tests/teste_apibrasil_completo.py
```

## APIs Disponíveis

### 🚗 API de Veículos
- **Endpoint:** Consulta dados de veículos
- **Parâmetro:** Placa do veículo (formato: ABC-1234)
- **Retorna:** Dados do veículo, FIPE, etc.

### 🏢 API de CNPJ
- **Endpoint:** Consulta dados de empresas
- **Parâmetro:** CNPJ (formato: 11.222.333/0001-81)
- **Retorna:** Razão social, endereço, situação, etc.

### 👤 API de CPF
- **Endpoint:** Validação de CPF
- **Parâmetro:** CPF (formato: 123.456.789-09)
- **Retorna:** Status de validade do CPF

### 📍 API de CEP
- **Endpoint:** Geolocalização por CEP
- **Parâmetro:** CEP (formato: 01310-100)
- **Retorna:** Endereço completo, coordenadas, etc.

## Códigos de Resposta

- **200:** Sucesso - Dados retornados corretamente
- **401:** Não autorizado - Token inválido ou expirado
- **402:** Pagamento necessário - Créditos insuficientes
- **404:** Não encontrado - Dados não localizados
- **429:** Muitas requisições - Limite de rate excedido

## Tratamento de Erros

Os scripts incluem tratamento para:
- Tokens inválidos ou expirados
- Falta de créditos na conta
- Dados não encontrados
- Problemas de conectividade
- Respostas malformadas

## Exemplo de Resposta Bem-sucedida

```json
{
  "status": "success",
  "data": {
    "placa": "ABC-1234",
    "marca": "VOLKSWAGEN",
    "modelo": "GOL",
    "ano": "2020",
    "cor": "BRANCA",
    "combustivel": "FLEX"
  }
}
```

## Exemplo de Resposta com Erro

```json
{
  "is_error": true,
  "response_status_code": 401,
  "response_reason": "Unauthorized",
  "response_body": {
    "error": true,
    "message": "O Bearer Token informado é inválido"
  }
}
```

## Dicas Importantes

1. **Tokens:** Mantenha seus tokens seguros e não os commite no repositório
2. **Créditos:** Monitore seus créditos na plataforma API Brasil
3. **Rate Limit:** Respeite os limites de requisições por minuto
4. **Dados Sensíveis:** Use dados fictícios para testes
5. **Ambiente:** Configure variáveis de ambiente para produção

## Suporte

- **Documentação:** [https://apibrasil.com.br/docs](https://apibrasil.com.br/docs)
- **Suporte:** [https://apibrasil.com.br/suporte](https://apibrasil.com.br/suporte)
- **GitHub:** [https://github.com/BrasilAPI/BrasilAPI](https://github.com/BrasilAPI/BrasilAPI)