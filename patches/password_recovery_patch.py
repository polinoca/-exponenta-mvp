from pathlib import Path
import re

main = Path("/app/app/main.py")
source = main.read_text(encoding="utf-8")
models = Path("/app/app/models.py").read_text(encoding="utf-8")

if "EXPONENTA PASSWORD RECOVERY V1" not in source:
    user_match = re.search(
        r'class\s+User\s*\([^)]*\)\s*:\s*.*?__tablename__\s*=\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']',
        models,
        re.S,
    )
    if not user_match:
        raise SystemExit("User table could not be identified safely")
    user_table = user_match.group(1)
    field_candidates = ("password_hash", "hashed_password", "password_digest")
    password_field = next(
        (field for field in field_candidates if re.search(rf'\b{field}\s*:', models)),
        None,
    )
    if not password_field:
        raise SystemExit("User password field could not be identified safely")
    email_field = "email" if re.search(r'\bemail\s*:', models) else None
    if not email_field:
        raise SystemExit("User email field could not be identified safely")

    anchor = '@app.get("/login"'
    pos = source.find(anchor)
    if pos < 0:
        raise SystemExit("Login route anchor missing")

    routes = r'''# EXPONENTA PASSWORD RECOVERY V1
# Tokens are stored only as SHA-256 hashes, expire in 30 minutes and may be used once.
import os
import secrets
import hashlib
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from argon2 import PasswordHasher

_PASSWORD_RESET_TABLE = "password_reset_tokens"
_PASSWORD_RESET_USER_TABLE = "__USER_TABLE__"
_PASSWORD_RESET_EMAIL_FIELD = "__EMAIL_FIELD__"
_PASSWORD_RESET_PASSWORD_FIELD = "__PASSWORD_FIELD__"
_PASSWORD_RESET_HASHER = PasswordHasher()


def _reset_mail_configured() -> bool:
    return bool(
        os.getenv("SMTP_HOST", "").strip()
        and os.getenv("SMTP_FROM", "team@exponenta.mx").strip()
        and os.getenv("SMTP_USERNAME", "").strip()
        and os.getenv("SMTP_PASSWORD", "").strip()
    )


def _ensure_password_reset_table(db: Session) -> None:
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id BIGSERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token_hash VARCHAR(128) NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            used_at TIMESTAMPTZ NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    db.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_lookup
        ON password_reset_tokens (token_hash, expires_at)
    """))
    db.commit()


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _reset_token_record(db: Session, token: str):
    if not token or len(token) < 32:
        return None
    _ensure_password_reset_table(db)
    return db.execute(
        text("""
            SELECT user_id FROM password_reset_tokens
            WHERE token_hash = :token_hash
              AND used_at IS NULL
              AND expires_at > NOW()
            LIMIT 1
        """),
        {"token_hash": _hash_reset_token(token)},
    ).mappings().first()


def _send_password_reset_email(destination: str, token: str) -> None:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "465").strip() or "465")
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    sender = os.getenv("SMTP_FROM", "team@exponenta.mx").strip()
    use_ssl = os.getenv("SMTP_USE_SSL", "true").lower() not in {"0", "false", "no"}
    reset_url = settings.app_base_url.rstrip("/") + "/restablecer-contrasena?token=" + token
    message = EmailMessage()
    message["Subject"] = "Restablece tu acceso a Exponenta"
    message["From"] = sender
    message["To"] = destination
    message.set_content(
        "Recibimos una solicitud para restablecer tu contraseña de Exponenta.\n\n"
        f"Abre este enlace para crear una nueva contraseña:\n{reset_url}\n\n"
        "El enlace vence en 30 minutos y solo puede usarse una vez. "
        "Si no solicitaste este cambio, puedes ignorar este correo."
    )
    smtp_client = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with smtp_client(host, port, timeout=15) as smtp:
        if not use_ssl and os.getenv("SMTP_USE_TLS", "true").lower() not in {"0", "false", "no"}:
            smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)


@app.get("/recuperar-acceso", response_class=HTMLResponse)
def password_recovery_request(request: Request):
    return render(
        request,
        "password_recovery_request.html",
        {
            "mail_ready": _reset_mail_configured(),
            "sent": request.query_params.get("enviado") == "1",
            "unavailable": request.query_params.get("no_disponible") == "1",
        },
    )


@app.post("/recuperar-acceso")
def password_recovery_submit(email: str = Form(""), db: Session = Depends(get_db)):
    # Keep the outward response identical for unknown addresses.
    if not _reset_mail_configured():
        return RedirectResponse("/recuperar-acceso?no_disponible=1", status_code=303)
    normalized = email.strip().lower()
    if normalized:
        _ensure_password_reset_table(db)
        user = db.execute(
            text(f"SELECT id, {_PASSWORD_RESET_EMAIL_FIELD} AS email FROM {_PASSWORD_RESET_USER_TABLE} "
                 f"WHERE lower({_PASSWORD_RESET_EMAIL_FIELD}) = :email LIMIT 1"),
            {"email": normalized},
        ).mappings().first()
        if user:
            recent = db.execute(
                text("""
                    SELECT COUNT(*) AS total FROM password_reset_tokens
                    WHERE user_id = :user_id AND created_at > NOW() - INTERVAL '1 hour'
                """),
                {"user_id": user["id"]},
            ).mappings().first()
            if int(recent["total"]) < 5:
                token = secrets.token_urlsafe(32)
                db.execute(
                    text("""
                        INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
                        VALUES (:user_id, :token_hash, :expires_at)
                    """),
                    {
                        "user_id": user["id"],
                        "token_hash": _hash_reset_token(token),
                        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30),
                    },
                )
                db.commit()
                try:
                    _send_password_reset_email(user["email"], token)
                except Exception as exc:
                    # Do not expose mail-provider details to visitors.
                    print("PASSWORD_RESET_EMAIL_ERROR", type(exc).__name__, flush=True)
    return RedirectResponse("/recuperar-acceso?enviado=1", status_code=303)


@app.get("/restablecer-contrasena", response_class=HTMLResponse)
def password_reset_form(request: Request, token: str = "", db: Session = Depends(get_db)):
    record = _reset_token_record(db, token)
    if not record:
        return RedirectResponse("/recuperar-acceso?enlace_invalido=1", status_code=303)
    return render(request, "password_reset_form.html", {"token": token, "error": ""})


@app.post("/restablecer-contrasena", response_class=HTMLResponse)
def password_reset_submit(
    request: Request,
    token: str = Form(""),
    password: str = Form(""),
    password_confirmation: str = Form(""),
    db: Session = Depends(get_db),
):
    record = _reset_token_record(db, token)
    if not record:
        return RedirectResponse("/recuperar-acceso?enlace_invalido=1", status_code=303)
    if len(password) < 10:
        return render(
            request,
            "password_reset_form.html",
            {"token": token, "error": "Usa una contraseña de al menos 10 caracteres."},
            status_code=422,
        )
    if password != password_confirmation:
        return render(
            request,
            "password_reset_form.html",
            {"token": token, "error": "Las contraseñas no coinciden."},
            status_code=422,
        )
    db.execute(
        text(f"UPDATE {_PASSWORD_RESET_USER_TABLE} "
             f"SET {_PASSWORD_RESET_PASSWORD_FIELD} = :password_hash WHERE id = :user_id"),
        {
            "password_hash": _PASSWORD_RESET_HASHER.hash(password),
            "user_id": record["user_id"],
        },
    )
    db.execute(
        text("UPDATE password_reset_tokens SET used_at = NOW() WHERE token_hash = :token_hash"),
        {"token_hash": _hash_reset_token(token)},
    )
    db.commit()
    return RedirectResponse("/login?message=Contraseña+actualizada.+Ya+puedes+iniciar+sesión", status_code=303)


'''
    routes = (
        routes.replace("__USER_TABLE__", user_table)
        .replace("__EMAIL_FIELD__", email_field)
        .replace("__PASSWORD_FIELD__", password_field)
    )
    source = source[:pos] + routes + source[pos:]

