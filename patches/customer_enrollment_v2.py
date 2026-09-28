from pathlib import Path

# CUSTOMER ENROLLMENT V2: one profile per business, birthday and auditable consent.
service_path = Path("/app/app/services/loyalty.py")
service = service_path.read_text(encoding="utf-8")
if "birthday: Optional[date] = None," not in service:
    service = service.replace(
        "    email: Optional[str] = None,\n):",
        "    email: Optional[str] = None,\n    birthday: Optional[date] = None,\n):",
        1,
    )
    old = '''    customer = db.scalar(
        select(Customer).where(
            Customer.organization_id == program.organization_id,
            Customer.phone == normalized_phone,
        )
    )
    created = False
    if not customer:
        customer = Customer(
            organization_id=program.organization_id,
            name=name.strip() or "Cliente",
            phone=normalized_phone,
            email=(email or "").strip() or None,
        )'''
    new = '''    normalized_email = (email or "").strip().lower() or None
    phone_customer = db.scalar(
        select(Customer).where(
            Customer.organization_id == program.organization_id,
            Customer.phone == normalized_phone,
        )
    )
    email_customer = (
        db.scalar(
            select(Customer).where(
                Customer.organization_id == program.organization_id,
                func.lower(Customer.email) == normalized_email,
            )
        )
        if normalized_email
        else None
    )
    if phone_customer and email_customer and phone_customer.id != email_customer.id:
        raise ValueError("Ese teléfono y correo ya pertenecen a perfiles distintos. Pide apoyo al negocio para unificarlos.")
    customer = phone_customer or email_customer
    created = False
    if not customer:
        customer = Customer(
            organization_id=program.organization_id,
            name=name.strip() or "Cliente",
            phone=normalized_phone,
            email=normalized_email,
            birthday=birthday,
        )'''
    if old not in service:
        raise SystemExit("Enrollment customer lookup anchor missing")
    service = service.replace(old, new, 1)
    old_update = '''    else:
        if name.strip():
            customer.name = name.strip()
        if email and email.strip():
            customer.email = email.strip()
'''
    new_update = '''    else:
        if name.strip():
            customer.name = name.strip()
        if normalized_email:
            customer.email = normalized_email
        if normalized_phone and customer.phone != normalized_phone:
            customer.phone = normalized_phone
        if birthday:
            customer.birthday = birthday
'''
    if old_update not in service:
        raise SystemExit("Enrollment customer update anchor missing")
    service = service.replace(old_update, new_update, 1)
service_path.write_text(service, encoding="utf-8")

main_path = Path("/app/app/main.py")
main = main_path.read_text(encoding="utf-8")
if "from datetime import date," not in main:
    main = main.replace("from datetime import datetime, timedelta, timezone", "from datetime import date, datetime, timedelta, timezone", 1)

old_sig = '''    phone: str = Form(...),
    email: str = Form(""),
    website: str = Form(""),
    db: Session = Depends(get_db),
):'''
new_sig = '''    phone: str = Form(...),
    email: str = Form(""),
    birthday: str = Form(""),
    terms_accepted: str = Form(""),
    marketing_opt_in: str = Form(""),
    website: str = Form(""),
    db: Session = Depends(get_db),
):'''
if old_sig in main and "terms_accepted: str = Form" not in main:
    main = main.replace(old_sig, new_sig, 1)

old_body = '''    if website:
        return RedirectResponse(f"/club/{slug}", status_code=303)
    try:
        _, membership, _ = get_or_create_membership(db, program=program, name=name, phone=phone, email=email)
    except ValueError as exc:
        return render(request, "public/join.html", {"organization": org, "program": program, "error": str(exc)}, status_code=422)
    db.commit()
    return RedirectResponse(f"/m/{membership.wallet_token}", status_code=303)
'''
new_body = '''    if website:
        return RedirectResponse(f"/club/{slug}", status_code=303)
    if terms_accepted != "yes":
        return render(request, "public/join.html", {"organization": org, "program": program, "error": "Necesitas aceptar los Términos y el Aviso de Privacidad para crear tu tarjeta."}, status_code=422)
    parsed_birthday = None
    if birthday:
        try:
            parsed_birthday = date.fromisoformat(birthday)
            if parsed_birthday > date.today():
                raise ValueError
        except ValueError:
            return render(request, "public/join.html", {"organization": org, "program": program, "error": "Ingresa una fecha de nacimiento válida."}, status_code=422)
    try:
        customer, membership, created = get_or_create_membership(
            db, program=program, name=name, phone=phone, email=email, birthday=parsed_birthday
        )
    except ValueError as exc:
        return render(request, "public/join.html", {"organization": org, "program": program, "error": str(exc)}, status_code=422)
    consent = db.scalar(select(MarketingConsent).where(MarketingConsent.customer_id == customer.id))
    if not consent:
        consent = MarketingConsent(
            organization_id=org.id, customer_id=customer.id,
            push_opt_in=False, location_opt_in=False, consent_version="v2",
        )
        db.add(consent)
    # Marketing is a separate, explicit opt-in. Browser permissions are requested later by the OS.
    if marketing_opt_in == "yes":
        db.add(Event(
            organization_id=org.id, customer_id=customer.id,
            event_type=EventType.MARKETING_CONSENT,
            metadata_json=json.dumps({"marketing": True, "source": "club_join_v2"}),
        ))
    db.commit()
    return RedirectResponse(f"/m/{membership.wallet_token}?welcome={'1' if created else 'return'}", status_code=303)
'''
if old_body in main and "club_join_v2" not in main:
    main = main.replace(old_body, new_body, 1)
