# Configuração de Email - Sistema de Garantia Viemar

## Visão Geral

O sistema possui duas formas de envio de email:

1. **vieutil.send_email (Produção)** - Método prioritário que usa relay autorizado (não requer credenciais SMTP)
2. **SMTP Tradicional (Desenvolvimento/Fallback)** - Requer configuração de credenciais

## Status Atual

O sistema usa EXCLUSIVAMENTE vieutil.send_email para envio de emails.
Não há fallback para SMTP tradicional - o vieutil.send_email é o único método suportado.

## Logs de Erro

```
2025-09-15 10:47:30 - app.email_service - ERROR - Erro ao enviar email para teste@viemar.com: (535, b'5.7.8 Username and Password not accepted. For more information, go to https://support.google.com/mail/?p=BadCredentials')
```

## Configuração para Produção (vieutil)

**Em produção, o sistema usa automaticamente o vieutil.send_email que:**
- ✅ Não requer configuração de credenciais SMTP
- ✅ Usa relay autorizado pelo servidor
- ✅ Funciona automaticamente quando o pacote vieutil está disponível
- ✅ É o método prioritário de envio

**Nenhuma configuração adicional é necessária em produção.**

## Configuração para Desenvolvimento

O sistema usa exclusivamente vieutil.send_email.
Não é necessário configurar credenciais SMTP para desenvolvimento.

Se o vieutil.send_email não estiver disponível no ambiente de desenvolvimento,
os emails simplesmente não serão enviados e será registrado um erro no log.

## Status Atual do Sistema

✅ **Funcionando Corretamente:**
- Cadastro de usuários
- Validação de formulários
- Armazenamento no banco de dados
- Interface web responsiva
- Sistema de autenticação

⚠️ **Necessita Configuração:**
- Envio de emails de confirmação
- Notificações por email

## Teste Realizado

```
=== Teste de Cadastro sem Email ===
Testando cadastro de usuário: teste_20250915_104723@viemar.com
Status Code: 302
Redirecionamento para: /cadastro/sucesso
✅ SUCESSO: Cadastro realizado com sucesso!
```

**Usuário criado com ID: 6** - Sistema funcionando perfeitamente para cadastros.

## Próximos Passos

1. Configurar credenciais de email seguindo uma das opções acima
2. Testar envio de email com um usuário real
3. Verificar logs para confirmar funcionamento

## Suporte

Para dúvidas sobre configuração de email, consulte:
- [Documentação Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Configuração SMTP Outlook](https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353)