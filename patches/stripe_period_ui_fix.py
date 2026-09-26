from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()

# Stripe Basil+ moved subscription billing periods to subscription items.
old='pe=o.get("current_period_end");b.current_period_end=datetime.fromtimestamp(pe,tz=timezone.utc) if pe else b.current_period_end'
new='''pe=o.get("current_period_end")
   if not pe:
    items=((o.get("items") or {}).get("data") or [])
    if items: pe=items[0].get("current_period_end")
   b.current_period_end=datetime.fromtimestamp(pe,tz=timezone.utc) if pe else b.current_period_end'''
if old not in s: raise SystemExit("period anchor missing")
s=s.replace(old,new,1)

# Backfill an already-paid account once from Stripe when the stored renewal date is missing.
old2='return render(request,"business/plan.html",{"user":user,"organization":org,"billing":b,"billing_notice":billing_notice(b),"billing_ready":any(price_ready.values()),"price_ready":price_ready,"test_billing":test_billing and allowed_checkout,"csrf":""})'
new2='''if b.access_type=="paid" and not b.current_period_end and b.stripe_subscription_id and settings.stripe_secret_key:
  try:
   stripe.api_key=settings.stripe_secret_key
   sub=stripe.Subscription.retrieve(b.stripe_subscription_id)
   if hasattr(sub,"to_dict_recursive"): sub=sub.to_dict_recursive()
   elif hasattr(sub,"to_dict"): sub=sub.to_dict()
   items=((sub.get("items") or {}).get("data") or [])
   pe=items[0].get("current_period_end") if items else sub.get("current_period_end")
   if pe:
    b.current_period_end=datetime.fromtimestamp(pe,tz=timezone.utc);db.add(b);db.commit();db.refresh(b)
  except Exception:
   pass
 return render(request,"business/plan.html",{"user":user,"organization":org,"billing":b,"billing_notice":billing_notice(b),"billing_ready":any(price_ready.values()),"price_ready":price_ready,"test_billing":test_billing and allowed_checkout,"csrf":""})'''
if old2 not in s: raise SystemExit("business plan render anchor missing")
s=s.replace(old2,new2,1)
p.write_text(s)

t=Path("/app/app/templates/business/plan.html")
h=t.read_text()
old3='<div class="xp-plan-status">{{ billing.status|upper }}</div>'
new3='''<div class="xp-plan-status">{% if billing.status == "trialing" %}PRUEBA ACTIVA{% elif billing.status == "paused" %}PAUSADA{% elif billing.status == "active" %}ACTIVA{% elif billing.status == "past_due" %}PAGO PENDIENTE{% elif billing.status == "canceled" %}CANCELADA{% else %}{{ billing.status|upper }}{% endif %}</div>'''
if old3 not in h: raise SystemExit("status UI anchor missing")
h=h.replace(old3,new3,1)
t.write_text(h)
print("Billing renewal date and Spanish status fixed for Stripe Basil+")