elif "club_join_v2" not in main:
    raise SystemExit("Public club join body anchor missing")
main_path.write_text(main, encoding="utf-8")

join_path = Path("/app/app/templates/public/join.html")
join_path.write_text(r'''{% extends "base.html" %}
{% block title %}Únete a {{ program.name }}{% endblock %}
{% block body %}
<main class="xp-join-shell">
  <section class="xp-join-hero" {% if organization.logo_url %}style="--xp-logo:url('{{ organization.logo_url }}')"{% endif %}>
    {% if organization.logo_url %}<img src="{{ organization.logo_url }}" alt="{{ organization.name }}">{% endif %}
    <div class="eyebrow">CLUB DE BENEFICIOS</div><h1>{{ program.name }}</h1>
    <p>{% if program.mechanic.value == 'points' %}Acumula puntos y recibe beneficios de {{ organization.name }}.{% else %}Acumula {{ program.stamps_required }} visitas y recibe {{ program.reward_name }}.{% endif %}</p>
  </section>
  <section class="xp-join-card">
    <div class="eyebrow">TU TARJETA EN EL CELULAR</div><h2>Únete en menos de un minuto.</h2>
    <p class="muted">Tus datos se usan para identificar tu tarjeta, registrar beneficios y, sólo si lo autorizas, compartirte novedades del negocio.</p>
    {% if error %}<div class="alert error">{{ error }}</div>{% endif %}
    <form class="form-stack xp-join-form" method="post">
      <label>Nombre completo <input name="name" autocomplete="name" required placeholder="Como aparece en tu tarjeta"></label>
      <label>WhatsApp <input name="phone" inputmode="tel" autocomplete="tel" required placeholder="+52 33 0000 0000"></label>
      <label>Correo electrónico <input name="email" type="email" autocomplete="email" required placeholder="Para recuperar tu tarjeta"></label>
      <label>Fecha de nacimiento <input name="birthday" type="date" autocomplete="bday"></label>
      <input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" class="xp-honeypot">
      <label class="xp-consent"><input name="terms_accepted" value="yes" type="checkbox" required><span>Acepto los <a href="/terminos" target="_blank">Términos de uso</a> y el <a href="/privacidad" target="_blank">Aviso de privacidad</a>.</span></label>
      <label class="xp-consent xp-consent-optional"><input name="marketing_opt_in" value="yes" type="checkbox"><span>Quiero recibir beneficios, promociones y recordatorios de {{ organization.name }}.</span></label>
      <button class="btn btn-primary" type="submit">Crear mi tarjeta</button>
    </form>
    <p class="xp-join-foot">Ya tienes tarjeta? <a href="/club/{{ organization.slug }}/recuperar">Recuperarla</a></p>
  </section>
</main>
{% endblock %}''', encoding="utf-8")

member_path = Path("/app/app/templates/public/member.html")
member = member_path.read_text(encoding="utf-8")
old_marketing = '''<section class="panel-card"><div class="kicker">MARKETING OPCIONAL</div><h2 style="margin:.3rem 0">Activa beneficios cercanos</h2><p class="muted">Tú decides. Puedes permitir notificaciones y ubicación para recibir promociones relevantes cuando estés cerca.</p><div style="display:grid;gap:8px"><button id="enable-push" class="btn btn-secondary">Activar notificaciones</button><button id="enable-location" class="btn btn-secondary">Activar ubicación</button><div id="permission-status" class="muted" style="font-size:.8rem"></div></div></section>'''
new_marketing = '''<section class="panel-card xp-member-benefits"><div class="kicker">BENEFICIOS DEL CLUB</div><h2 style="margin:.3rem 0">No te pierdas tu recompensa.</h2><p class="muted">Activa avisos para enterarte de beneficios, cumpleaños y promociones. La ubicación sólo se solicita cuando eliges beneficios cercanos.</p><div style="display:grid;gap:8px"><button id="enable-push" class="btn btn-secondary">Activar avisos</button><button id="enable-location" class="btn btn-secondary">Activar beneficios cercanos</button><div id="permission-status" class="muted" style="font-size:.8rem"></div></div></section><div id="xp-welcome" class="xp-welcome" hidden><div class="xp-confetti" aria-hidden="true"></div><div class="xp-success-mark">✓</div><h2>¡Tu tarjeta está lista!</h2><p>Muéstrala en cada visita para recibir tus beneficios.</p><button type="button" class="btn btn-primary" id="xp-welcome-close">Ver mi tarjeta</button></div>'''
if old_marketing in member:
    member = member.replace(old_marketing, new_marketing, 1)
