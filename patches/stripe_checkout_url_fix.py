from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()
# Stripe requires ASCII/percent-encoded return URLs.
s=s.replace('settings.app_base_url+"/negocio/plan?message=Suscripción+activada"', 'settings.app_base_url+"/negocio/plan?message=Suscripcion+activada"')
# Avoid exposing a 405 page if a browser revisits the POST-only checkout URL.
anchor='@app.post("/negocio/plan/checkout")'
if anchor not in s: raise SystemExit("checkout route missing")
if '@app.get("/negocio/plan/checkout")' not in s:
    s=s.replace(anchor, '@app.get("/negocio/plan/checkout")\ndef billing_checkout_get():\n return RedirectResponse("/negocio/plan",status_code=303)\n\n'+anchor, 1)
p.write_text(s)
print("Stripe checkout return URL encoded safely; GET checkout redirects to plan")
