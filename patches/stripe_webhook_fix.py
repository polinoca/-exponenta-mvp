from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()
old='o=e["data"]["object"];t=e["type"];b=None'
new='''o=e["data"]["object"]
 if hasattr(o,"to_dict_recursive"): o=o.to_dict_recursive()
 elif hasattr(o,"to_dict"): o=o.to_dict()
 t=e["type"];b=None'''
if old not in s: raise SystemExit("webhook object anchor missing")
s=s.replace(old,new,1)
old2='if b:b.stripe_customer_id=o.get("customer");b.stripe_subscription_id=o.get("subscription");b.access_type="paid";b.status="active";b.plan_name="Suscripción Exponenta";b.billing_interval=(o.get("metadata") or {}).get("interval")'
new2='''if b:
   b.stripe_customer_id=o.get("customer");b.stripe_subscription_id=o.get("subscription");b.access_type="paid";b.status="active";b.plan_name="Pro";b.billing_interval=(o.get("metadata") or {}).get("interval")
   template=PLAN_TEMPLATES.get("pro")
   if template:
    current={r.feature_key:r for r in db.scalars(select(OrganizationFeature).where(OrganizationFeature.organization_id==b.organization_id)).all()}
    for key,enabled in template["features"].items():
     row=current.get(key)
     if not row: row=OrganizationFeature(organization_id=b.organization_id,feature_key=key)
     row.enabled=enabled;row.source="billing:pro";db.add(row)'''
if old2 not in s: raise SystemExit("checkout completion anchor missing")
s=s.replace(old2,new2,1)
p.write_text(s)
print("Stripe webhook objects normalized; successful checkout activates Pro entitlements")
