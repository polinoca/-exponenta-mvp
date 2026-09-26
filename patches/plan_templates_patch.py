from pathlib import Path

# Exponenta Plan Templates + reseller-ready architecture.
m=Path("/app/app/models.py");s=m.read_text()
if "class PartnerAccount(Base):" not in s:
 s += '''

class PartnerAccount(Base):
    __tablename__ = "partner_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="reserved", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class PartnerOrganization(Base):
    __tablename__ = "partner_organizations"
    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partner_accounts.id"), index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
'''
 m.write_text(s)

v=Path("/app/alembic/versions/g7b013d9e315_add_partner_architecture.py")
if not v.exists():
 v.write_text('''from alembic import op
import sqlalchemy as sa
revision="g7b013d9e315"; down_revision="f6a912c8d204"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("partner_accounts",
  sa.Column("id",sa.Integer(),primary_key=True),
  sa.Column("name",sa.String(160),nullable=False),
  sa.Column("slug",sa.String(160),nullable=False,unique=True),
  sa.Column("status",sa.String(32),nullable=False,server_default="reserved"),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
  sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
 op.create_index("ix_partner_accounts_slug","partner_accounts",["slug"],unique=True)
 op.create_index("ix_partner_accounts_status","partner_accounts",["status"])
 op.create_table("partner_organizations",
  sa.Column("id",sa.Integer(),primary_key=True),
  sa.Column("partner_id",sa.Integer(),sa.ForeignKey("partner_accounts.id"),nullable=False),
  sa.Column("organization_id",sa.Integer(),sa.ForeignKey("organizations.id"),nullable=False,unique=True),
  sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
 op.create_index("ix_partner_org_partner","partner_organizations",["partner_id"])
 op.create_index("ix_partner_org_org","partner_organizations",["organization_id"],unique=True)
def downgrade():
 op.drop_index("ix_partner_org_org",table_name="partner_organizations");op.drop_index("ix_partner_org_partner",table_name="partner_organizations");op.drop_table("partner_organizations")
 op.drop_index("ix_partner_accounts_status",table_name="partner_accounts");op.drop_index("ix_partner_accounts_slug",table_name="partner_accounts");op.drop_table("partner_accounts")
''')

