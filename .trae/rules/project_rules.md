## Estrutura do Projeto
- O banco de dados deve ser SQLite e deve estar localizado em `/data/viemar_garantia.db`
- Os testes devem ficar somente na pasta `/tests`
- Os arquivos temporários de testes devem ficar na pasta `/tmp`
- **NUNCA criar arquivos soltos na raiz sem permissão explícita**

## Organização de Arquivos
- **Scripts de análise e debug**: devem ficar em `/scripts/analysis/`
- **Scripts de desenvolvimento**: devem ficar em `/scripts/dev/`
- **Scripts utilitários**: devem ficar em `/scripts/utils/`
- **Arquivos temporários e logs**: devem ficar em `/tmp/`
- **Relatórios e outputs**: devem ficar em `/tmp/` ou pasta específica
- **Imagens de debug**: devem ficar em `/tmp/`
- **PROIBIDO**: deixar arquivos .py, .txt, .png, .log soltos na raiz
- **Exceções permitidas na raiz**: main.py, pyproject.toml, requirements.txt, README.md, .env.example, .gitignore, uv.lock

## Formatação de Datas
- Para exibição nas telas: usar formato brasileiro dd/MM/yyyy
- Para data e hora nas telas: usar formato brasileiro dd/MM/yyyy HH:mm
- Para logs: manter formato atual yyyy-MM-dd HH:mm:ss
- Sempre usar timezone local do Brasil

## Email Service
O sistema usa vieutil.send_email para envio de emails em produção.
O vieutil.send_email NÃO requer autenticação SMTP pois funciona como relay autorizado pelo servidor SMTP.
Não é necessário configurar credenciais SMTP (username/password) quando usando vieutil.send_email.

a aplicação deve ser com fasthtml (pacote python-fasthtml).
entenda toda a documentação completa em https://www.fastht.ml/docs/ incluindo tutoriais e exemplos.
adote as melhores práticas.
use este guia oficial específico para LLM e entenda como usar corretamente o fasthtml https://www.fastht.ml/docs/llms-ctx.txt

use também monsterui para elevar a qualidade visual do fasthtml: https://monsterui.answer.ai/
leia os guias oficiais para LLMs:
https://raw.githubusercontent.com/AnswerDotAI/MonsterUI/refs/heads/main/docs/llms.txt
https://raw.githubusercontent.com/AnswerDotAI/MonsterUI/refs/heads/main/docs/llms-ctx.txt
https://raw.githubusercontent.com/AnswerDotAI/MonsterUI/refs/heads/main/docs/apilist.txt
https://raw.githubusercontent.com/AnswerDotAI/MonsterUI/refs/heads/main/docs/llms-ctx-full.txt

faça testes completos com pytest usando melhores práticas.
garanta que tudo esteja 85% testado.
se encontrar erros, corrija até ficar correto.
faça testes cobertos.
faça testes unitários.
faça testes integrados.
faça testes de integração.
faça testes simulando todas as funcionalidades como se fosse um usuário real.
se a aplicação for web, faça testes com pytest-playwright.
faça testes de end-to-end.
