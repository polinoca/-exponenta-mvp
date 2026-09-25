from pathlib import Path

# Exponenta Control Center V1: entitlements, Wallet branding, white-label-ready data model.
m=Path("/app/app/models.py"); s=m.read_text()
if "from sqlalchemy import LargeBinary" not in s:
    s=s.replace("from __future__ import annotations\n","from __future__ import annotations\nfrom sqlalchemy import LargeBinary\n",1)
if "class OrganizationFeature(Base):" not in s:
    s += '''

class OrganizationFeature(Base):
    __tablename__ = "organization_features"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    feature_key: Mapped[str] = mapped_column(String(64), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    source: Mapped[str] = mapped_column(String(32), default="superadmin")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class WalletBranding(Base):
    __tablename__ = "wallet_branding"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), unique=True, index=True)
    background_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    hero_image: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    hero_image_mime: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    hero_image_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hero_image_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class WhiteLabelProfile(Base):
    __tablename__ = "white_label_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), nullable=True, unique=True)
    brand_name: Mapped[str] = mapped_column(String(120), default="Exponenta")
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    custom_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    support_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="reserved")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
'''
    m.write_text(s)

v=Path("/app/alembic/versions/f6a912c8d204_add_entitlements_wallet_branding.py")
if not v.exists():
    v.write_text('''from alembic import op
import sqlalchemy as sa
revision="f6a912c8d204"; down_revision="e5f8b21d731a"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("organization_features",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("organization_id",sa.Integer(),sa.ForeignKey("organizations.id"),nullable=False),sa.Column("feature_key",sa.String(64),nullable=False),sa.Column("enabled",sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column("source",sa.String(32),nullable=False,server_default="superadmin"),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),sa.UniqueConstraint("organization_id","feature_key",name="uq_org_feature"))
 op.create_index("ix_org_feature_org","organization_features",["organization_id"]);op.create_index("ix_org_feature_key","organization_features",["feature_key"])
 op.create_table("wallet_branding",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("organization_id",sa.Integer(),sa.ForeignKey("organizations.id"),nullable=False,unique=True),sa.Column("background_color",sa.String(16)),sa.Column("hero_image",sa.LargeBinary()),sa.Column("hero_image_mime",sa.String(64)),sa.Column("hero_image_width",sa.Integer()),sa.Column("hero_image_height",sa.Integer()),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
 op.create_index("ix_wallet_branding_org","wallet_branding",["organization_id"])
 op.create_table("white_label_profiles",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("organization_id",sa.Integer(),sa.ForeignKey("organizations.id"),unique=True),sa.Column("brand_name",sa.String(120),nullable=False,server_default="Exponenta"),sa.Column("logo_url",sa.String(500)),sa.Column("primary_color",sa.String(16)),sa.Column("custom_domain",sa.String(255),unique=True),sa.Column("support_email",sa.String(255)),sa.Column("status",sa.String(32),nullable=False,server_default="reserved"),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
def downgrade():
 op.drop_table("white_label_profiles");op.drop_index("ix_wallet_branding_org",table_name="wallet_branding");op.drop_table("wallet_branding");op.drop_index("ix_org_feature_key",table_name="organization_features");op.drop_index("ix_org_feature_org",table_name="organization_features");op.drop_table("organization_features")
''')

