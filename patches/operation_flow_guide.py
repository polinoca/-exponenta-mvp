from pathlib import Path

main=Path("/app/app/main.py")
s=main.read_text(encoding="utf-8")
marker="# XP OPERATION FLOW V1"
if marker not in s:
    anchor='@app.get("/negocio/lealtad", response_class=HTMLResponse)'
    if anchor not in s: raise SystemExit("operation route anchor missing")
    routes=r'''
# XP OPERATION FLOW V1
@app.get("/negocio/operacion", response_class=HTMLResponse)
def business_operation_guide(request: Request, db: Session = Depends(get_db)):
    user, org = business_admin_context(request, db)
    require_org_feature(db, org, "loyalty")
    program=db.scalar(select(LoyaltyProgram).where(
        LoyaltyProgram.organization_id==org.id,
        LoyaltyProgram.active.is_(True),
    ).order_by(LoyaltyProgram.id.desc()))
    return render(request, "business/operation_guide.html", {
        "user":user, "organization":org, "program":program,
    })

'''
    s=s.replace(anchor,routes+anchor,1)
    main.write_text(s,encoding="utf-8")

template=Path("/app/app/templates/business/operation_guide.html")
template.write_text(r'''{% extends "base.html" %}
{% block title %}Operación · {{ organization.name }}{% endblock %}
{% block body %}
<main class="business-shell xp-operation-page">
  <nav class="xp-business-nav">
    <a href="/negocio">Inicio</a><a class="active" href="/negocio/operacion">Operación</a><a href="/negocio/lealtad">Clientes</a><a href="/negocio/seguridad">Equipo</a><a href="/negocio/marketing">Reseñas</a><a href="/negocio/marca">Marca</a><a href="/negocio/configuracion">Más</a>
  </nav>
  <header class="xp-operation-head"><span class="eyebrow">OPERACIÓN EN NEGOCIO</span><h1>Registrar debe tomar segundos, no explicar un sistema.</h1><p>Usa un celular del negocio con sesión iniciada. El cliente muestra su QR o acerca su tarjeta NFC.</p></header>
  <section class="xp-operation-start">
    <div><span>LISTO PARA ATENDER</span><h2>Abre el modo de registro.</h2><p>Déjalo abierto en el celular o tablet que estará en caja.</p></div>
    <a class="btn btn-primary" href="/operar">Abrir modo escáner</a>
  </section>
  <section class="xp-operation-steps">
    <article><b>1</b><span class="xp-op-icon">◫</span><h2>El cliente muestra su tarjeta</h2><p>Puede abrir su tarjeta desde el link, Google Wallet o mostrar su QR. Si tiene NFC, sólo acerca la tarjeta al celular.</p></article>
    <article><b>2</b><span class="xp-op-icon">⌁</span><h2>El equipo registra</h2><p>Escanea el QR o toca el enlace NFC. Confirma el nombre del cliente y presiona una sola vez para registrar.</p></article>
    <article><b>3</b><span class="xp-op-icon">✓</span><h2>El cliente ve su avance</h2><p>El registro se actualiza en su tarjeta. Si llega a la meta, aparece su recompensa disponible.</p></article>
  </section>
  <section class="xp-operation-rules">
    <div><span class="eyebrow">REGLAS SIMPLES</span><h2>Así evitas errores en horas de mayor movimiento.</h2></div>
    <ul><li><b>Un celular por turno.</b> Inicia sesión con la cuenta asignada al equipo.</li><li><b>Una confirmación por compra.</b> Espera el mensaje de éxito antes de pasar al siguiente cliente.</li><li><b>Si el cliente no trae su tarjeta,</b> búscalo desde Clientes y registra desde su ficha.</li><li><b>Todo queda registrado.</b> Las visitas, puntos y premios quedan asociados al usuario que los realizó.</li></ul>
  </section>
  <section class="xp-operation-support">
    <div><span>¿PRIMERA VEZ?</span><strong>Haz una prueba con tu propia tarjeta antes de abrir al público.</strong></div>
    <a class="btn btn-secondary" href="/negocio/lealtad">Ver clientes y probar</a>
  </section>
</main>
{% endblock %}''',encoding="utf-8")

# Show Operación throughout the owner panel, without replacing any present links.
for f in Path("/app/app/templates/business").glob("*.html"):
    if f.name=="operation_guide.html": continue
    t=f.read_text(encoding="utf-8")
    if 'class="xp-business-nav"' in t and 'href="/negocio/operacion"' not in t:
        t=t.replace('<a href="/negocio">Inicio</a>','<a href="/negocio">Inicio</a><a href="/negocio/operacion">Operación</a>',1)
        f.write_text(t,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "/* XP OPERATION FLOW V1 */" not in c:
    c+=r'''
/* XP OPERATION FLOW V1 */
.xp-operation-page{max-width:1120px!important}.xp-operation-head{margin:24px 0 18px}.xp-operation-head h1{max-width:760px;margin:5px 0 10px;font-size:clamp(2rem,4.8vw,3.35rem)!important}.xp-operation-head p{max-width:710px;color:#6d635c}.xp-operation-start{display:flex;align-items:center;justify-content:space-between;gap:18px;border-radius:22px;padding:22px 24px;background:#241c17;color:#fff}.xp-operation-start span,.xp-operation-support span{font-size:.59rem;letter-spacing:.13em;font-weight:900;color:#d7b29a}.xp-operation-start h2{margin:5px 0;font-size:1.35rem;color:#fff}.xp-operation-start p{margin:0;color:#ded0c6;font-size:.78rem}.xp-operation-start .btn{background:#fff!important;color:#251d18!important;white-space:nowrap}.xp-operation-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:19px 0}.xp-operation-steps article{position:relative;padding:21px;border:1px solid #e4d9d0;border-radius:20px;background:#fff}.xp-operation-steps article>b{position:absolute;top:15px;right:15px;color:#ad9280;font-size:.65rem}.xp-op-icon{display:grid;place-items:center;width:40px;height:40px;border-radius:13px;background:#f3ece6;color:#61391f;font-size:1.25rem;font-weight:900}.xp-operation-steps h2{margin:18px 0 7px;font-size:1rem}.xp-operation-steps p{font-size:.77rem;line-height:1.5;color:#716862;margin:0}.xp-operation-rules{display:grid;grid-template-columns:.9fr 1.1fr;gap:25px;margin:18px 0;padding:23px;border:1px solid #e4d9d0;border-radius:20px;background:#faf7f4}.xp-operation-rules h2{margin:5px 0;font-size:1.35rem}.xp-operation-rules ul{display:grid;gap:11px;margin:0;padding:0;list-style:none}.xp-operation-rules li{font-size:.78rem;line-height:1.45;color:#625951}.xp-operation-rules li:before{content:"✓";display:inline-grid;place-items:center;width:17px;height:17px;margin-right:8px;border-radius:50%;background:#dceede;color:#1f763b;font-weight:900;font-size:.65rem}.xp-operation-support{display:flex;align-items:center;justify-content:space-between;gap:15px;padding:18px 2px}.xp-operation-support div{display:grid;gap:5px}.xp-operation-support strong{font-size:.86rem;color:#383029}@media(max-width:760px){.xp-operation-start,.xp-operation-support{align-items:flex-start;flex-direction:column}.xp-operation-start .btn,.xp-operation-support .btn{width:100%}.xp-operation-steps,.xp-operation-rules{grid-template-columns:1fr}.xp-operation-rules{gap:15px}.xp-operation-steps article{padding:18px}}
'''
    css.write_text(c,encoding="utf-8")
print("Operational QR/NFC flow installed")
