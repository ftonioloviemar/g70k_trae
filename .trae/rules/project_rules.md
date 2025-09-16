## Estrutura do Projeto
- O banco de dados deve ser SQLite e deve estar localizado em `/data/viemar_garantia.db`
- Os testes devem ficar somente na pasta `/tests`
- Os arquivos temporários de testes devem ficar na pasta `/tmp`
- Não criar arquivos soltos na raiz sem permissão explícita

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