p=Path("/app/app/main.py"); s=p.read_text()
if "EXPONENTA CONTROL CENTER V1" not in s:
    anchor="from __future__ import annotations\n"
    extra='''from app.models import OrganizationFeature, WalletBranding, WhiteLabelProfile, User, Organization
from fastapi import UploadFile, File
from PIL import Image
import io
'''
    if extra not in s: s=s.replace(anchor,anchor+extra,1)
    route_anchor='@app.get("/negocio/lealtad", response_class=HTMLResponse)'
    if route_anchor not in s: raise SystemExit("control center route anchor missing")
    routes=r'''
# EXPONENTA CONTROL CENTER V1
FEATURE_CATALOG = [
 ("loyalty","Lealtad","Programa de visitas y recompensas"),
 ("reviews","Reseñas","Acceso y seguimiento de reseñas de Google"),
 ("wallet","Wallet","Tarjeta digital y acceso a Wallet"),
 ("wallet_branding","Personalización Wallet","Color e imagen de la tarjeta"),
 ("staff","Equipo","Usuarios para registrar visitas"),
 ("customer_data","Clientes y resultados","Directorio, progreso y métricas"),
 ("qr_nfc","QR y NFC","Puntos físicos y enlaces medibles"),
 ("campaigns","Campañas","Comunicaciones y reactivación"),
 ("reservations","Reservas","Módulo preparado para futuras reservas"),
]
FEATURE_DEFAULTS={k: True for k,_,_ in FEATURE_CATALOG}
FEATURE_DEFAULTS.update({"campaigns":False,"reservations":False})

def feature_states(db,org_id):
 rows=db.scalars(select(OrganizationFeature).where(OrganizationFeature.organization_id==org_id)).all()
 out=dict(FEATURE_DEFAULTS)
 for row in rows: out[row.feature_key]=bool(row.enabled)
 return out

def org_feature_on(db,org_id,key):
 return feature_states(db,org_id).get(key,False)

def require_org_feature(db,org,key):
 if not org_feature_on(db,org.id,key): raise HTTPException(403,"Esta función no está incluida en tu plan.")

def control_superadmin(request,db):
 uid=request.session.get("user_id") or request.session.get("uid")
 if not uid: raise HTTPException(401,"Inicia sesión")
 user=db.get(User,int(uid))
 role=str(getattr(getattr(user,"role",None),"value",getattr(user,"role",""))).lower() if user else ""
 if "superadmin" not in role: raise HTTPException(403,"Acceso restringido")
 return user

@app.get("/admin/control",response_class=HTMLResponse)
def admin_control(request:Request,db:Session=Depends(get_db)):
 user=control_superadmin(request,db);orgs=db.scalars(select(Organization).order_by(Organization.name)).all()
 return render(request,"admin/control.html",{"user":user,"organizations":orgs})

@app.get("/admin/control/{org_id}",response_class=HTMLResponse)
def admin_control_business(org_id:int,request:Request,db:Session=Depends(get_db)):
 user=control_superadmin(request,db);org=db.get(Organization,org_id)
 if not org: raise HTTPException(404,"Negocio no encontrado")
 b=get_billing(db,org);states=feature_states(db,org.id)
 return render(request,"admin/control_business.html",{"user":user,"organization":org,"billing":b,"feature_catalog":FEATURE_CATALOG,"feature_states":states})

@app.post("/admin/control/{org_id}/features")
def admin_control_features(org_id:int,request:Request,csrf_token:str=Form(...),db:Session=Depends(get_db)):
 control_superadmin(request,db);verify_csrf(request,csrf_token);org=db.get(Organization,org_id)
 if not org: raise HTTPException(404,"Negocio no encontrado")
 form={}
 # Starlette form is async; route converted below by using request state helper is unavailable.
 raise HTTPException(500,"feature form handler not initialized")

@app.post("/admin/control/{org_id}/feature/{feature_key}")
def admin_toggle_feature(org_id:int,feature_key:str,request:Request,enabled:str=Form("0"),csrf_token:str=Form(...),db:Session=Depends(get_db)):
 control_superadmin(request,db);verify_csrf(request,csrf_token)
 if feature_key not in FEATURE_DEFAULTS: raise HTTPException(404,"Función no encontrada")
 org=db.get(Organization,org_id)
 if not org: raise HTTPException(404,"Negocio no encontrado")
 row=db.scalar(select(OrganizationFeature).where(OrganizationFeature.organization_id==org_id,OrganizationFeature.feature_key==feature_key))
 if not row: row=OrganizationFeature(organization_id=org_id,feature_key=feature_key)
 row.enabled=enabled=="1";row.source="superadmin";db.add(row);db.commit()
 return RedirectResponse(f"/admin/control/{org_id}",status_code=303)

@app.post("/admin/control/{org_id}/access")
def admin_set_access(org_id:int,request:Request,access_type:str=Form(...),days:int=Form(14),plan_name:str=Form(""),csrf_token:str=Form(...),db:Session=Depends(get_db)):
 control_superadmin(request,db);verify_csrf(request,csrf_token);org=db.get(Organization,org_id)
 if not org: raise HTTPException(404,"Negocio no encontrado")
 if access_type not in {"trial","courtesy","special","paid"}: raise HTTPException(422,"Modalidad inválida")
 days=max(1,min(days,3650));b=get_billing(db,org);now=datetime.now(timezone.utc)
 b.access_type=access_type;b.status="active" if access_type!="trial" else "trialing"
 b.plan_name=(plan_name.strip()[:120] if plan_name.strip() else {"trial":"Prueba gratuita","courtesy":"Cortesía","special":"Plan especial","paid":"Suscripción pagada"}[access_type])
 if access_type=="trial": b.trial_ends_at=now+timedelta(days=days)
 elif access_type=="courtesy": b.courtesy_ends_at=now+timedelta(days=days)
 elif access_type=="special": b.special_ends_at=now+timedelta(days=days)
 elif access_type=="paid": b.current_period_end=now+timedelta(days=days)
 db.add(b);db.commit();return RedirectResponse(f"/admin/control/{org_id}",status_code=303)

def wallet_branding_for(db,org):
 w=db.scalar(select(WalletBranding).where(WalletBranding.organization_id==org.id))
 if not w:
  w=WalletBranding(organization_id=org.id,background_color=getattr(org,"brand_color",None) or "#6b3b22");db.add(w);db.commit();db.refresh(w)
 return w

@app.get("/negocio/wallet",response_class=HTMLResponse)
def business_wallet_branding(request:Request,db:Session=Depends(get_db)):
 user,org=business_admin_context(request,db);require_org_feature(db,org,"wallet")
 w=wallet_branding_for(db,org)
 return render(request,"business/wallet_branding.html",{"user":user,"organization":org,"wallet_branding":w,"wallet_customization":org_feature_on(db,org.id,"wallet_branding")})

@app.post("/negocio/wallet")
async def save_business_wallet(request:Request,background_color:str=Form("#6b3b22"),hero_image:UploadFile|None=File(None),csrf_token:str=Form(...),db:Session=Depends(get_db)):
 user,org=business_admin_context(request,db);verify_csrf(request,csrf_token);require_org_feature(db,org,"wallet");require_org_feature(db,org,"wallet_branding")
 if not background_color.startswith("#") or len(background_color)!=7: raise HTTPException(422,"Color inválido")
 w=wallet_branding_for(db,org);w.background_color=background_color
 if hero_image and hero_image.filename:
  if hero_image.content_type not in {"image/png","image/jpeg","image/webp"}: raise HTTPException(422,"Usa PNG, JPG o WEBP")
  data=await hero_image.read()
  if len(data)>3*1024*1024: raise HTTPException(422,"La imagen debe pesar máximo 3 MB")
  try:
   im=Image.open(io.BytesIO(data));im.verify();im=Image.open(io.BytesIO(data));width,height=im.size
  except Exception: raise HTTPException(422,"No pudimos leer esa imagen")
  ratio=width/height
  if width<800 or height<600 or not 1.15<=ratio<=1.40: raise HTTPException(422,"Usa una imagen horizontal de al menos 800 × 600 px, cercana a proporción 5:4")
  w.hero_image=data;w.hero_image_mime=hero_image.content_type;w.hero_image_width=width;w.hero_image_height=height
 db.add(w);db.commit();return RedirectResponse("/negocio/wallet?message=Tarjeta+actualizada",status_code=303)

@app.get("/branding/wallet/{org_id}/hero")
def wallet_hero_image(org_id:int,db:Session=Depends(get_db)):
 w=db.scalar(select(WalletBranding).where(WalletBranding.organization_id==org_id))
 if not w or not w.hero_image: raise HTTPException(404)
 return Response(content=w.hero_image,media_type=w.hero_image_mime or "image/png",headers={"Cache-Control":"public, max-age=3600"})

'''
    s=s.replace(route_anchor,routes+route_anchor,1)
    # Remove deliberately unused bulk endpoint before compile.
    start=s.find('@app.post("/admin/control/{org_id}/features")')
    end=s.find('@app.post("/admin/control/{org_id}/feature/{feature_key}")',start)
    if start>=0 and end>start: s=s[:start]+s[end:]
    # Enforce the clearest business modules at server route level wherever context is present.
    lines=s.splitlines(); out=[]; current_feature=None
    pathmap={"/negocio/marketing":"reviews","/negocio/seguridad":"staff","/negocio/lealtad":"loyalty"}
    for line in lines:
      stripped=line.strip()
      if stripped.startswith("@app.") and '("' in stripped:
       current_feature=None
       for prefix,key in pathmap.items():
        if f'("{prefix}' in stripped: current_feature=key;break
      out.append(line)
      if current_feature and "business_admin_context(request, db)" in line and "require_org_feature" not in line:
       indent=line[:len(line)-len(line.lstrip())]
       # infer org variable from common tuple assignment
       left=line.split("=")[0]
       orgvar="org" if "org" in left else "organization"
       out.append(indent+f'require_org_feature(db,{orgvar},"{current_feature}")')
    s="\n".join(out)+"\n"
    p.write_text(s)

