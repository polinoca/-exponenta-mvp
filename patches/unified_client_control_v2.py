from pathlib import Path

main=Path("/app/app/main.py")
s=main.read_text(encoding="utf-8")

# Robustly link an existing Connect profile to its Organization.
old='''connect_profile=db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE organization_id=:org_id OR slug=:slug ORDER BY CASE WHEN organization_id=:org_id THEN 0 ELSE 1 END LIMIT 1"),{"org_id":org.id,"slug":org.slug}).mappings().first()'''
new='''connect_profile=db.execute(xp_sql_text("""
 SELECT * FROM exponenta_connect_profiles
 WHERE organization_id=:org_id
    OR lower(slug)=lower(:slug)
    OR lower(name)=lower(:name)
 ORDER BY CASE
   WHEN organization_id=:org_id THEN 0
   WHEN lower(slug)=lower(:slug) THEN 1
   ELSE 2 END
 LIMIT 1
 """),{"org_id":org.id,"slug":org.slug,"name":org.name}).mappings().first()'''
if old in s:
    s=s.replace(old,new,1)

# Allow Superadmin to create the first login for a business from the same client card.
if 'def admin_create_business_access(' not in s:
    anchor='@app.post("/admin/control/{org_id}/feature/{feature_key}")'
    route=r'''@app.post("/admin/control/{org_id}/usuario/crear")
def admin_create_business_access(
    org_id: int,
    request: Request,
    access_name: str = Form(""),
    access_email: str = Form(""),
    temporary_password: str = Form(""),
    password_confirmation: str = Form(""),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    control_superadmin(request, db)
    verify_csrf(request, csrf_token)
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404, "Negocio no encontrado")
    email = access_email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        return RedirectResponse(f"/admin/control/{org_id}?access_error=email", status_code=303)
    if len(temporary_password) < 10:
        return RedirectResponse(f"/admin/control/{org_id}?access_error=length", status_code=303)
    if temporary_password != password_confirmation:
        return RedirectResponse(f"/admin/control/{org_id}?access_error=mismatch", status_code=303)
    existing = db.scalar(select(User).where(func.lower(User.email) == email))
    if existing:
        if existing.organization_id == org_id:
            return RedirectResponse(f"/admin/control/{org_id}?access_error=exists", status_code=303)
        return RedirectResponse(f"/admin/control/{org_id}?access_error=email_used", status_code=303)

    account = User()
    account.email = email
    account.organization_id = org_id
    account.role = Role.BUSINESS_ADMIN
    if hasattr(account, "active"):
        account.active = True
    clean_name = access_name.strip() or org.name
    for field in ("name","full_name","display_name"):
        if hasattr(account, field):
            setattr(account, field, clean_name)
            break
    setattr(account, _PASSWORD_RESET_PASSWORD_FIELD, _PASSWORD_RESET_HASHER.hash(temporary_password))
    db.add(account)
    db.commit()
    return RedirectResponse(f"/admin/control/{org_id}?access_created=1", status_code=303)

'''
    if anchor in s:
        s=s.replace(anchor,route+anchor,1)

# Add access creation status to the control page context.
needle='password_error=request.query_params.get("password_error","")'
if needle in s and 'access_error=request.query_params.get("access_error","")' not in s:
    s=s.replace(
        needle,
        needle+';access_error=request.query_params.get("access_error","");access_created=request.query_params.get("access_created","")',
        1
    )
for render_pat in [
    '"password_error":password_error',
]:
    if render_pat in s and '"access_error":access_error' not in s:
        s=s.replace(render_pat,render_pat+',"access_error":access_error,"access_created":access_created',1)

main.write_text(s,encoding="utf-8")

