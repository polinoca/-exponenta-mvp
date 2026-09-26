from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()
old='return render(request,"business/plan.html",{"user":user,"organization":org,"billing":b,"billing_notice":billing_notice(b),"billing_ready":settings.stripe_billing_ready})'
new='''test_billing=bool(settings.stripe_secret_key.startswith("sk_test_"))
 allowed_checkout=(not test_billing) or getattr(org,"slug","")=="linopo"
 price_ready={"monthly":bool(settings.stripe_secret_key and settings.stripe_price_monthly and allowed_checkout),"semiannual":bool(settings.stripe_secret_key and settings.stripe_price_semiannual and allowed_checkout),"annual":bool(settings.stripe_secret_key and settings.stripe_price_annual and allowed_checkout)}
 csrf_value=request.session.get("csrf_token") or request.session.get("csrf") or ""\n return render(request,"business/plan.html",{"user":user,"organization":org,"billing":b,"billing_notice":billing_notice(b),"billing_ready":any(price_ready.values()),"price_ready":price_ready,"test_billing":test_billing and allowed_checkout,"csrf":csrf_value})'''
if old not in s: raise SystemExit("plan context anchor missing")
s=s.replace(old,new,1)
old2='if not settings.stripe_billing_ready:return RedirectResponse("/negocio/plan?message=Pagos+automáticos+en+preparación",status_code=303)\n b=get_billing(db,org);stripe.api_key=settings.stripe_secret_key\n prices={"monthly":settings.stripe_price_monthly,"semiannual":settings.stripe_price_semiannual,"annual":settings.stripe_price_annual}'
new2='''prices={"monthly":settings.stripe_price_monthly,"semiannual":settings.stripe_price_semiannual,"annual":settings.stripe_price_annual}
 if settings.stripe_secret_key.startswith("sk_test_") and getattr(org,"slug","")!="linopo":return RedirectResponse("/negocio/plan?message=Pagos+de+prueba+restringidos",status_code=303)
 if not settings.stripe_secret_key or not prices.get(interval):return RedirectResponse("/negocio/plan?message=Este+periodo+aún+no+está+disponible",status_code=303)
 b=get_billing(db,org);stripe.api_key=settings.stripe_secret_key'''
if old2 not in s: raise SystemExit("checkout anchor missing")
s=s.replace(old2,new2,1)
old3='if not settings.stripe_billing_ready or not b.stripe_customer_id:return RedirectResponse("/negocio/plan",status_code=303)'
new3='if not settings.stripe_secret_key or not b.stripe_customer_id:return RedirectResponse("/negocio/plan",status_code=303)'
if old3 in s:s=s.replace(old3,new3,1)
p.write_text(s)

t=Path("/app/app/templates/business/plan.html")
h=t.read_text()
old4='''<strong>Precio por definir</strong><small>{{ n }}</small><button class="btn btn-secondary">{% if billing_ready %}Elegir {{ l|lower }}{% else %}Próximamente{% endif %}</button>'''
new4='''<strong>{% if k == "monthly" and price_ready.get(k) %}$499 MXN / mes{% else %}Precio por definir{% endif %}</strong><small>{{ n }}</small><button class="btn btn-secondary" {% if not price_ready.get(k) %}disabled{% endif %}>{% if price_ready.get(k) %}{% if test_billing %}Probar pago{% else %}Elegir {{ l|lower }}{% endif %}{% else %}Próximamente{% endif %}</button>'''
if old4 not in h: raise SystemExit("template pricing anchor missing")
h=h.replace(old4,new4,1)
h=h.replace('<span class="xp-status">{{ billing.status|upper }}</span>','<span class="xp-status">{% if billing.status == "trialing" %}PRUEBA ACTIVA{% elif billing.status == "paused" %}PAUSADA{% elif billing.status == "active" %}ACTIVA{% elif billing.status == "past_due" %}PAGO PENDIENTE{% elif billing.status == "canceled" %}CANCELADA{% else %}{{ billing.status|upper }}{% endif %}</span>')
t.write_text(h)
print("Per-interval Stripe checkout and safe test UI enabled")