member_path.write_text(member, encoding="utf-8")

js_path = Path("/app/app/static/member-marketing.js")
js = js_path.read_text(encoding="utf-8")
if "xp-welcome-close" not in js:
    js += r'''
;(()=>{const modal=document.getElementById("xp-welcome"),close=document.getElementById("xp-welcome-close");if(!modal)return;const state=new URLSearchParams(location.search).get("welcome");if(state){modal.hidden=false;history.replaceState({},'',location.pathname);close?.addEventListener("click",()=>modal.hidden=true);navigator.vibrate?.([60,30,90]);}})();
'''
js_path.write_text(js, encoding="utf-8")

css_path = Path("/app/app/static/app.css")
css = css_path.read_text(encoding="utf-8")
if "/* XP ENROLLMENT V2 */" not in css:
    css += r'''
/* XP ENROLLMENT V2 */
.xp-join-shell{min-height:100vh;padding:28px 18px 44px;background:#f5f1eb;display:grid;gap:18px;align-content:center}.xp-join-hero,.xp-join-card{width:min(100%,560px);margin:auto;border-radius:26px}.xp-join-hero{background:#201711;color:#fff;padding:28px;overflow:hidden}.xp-join-hero img{width:68px;height:68px;object-fit:contain;background:#fff;border-radius:16px;padding:5px;margin-bottom:18px}.xp-join-hero h1{font-size:clamp(2rem,10vw,3.1rem);line-height:.98;margin:.35rem 0 .8rem;letter-spacing:-.06em}.xp-join-hero p{margin:0;color:#e3d7cc;line-height:1.5}.xp-join-card{background:#fff;padding:27px;border:1px solid #e1d9d0;box-shadow:0 18px 40px #3e261414}.xp-join-card h2{font-size:1.65rem;letter-spacing:-.045em;margin:.3rem 0}.xp-join-form label{font-weight:760}.xp-join-form input:not([type=checkbox]){border:1px solid #d9d0c8;border-radius:14px;padding:14px;font:inherit;background:#fff;width:100%;margin-top:7px}.xp-honeypot{position:absolute!important;left:-9999px!important}.xp-consent{display:flex!important;gap:10px;align-items:flex-start;font-size:.8rem;line-height:1.4;font-weight:560!important}.xp-consent input{margin:3px 0 0;width:18px;height:18px;accent-color:#8c5637}.xp-consent a{color:#57321e;font-weight:800}.xp-consent-optional{color:#6f645c}.xp-join-foot{text-align:center;font-size:.85rem}.xp-join-foot a{font-weight:800;color:#603a25}.xp-welcome{position:fixed;inset:0;z-index:200;background:rgba(26,18,13,.72);backdrop-filter:blur(5px);display:grid;place-content:center;text-align:center;padding:28px}.xp-welcome[hidden]{display:none}.xp-welcome>h2,.xp-welcome>p,.xp-welcome>button,.xp-success-mark{position:relative;z-index:2}.xp-welcome>h2{color:#fff;font-size:2.3rem;margin:.3rem}.xp-welcome>p{color:#eadfd5;margin:0 0 20px}.xp-success-mark{margin:auto;width:76px;height:76px;border-radius:50%;display:grid;place-items:center;background:#7dc775;color:#143812;font-size:2.6rem;font-weight:900;box-shadow:0 8px 28px #0005}.xp-welcome .btn{width:min(100%,320px);margin:auto}.xp-confetti{position:absolute;inset:0;background:radial-gradient(circle at 20% 30%,#f7b44a 0 5px,transparent 6px),radial-gradient(circle at 70% 20%,#e8786d 0 6px,transparent 7px),radial-gradient(circle at 78% 70%,#85c778 0 5px,transparent 6px),radial-gradient(circle at 25% 75%,#7bb7dd 0 5px,transparent 6px);background-size:130px 160px;animation:xp-confetti-fall 1.4s linear infinite}@keyframes xp-confetti-fall{to{background-position:0 180px}}
'''
css_path.write_text(css, encoding="utf-8")
print("Customer enrollment V2 installed")