# Unified client page: if there is no account, create it here. Otherwise show reset.
tpl=Path("/app/app/templates/admin/control_business.html")
t=tpl.read_text(encoding="utf-8")
if "EXPONENTA CREATE BUSINESS ACCESS V1" not in t:
    start=t.find('<section class="xp-admin-password">')
    if start>=0:
        end=t.find('</section>',start)
        if end>=0:
            end+=len('</section>')
            existing=t[start:end]
            create=r'''<!-- EXPONENTA CREATE BUSINESS ACCESS V1 -->
{% if organization_users %}
'''+existing+r'''
{% else %}
<section class="xp-admin-password xp-create-access">
  <span class="eyebrow">ACCESO DEL CLIENTE</span>
  <h2>Crear acceso al negocio.</h2>
  <p>Este será el único usuario que necesita el cliente para entrar a Exponenta. Después podrá usar los módulos que le actives.</p>
  {% if access_created %}<div class="xp-auth-message success">Acceso creado correctamente.</div>{% endif %}
  {% if access_error == "email" %}<div class="xp-auth-message warning">Escribe un correo válido.</div>{% endif %}
  {% if access_error == "length" %}<div class="xp-auth-message warning">La contraseña temporal debe tener al menos 10 caracteres.</div>{% endif %}
  {% if access_error == "mismatch" %}<div class="xp-auth-message warning">Las contraseñas no coinciden.</div>{% endif %}
  {% if access_error == "exists" %}<div class="xp-auth-message warning">Este negocio ya tiene ese usuario.</div>{% endif %}
  {% if access_error == "email_used" %}<div class="xp-auth-message warning">Ese correo ya pertenece a otra cuenta.</div>{% endif %}
  <form method="post" action="/admin/control/{{ organization.id }}/usuario/crear">
    <input type="hidden" name="csrf_token" value="{{ csrf }}">
    <label>Nombre<input name="access_name" value="{{ organization.name }}" required></label>
    <label>Correo de acceso<input type="email" name="access_email" placeholder="cliente@negocio.com" required></label>
    <label>Contraseña temporal<input type="password" name="temporary_password" minlength="10" required></label>
    <label>Confirmar contraseña<input type="password" name="password_confirmation" minlength="10" required></label>
    <button class="btn btn-primary" type="submit">Crear acceso</button>
  </form>
  <p class="xp-login-hint"><b>Link que recibe el cliente:</b> https://app.exponenta.mx/login</p>
</section>
{% endif %}'''
            t=t[:start]+create+t[end:]

# Simplify wording: this is the general customer control, not a Wallet-only screen.
t=t.replace("Planes, accesos y funciones por cliente.","Todo el cliente en un solo lugar.")
t=t.replace("Lo que actives aquí determina lo que incluye su cuenta.","Activa sólo lo que este cliente usa y administra todo desde aquí.")
tpl.write_text(t,encoding="utf-8")

# Simplify client navigation to six clear destinations while preserving existing pages/routes.
base=Path("/app/app/templates/base.html")
b=base.read_text(encoding="utf-8")
old='''  const links=[
    ["/negocio","Inicio","⌂"],
    ["/negocio/operacion","Operación","⌁"],
    ["/negocio/lealtad","Clientes","♧"],
    ["/negocio/seguridad","Equipo","♧"],
    ["/negocio/marketing","Reseñas","☆"],
    ["/negocio/marca","Mi tarjeta","▭"],
    ["/negocio/configuracion","Mi plan","⚙"]
  ];'''
new='''  const links=[
    ["/negocio","Inicio","⌂"],
    ["/negocio/connect","Connect","◎"],
    ["/negocio/wallet","Wallet","▭"],
    ["/negocio/lealtad","Clientes","♧"],
    ["/negocio/marketing","Reseñas","☆"],
    ["/negocio/configuracion","Cuenta","⚙"]
  ];'''
if old in b:
    b=b.replace(old,new,1)
base.write_text(b,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "/* XP SIMPLE ACCESS V1 */" not in c:
    c+=r'''
/* XP SIMPLE ACCESS V1 */
.xp-create-access .xp-login-hint{margin-top:14px;padding:12px 14px;border-radius:12px;background:#f6f3ef;color:#544a43!important;font-size:.75rem}.xp-create-access form{grid-template-columns:repeat(2,1fr)}.xp-create-access form .btn{align-self:end}@media(max-width:720px){.xp-create-access form{grid-template-columns:1fr}}
'''
css.write_text(c,encoding="utf-8")
print("Simplified client access and unified account creation installed")
