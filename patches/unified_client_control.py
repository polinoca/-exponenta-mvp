from pathlib import Path

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")

# 1) Add Connect as a first-class entitlement, disabled by default.
if '("connect","Connect"' not in s:
    s=s.replace(
        '("reviews","Reseñas","Acceso y seguimiento de reseñas de Google"),',
        '("reviews","Reseñas","Acceso y seguimiento de reseñas de Google"),\n ("connect","Connect","Hub dinámico: reseñas, redes, contacto, QR y NFC"),',
        1
    )
s=s.replace(
    'FEATURE_DEFAULTS.update({"campaigns":False,"reservations":False})',
    'FEATURE_DEFAULTS.update({"campaigns":False,"reservations":False,"connect":False})'
)

# 2) Gate the business Connect module by entitlement.
needle='''def business_connect_page(request: Request, db: Session = Depends(get_db)):
    current_user = require_user(request, db)
    if current_user.role == Role.SUPERADMIN:
        return RedirectResponse("/admin/connect", status_code=303)
    user, org = business_admin_context(request, db)'''
replacement='''def business_connect_page(request: Request, db: Session = Depends(get_db)):
    current_user = require_user(request, db)
    if current_user.role == Role.SUPERADMIN:
        return RedirectResponse("/admin/connect", status_code=303)
    user, org = business_admin_context(request, db)
    require_org_feature(db, org, "connect")'''
if needle in s:
    s=s.replace(needle,replacement,1)

needle2='''    user, org = business_admin_context(request, db)
    verify_csrf(request, csrf_token)
    xp_connect_ensure_org_column(db)'''
replacement2='''    user, org = business_admin_context(request, db)
    require_org_feature(db, org, "connect")
    verify_csrf(request, csrf_token)
    xp_connect_ensure_org_column(db)'''
# Only replace first occurrence inside business_connect_save area if present.
idx=s.find('async def business_connect_save(')
if idx>=0:
    tail=s[idx:]
    if needle2 in tail:
        tail=tail.replace(needle2,replacement2,1)
        s=s[:idx]+tail

# 3) Enrich the existing client control route with Connect data.
route_start=s.find('def admin_control_business(')
route_end=s.find('\n\n@app.', route_start)
if route_start>=0 and route_end>route_start:
    block=s[route_start:route_end]
    if 'connect_profile=' not in block:
        marker='b=get_billing(db,org);states=feature_states(db,org.id)'
        enrich='''b=get_billing(db,org);states=feature_states(db,org.id)
 xp_connect_ensure_org_column(db)
 connect_profile=db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE organization_id=:org_id OR slug=:slug ORDER BY CASE WHEN organization_id=:org_id THEN 0 ELSE 1 END LIMIT 1"),{"org_id":org.id,"slug":org.slug}).mappings().first()
 if connect_profile and not connect_profile.get("organization_id"):
  db.execute(xp_sql_text("UPDATE exponenta_connect_profiles SET organization_id=:org_id WHERE slug=:slug"),{"org_id":org.id,"slug":connect_profile["slug"]});db.commit()
  connect_profile=db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug"),{"slug":connect_profile["slug"]}).mappings().first()
 connect_code=None
 if connect_profile:
  connect_code=db.execute(xp_sql_text("SELECT * FROM exponenta_connect_codes WHERE assigned_slug=:slug ORDER BY code LIMIT 1"),{"slug":connect_profile["slug"]}).mappings().first()'''
        if marker in block:
            block=block.replace(marker,enrich,1)
        # Inject context into render dict irrespective of later plan-template patches.
        close='})'
        pos=block.rfind(close)
        if pos>=0:
            before=block[:pos]
            if '"connect_profile":connect_profile' not in before:
                before=before.rstrip()
                if before.endswith('}'): pass
                # append before final dictionary close pattern
                last_brace=before.rfind('}')
                if last_brace>=0:
                    prefix=before[:last_brace]
                    if not prefix.rstrip().endswith(','):
                        prefix=prefix.rstrip()+','
                    before=prefix+' "connect_profile":connect_profile,"connect_code":connect_code'+before[last_brace:]
            block=before+block[pos:]
        s=s[:route_start]+block+s[route_end:]

p.write_text(s,encoding="utf-8")

