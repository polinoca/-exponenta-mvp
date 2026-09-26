from pathlib import Path
import re

p=Path("/app/app/main.py")
s=p.read_text()

start=s.find('@app.post("/negocio/plan/checkout")')
end=s.find('@app.post("/negocio/plan/portal")', start)
if start < 0 or end < 0:
    raise SystemExit("billing checkout route anchors missing")

route=r'''@app.post("/negocio/plan/checkout")
def billing_checkout(request:Request,interval:str=Form(...),csrf_token:str=Form(""),db:Session=Depends(get_db)):
 user,org=business_admin_context(request,db)
 origin=(request.headers.get("origin") or "").rstrip("/")
 referer=request.headers.get("referer") or ""
 base=settings.app_base_url.rstrip("/")
 if origin and origin!=base: raise HTTPException(403,"Solicitud no válida")
 if not origin and not referer.startswith(base+"/"): raise HTTPException(403,"Solicitud no válida")
 if interval not in {"monthly","annual"}: raise HTTPException(422,"Periodo inválido")
 prices={"monthly":settings.stripe_price_monthly,"annual":settings.stripe_price_annual}
 if settings.stripe_secret_key.startswith("sk_test_") and getattr(org,"slug","")!="linopo":
  return RedirectResponse("/negocio/plan?message=Pagos+de+prueba+restringidos",status_code=303)
 if not settings.stripe_secret_key or not prices.get(interval):
  return RedirectResponse("/negocio/plan?message=Este+periodo+aun+no+esta+disponible",status_code=303)
 b=get_billing(db,org);stripe.api_key=settings.stripe_secret_key

 # Never create a second subscription for a business that already has one.
 # Replace the existing subscription item instead. Stripe prorates the unused
 # monthly time, charges the new annual interval immediately, and resets the
 # billing date when the interval changes.
 if b.stripe_subscription_id and b.status in {"active","trialing","past_due"}:
  if b.billing_interval==interval and b.status=="active":
   return RedirectResponse("/negocio/plan?message=Este+es+tu+plan+actual",status_code=303)
  try:
   sub=stripe.Subscription.retrieve(b.stripe_subscription_id,expand=["latest_invoice"])
   sub=sub.to_dict_recursive() if hasattr(sub,"to_dict_recursive") else sub.to_dict() if hasattr(sub,"to_dict") else sub
   items=((sub.get("items") or {}).get("data") or [])
   if not items:
    return RedirectResponse("/negocio/plan?message=No+se+pudo+identificar+tu+suscripcion",status_code=303)
   updated=stripe.Subscription.modify(
    b.stripe_subscription_id,
    items=[{"id":items[0]["id"],"price":prices[interval],"quantity":1}],
    proration_behavior="always_invoice",
    metadata={"organization_id":str(org.id),"interval":interval},
    cancel_at_period_end=False,
   )
   updated=updated.to_dict_recursive() if hasattr(updated,"to_dict_recursive") else updated.to_dict() if hasattr(updated,"to_dict") else updated
   pending=updated.get("pending_update")
   invoice=updated.get("latest_invoice")
   if pending:
    if isinstance(invoice,str):
     invoice=stripe.Invoice.retrieve(invoice)
     invoice=invoice.to_dict_recursive() if hasattr(invoice,"to_dict_recursive") else invoice.to_dict() if hasattr(invoice,"to_dict") else invoice
    pay_url=(invoice or {}).get("hosted_invoice_url") if invoice else None
    if pay_url:
     return RedirectResponse(pay_url,status_code=303)
    return RedirectResponse("/negocio/plan?message=El+cambio+esta+pendiente+de+pago",status_code=303)
   b.billing_interval=interval
   b.status=updated.get("status") or b.status
   b.cancel_at_period_end=bool(updated.get("cancel_at_period_end"))
   item_data=((updated.get("items") or {}).get("data") or [])
   pe=(item_data[0].get("current_period_end") if item_data else None) or updated.get("current_period_end")
   if pe:
    b.current_period_end=datetime.fromtimestamp(pe,tz=timezone.utc)
   db.add(b);db.commit()
   return RedirectResponse("/negocio/plan?message=Plan+actualizado+correctamente",status_code=303)
  except Exception as e:
   print("STRIPE_PLAN_SWITCH_ERROR",type(e).__name__,str(e),flush=True)
   return RedirectResponse("/negocio/plan?message=No+se+pudo+actualizar+el+plan.+Intenta+de+nuevo",status_code=303)

 kw={"mode":"subscription","line_items":[{"price":prices[interval],"quantity":1}],"success_url":settings.app_base_url+"/negocio/plan?message=Suscripcion+activada","cancel_url":settings.app_base_url+"/negocio/plan","client_reference_id":str(org.id),"allow_promotion_codes":True,"metadata":{"organization_id":str(org.id),"interval":interval},"subscription_data":{"metadata":{"organization_id":str(org.id),"interval":interval}}}
 if b.stripe_customer_id:kw["customer"]=b.stripe_customer_id
 else:kw["customer_email"]=user.email
 session=stripe.checkout.Session.create(**kw)
 return RedirectResponse(session.url,status_code=303)

'''
s=s[:start]+route+s[end:]
p.write_text(s)

t=Path("/app/app/templates/business/plan.html")
h=t.read_text()
old='''<button class="btn btn-secondary" {% if not price_ready.get(k) %}disabled{% endif %}>{% if price_ready.get(k) %}{% if test_billing %}Probar pago{% else %}Elegir {{ l|lower }}{% endif %}{% else %}Próximamente{% endif %}</button>'''
new='''<button class="btn btn-secondary" {% if billing.access_type == "paid" and billing.stripe_subscription_id and not (billing.status == "active" and billing.billing_interval == k) %}onclick="return confirm('Vas a cambiar la periodicidad de tu suscripción. Stripe aplicará el ajuste proporcional del periodo actual y cobrará automáticamente al método de pago guardado. ¿Confirmas el cambio?')"{% endif %} {% if not price_ready.get(k) or (billing.access_type == "paid" and billing.status == "active" and billing.billing_interval == k) %}disabled{% endif %}>{% if billing.access_type == "paid" and billing.status == "active" and billing.billing_interval == k %}Plan actual{% elif price_ready.get(k) %}{% if billing.access_type == "paid" and billing.stripe_subscription_id %}Cambiar a {{ l|lower }}{% elif test_billing %}Probar pago{% else %}Elegir {{ l|lower }}{% endif %}{% else %}Próximamente{% endif %}</button>'''
if old not in h:
    raise SystemExit("billing plan button anchor missing")
h=h.replace(old,new,1)
t.write_text(h)
print("Safe subscription plan switching enabled without duplicate subscriptions")
