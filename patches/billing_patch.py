from pathlib import Path

# Exponenta Billing V1
cfg=Path("/app/app/config.py"); s=cfg.read_text()
if "stripe_secret_key:" not in s:
 a='    @property\n    def is_production(self) -> bool:\n'
 x='''    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "").strip()
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
    stripe_price_monthly: str = os.getenv("STRIPE_PRICE_MONTHLY", "").strip()
    stripe_price_semiannual: str = os.getenv("STRIPE_PRICE_SEMIANNUAL", "").strip()
    stripe_price_annual: str = os.getenv("STRIPE_PRICE_ANNUAL", "").strip()

    @property
    def stripe_billing_ready(self) -> bool:
        return bool(self.stripe_secret_key and self.stripe_webhook_secret and self.stripe_price_monthly and self.stripe_price_semiannual and self.stripe_price_annual)

'''
 if a not in s: raise SystemExit("config anchor missing")
 cfg.write_text(s.replace(a,x+a,1))

r=Path("/app/requirements.txt"); s=r.read_text()
if "\nstripe" not in s.lower(): r.write_text(s+"\nstripe>=11.0.0\n")

m=Path("/app/app/models.py"); s=m.read_text()
if "class BillingAccount(Base):" not in s:
 s+='''

class BillingAccount(Base):
    __tablename__ = "billing_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), unique=True, index=True)
    access_type: Mapped[str] = mapped_column(String(32), default="trial", index=True)
    status: Mapped[str] = mapped_column(String(32), default="trialing", index=True)
    plan_name: Mapped[str] = mapped_column(String(120), default="Prueba gratuita")
    billing_interval: Mapped[Optional[str]] = mapped_column(String(24), nullable=True)
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    courtesy_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    special_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    grace_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    last_payment_failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
'''
 m.write_text(s)

v=Path("/app/alembic/versions/e5f8b21d731a_add_billing_accounts.py")
if not v.exists(): v.write_text('''from alembic import op
import sqlalchemy as sa
revision="e5f8b21d731a"; down_revision="c4e7a1b29d11"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("billing_accounts",
  sa.Column("id",sa.Integer(),primary_key=True),
  sa.Column("organization_id",sa.Integer(),sa.ForeignKey("organizations.id"),nullable=False,unique=True),
  sa.Column("access_type",sa.String(32),nullable=False,server_default="trial"),
  sa.Column("status",sa.String(32),nullable=False,server_default="trialing"),
  sa.Column("plan_name",sa.String(120),nullable=False,server_default="Prueba gratuita"),
  sa.Column("billing_interval",sa.String(24)),
  sa.Column("trial_ends_at",sa.DateTime(timezone=True)),sa.Column("courtesy_ends_at",sa.DateTime(timezone=True)),
  sa.Column("special_ends_at",sa.DateTime(timezone=True)),sa.Column("current_period_end",sa.DateTime(timezone=True)),
  sa.Column("grace_ends_at",sa.DateTime(timezone=True)),sa.Column("stripe_customer_id",sa.String(255)),
  sa.Column("stripe_subscription_id",sa.String(255),unique=True),sa.Column("cancel_at_period_end",sa.Boolean(),nullable=False,server_default=sa.false()),
  sa.Column("last_payment_failed_at",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
  sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
 op.create_index("ix_billing_org","billing_accounts",["organization_id"]); op.create_index("ix_billing_customer","billing_accounts",["stripe_customer_id"])
def downgrade():
 op.drop_index("ix_billing_customer",table_name="billing_accounts"); op.drop_index("ix_billing_org",table_name="billing_accounts"); op.drop_table("billing_accounts")
''')

