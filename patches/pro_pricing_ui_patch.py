from pathlib import Path
t=Path("/app/app/templates/business/plan.html")
h=t.read_text()
old='''<strong>{% if k == "monthly" and price_ready.get(k) %}$499 MXN / mes{% else %}Precio por definir{% endif %}</strong><small>{{ n }}</small><button class="btn btn-secondary" {% if not price_ready.get(k) %}disabled{% endif %}>{% if price_ready.get(k) %}{% if test_billing %}Probar pago{% else %}Elegir {{ l|lower }}{% endif %}{% else %}Próximamente{% endif %}</button>'''
new='''<strong>{% if k == "monthly" %}$499 MXN / mes{% elif k == "semiannual" %}$2,495 MXN / 6 meses{% elif k == "annual" %}$4,990 MXN / año{% endif %}</strong><small>{% if k == "monthly" %}Pago mensual{% elif k == "semiannual" %}6 meses por el precio de 5 · Ahorras $499{% elif k == "annual" %}12 meses por el precio de 10 · Ahorras $998{% endif %}</small><button class="btn btn-secondary" {% if not price_ready.get(k) %}disabled{% endif %}>{% if price_ready.get(k) %}{% if test_billing %}Probar pago{% else %}Elegir {{ l|lower }}{% endif %}{% else %}Próximamente{% endif %}</button>'''
if old not in h: raise SystemExit("pricing UI anchor missing")
h=h.replace(old,new,1)
t.write_text(h)
print("Exponenta Pro monthly, semiannual and annual commercial prices added")
