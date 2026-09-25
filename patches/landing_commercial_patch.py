from pathlib import Path
import base64

logo_b64_path = Path("/bootstrap/patches/exponenta_logo.b64")
logo_out = Path("/app/app/static/exponenta-logo.webp")
logo_out.write_bytes(base64.b64decode(logo_b64_path.read_text(encoding="utf-8").strip()))

landing = """{% extends "base.html" %}
{% block title %}Exponenta — Clientes que regresan{% endblock %}
{% block body %}
<header class="site-header container landing-header">
  <a class="brand-logo" href="/" aria-label="Exponenta">
    <img src="/static/exponenta-logo.webp" alt="Exponenta">
  </a>
  <nav class="landing-nav">
    <a href="#como-funciona">Cómo funciona</a>
    <a href="#soluciones">Soluciones</a>
    <a href="#negocios">Para quién</a>
    {% if user %}<a class="btn btn-primary" href="/panel">Abrir panel</a>{% else %}<a class="btn btn-ghost" href="/login">Ingresar</a>{% endif %}
  </nav>
</header>

<main>
  <section class="landing-hero container">
    <div class="landing-hero-copy">
      <div class="eyebrow">FIDELIZACIÓN · RESEÑAS · WALLET · QR/NFC</div>
      <h1>Haz que una compra se convierta en la <em>siguiente.</em></h1>
      <p class="hero-lead">Exponenta conecta reseñas de Google, tarjetas de lealtad, Wallet, QR/NFC y métricas en una sola experiencia para negocios locales. Sin obligar al cliente a descargar una app.</p>
      <div class="hero-actions">
        <a class="btn btn-primary btn-lg" href="#como-funciona">Ver cómo funciona</a>
        {% if user %}<a class="btn btn-secondary btn-lg" href="/panel">Ir a mi panel</a>{% else %}<a class="btn btn-secondary btn-lg" href="/login">Ya soy cliente</a>{% endif %}
      </div>
      <div class="hero-proof">
        <span><strong>01</strong> Escanea o toca</span>
        <span><strong>02</strong> Guarda su tarjeta</span>
        <span><strong>03</strong> Regresa y acumula</span>
      </div>
    </div>
    <div class="hero-product">
      <div class="phone-frame">
        <div class="phone-status"><span>9:41</span><span>● ● ●</span></div>
        <div class="demo-pass">
          <div class="demo-pass-top"><span>EXPONENTA CLUB</span><strong>CAFÉ LOCAL</strong></div>
          <div><small>CLIENTE</small><h3>Diego</h3></div>
          <div><small>PROGRESO</small><h2>6 / 9 sellos</h2></div>
          <div class="demo-stamps">{% for i in range(9) %}<i class="{% if i < 6 %}filled{% endif %}"></i>{% endfor %}</div>
          <div class="demo-reward"><small>PRÓXIMA RECOMPENSA</small><strong>Tu café va por la casa</strong></div>
          <div class="demo-cta">Reservar / WhatsApp</div>
        </div>
        <div class="wallet-badges"><span>Google Wallet</span><span>Apple Wallet</span></div>
      </div>
    </div>
  </section>

  <section class="landing-strip">
    <div class="container strip-grid">
      <div><strong>Sin app</strong><span>El cliente no instala nada.</span></div>
      <div><strong>Medible</strong><span>Cada escaneo y visita deja datos.</span></div>
      <div><strong>Redirigible</strong><span>Cambia destinos sin reimprimir.</span></div>
      <div><strong>Tu marca</strong><span>La experiencia se adapta a tu negocio.</span></div>
    </div>
  </section>

  <section id="como-funciona" class="container landing-section">
    <div class="section-heading">
      <div class="eyebrow">CÓMO FUNCIONA</div>
      <h2>Del mostrador al celular del cliente en segundos.</h2>
      <p>Una experiencia simple para el cliente y una herramienta de recurrencia para el negocio.</p>
    </div>
    <div class="steps-grid">
      <article><span>01</span><h3>Toca o escanea</h3><p>Un QR o NFC abre la experiencia del negocio: reseña, registro, lealtad, menú o acceso directo.</p></article>
      <article><span>02</span><h3>Guarda su tarjeta</h3><p>El cliente se registra y puede llevar su tarjeta digital en el celular y, cuando esté habilitado, en Google o Apple Wallet.</p></article>
      <article><span>03</span><h3>Vuelve y acumula</h3><p>El negocio registra visitas, sellos y recompensas. El cliente ve su progreso y tiene un CTA directo para volver a comprar, reservar o escribir.</p></article>
    </div>
  </section>

  <section id="soluciones" class="landing-dark">
    <div class="container landing-section">
      <div class="section-heading light">
        <div class="eyebrow">TODO EN UN MISMO SISTEMA</div>
        <h2>No es sólo un QR. Es una capa de relación con tus clientes.</h2>
      </div>
      <div class="solution-grid">
        <article><div class="solution-icon">★</div><h3>Reseñas de Google</h3><p>Facilita que los clientes satisfechos lleguen directo a dejar su opinión.</p></article>
        <article><div class="solution-icon">⌁</div><h3>QR + NFC inteligente</h3><p>Códigos únicos, medibles y con destino modificable sin volver a imprimir.</p></article>
        <article><div class="solution-icon">▣</div><h3>Lealtad digital</h3><p>Sellos, visitas y recompensas configurables para crear recurrencia.</p></article>
        <article><div class="solution-icon">W</div><h3>Wallet</h3><p>Tarjetas digitales que viven en el teléfono del cliente y mantienen tu marca presente.</p></article>
        <article><div class="solution-icon">↗</div><h3>WhatsApp o reserva</h3><p>Un botón directo desde la experiencia del cliente para convertir la intención en acción.</p></article>
        <article><div class="solution-icon">◎</div><h3>Clientes y métricas</h3><p>Visualiza actividad, visitas, recompensas, escaneos y comportamiento básico.</p></article>
      </div>
    </div>
  </section>

  <section class="container landing-section">
    <div class="split-feature">
      <div>
        <div class="eyebrow">RESEÑA HOY. REGRESO MAÑANA.</div>
        <h2>Convierte reputación y recurrencia en un solo flujo.</h2>
        <p>Una reseña ayuda a que nuevos clientes te encuentren. Un programa de lealtad ayuda a que los que ya llegaron vuelvan. Exponenta une ambas cosas.</p>
      </div>
      <div class="flow-card">
        <div><span>1</span><strong>Cliente compra</strong></div>
        <i>→</i>
        <div><span>2</span><strong>Deja reseña</strong></div>
        <i>→</i>
        <div><span>3</span><strong>Guarda tarjeta</strong></div>
        <i>→</i>
        <div><span>4</span><strong>Regresa</strong></div>
      </div>
    </div>
  </section>

  <section id="negocios" class="container landing-section">
    <div class="section-heading">
      <div class="eyebrow">HECHO PARA NEGOCIOS LOCALES</div>
      <h2>Una misma plataforma, distintas formas de usarla.</h2>
    </div>
    <div class="business-chips">
      <span>Cafeterías</span><span>Restaurantes</span><span>Estéticas</span><span>Salones</span><span>Clínicas</span><span>Gimnasios</span><span>Tiendas</span><span>Servicios</span>
    </div>
  </section>

  <section class="landing-final">
    <div class="container final-card">
      <div>
        <div class="eyebrow">EXPONENTA</div>
        <h2>Tu cliente ya tiene un celular. Haz que tu negocio viva ahí.</h2>
        <p>QR/NFC, reseñas, lealtad y Wallet en una experiencia simple para el cliente y medible para tu negocio.</p>
      </div>
      <div class="final-actions">
        <a class="btn btn-light btn-lg" href="/login">Ingresar al panel</a>
        <a class="btn btn-outline-light btn-lg" href="#como-funciona">Ver la experiencia</a>
      </div>
    </div>
  </section>
</main>

<footer class="container footer landing-footer">
  <img src="/static/exponenta-logo.webp" alt="Exponenta">
  <span>Exponenta · Tecnología para negocios que quieren clientes recurrentes.</span>
</footer>
{% endblock %}
"""