p=Path("/app/app/main.py"); s=p.read_text()
if "EXPONENTA BILLING V1" not in s:
 if "import stripe\n" not in s: s=s.replace("import jwt\n","import jwt\nimport stripe\n",1)
 a="from app.models import (\n"
 if a not in s: raise SystemExit("models anchor missing")
 s=s.replace(a,a+"    BillingAccount,\n",1)
 a='@app.get("/negocio/lealtad", response_class=HTMLResponse)'
 if a not in s: raise SystemExit("route anchor missing")
 routes=r'''
# EXPONENTA BILLING V1
def get_billing(db,org):
 b=db.scalar(select(BillingAccount).where(BillingAccount.organization_id==org.id))
 if b:return b
 b=BillingAccount(organization_id=org.id,access_type="trial",status="trialing",plan_name="Prueba gratuita",trial_ends_at=datetime.now(timezone.utc)+timedelta(days=14))
 db.add(b);db.commit();db.refresh(b);return b

def billing_end(b):
 return b.trial_ends_at if b.access_type=="trial" else b.courtesy_ends_at if b.access_type=="courtesy" else (b.special_ends_at or b.current_period_end) if b.access_type=="special" else b.current_period_end

def billing_notice(b):
 end=billing_end(b);now=datetime.now(timezone.utc)
 if b.status in {"past_due","unpaid"}:return {"level":"danger","title":"Tu pago necesita atención","text":"Actualiza tu método de pago para evitar una interrupción."}
 if end:
  if end.tzinfo is None:end=end.replace(tzinfo=timezone.utc)
  d=(end-now).days
  if d<0:return {"level":"danger","title":"Tu acceso venció","text":"Elige un plan para continuar."}
  if d<=7:return {"level":"warning","title":f"Tu plan vence en {max(d,0)} días","text":"Te avisamos con tiempo para que puedas continuar sin interrupciones."}
 return {}

@app.get("/negocio/plan",response_class=HTMLResponse)
def business_plan(request:Request,db:Session=Depends(get_db)):
 user,org=business_admin_context(request,db);b=get_billing(db,org)
 return render(request,"business/plan.html",{"user":user,"organization":org,"billing":b,"billing_notice":billing_notice(b),"billing_ready":settings.stripe_billing_ready})

@app.post("/negocio/plan/checkout")
def billing_checkout(request:Request,interval:str=Form(...),csrf_token:str=Form(...),db:Session=Depends(get_db)):
 user,org=business_admin_context(request,db);verify_csrf(request,csrf_token)
 if interval not in {"monthly","semiannual","annual"}:raise HTTPException(422,"Periodo inválido")
 if not settings.stripe_billing_ready:return RedirectResponse("/negocio/plan?message=Pagos+automáticos+en+preparación",status_code=303)
 b=get_billing(db,org);stripe.api_key=settings.stripe_secret_key
 prices={"monthly":settings.stripe_price_monthly,"semiannual":settings.stripe_price_semiannual,"annual":settings.stripe_price_annual}
 kw={"mode":"subscription","line_items":[{"price":prices[interval],"quantity":1}],"success_url":settings.app_base_url+"/negocio/plan?message=Suscripción+activada","cancel_url":settings.app_base_url+"/negocio/plan","client_reference_id":str(org.id),"allow_promotion_codes":True,"metadata":{"organization_id":str(org.id),"interval":interval},"subscription_data":{"metadata":{"organization_id":str(org.id),"interval":interval}}}
 if b.stripe_customer_id:kw["customer"]=b.stripe_customer_id
 else:kw["customer_email"]=user.email
 session=stripe.checkout.Session.create(**kw);return RedirectResponse(session.url,status_code=303)

@app.post("/negocio/plan/portal")
def billing_portal(request:Request,csrf_token:str=Form(...),db:Session=Depends(get_db)):
 _,org=business_admin_context(request,db);verify_csrf(request,csrf_token);b=get_billing(db,org)
 if not settings.stripe_billing_ready or not b.stripe_customer_id:return RedirectResponse("/negocio/plan",status_code=303)
 stripe.api_key=settings.stripe_secret_key;p=stripe.billing_portal.Session.create(customer=b.stripe_customer_id,return_url=settings.app_base_url+"/negocio/plan")
 return RedirectResponse(p.url,status_code=303)

@app.post("/api/billing/stripe/webhook")
async def billing_webhook(request:Request,db:Session=Depends(get_db)):
 if not settings.stripe_webhook_secret:raise HTTPException(503,"Billing no configurado")
 try:e=stripe.Webhook.construct_event(await request.body(),request.headers.get("stripe-signature",""),settings.stripe_webhook_secret)
 except Exception:raise HTTPException(400,"Webhook inválido")
 o=e["data"]["object"];t=e["type"];b=None
 if t=="checkout.session.completed":
  oid=(o.get("metadata") or {}).get("organization_id") or o.get("client_reference_id")
  if oid:b=db.scalar(select(BillingAccount).where(BillingAccount.organization_id==int(oid)))
  if b:b.stripe_customer_id=o.get("customer");b.stripe_subscription_id=o.get("subscription");b.access_type="paid";b.status="active";b.plan_name="Suscripción Exponenta";b.billing_interval=(o.get("metadata") or {}).get("interval")
 elif t.startswith("customer.subscription."):
  md=o.get("metadata") or {};oid=md.get("organization_id")
  if oid:b=db.scalar(select(BillingAccount).where(BillingAccount.organization_id==int(oid)))
  if not b and o.get("customer"):b=db.scalar(select(BillingAccount).where(BillingAccount.stripe_customer_id==o.get("customer")))
  if b:
   b.access_type="paid";b.status="canceled" if t=="customer.subscription.deleted" else o.get("status",b.status);b.stripe_customer_id=o.get("customer");b.stripe_subscription_id=o.get("id");b.billing_interval=md.get("interval") or b.billing_interval;b.cancel_at_period_end=bool(o.get("cancel_at_period_end"))
   pe=o.get("current_period_end");b.current_period_end=datetime.fromtimestamp(pe,tz=timezone.utc) if pe else b.current_period_end
 elif t in {"invoice.payment_failed","invoice.paid"}:
  if o.get("customer"):b=db.scalar(select(BillingAccount).where(BillingAccount.stripe_customer_id==o.get("customer")))
  if b and t=="invoice.payment_failed":b.status="past_due";b.last_payment_failed_at=datetime.now(timezone.utc);b.grace_ends_at=datetime.now(timezone.utc)+timedelta(days=7)
  elif b:b.status="active";b.last_payment_failed_at=None;b.grace_ends_at=None
 if b:db.add(b);db.commit()
 return {"received":True}

'''
 p.write_text(s.replace(a,routes+a,1))