# Admin pages.
ad=Path("/app/app/templates/admin");ad.mkdir(parents=True,exist_ok=True)
(ad/"control.html").write_text(r'''{% extends "base.html" %}{% block title %}Control · Exponenta{% endblock %}{% block body %}<main class="business-shell xp-control"><div class="xp-control-head"><div><span class="eyebrow">SUPERADMIN</span><h1>Control de negocios</h1><p>Planes, accesos y funciones por cliente.</p></div><a class="btn btn-secondary" href="/admin">Volver</a></div><div class="xp-control-list">{% for org in organizations %}<a href="/admin/control/{{ org.id }}"><div><strong>{{ org.name }}</strong><span>{{ org.slug }}</span></div><b>Administrar →</b></a>{% else %}<p>No hay negocios.</p>{% endfor %}</div></main>{% endblock %}''')
(ad/"control_business.html").write_text(r'''{% extends "base.html" %}{% block title %}{{ organization.name }} · Control{% endblock %}{% block body %}<main class="business-shell xp-control"><div class="xp-control-head"><div><span class="eyebrow">CONTROL DEL CLIENTE</span><h1>{{ organization.name }}</h1><p>Lo que actives aquí determina lo que incluye su cuenta.</p></div><a class="btn btn-secondary" href="/admin/control">Negocios</a></div>
<section class="xp-admin-plan"><div><span>ACCESO ACTUAL</span><h2>{{ billing.plan_name }}</h2><p>{{ billing.status }}</p></div><form method="post" action="/admin/control/{{ organization.id }}/access"><input type="hidden" name="csrf_token" value="{{ csrf }}"><label>Modalidad<select name="access_type"><option value="trial">Prueba gratuita</option><option value="courtesy">Cortesía</option><option value="special">Plan especial</option><option value="paid">Suscripción pagada</option></select></label><label>Días de acceso<input type="number" name="days" min="1" max="3650" value="14"></label><label>Nombre del plan<input name="plan_name" placeholder="Opcional"></label><button class="btn btn-primary">Guardar acceso</button></form></section>
<section class="xp-feature-control"><span class="eyebrow">FUNCIONES</span><h2>Enciende sólo lo que este cliente necesita.</h2><div class="xp-feature-grid">{% for key,label,desc in feature_catalog %}<article><div><strong>{{ label }}</strong><span>{{ desc }}</span></div><form method="post" action="/admin/control/{{ organization.id }}/feature/{{ key }}"><input type="hidden" name="csrf_token" value="{{ csrf }}"><input type="hidden" name="enabled" value="{{ '0' if feature_states[key] else '1' }}"><button class="xp-toggle {{ 'on' if feature_states[key] else 'off' }}" aria-label="Cambiar {{ label }}"><i></i><b>{{ 'Activo' if feature_states[key] else 'Apagado' }}</b></button></form></article>{% endfor %}</div></section>
<section class="xp-whitelabel-note"><span class="eyebrow">ARQUITECTURA</span><h2>Marca blanca preparada.</h2><p>La base de datos ya separa la identidad comercial de la operación. No está habilitada para clientes todavía.</p></section></main>{% endblock %}''')

