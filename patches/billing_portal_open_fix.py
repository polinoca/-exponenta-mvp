from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()
anchor='@app.post("/api/billing/stripe/webhook")'
route='''@app.get("/negocio/plan/portal/open")
def billing_portal_open(request:Request,db:Session=Depends(get_db)):
 _,org=business_admin_context(request,db)
 b=get_billing(db,org)
 if not settings.stripe_secret_key or not b.stripe_customer_id:
  return RedirectResponse("/negocio/plan",status_code=303)
 stripe.api_key=settings.stripe_secret_key
 portal=stripe.billing_portal.Session.create(customer=b.stripe_customer_id,return_url=settings.app_base_url+"/negocio/plan")
 return RedirectResponse(portal.url,status_code=303)

'''
if route.strip() not in s:
 if anchor not in s: raise SystemExit("webhook anchor missing")
 s=s.replace(anchor,route+anchor,1)
p.write_text(s)

t=Path("/app/app/templates/business/plan.html")
h=t.read_text()
old='<form method="post" action="/negocio/plan/portal" class="xp-payment-manage"><input type="hidden" name="csrf_token" value="{{ csrf }}"><div><strong>Método de pago y facturación</strong><span>Actualiza tu tarjeta o administra tu suscripción.</span></div><button class="btn btn-secondary">Administrar pagos</button></form>'
new='<div class="xp-payment-manage"><div><strong>Método de pago y facturación</strong><span>Actualiza tu tarjeta o administra tu suscripción.</span></div><a class="btn btn-secondary" href="/negocio/plan/portal/open">Administrar pagos</a></div>'
if old not in h: raise SystemExit("payment manage form anchor missing")
h=h.replace(old,new,1)
t.write_text(h)
print("Manage payments now opens Stripe Billing Portal through authenticated navigation")