main.write_text(source, encoding="utf-8")

login = Path("/app/app/templates/login.html")
template = login.read_text(encoding="utf-8")
if "EXPONENTA PASSWORD RECOVERY LINK V1" not in template:
    marker = "<!-- EXPONENTA LOGIN UX V1 -->"
    if marker not in template:
        raise SystemExit("Login UX marker missing")
    template = template.replace(
        marker,
        '''<p class="xp-forgot-password"><a href="/recuperar-acceso">¿Olvidaste tu contraseña?</a></p>
<!-- EXPONENTA PASSWORD RECOVERY LINK V1 -->
''' + marker,
        1,
    )
login.write_text(template, encoding="utf-8")

templates = Path("/app/app/templates")
(templates / "password_recovery_request.html").write_text(r'''{% extends "base.html" %}
{% block title %}Recuperar acceso · Exponenta{% endblock %}
{% block body %}
<main class="xp-auth-page">
  <section class="xp-auth-card">
    <a class="xp-auth-back" href="/login">← Volver a iniciar sesión</a>
    <span class="eyebrow">RECUPERAR ACCESO</span>
    <h1>Recupera tu acceso.</h1>
    <p>Escribe el correo con el que ingresas. Te enviaremos un enlace seguro para crear una contraseña nueva.</p>
    {% if sent %}<div class="xp-auth-message success">Si existe una cuenta con ese correo, te enviamos un enlace para restablecer la contraseña.</div>{% endif %}
    {% if unavailable %}<div class="xp-auth-message warning">La recuperación por correo se está activando. Intenta nuevamente más tarde.</div>{% endif %}
    {% if mail_ready %}
    <form method="post" action="/recuperar-acceso" class="xp-auth-form">
      <label>Correo<input name="email" type="email" autocomplete="email" required></label>
      <button class="btn btn-primary" type="submit">Enviar enlace de recuperación</button>
    </form>
    {% endif %}
  </section>
</main>
{% endblock %}''', encoding="utf-8")