bd=Path("/app/app/templates/business")
(bd/"wallet_branding.html").write_text(r'''{% extends "base.html" %}{% block title %}Mi tarjeta · Exponenta{% endblock %}{% block body %}<main class="business-shell xp-wallet-editor"><nav class="xp-business-nav"><a href="/negocio">Inicio</a><a href="/negocio/lealtad">Clientes</a><a href="/negocio/seguridad">Equipo</a><a href="/negocio/marketing">Reseñas</a><a class="active" href="/negocio/wallet">Mi tarjeta</a><a href="/negocio/plan">Mi plan</a><a href="/negocio/configuracion">Más</a></nav><div class="xp-wallet-editor-head"><span class="eyebrow">MI TARJETA</span><h1>Haz que se sienta como tu negocio.</h1><p>Elige el color y, si tu plan lo incluye, agrega una imagen. Exponenta adapta el resto.</p></div>
{% if wallet_customization %}<form class="xp-wallet-form" method="post" enctype="multipart/form-data"><input type="hidden" name="csrf_token" value="{{ csrf }}"><label>Color principal<input type="color" name="background_color" value="{{ wallet_branding.background_color or organization.brand_color or '#6b3b22' }}"></label><label>Imagen de tu tarjeta<input type="file" name="hero_image" accept="image/png,image/jpeg,image/webp"><small>PNG, JPG o WEBP · máximo 3 MB · mínimo 800 × 600 px · proporción cercana a 5:4. Evita texto dentro de la foto.</small></label><button class="btn btn-primary">Guardar diseño</button></form>{% else %}<div class="xp-locked"><strong>Personalización avanzada no incluida.</strong><span>Puedes seguir usando tu tarjeta con la identidad básica de tu negocio.</span></div>{% endif %}
<div class="xp-wallet-preview" style="--wallet-brand:{{ wallet_branding.background_color or organization.brand_color or '#6b3b22' }}">{% if wallet_branding.hero_image %}<img src="/branding/wallet/{{ organization.id }}/hero" alt="Imagen de {{ organization.name }}">{% endif %}<div><span>MI CLUB</span><h2>{{ organization.name }}</h2><p>6 de 9 visitas</p><div class="xp-preview-dots">{% for i in range(9) %}<i class="{{ 'done' if i < 6 else '' }}"></i>{% endfor %}</div></div></div><p class="xp-wallet-platform-note">En la tarjeta digital de Exponenta usamos esta imagen como portada. En Google Wallet se adapta al espacio de imagen permitido por la plataforma.</p></main>{% endblock %}''')

