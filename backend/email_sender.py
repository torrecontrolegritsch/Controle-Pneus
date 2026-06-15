"""
Módulo de envio de e-mail via SMTP.
Configurar no .env:
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=seuemail@gmail.com
  SMTP_PASS=sua_senha_de_app
  SMTP_FROM_NAME=Sistema de Pneus Gritsch
  APP_URL=https://pneus-controle.vercel.app
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)

SMTP_HOST      = os.getenv("SMTP_HOST", "")
SMTP_PORT      = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER      = os.getenv("SMTP_USER", "")
SMTP_PASS      = os.getenv("SMTP_PASS", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Sistema de Pneus Gritsch")
APP_URL        = os.getenv("APP_URL", "https://pneus-controle.vercel.app")


def _smtp_configurado() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASS)


def _build_boas_vindas(nome: str, email: str, role: str, filial: str | None) -> str:
    role_map = {"admin": "Administrador", "gerente": "Gerente", "operador": "Operador"}
    role_label = role_map.get(role, "Operador")
    filial_linha = f"<p style='margin:4px 0;font-size:14px;color:#475569;'><strong>Filial:</strong> {filial}</p>" if filial else ""
    primeiro_nome = nome.split()[0] if nome else "Usuário"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bem-vindo ao Sistema de Pneus</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 20px;">
    <tr><td align="center">

      <!-- Card principal -->
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.10);">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);padding:40px 40px 32px;text-align:center;">
            <div style="width:60px;height:60px;background:rgba(255,255,255,.15);border-radius:14px;display:inline-flex;align-items:center;justify-content:center;margin-bottom:16px;">
              <!-- Tire icon -->
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="12" cy="12" r="4"/>
                <line x1="12" y1="2" x2="12" y2="8"/>
                <line x1="12" y1="16" x2="12" y2="22"/>
                <line x1="2" y1="12" x2="8" y2="12"/>
                <line x1="16" y1="12" x2="22" y2="12"/>
              </svg>
            </div>
            <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:-.3px;">Sistema de Gestão de Pneus</h1>
            <p style="margin:6px 0 0;color:rgba(255,255,255,.75);font-size:14px;">Gritsch Transportes · Torre de Controle</p>
          </td>
        </tr>

        <!-- Saudação -->
        <tr>
          <td style="padding:36px 40px 0;">
            <p style="margin:0 0 6px;font-size:22px;font-weight:700;color:#1e293b;">Olá, {primeiro_nome}! 👋</p>
            <p style="margin:0;font-size:15px;color:#64748b;line-height:1.6;">
              Seu acesso ao <strong>Sistema de Gestão de Pneus</strong> foi criado com sucesso. A partir de agora você pode controlar toda a frota de pneus da Gritsch em tempo real.
            </p>
          </td>
        </tr>

        <!-- Card de credenciais -->
        <tr>
          <td style="padding:24px 40px 0;">
            <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:12px;padding:20px 24px;">
              <p style="margin:0 0 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#94a3b8;">Suas credenciais de acesso</p>
              <p style="margin:4px 0;font-size:14px;color:#475569;"><strong>E-mail:</strong> {email}</p>
              <p style="margin:4px 0;font-size:14px;color:#475569;"><strong>Perfil:</strong> {role_label}</p>
              {filial_linha}
              <p style="margin:12px 0 0;font-size:12px;color:#94a3b8;">
                A senha foi definida pelo administrador. Recomendamos alterá-la após o primeiro acesso.
              </p>
            </div>
          </td>
        </tr>

        <!-- Botão de acesso -->
        <tr>
          <td style="padding:28px 40px 0;text-align:center;">
            <a href="{APP_URL}" target="_blank"
               style="display:inline-block;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#ffffff;text-decoration:none;
                      font-size:15px;font-weight:700;padding:14px 40px;border-radius:10px;
                      letter-spacing:.2px;box-shadow:0 4px 14px rgba(37,99,235,.4);">
              Acessar o Sistema →
            </a>
            <p style="margin:12px 0 0;font-size:12px;color:#94a3b8;">
              Ou copie o link: <a href="{APP_URL}" style="color:#2563eb;">{APP_URL}</a>
            </p>
          </td>
        </tr>

        <!-- Funcionalidades -->
        <tr>
          <td style="padding:32px 40px 0;">
            <p style="margin:0 0 16px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#94a3b8;">O que você pode fazer no sistema</p>
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td width="50%" style="padding:0 8px 12px 0;vertical-align:top;">
                  <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 16px;">
                    <span style="font-size:18px;">🏠</span>
                    <p style="margin:6px 0 0;font-size:13px;font-weight:600;color:#1e293b;">Estoque Central</p>
                    <p style="margin:3px 0 0;font-size:12px;color:#64748b;">Controle todos os pneus em estoque por medida e marca</p>
                  </div>
                </td>
                <td width="50%" style="padding:0 0 12px 8px;vertical-align:top;">
                  <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:14px 16px;">
                    <span style="font-size:18px;">🚛</span>
                    <p style="margin:6px 0 0;font-size:13px;font-weight:600;color:#1e293b;">Frota & Alocações</p>
                    <p style="margin:3px 0 0;font-size:12px;color:#64748b;">Acompanhe cada pneu instalado por veículo e posição de eixo</p>
                  </div>
                </td>
              </tr>
              <tr>
                <td width="50%" style="padding:0 8px 12px 0;vertical-align:top;">
                  <div style="background:#fefce8;border:1px solid #fef08a;border-radius:10px;padding:14px 16px;">
                    <span style="font-size:18px;">📦</span>
                    <p style="margin:6px 0 0;font-size:13px;font-weight:600;color:#1e293b;">Transferência entre Filiais</p>
                    <p style="margin:3px 0 0;font-size:12px;color:#64748b;">Distribua pneus entre unidades com rastreamento completo</p>
                  </div>
                </td>
                <td width="50%" style="padding:0 0 12px 8px;vertical-align:top;">
                  <div style="background:#fdf4ff;border:1px solid #e9d5ff;border-radius:10px;padding:14px 16px;">
                    <span style="font-size:18px;">📊</span>
                    <p style="margin:6px 0 0;font-size:13px;font-weight:600;color:#1e293b;">Relatórios & Histórico</p>
                    <p style="margin:3px 0 0;font-size:12px;color:#64748b;">Rastreie NFs, vidas úteis, custos e retorno de reciclagem</p>
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Dica de segurança -->
        <tr>
          <td style="padding:20px 40px 0;">
            <div style="background:#fffbeb;border-left:4px solid #f59e0b;border-radius:0 8px 8px 0;padding:14px 16px;">
              <p style="margin:0;font-size:13px;color:#92400e;">
                <strong>🔒 Dica de segurança:</strong> Não compartilhe sua senha. Em caso de dúvidas ou problemas de acesso, contate o administrador do sistema.
              </p>
            </div>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:32px 40px 0;"><hr style="border:none;border-top:1px solid #f1f5f9;margin:0;" /></td></tr>

        <!-- Footer -->
        <tr>
          <td style="padding:24px 40px 32px;text-align:center;">
            <p style="margin:0 0 4px;font-size:12px;font-weight:700;color:#1e293b;">Gritsch Transportes</p>
            <p style="margin:0 0 12px;font-size:11px;color:#94a3b8;">Sistema de Gestão de Pneus · Torre de Controle</p>
            <p style="margin:0;font-size:11px;color:#cbd5e1;">
              Este e-mail foi enviado automaticamente. Por favor, não responda.
            </p>
          </td>
        </tr>

      </table>
      <!-- /Card -->

    </td></tr>
  </table>

</body>
</html>"""


def enviar_boas_vindas(nome: str, email_destino: str, role: str, filial: str | None = None) -> bool:
    """Envia e-mail de boas-vindas ao novo usuário. Retorna True se enviou, False se não configurado ou erro."""
    if not _smtp_configurado():
        logger.info("SMTP não configurado — e-mail de boas-vindas não enviado")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "✅ Seu acesso ao Sistema de Pneus foi criado"
        msg["From"]    = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg["To"]      = email_destino

        html = _build_boas_vindas(nome, email_destino, role, filial)
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, email_destino, msg.as_string())

        logger.info(f"E-mail de boas-vindas enviado para {email_destino}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {email_destino}: {e}")
        return False