(templates / "password_reset_form.html").write_text(r'''{% extends "base.html" %}
{% block title %}Nueva contraseña · Exponenta{% endblock %}
{% block body %}
<main class="xp-auth-page">
  <section class="xp-auth-card">
    <span class="eyebrow">NUEVA CONTRASEÑA</span>
    <h1>Crea tu nueva contraseña.</h1>
    <p>Usa al menos 10 caracteres. Este enlace vence en 30 minutos y solo puede utilizarse una vez.</p>
    {% if error %}<div class="xp-auth-message warning">{{ error }}</div>{% endif %}
    <form method="post" action="/restablecer-contrasena" class="xp-auth-form">
      <input type="hidden" name="token" value="{{ token }}">
      <label>Nueva contraseña<input name="password" type="password" autocomplete="new-password" minlength="10" required></label>
      <label>Confirma tu contraseña<input name="password_confirmation" type="password" autocomplete="new-password" minlength="10" required></label>
      <button class="btn btn-primary" type="submit">Guardar contraseña nueva</button>
    </form>
  </section>
</main>
{% endblock %}''', encoding="utf-8")

css = Path("/app/app/static/app.css")
styles = css.read_text(encoding="utf-8")
if "EXPONENTA PASSWORD RECOVERY V1" not in styles:
    styles += r'''
/* EXPONENTA PASSWORD RECOVERY V1 */
.xp-forgot-password{margin:4px 0 0;text-align:right;font-size:.78rem;font-weight:800}.xp-forgot-password a{color:#754127;text-decoration:none}.xp-auth-page{min-height:70vh;display:grid;place-items:center;padding:38px 18px}.xp-auth-card{width:min(100%,500px);padding:28px;border:1px solid #e2d8cf;border-radius:22px;background:#fff;box-shadow:0 18px 42px rgba(73,42,24,.08)}.xp-auth-card h1{margin:6px 0 8px;letter-spacing:-.045em}.xp-auth-card>p{color:#6f655d;line-height:1.55}.xp-auth-back{display:inline-block;margin-bottom:22px;color:#754127;text-decoration:none;font-size:.76rem;font-weight:850}.xp-auth-form{display:grid;gap:14px;margin-top:20px}.xp-auth-form label{display:grid;gap:6px;font-size:.76rem;font-weight:850;color:#594d45}.xp-auth-form input{min-height:46px;padding:0 12px;border:1px solid #d9cec4;border-radius:11px;font:inherit}.xp-auth-message{margin:17px 0 0;padding:12px 13px;border-radius:12px;font-size:.78rem;line-height:1.45}.xp-auth-message.success{background:#e8f3ea;color:#285d38}.xp-auth-message.warning{background:#f7ead9;color:#754d1e}
'''
css.write_text(styles, encoding="utf-8")
# Railway source sync trigger: SMTP SSL recovery patch\nprint("Password recovery flow installed")
