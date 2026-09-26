from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()
old='b.access_type="paid";b.status="canceled" if t=="customer.subscription.deleted" else o.get("status",b.status);b.stripe_customer_id=o.get("customer");b.stripe_subscription_id=o.get("id")'
new='b.access_type="paid";b.status=("paused" if t=="customer.subscription.paused" else ("canceled" if t=="customer.subscription.deleted" else o.get("status",b.status)));b.stripe_customer_id=o.get("customer");b.stripe_subscription_id=o.get("id")'
if old in s:
 s=s.replace(old,new,1)
elif 'customer.subscription.paused' not in s:
 raise SystemExit("subscription status anchor missing")
p.write_text(s)
print("Stripe paused subscription state enabled")
