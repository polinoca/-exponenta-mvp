from pathlib import Path

p=Path("/app/app/templates/landing.html")
s=p.read_text(encoding="utf-8")
if 'xp-launch-places' not in s:
    block=r'''
    <section class="xp-launch-places"><div class="xp-launch-wrap">
      <div class="xp-launch-places-head"><span class="xp-launch-eyebrow">HECHO PARA NEGOCIOS REALES</span><h2>Tu cliente ya vive en su celular.<br>Tu relación con él también puede vivir ahí.</h2></div>
      <div class="xp-launch-place-grid">
        <article class="cafe"><img src="https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1200&q=82" alt="Cafetería con clientes" loading="lazy"><div><span>CAFETERÍAS Y RESTAURANTES</span><h3>Haz visible la próxima visita.</h3></div></article>
        <article class="salon"><img src="https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1200&q=82" alt="Salón de belleza" loading="lazy"><div><span>ESTÉTICAS Y SALONES</span><h3>Convierte una cita en la siguiente.</h3></div></article>
        <article class="retail"><img src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=82" alt="Restaurante y negocio local" loading="lazy"><div><span>NEGOCIOS CON RECURRENCIA</span><h3>Da razones reales para volver.</h3></div></article>
      </div>
    </div></section>
'''
    s=s.replace('    <section class="xp-launch-intro" id="beneficios">',block+'\n    <section class="xp-launch-intro" id="beneficios">',1)
p.write_text(s,encoding="utf-8")

cssp=Path("/app/app/static/app.css")
css=cssp.read_text(encoding="utf-8")
if "/* XP LAUNCH REAL WORLD VISUALS V1 */" not in css:
 css+=r'''
/* XP LAUNCH REAL WORLD VISUALS V1 */
.xp-launch-device{background-image:linear-gradient(135deg,rgba(247,241,235,.82),rgba(212,184,163,.28)),url("https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1400&q=84")!important;background-size:cover!important;background-position:center!important}
.xp-launch-device:after{content:"";position:absolute;inset:0;background:linear-gradient(0deg,rgba(255,255,255,.08),rgba(255,255,255,.23));pointer-events:none}.xp-launch-device>*{position:relative;z-index:1}
.xp-launch-places{padding:0 0 42px}.xp-launch-places-head{display:flex;justify-content:space-between;align-items:end;gap:36px;padding:30px 0}.xp-launch-places-head h2{max-width:690px;margin:0;font-size:clamp(2rem,3.7vw,3.35rem);line-height:.98;letter-spacing:-.05em}.xp-launch-place-grid{display:grid;grid-template-columns:1.15fr .85fr .85fr;gap:14px}.xp-launch-place-grid article{position:relative;min-height:330px;overflow:hidden;border-radius:22px;background:#34251c}.xp-launch-place-grid img{width:100%;height:100%;position:absolute;inset:0;object-fit:cover;transition:transform .55s ease}.xp-launch-place-grid article:hover img{transform:scale(1.045)}.xp-launch-place-grid article:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,7,6,.06) 24%,rgba(10,8,6,.84) 100%)}.xp-launch-place-grid article>div{position:absolute;z-index:1;left:23px;right:20px;bottom:22px;color:#fff}.xp-launch-place-grid span{font-size:.6rem;font-weight:900;letter-spacing:.13em;color:#e5b18b}.xp-launch-place-grid h3{max-width:250px;margin:8px 0 0;font-size:1.55rem;line-height:1;letter-spacing:-.05em}.xp-launch-automation-visual{background-image:linear-gradient(145deg,rgba(42,25,14,.75),rgba(180,114,72,.52)),url("https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=82")!important;background-size:cover!important;background-position:center!important}
@media(max-width:760px){.xp-launch-places{padding-bottom:20px}.xp-launch-places-head{display:block;padding:12px 0 23px}.xp-launch-place-grid{grid-template-columns:1fr;gap:10px}.xp-launch-place-grid article{min-height:235px}.xp-launch-place-grid article:first-child{min-height:300px}.xp-launch-place-grid h3{font-size:1.45rem}}
'''
 cssp.write_text(css,encoding="utf-8")
print("Real-world visuals added to launch landing")
