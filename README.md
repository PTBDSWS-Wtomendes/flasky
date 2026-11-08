# Aula 080. Estrutura completa da aplicação

## Entrega de e-mails

Para evitar que mensagens transacionais sejam classificadas como spam, autentique o domínio usado em `SENDGRID_FROM` no SendGrid (Settings > Sender Authentication > Domain Authentication). Publique os registros SPF e DKIM fornecidos pelo SendGrid e configure um registro DMARC para o domínio.

Defina também `APP_BASE_URL` com a URL pública HTTPS da aplicação. Assim, os links de confirmação e redefinição de senha não apontam para `localhost`. Veja `.env.example`.