# Add Mi tarjeta navigation and plan feature summary.
for f in bd.glob("*.html"):
    t=f.read_text()
    if f.name!="wallet_branding.html" and 'href="/negocio/wallet"' not in t:
      needle='<a href="/negocio/plan">Mi plan</a>'
      if needle in t: t=t.replace(needle,'<a href="/negocio/wallet">Mi tarjeta</a>'+needle,1)
      f.write_text(t)

plan=bd/"plan.html"
if plan.exists():
 t=plan.read_text()
 if "LO QUE INCLUYE TU PLAN" not in t:
  insert='''<section class="xp-plan-includes"><span class="eyebrow">LO QUE INCLUYE TU PLAN</span><h2>Tus funciones activas.</h2><p>Estas son las herramientas disponibles actualmente en tu cuenta. Los cambios de plan los administra Exponenta.</p><div class="xp-plan-feature-list">{% for key,label,desc in feature_catalog %}<div class="{{ 'enabled' if feature_states[key] else 'disabled' }}"><i>{{ '✓' if feature_states[key] else '—' }}</i><span><strong>{{ label }}</strong><small>{{ 'Incluido' if feature_states[key] else 'No incluido' }}</small></span></div>{% endfor %}</div></section>'''
  t=t.replace('<section class="xp-plan-options">',insert+'<section class="xp-plan-options">',1)
  plan.write_text(t)

# Extend business_plan context added by Billing V1.
s=p.read_text()
old='"billing_ready":settings.stripe_billing_ready})'
if old in s and '"feature_catalog":FEATURE_CATALOG' not in s[s.find('def business_plan'):s.find('def business_plan')+1000]:
 s=s.replace(old,'billing_ready":settings.stripe_billing_ready,"feature_catalog":FEATURE_CATALOG,"feature_states":feature_states(db,org.id)})',1)
 p.write_text(s)