Path("/app/app/templates/landing.html").write_text(landing, encoding="utf-8")

css_path = Path("/app/app/static/app.css")
css = css_path.read_text(encoding="utf-8")
marker = "/* EXPONENTA LANDING V1 */"
if marker not in css:
    css += """
/* EXPONENTA LANDING V1 */
.landing-header{height:92px}.brand-logo{display:flex;align-items:center}.brand-logo img{width:155px;height:auto;display:block}.landing-nav{display:flex;align-items:center;gap:22px;font-size:.84rem;font-weight:800}.landing-nav>a:not(.btn){color:#5c5c56}.landing-hero{min-height:720px;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(340px,.7fr);gap:70px;align-items:center;padding:70px 0 100px}.landing-hero h1{font-size:clamp(3.7rem,7.5vw,7rem);line-height:.9;letter-spacing:-.065em;margin:.55rem 0 1.5rem;max-width:800px}.landing-hero h1 em{font-style:normal;background:linear-gradient(90deg,#9b5527,#da7b37);-webkit-background-clip:text;color:transparent}.hero-lead{font-size:clamp(1.08rem,1.6vw,1.32rem);max-width:700px;color:#595953}.btn-lg{padding:.95rem 1.35rem;font-size:.96rem}.hero-proof{display:flex;gap:20px;flex-wrap:wrap;margin-top:32px;padding-top:20px;border-top:1px solid var(--line);font-size:.82rem;color:#66655e}.hero-proof span{display:flex;gap:7px;align-items:center}.hero-proof strong{font-size:.68rem;background:#fff;border:1px solid var(--line);padding:5px 7px;border-radius:999px}.hero-product{display:flex;justify-content:center}.phone-frame{width:min(390px,100%);background:#11120f;border-radius:44px;padding:13px;box-shadow:0 36px 90px rgba(17,17,15,.22);border:1px solid #24251f}.phone-status{height:38px;color:#fff;display:flex;justify-content:space-between;align-items:center;padding:0 16px;font-size:.72rem}.demo-pass{min-height:490px;border-radius:32px;padding:24px;background:linear-gradient(145deg,#9b5527,#db7a36 54%,#5b321f);color:#fff;display:flex;flex-direction:column;gap:24px}.demo-pass-top{display:flex;justify-content:space-between;font-size:.69rem;letter-spacing:.05em}.demo-pass small{font-size:.6rem;letter-spacing:.11em;opacity:.75}.demo-pass h3{font-size:1.65rem;margin:.1rem 0}.demo-pass h2{font-size:2.2rem;margin:.1rem 0;letter-spacing:-.05em}.demo-stamps{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}.demo-stamps i{aspect-ratio:1;border:2px solid rgba(255,255,255,.38);border-radius:50%}.demo-stamps i.filled{background:#fff;border-color:#fff}.demo-reward{margin-top:auto;background:rgba(0,0,0,.2);backdrop-filter:blur(5px);border-radius:16px;padding:15px;display:grid;gap:3px}.demo-cta{background:#fff;color:#21160f;text-align:center;padding:12px;border-radius:999px;font-weight:900;font-size:.86rem}.wallet-badges{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:12px 4px 4px}.wallet-badges span{background:#22231f;color:#fff;text-align:center;padding:10px 6px;border-radius:12px;font-size:.7rem;font-weight:800}.landing-strip{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.strip-grid{display:grid;grid-template-columns:repeat(4,1fr)}.strip-grid>div{padding:24px;border-right:1px solid var(--line);display:grid;gap:4px}.strip-grid>div:last-child{border-right:0}.strip-grid strong{font-size:.95rem}.strip-grid span{font-size:.78rem;color:var(--muted)}.landing-section{padding:100px 0}.section-heading{max-width:820px;margin-bottom:42px}.section-heading h2,.split-feature h2,.final-card h2{font-size:clamp(2.4rem,5vw,4.8rem);line-height:.98;letter-spacing:-.055em;margin:.45rem 0 1rem}.section-heading>p,.split-feature p{font-size:1.08rem;color:var(--muted);max-width:680px}.steps-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.steps-grid article{background:#fff;border:1px solid var(--line);border-radius:24px;padding:28px;min-height:300px}.steps-grid article>span{display:inline-grid;place-items:center;width:42px;height:42px;border-radius:50%;background:#f1efe9;font-size:.72rem;font-weight:900}.steps-grid h3{font-size:1.55rem;letter-spacing:-.03em;margin-top:70px;margin-bottom:.5rem}.steps-grid p{color:var(--muted);font-size:.92rem}.landing-dark{background:#151612;color:#fff}.section-heading.light .eyebrow{color:#a0a297}.section-heading.light h2{color:#fff}.solution-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.solution-grid article{border:1px solid #30322b;border-radius:20px;padding:24px;min-height:245px;background:#1c1d19}.solution-icon{width:42px;height:42px;border-radius:12px;background:#2d2f27;display:grid;place-items:center;font-weight:900;color:#e39a64}.solution-grid h3{font-size:1.3rem;margin-top:52px;margin-bottom:.4rem}.solution-grid p{color:#aaada4;font-size:.88rem}.split-feature{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}.flow-card{background:#fff;border:1px solid var(--line);border-radius:26px;padding:22px;display:grid;gap:9px;box-shadow:var(--shadow)}.flow-card div{display:flex;align-items:center;gap:12px;background:#f5f3ee;border-radius:15px;padding:14px}.flow-card span{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#111;color:#fff;font-size:.7rem;font-weight:900}.flow-card i{text-align:center;font-style:normal;color:#9c9b94}.business-chips{display:flex;flex-wrap:wrap;gap:10px}.business-chips span{background:#fff;border:1px solid var(--line);border-radius:999px;padding:13px 18px;font-weight:800;font-size:.9rem}.landing-final{padding:40px 0 100px}.final-card{background:linear-gradient(135deg,#8a4b25,#d77936);border-radius:34px;color:#fff;padding:54px;display:grid;grid-template-columns:1.25fr .75fr;gap:50px;align-items:end}.final-card .eyebrow{color:#f2d7c5}.final-card p{color:#f7e8df;max-width:650px}.final-actions{display:grid;gap:10px}.btn-outline-light{border-color:rgba(255,255,255,.5);color:#fff}.landing-footer{display:flex;align-items:center;justify-content:space-between;gap:20px}.landing-footer img{width:120px}.landing-footer span{font-size:.76rem}@media(max-width:900px){.landing-nav>a:not(.btn){display:none}.landing-hero{grid-template-columns:1fr;min-height:auto;padding:45px 0 75px;gap:50px}.hero-product{justify-content:flex-start}.strip-grid{grid-template-columns:1fr 1fr}.strip-grid>div:nth-child(2){border-right:0}.steps-grid,.solution-grid{grid-template-columns:1fr 1fr}.split-feature,.final-card{grid-template-columns:1fr}.landing-section{padding:75px 0}}@media(max-width:560px){.landing-header{height:78px}.brand-logo img{width:125px}.landing-nav{gap:8px}.landing-nav .btn{padding:.65rem .85rem}.landing-hero h1{font-size:3.25rem}.hero-proof{display:grid;gap:9px}.phone-frame{width:100%}.strip-grid,.steps-grid,.solution-grid{grid-template-columns:1fr}.strip-grid>div{border-right:0;border-bottom:1px solid var(--line)}.strip-grid>div:last-child{border-bottom:0}.landing-section{padding:60px 0}.section-heading h2,.split-feature h2,.final-card h2{font-size:2.55rem}.steps-grid article{min-height:240px}.steps-grid h3{margin-top:42px}.solution-grid article{min-height:220px}.final-card{padding:28px;border-radius:24px}.landing-footer{align-items:flex-start;flex-direction:column}.landing-footer img{width:105px}}
"""
    css_path.write_text(css, encoding="utf-8")

print("Landing comercial Exponenta instalada")
