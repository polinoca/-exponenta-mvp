from pathlib import Path

# Keep one simple public path: the same form creates or reopens a card.
path = Path("/app/app/templates/public/join.html")
html = path.read_text(encoding="utf-8")
html = html.replace(
    '<div class="eyebrow">TU TARJETA EN EL CELULAR</div><h2>Únete en menos de un minuto.</h2>\n    <p class="muted">Tus datos se usan para identificar tu tarjeta, registrar beneficios y, sólo si lo autorizas, compartirte novedades del negocio.</p>',
    '<div class="eyebrow">TU TARJETA EN EL CELULAR</div><h2>Únete o vuelve a tu tarjeta.</h2>\n    <p class="muted">Ingresa tus datos. Si ya perteneces al club, abriremos tu misma tarjeta: no se crea otra ni pierdes tu avance.</p>',
)
html = html.replace('placeholder="Para recuperar tu tarjeta"', 'placeholder="Para identificar tu tarjeta"')
html = html.replace('>Crear mi tarjeta</button>', '>Continuar a mi tarjeta</button>')
html = html.replace(
    '<p class="xp-join-foot">Ya tienes tarjeta? <a href="/club/{{ organization.slug }}/recuperar">Recuperarla</a></p>',
    '<p class="xp-join-foot">¿Ya perteneces al club? Usa el mismo teléfono o correo y entra directo. <a href="/club/{{ organization.slug }}/recuperar">¿No recuerdas tus datos?</a></p>',
)
path.write_text(html, encoding="utf-8")
print("Simplified returning-member journey installed")