# 4) Add unified Connect card to the existing customer-control template.
t=Path("/app/app/templates/admin/control_business.html")
html=t.read_text(encoding="utf-8")
if "EXPONENTA UNIFIED CONNECT CONTROL V1" not in html:
    anchor='<section class="xp-feature-control">'
    connect_block=r'''<!-- EXPONENTA UNIFIED CONNECT CONTROL V1 -->
<section class="xp-client-connect">
  <div class="xp-client-connect-head">
    <div><span class="eyebrow">EXPONENTA CONNECT</span><h2>Hub dinámico del cliente</h2><p>Administra el perfil, el QR dinámico y el acceso del negocio desde esta misma cuenta.</p></div>
    <span class="xp-product-status {{ 'on' if feature_states.get('connect') else 'off' }}">{{ 'ACTIVO' if feature_states.get('connect') else 'APAGADO' }}</span>
  </div>
  <div class="xp-client-connect-grid">
    <article>
      <small>PERFIL</small>
      {% if connect_profile %}
        <strong>{{ connect_profile.name }}</strong>
        <span>/connect/{{ connect_profile.slug }}</span>
        <div class="xp-client-actions">
          <a class="btn btn-secondary" href="/connect/{{ connect_profile.slug }}" target="_blank">Ver hub</a>
          <a class="btn btn-secondary" href="/admin/connect/{{ connect_profile.slug }}/editar">Editar</a>
        </div>
      {% else %}
        <strong>Sin perfil Connect</strong>
        <span>Créalo y asígnalo a este negocio.</span>
        <a class="btn btn-secondary" href="/admin/connect/nuevo">Crear Connect</a>
      {% endif %}
    </article>
    <article>
      <small>QR DINÁMICO</small>
      {% if connect_code %}
        <strong>{{ connect_code.code }}</strong>
        <span>Asignado a {{ connect_profile.slug }}</span>
        <div class="xp-client-actions">
          <a class="btn btn-secondary" href="/admin/connect/{{ connect_profile.slug }}/material">QR / banner</a>
        </div>
      {% elif connect_profile %}
        <strong>Sin código físico</strong>
        <span>Asigna un código Connect al perfil.</span>
        <a class="btn btn-secondary" href="/admin/connect">Asignar QR</a>
      {% else %}
        <strong>Sin QR</strong><span>Primero crea el perfil Connect.</span>
      {% endif %}
    </article>
    <article>
      <small>USUARIOS DEL NEGOCIO</small>
      {% for account in organization_users %}
        <strong>{{ account.email }}</strong>
        <span>{{ account.role.value if account.role and account.role.value else account.role }} · {{ 'Activo' if account.active else 'Inactivo' }}</span>
      {% else %}
        <strong>Sin usuarios</strong>
      {% endfor %}
      <span class="xp-note">Estos mismos accesos sirven para los módulos que tenga activos el cliente.</span>
    </article>
  </div>
</section>
'''
    if anchor in html:
        html=html.replace(anchor,connect_block+anchor,1)
    else:
        end='{% endblock %}'
        html=html.replace(end,connect_block+end,1)
t.write_text(html,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "EXPONENTA UNIFIED CONNECT CONTROL V1" not in c:
    c+=r'''
/* EXPONENTA UNIFIED CONNECT CONTROL V1 */
.xp-client-connect{background:#fff;border:1px solid #e2d7cd;border-radius:22px;padding:20px;margin-top:14px}.xp-client-connect-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}.xp-client-connect-head h2{margin:5px 0}.xp-client-connect-head p{margin:0;color:#70655e}.xp-product-status{font-size:.65rem;font-weight:900;padding:8px 11px;border-radius:999px}.xp-product-status.on{background:#e8f7ed;color:#14733b}.xp-product-status.off{background:#fdebea;color:#a12820}.xp-client-connect-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:18px}.xp-client-connect-grid article{border:1px solid #e8ded6;border-radius:16px;padding:15px;display:flex;flex-direction:column;gap:7px;min-width:0}.xp-client-connect-grid article small{font-size:.58rem;letter-spacing:.12em;font-weight:900;color:#8b7d73}.xp-client-connect-grid article strong{font-size:1rem;overflow-wrap:anywhere}.xp-client-connect-grid article span{font-size:.75rem;color:#746960;overflow-wrap:anywhere}.xp-client-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:7px}.xp-note{margin-top:7px!important;font-size:.68rem!important}@media(max-width:800px){.xp-client-connect-grid{grid-template-columns:1fr}.xp-client-connect-head{flex-direction:column}}
'''
css.write_text(c,encoding="utf-8")
print("Unified client control with Connect installed")