p=Path("/app/app/main.py");s=p.read_text()
if "EXPONENTA PLAN TEMPLATES V1" not in s:
 anchor="FEATURE_DEFAULTS.update({\"campaigns\":False,\"reservations\":False})"
 if anchor not in s: raise SystemExit("feature defaults anchor missing")
 add=r'''
# EXPONENTA PLAN TEMPLATES V1
PLAN_TEMPLATES = {
 "basic": {
  "label":"Básico",
  "description":"Lealtad, reseñas, equipo, clientes y QR/NFC.",
  "features":{"loyalty":True,"reviews":True,"wallet":False,"wallet_branding":False,"staff":True,"customer_data":True,"qr_nfc":True,"campaigns":False,"reservations":False},
 },
 "pro": {
  "label":"Pro",
  "description":"Todo lo esencial más Wallet y personalización de tarjeta.",
  "features":{"loyalty":True,"reviews":True,"wallet":True,"wallet_branding":True,"staff":True,"customer_data":True,"qr_nfc":True,"campaigns":False,"reservations":False},
 },
 "special": {
  "label":"Especial",
  "description":"Base amplia para acuerdos personalizados; después puedes ajustar cada función.",
  "features":{"loyalty":True,"reviews":True,"wallet":True,"wallet_branding":True,"staff":True,"customer_data":True,"qr_nfc":True,"campaigns":True,"reservations":False},
 },
 "courtesy": {
  "label":"Cortesía",
  "description":"Acceso completo a las funciones actuales para cuentas autorizadas por Exponenta.",
  "features":{"loyalty":True,"reviews":True,"wallet":True,"wallet_branding":True,"staff":True,"customer_data":True,"qr_nfc":True,"campaigns":True,"reservations":False},
 },
 "white_label": {
  "label":"Marca blanca",
  "description":"Todas las funciones y arquitectura preparada para identidad de distribuidor.",
  "features":{"loyalty":True,"reviews":True,"wallet":True,"wallet_branding":True,"staff":True,"customer_data":True,"qr_nfc":True,"campaigns":True,"reservations":True},
 },
}
'''
 s=s.replace(anchor,anchor+add,1)

 route_anchor='@app.post("/admin/control/{org_id}/feature/{feature_key}")'
 if route_anchor not in s: raise SystemExit("admin feature route missing")
 route=r'''@app.post("/admin/control/{org_id}/template/{template_key}")
def admin_apply_plan_template(org_id:int,template_key:str,request:Request,csrf_token:str=Form(...),db:Session=Depends(get_db)):
 control_superadmin(request,db);verify_csrf(request,csrf_token)
 template=PLAN_TEMPLATES.get(template_key)
 if not template: raise HTTPException(404,"Plantilla no encontrada")
 org=db.get(Organization,org_id)
 if not org: raise HTTPException(404,"Negocio no encontrado")
 current={r.feature_key:r for r in db.scalars(select(OrganizationFeature).where(OrganizationFeature.organization_id==org_id)).all()}
 for key,enabled in template["features"].items():
  row=current.get(key)
  if not row: row=OrganizationFeature(organization_id=org_id,feature_key=key)
  row.enabled=enabled;row.source=f"template:{template_key}";db.add(row)
 b=get_billing(db,org);b.plan_name=template["label"];db.add(b);db.commit()
 return RedirectResponse(f"/admin/control/{org_id}?template={template_key}",status_code=303)

'''
 s=s.replace(route_anchor,route+route_anchor,1)

 old='return render(request,"admin/control_business.html",{"user":user,"organization":org,"billing":b,"feature_catalog":FEATURE_CATALOG,"feature_states":states})'
 new='return render(request,"admin/control_business.html",{"user":user,"organization":org,"billing":b,"feature_catalog":FEATURE_CATALOG,"feature_states":states,"plan_templates":PLAN_TEMPLATES})'
 if old not in s: raise SystemExit("control business context missing")
 s=s.replace(old,new,1)
 p.write_text(s)

t=Path("/app/app/templates/admin/control_business.html");s=t.read_text()
if "PLANTILLAS DE PLAN" not in s:
 marker='<section class="xp-feature-control">'
 block=r'''<section class="xp-plan-templates"><span class="eyebrow">PLANTILLAS DE PLAN</span><h2>Configura el paquete en un toque.</h2><p>Aplica una base y después enciende o apaga cualquier función para este cliente.</p><div class="xp-template-grid">{% for key,item in plan_templates.items() %}<form method="post" action="/admin/control/{{ organization.id }}/template/{{ key }}"><input type="hidden" name="csrf_token" value="{{ csrf }}"><strong>{{ item.label }}</strong><span>{{ item.description }}</span><button class="btn btn-secondary">Aplicar {{ item.label }}</button></form>{% endfor %}</div></section>'''
 if marker not in s: raise SystemExit("feature section missing")
 s=s.replace(marker,block+marker,1)
 t.write_text(s)

css=Path("/app/app/static/app.css");s=css.read_text()
if "EXPONENTA PLAN TEMPLATES V1" not in s:
 s+=r'''
/* EXPONENTA PLAN TEMPLATES V1 */
.xp-plan-templates{background:#fff;border:1px solid #e2d7cd;border-radius:22px;padding:20px;margin-top:14px}.xp-plan-templates>p{color:#766b64;font-size:.72rem}.xp-template-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:14px}.xp-template-grid form{display:flex;flex-direction:column;gap:8px;padding:14px;border:1px solid #e7ddd4;border-radius:16px;background:#fbf8f5}.xp-template-grid strong{font-size:.85rem}.xp-template-grid span{font-size:.59rem;color:#776c65;line-height:1.4;min-height:50px}.xp-template-grid .btn{margin-top:auto;font-size:.58rem;padding:9px}@media(max-width:900px){.xp-template-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:520px){.xp-template-grid{grid-template-columns:1fr}}
'''
 css.write_text(s)
print("Exponenta Plan Templates V1 installed")