td=Path("/app/app/templates/business")
(td/"plan.html").write_text(r'''{% extends "base.html" %}{% block title %}Mi plan · Exponenta{% endblock %}{% block body %}
<section class="business-shell xp-plan-page"><header class="site-header"><a class="brand" href="/negocio">{{ organization.name }}</a></header>
<nav class="xp-business-nav"><a href="/negocio">Inicio</a><a href="/negocio/lealtad">Clientes</a><a href="/negocio/seguridad">Equipo</a><a href="/negocio/marketing">Reseñas</a><a class="active" href="/negocio/plan">Mi plan</a><a href="/negocio/configuracion">Más</a></nav>
<div class="xp-plan-hero"><span class="eyebrow">MI PLAN</span><h1>Tu acceso a Exponenta.</h1><p>Consulta tu modalidad, vigencia y administra tu forma de pago.</p></div>
{% if billing_notice %}<div class="xp-billing-notice {{ billing_notice.level }}"><strong>{{ billing_notice.title }}</strong><span>{{ billing_notice.text }}</span></div>{% endif %}
<section class="xp-current-plan"><div><span>PLAN ACTUAL</span><h2>{{ billing.plan_name }}</h2></div><div class="xp-plan-status">{{ billing.status|upper }}</div><div class="xp-plan-facts">
<p><small>Modalidad</small><strong>{% if billing.access_type=='trial' %}Prueba gratuita{% elif billing.access_type=='courtesy' %}Cortesía{% elif billing.access_type=='special' %}Plan especial{% else %}Suscripción pagada{% endif %}</strong></p>
<p><small>Renovación</small><strong>{% if billing.billing_interval=='monthly' %}Mensual{% elif billing.billing_interval=='semiannual' %}Semestral{% elif billing.billing_interval=='annual' %}Anual{% else %}—{% endif %}</strong></p>
<p><small>Vigencia</small><strong>{% if billing.access_type=='trial' and billing.trial_ends_at %}{{ billing.trial_ends_at.strftime('%d/%m/%Y') }}{% elif billing.access_type=='courtesy' and billing.courtesy_ends_at %}{{ billing.courtesy_ends_at.strftime('%d/%m/%Y') }}{% elif billing.access_type=='special' and billing.special_ends_at %}{{ billing.special_ends_at.strftime('%d/%m/%Y') }}{% elif billing.current_period_end %}{{ billing.current_period_end.strftime('%d/%m/%Y') }}{% else %}Sin fecha definida{% endif %}</strong></p></div></section>
<section class="xp-plan-options"><span class="eyebrow">ELIGE CÓMO PAGAR</span><h2>Mensual, semestral o anual.</h2><div class="xp-plan-grid">{% for k,l,n in [('monthly','Mensual','Flexibilidad mes a mes'),('semiannual','Semestral','Menos renovaciones'),('annual','Anual','Una renovación al año')] %}<form class="xp-plan-option" method="post" action="/negocio/plan/checkout"><input type="hidden" name="csrf_token" value="{{ csrf }}"><input type="hidden" name="interval" value="{{ k }}"><span>{{ l }}</span><strong>Precio por definir</strong><small>{{ n }}</small><button class="btn btn-secondary">{% if billing_ready %}Elegir {{ l|lower }}{% else %}Próximamente{% endif %}</button></form>{% endfor %}</div></section>
{% if billing.stripe_customer_id %}<form method="post" action="/negocio/plan/portal" class="xp-payment-manage"><input type="hidden" name="csrf_token" value="{{ csrf }}"><div><strong>Método de pago y facturación</strong><span>Actualiza tu tarjeta o administra tu suscripción.</span></div><button class="btn btn-secondary">Administrar pagos</button></form>{% endif %}
<div class="xp-plan-security"><strong>Tu tarjeta no se guarda en Exponenta.</strong><span>Los datos sensibles se procesan con el proveedor de pagos.</span></div></section>{% endblock %}''')

