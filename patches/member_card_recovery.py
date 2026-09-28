from pathlib import Path

main_path = Path("/app/app/main.py")
text = main_path.read_text(encoding="utf-8")

imports_anchor = "import io\nimport json\n"
imports = "import io\nimport json\nimport smtplib\nfrom email.mime.text import MIMEText\n"
if imports_anchor in text and "import smtplib\n" not in text:
    text = text.replace(imports_anchor, imports, 1)

route_anchor = '@app.get("/m/{token}/wallet/{provider}")\n'
if route_anchor not in text:
    raise SystemExit("Member wallet route anchor not found")

if 'def member_recovery_form(' not in text:
    block = r'''
# MEMBER CARD RECOVERY
# Recovery links are short lived and are only sent to the verified email on the customer record.

def _send_recovery_email(to_email: str, business_name: str, recovery_url: str) -> bool:
    if not settings.smtp_host or not settings.smtp_from:
        return False
    message = MIMEText(
        f"""Hola,

Solicitaste volver a abrir tu tarjeta de {business_name}.

Usa este enlace desde tu celular:
{recovery_url}

El enlace vence en 15 minutos. Si no solicitaste esta tarjeta, puedes ignorar este mensaje.
""",
        "plain",
        "utf-8",
    )
    message["Subject"] = f"Recupera tu tarjeta de {business_name}"
    message["From"] = settings.smtp_from
    message["To"] = to_email
    try:
        if settings.smtp_use_ssl:
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=12)
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=12)
            if settings.smtp_use_tls:
                server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
        server.quit()
        return True
    except Exception:
        return False


def _recovery_page(title: str, body: str, *, status: int = 200) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html><html lang="es"><meta name="viewport" content="width=device-width,initial-scale=1">
        <title>{title} · Exponenta</title>
        <style>
        *{{box-sizing:border-box}} body{{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;background:#f7f4f0;color:#1d1713;font-family:Inter,ui-sans-serif,system-ui,sans-serif}}
        main{{width:min(100%,500px);background:#fff;border:1px solid #e6ded5;border-radius:26px;padding:32px;box-shadow:0 18px 45px #3b241314}}
        .eyebrow{{font-size:.72rem;letter-spacing:.15em;font-weight:800;color:#9a6644}}h1{{margin:.4rem 0 .8rem;font-size:2rem;letter-spacing:-.05em}}p{{line-height:1.55;color:#695f58}}label{{display:block;font-size:.9rem;font-weight:750;margin:22px 0 8px}}input{{width:100%;border:1px solid #d9d0c7;border-radius:14px;padding:16px;font-size:1rem}}button,a.button{{display:block;width:100%;border:0;border-radius:14px;padding:16px;background:#1d1713;color:#fff;font:inherit;font-weight:800;text-align:center;text-decoration:none;margin-top:18px}}.note{{font-size:.82rem;color:#837971;margin-top:16px}}
        </style><main>{body}</main></html>""",
        status_code=status,
    )


@app.get("/club/{slug}/recuperar", response_class=HTMLResponse)
def member_recovery_form(slug: str, db: Session = Depends(get_db)):
    organization = db.scalar(select(Organization).where(Organization.slug == slug))
    if not organization:
        raise HTTPException(404)
    return _recovery_page(
        "Recupera tu tarjeta",
        f'''<div class="eyebrow">MI TARJETA</div><h1>Vuelve a tener tu tarjeta.</h1>
        <p>Escribe el correo con el que te registraste en <b>{organization.name}</b>. Te enviaremos un enlace seguro para abrir tu tarjeta y agregarla nuevamente a tu celular.</p>
        <form method="post"><label for="email">Correo electrónico</label><input id="email" type="email" name="email" autocomplete="email" required placeholder="tu@correo.com"><button type="submit">Enviar enlace de recuperación</button></form>
        <p class="note">Por seguridad, el enlace sólo se envía al correo registrado y vence en 15 minutos.</p>''',
    )


@app.post("/club/{slug}/recuperar", response_class=HTMLResponse)
def member_recovery_request(slug: str, email: str = Form(...), db: Session = Depends(get_db)):
    organization = db.scalar(select(Organization).where(Organization.slug == slug))
    if not organization:
        raise HTTPException(404)
    normalized_email = (email or "").strip().lower()
    membership = db.scalar(
        select(LoyaltyMembership)
        .join(LoyaltyProgram, LoyaltyMembership.program_id == LoyaltyProgram.id)
        .join(Customer, LoyaltyMembership.customer_id == Customer.id)
        .where(
            LoyaltyProgram.organization_id == organization.id,
            LoyaltyMembership.active.is_(True),
            func.lower(Customer.email) == normalized_email,
        )
        .order_by(LoyaltyMembership.id.desc())
    )
    if membership:
        token = jwt.encode(
            {
                "scope": "member_card_recovery",
                "membership_id": membership.id,
                "organization_id": organization.id,
                "email": normalized_email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            },
            settings.session_secret,
            algorithm="HS256",
        )
        recovery_url = f"{settings.app_base_url.rstrip('/')}/recuperar/tarjeta/{token}"
        _send_recovery_email(normalized_email, organization.name, recovery_url)
    # Same response whether the email exists or not: no customer data is disclosed.
    return _recovery_page(
        "Revisa tu correo",
        '''<div class="eyebrow">SOLICITUD ENVIADA</div><h1>Revisa tu correo.</h1>
        <p>Si existe una tarjeta asociada a ese correo, recibirás un enlace seguro para volver a abrirla.</p>
        <a class="button" href="/club/''' + slug + '''">Volver al negocio</a>
        <p class="note">Revisa también correo no deseado. El enlace vence en 15 minutos.</p>''',
    )


@app.get("/recuperar/tarjeta/{recovery_token}")
def member_recovery_open(recovery_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(recovery_token, settings.session_secret, algorithms=["HS256"])
        if payload.get("scope") != "member_card_recovery":
            raise ValueError("scope")
        membership_id = int(payload["membership_id"])
        organization_id = int(payload["organization_id"])
    except Exception as exc:
        raise HTTPException(400, "Este enlace expiró o ya no es válido. Solicita uno nuevo.") from exc
    membership = db.get(LoyaltyMembership, membership_id)
    if not membership or not membership.active or membership.program.organization_id != organization_id:
        raise HTTPException(404)
    return RedirectResponse(f"/m/{membership.wallet_token}", status_code=303)


'''
    text = text.replace(route_anchor, block + route_anchor, 1)

main_path.write_text(text, encoding="utf-8")

join_path = Path("/app/app/templates/public/join.html")
join = join_path.read_text(encoding="utf-8")
if "recuperar" not in join.lower():
    marker = "{% endblock %}"
    if marker not in join:
        raise SystemExit("Join template footer anchor not found")
    join = join.replace(marker, '''<p class="xp-card-recovery"><a href="/club/{{ organization.slug }}/recuperar">¿Ya tienes tarjeta? Recuperarla</a></p>
{% endblock %}''', 1)
join_path.write_text(join, encoding="utf-8")

css_path = Path("/app/app/static/app.css")
css = css_path.read_text(encoding="utf-8")
if ".xp-card-recovery" not in css:
    css += "\n.xp-card-recovery{margin:18px auto 0;text-align:center;font-size:.9rem}.xp-card-recovery a{color:inherit;font-weight:750;text-underline-offset:3px}\n"
css_path.write_text(css, encoding="utf-8")

print("Secure member card recovery installed")
