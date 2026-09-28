from pathlib import Path

# Public enrollment: lead with the benefit; returning access is explained only at the end.
path = Path("/app/app/templates/public/join.html")
html = path.read_text(encoding="utf-8")
html = html.replace(
    '<div class="eyebrow">TU TARJETA EN EL CELULAR</div><h2>Únete o vuelve a tu tarjeta.</h2>\n    <p class="muted">Ingresa tus datos. Si ya perteneces al club, abriremos tu misma tarjeta: no se crea otra ni pierdes tu avance.</p>',
    '<div class="eyebrow">TU TARJETA EN EL CELULAR</div><h2>Únete en menos de un minuto.</h2>\n    <p class="muted">Regístrate para llevar tus beneficios contigo.</p>',
)
path.write_text(html, encoding="utf-8")
print("Enrollment header simplified")