# Add Superadmin control link without depending on exact admin layout.
dash=ad/"dashboard.html"
if dash.exists():
 t=dash.read_text()
 if 'href="/admin/control"' not in t:
  pos=t.find("</header>")
  link='<a class="btn btn-secondary" href="/admin/control">Control de clientes</a>'
  if pos>=0:t=t[:pos]+link+t[pos:]
  else:t=link+t
  dash.write_text(t)

css=Path("/app/app/static/app.css");s=css.read_text()
if "EXPONENTA CONTROL CENTER V1" not in s:
 s+=r'''
/* EXPONENTA CONTROL CENTER V1 */
.xp-control,.xp-wallet-editor{max-width:1100px;margin:auto}.xp-control-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;padding:25px 0}.xp-control-head h1,.xp-wallet-editor-head h1{font-size:clamp(2rem,6vw,3.4rem);letter-spacing:-.05em;margin:5px 0}.xp-control-list{display:grid;gap:8px}.xp-control-list>a{display:flex;justify-content:space-between;align-items:center;padding:16px 18px;border:1px solid #e3d8ce;background:#fff;border-radius:16px;text-decoration:none;color:#2b211b}.xp-control-list span{display:block;font-size:.65rem;color:#85786f}.xp-admin-plan,.xp-feature-control,.xp-whitelabel-note,.xp-wallet-form,.xp-locked,.xp-plan-includes{background:#fff;border:1px solid #e2d7cd;border-radius:22px;padding:20px;margin-top:14px}.xp-admin-plan{display:grid;grid-template-columns:.8fr 1.2fr;gap:22px}.xp-admin-plan form{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.xp-admin-plan label,.xp-wallet-form label{display:grid;gap:6px;font-size:.62rem;font-weight:900}.xp-admin-plan input,.xp-admin-plan select,.xp-wallet-form input[type=file]{min-height:42px;border:1px solid #d9cec5;border-radius:11px;padding:8px;background:#faf7f4}.xp-feature-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:14px}.xp-feature-grid article{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:14px;border:1px solid #e6ddd5;border-radius:15px}.xp-feature-grid article span{display:block;font-size:.61rem;color:#7e746d;margin-top:3px}.xp-toggle{border:0;border-radius:999px;padding:5px 8px 5px 5px;display:flex;align-items:center;gap:6px;cursor:pointer}.xp-toggle i{width:19px;height:19px;border-radius:50%;background:#fff}.xp-toggle b{font-size:.55rem}.xp-toggle.on{background:#6b3b22;color:#fff}.xp-toggle.off{background:#e8e1db;color:#6d625b}.xp-wallet-editor-head{padding:24px 0 8px}.xp-wallet-form{display:grid;gap:16px}.xp-wallet-form input[type=color]{width:100%;height:48px;border:0;border-radius:12px;background:none}.xp-wallet-form small,.xp-wallet-platform-note{font-size:.63rem;color:#766b64}.xp-wallet-preview{position:relative;overflow:hidden;margin-top:14px;border-radius:25px;background:var(--wallet-brand);color:#fff;min-height:270px;box-shadow:0 18px 45px rgba(48,31,21,.15)}.xp-wallet-preview>img{width:100%;height:150px;object-fit:cover;display:block}.xp-wallet-preview>div{padding:20px}.xp-wallet-preview h2{font-size:1.8rem;margin:4px 0}.xp-preview-dots{display:flex;gap:6px;margin-top:15px}.xp-preview-dots i{width:18px;height:18px;border-radius:50%;border:1px solid rgba(255,255,255,.6)}.xp-preview-dots i.done{background:#fff}.xp-plan-feature-list{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:14px}.xp-plan-feature-list>div{display:flex;gap:9px;padding:11px;border-radius:13px;background:#f7f3ef}.xp-plan-feature-list>div.disabled{opacity:.48}.xp-plan-feature-list i{font-style:normal;font-weight:950}.xp-plan-feature-list small{display:block;font-size:.58rem;color:#776c65}@media(max-width:720px){.xp-control-head{flex-direction:column}.xp-admin-plan,.xp-feature-grid,.xp-plan-feature-list{grid-template-columns:1fr}.xp-admin-plan form{grid-template-columns:1fr}}
'''
 css.write_text(s)
print("Exponenta Control Center V1 installed")