for f in td.glob("*.html"):
 s=f.read_text()
 if f.name!="plan.html" and 'href="/negocio/plan"' not in s:
  for old in ['<a href="/negocio/configuracion">Más</a>','<a href="/negocio/configuracion">Configuración</a>']:
   if old in s:s=s.replace(old,'<a href="/negocio/plan">Mi plan</a>'+old,1);break
  f.write_text(s)

css=Path("/app/app/static/app.css");s=css.read_text()
if "EXPONENTA BILLING V1" not in s:
 s+=r'''
/* EXPONENTA BILLING V1 */
.xp-plan-page{max-width:1120px;margin:auto}.xp-plan-hero{padding:24px 0 16px}.xp-plan-hero h1{font-size:clamp(2rem,6vw,3.4rem);letter-spacing:-.05em;margin:5px 0}.xp-current-plan,.xp-plan-options,.xp-payment-manage,.xp-plan-security{border:1px solid #e0d6cc;background:#fff;border-radius:22px;padding:20px;margin-top:14px}.xp-current-plan{display:grid;grid-template-columns:1fr auto;gap:18px}.xp-current-plan>div>span{font-size:.58rem;letter-spacing:.13em;font-weight:950;color:#8d5532}.xp-plan-status{border-radius:999px;background:#efe5dc;color:#6f4025;padding:8px 10px;font-size:.6rem;font-weight:950}.xp-plan-facts{grid-column:1/-1;display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.xp-plan-facts p{display:grid;gap:4px;margin:0;padding:12px;border-radius:14px;background:#f7f3ef}.xp-plan-facts small{font-size:.58rem;color:#857970}.xp-plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px}.xp-plan-option{display:grid;gap:8px;padding:15px;border:1px solid #e2d8cf;border-radius:17px;background:#faf7f3}.xp-plan-option span{font-size:.65rem;font-weight:950;color:#744429}.xp-plan-option small,.xp-payment-manage span,.xp-plan-security span{font-size:.64rem;color:#776d65}.xp-payment-manage{display:flex;justify-content:space-between;align-items:center}.xp-plan-security{display:flex;gap:8px;flex-wrap:wrap;background:#f2ebe4}.xp-billing-notice{display:grid;gap:3px;border-radius:16px;padding:13px 15px}.xp-billing-notice.warning{background:#f5ead9;color:#754d1e}.xp-billing-notice.danger{background:#f3dfdc;color:#7b332b}@media(max-width:720px){.xp-plan-facts,.xp-plan-grid{grid-template-columns:1fr}.xp-current-plan{grid-template-columns:1fr}.xp-payment-manage{flex-direction:column;align-items:flex-start}}
'''
 css.write_text(s)
print("Exponenta Billing V1 installed")
