from pathlib import Path
t=Path("/app/app/templates/business/plan.html")
h=t.read_text()

# Commercial offer: keep the decision simple — monthly or annual only.
h=h.replace(
    '<h2>Mensual, semestral o anual.</h2><div class="xp-plan-grid">{% for k,l,n in [(\'monthly\',\'Mensual\',\'Flexibilidad mes a mes\'),(\'semiannual\',\'Semestral\',\'Menos renovaciones\'),(\'annual\',\'Anual\',\'Una renovación al año\')] %}',
    '<h2>Mensual o anual.</h2><div class="xp-plan-grid">{% for k,l,n in [(\'monthly\',\'Mensual\',\'Flexibilidad mes a mes\'),(\'annual\',\'Anual\',\'2 meses incluidos · Ahorras $998\')] %}',
    1
)

old='''<strong>{% if k == "monthly" and price_ready.get(k) %}$499 MXN / mes{% else %}Precio por definir{% endif %}</strong><small>{{ n }}</small><button class="btn btn-secondary" {% if not price_ready.get(k) %}disabled{% endif %}>{% if price_ready.get(k) %}{% if test_billing %}Probar pago{% else %}Elegir {{ l|lower }}{% endif %}{% else %}Próximamente{% endif %}</button>'''
new='''<strong>{% if k == "monthly" %}$499 MXN / mes{% elif k == "annual" %}$4,990 MXN / año{% endif %}</strong><small>{% if k == "monthly" %}Pago mensual · Flexibilidad mes a mes{% elif k == "annual" %}12 meses por el precio de 10 · Ahorras $998{% endif %}</small><button class="btn btn-secondary" {% if not price_ready.get(k) %}disabled{% endif %}>{% if price_ready.get(k) %}{% if test_billing %}Probar pago{% else %}Elegir {{ l|lower }}{% endif %}{% else %}Próximamente{% endif %}</button>'''
if old not in h: raise SystemExit("pricing UI anchor missing")
h=h.replace(old,new,1)
t.write_text(h)
print("Exponenta Pro commercial pricing set to monthly and annual only")
