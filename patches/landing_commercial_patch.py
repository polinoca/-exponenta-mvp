from pathlib import Path
import base64

# Brand asset: exact supplied Exponenta artwork, background removed without changing the brown/copper tones.
logo_b64 = Path("/bootstrap/patches/exponenta_logo.b64").read_text(encoding="utf-8").strip()
Path("/app/app/static/exponenta-logo.webp?v=20260925-4").write_bytes(base64.b64decode(logo_b64))

base = Path("/app/app/templates/base.html")
base.write_text("""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="description" content="Exponenta convierte visitas en reseñas, clientes recurrentes y relaciones medibles con QR/NFC, lealtad digital y Wallet.">
  <meta name="theme-color" content="#f6f3ee">
  <title>{% block title %}Exponenta{% endblock %}</title>
  <link rel="stylesheet" href="/static/app.css?v=20260925-3">
</head>
<body>
  {% block body %}{% endblock %}
  <script src="/static/app.js?v=20260925-3" defer></script>
</body>
</html>
""", encoding="utf-8")

landing = r"""{% extends "base.html" %}
{% block title %}Exponenta — Haz que tus clientes vuelvan{% endblock %}
{% block body %}
<div class="xp-page">
  <header class="xp-nav">
    <div class="xp-wrap xp-nav-inner">
      <a class="xp-logo" href="/" aria-label="Exponenta"><img src="/static/exponenta-logo.webp?v=20260925-4" alt="Exponenta"></a>
      <nav class="xp-nav-links" aria-label="Navegación">
        <a href="#ventajas">Ventajas</a>
        <a href="#como">Cómo funciona</a>
        <a href="#incluye">Qué incluye</a>
        <a href="#comparacion">Comparación</a>
      </nav>
      {% if user %}<a class="xp-btn xp-btn-small xp-btn-dark" href="/panel">Abrir panel</a>{% else %}<a class="xp-btn xp-btn-small xp-btn-light" href="/login">Ingresar</a>{% endif %}
    </div>
  </header>

  <main>
    <section class="xp-hero xp-wrap">
      <div class="xp-hero-copy">
        <div class="xp-kicker">RESEÑAS · LEALTAD · WALLET · QR/NFC</div>
        <h1>Convierte cada visita en una razón para <span>volver.</span></h1>
        <p class="xp-lead">Exponenta pone tu negocio en el celular de tus clientes: les facilita dejar una reseña, acumular recompensas y regresar con un toque. Tú ves quién vuelve, qué funciona y qué está generando recurrencia.</p>
        <div class="xp-hero-actions">
          <a class="xp-btn xp-btn-dark" href="#como">Ver cómo funciona</a>
          {% if user %}<a class="xp-btn xp-btn-outline" href="/panel">Ir a mi panel</a>{% else %}<a class="xp-btn xp-btn-outline" href="/login">Ya soy cliente</a>{% endif %}
        </div>
        <p class="xp-noapp"><strong>Sin descargar una app.</strong> QR o NFC → registro → tarjeta digital → recompensa.</p>
      </div>

      <div class="xp-hero-visual" aria-label="Vista previa de la experiencia Exponenta">
        <div class="xp-phone xp-phone-main">
          <div class="xp-phone-bar"><span>9:41</span><span>● ● ●</span></div>
          <div class="xp-pass">
            <div class="xp-pass-top"><strong>CAFÉ LOCAL</strong><span>EXPONENTA CLUB</span></div>
            <div><small>CLIENTE</small><h3>Diego</h3></div>
            <div><small>PROGRESO</small><h2>6 / 9 sellos</h2></div>
            <div class="xp-stamps">{% for i in range(9) %}<i class="{% if i < 6 %}on{% endif %}"></i>{% endfor %}</div>
            <div class="xp-reward"><small>PRÓXIMA RECOMPENSA</small><strong>Tu café va por la casa</strong></div>
            <div class="xp-pass-cta">Reservar / WhatsApp</div>
          </div>
        </div>
        <div class="xp-float xp-float-a"><span>★</span><b>Reseña recibida</b><small>Google</small></div>
        <div class="xp-float xp-float-b"><span>+1</span><b>Nuevo sello</b><small>6 de 9</small></div>
      </div>
    </section>

    <section class="xp-proof">
      <div class="xp-wrap xp-proof-grid">
        <div><b>Sin app</b><span>El cliente usa lo que ya tiene: su celular.</span></div>
        <div><b>Más fácil de repetir</b><span>La recompensa y el acceso al negocio quedan a un toque.</span></div>
        <div><b>Datos útiles</b><span>Visitas, sellos, recompensas, escaneos y actividad.</span></div>
        <div><b>Control del equipo</b><span>Permisos, límites y auditoría de operaciones.</span></div>
      </div>
    </section>

    <section id="ventajas" class="xp-section xp-wrap">
      <div class="xp-section-head">
        <span class="xp-kicker">EL PROBLEMA REAL</span>
        <h2>Ya pagaste por conseguir al cliente. El error caro es dejarlo ir sin una razón para volver.</h2>
        <p>Exponenta une adquisición, reputación y recurrencia en el mismo flujo. No reemplaza la atención del negocio: la convierte en una relación que puedes medir y repetir.</p>
      </div>
      <div class="xp-three">
        <article class="xp-card"><span class="xp-index">01</span><h3>Más recurrencia</h3><p>Sellos y recompensas visibles hacen que volver tenga una razón concreta, no sólo buena intención.</p></article>
        <article class="xp-card xp-card-dark"><span class="xp-index">02</span><h3>Más reputación</h3><p>El mismo ecosistema puede llevar a tus clientes satisfechos directamente a dejar una reseña en Google.</p></article>
        <article class="xp-card"><span class="xp-index">03</span><h3>Más información</h3><p>Dejas de depender de tarjetas de papel y comienzas a construir una base de clientes con actividad real.</p></article>
      </div>
    </section>

    <section id="como" class="xp-band">
      <div class="xp-wrap xp-section">
        <div class="xp-section-head xp-section-head-light">
          <span class="xp-kicker">ASÍ DE SIMPLE</span>
          <h2>El sistema que el cliente entiende en segundos.</h2>
          <p>Menos pasos para el cliente. Más visibilidad para el negocio.</p>
        </div>
        <div class="xp-steps">
          <article><span>1</span><div><h3>Toca o escanea</h3><p>Un QR o NFC abre la experiencia del negocio. Sin buscar links ni descargar aplicaciones.</p></div></article>
          <article><span>2</span><div><h3>Se registra una vez</h3><p>El cliente obtiene su tarjeta digital y puede consultar su progreso desde el celular.</p></div></article>
          <article><span>3</span><div><h3>Acumula y vuelve</h3><p>Tu equipo registra visitas o sellos; la recompensa aparece y el cliente tiene un acceso directo para volver a comprar, reservar o escribir.</p></div></article>
        </div>
      </div>
    </section>

    <section id="incluye" class="xp-section xp-wrap">
      <div class="xp-section-head">
        <span class="xp-kicker">UNA SOLA PLATAFORMA</span>
        <h2>Lo que normalmente tendrías disperso, conectado en un mismo sistema.</h2>
      </div>
      <div class="xp-feature-grid">
        <article><div class="xp-icon">★</div><h3>Reseñas de Google</h3><p>QR/NFC directo a reseña y medición de aperturas.</p></article>
        <article><div class="xp-icon">⌁</div><h3>QR + NFC redirigible</h3><p>Cambia el destino sin volver a imprimir el material físico.</p></article>
        <article><div class="xp-icon">●</div><h3>Lealtad digital</h3><p>Sellos, visitas, recompensas y canjes desde el panel.</p></article>
        <article><div class="xp-icon">W</div><h3>Wallet</h3><p>Tarjeta preparada para Google Wallet y Apple Wallet, con experiencia móvil propia mientras se activa cada proveedor.</p></article>
        <article><div class="xp-icon">↗</div><h3>WhatsApp / reserva</h3><p>CTA principal desde la tarjeta para convertir la intención en acción.</p></article>
        <article><div class="xp-icon">◎</div><h3>Clientes y métricas</h3><p>Actividad, visitas, premios, escaneos y eventos en un solo lugar.</p></article>
        <article><div class="xp-icon">✓</div><h3>Control de empleados</h3><p>Permisos individuales, límites de sellos y trazabilidad de operaciones.</p></article>
        <article><div class="xp-icon">↺</div><h3>Correcciones auditadas</h3><p>Los cambios sensibles dejan rastro; no se borran silenciosamente.</p></article>
      </div>
    </section>

    <section class="xp-section xp-wrap">
      <div class="xp-offer">
        <div class="xp-offer-copy">
          <span class="xp-kicker">LA OFERTA EN UNA FRASE</span>
          <h2>Haz que cada cliente pueda dejarte una reseña hoy y tenga una razón visible para volver mañana.</h2>
          <p>Si tu negocio ya invierte tiempo o dinero en conseguir clientes, perder el contacto después de la compra es una fuga innecesaria. Exponenta cierra ese hueco con una experiencia simple y medible.</p>
          <a class="xp-btn xp-btn-copper" href="#comparacion">Ver qué reemplaza</a>
        </div>
        <div class="xp-stack">
          <div><b>QR/NFC inteligente</b><span>incluido</span></div>
          <div><b>Tarjeta de lealtad</b><span>incluido</span></div>
          <div><b>Reseñas Google</b><span>incluido</span></div>
          <div><b>Panel + clientes</b><span>incluido</span></div>
          <div><b>Seguridad de operadores</b><span>incluido</span></div>
          <div><b>CTA WhatsApp / reserva</b><span>incluido</span></div>
        </div>
      </div>
    </section>

    <section id="comparacion" class="xp-section xp-wrap">
      <div class="xp-section-head">
        <span class="xp-kicker">COMPARA EL FLUJO</span>
        <h2>Seguir como hoy vs. convertir cada visita en un activo.</h2>
      </div>
      <div class="xp-compare">
        <div class="xp-compare-col">
          <h3>Sin Exponenta</h3>
          <ul>
            <li>Tarjetas de papel que se pierden</li>
            <li>QR fijo que obliga a reimprimir</li>
            <li>Reseñas pedidas de forma improvisada</li>
            <li>Sin historial claro de visitas</li>
            <li>Promociones sin trazabilidad</li>
            <li>Difícil controlar quién otorgó un sello</li>
          </ul>
        </div>
        <div class="xp-compare-col xp-compare-good">
          <h3>Con Exponenta</h3>
          <ul>
            <li>Tarjeta digital en el celular</li>
            <li>QR/NFC medible y redirigible</li>
            <li>Acceso directo a reseña Google</li>
            <li>Visitas y recompensas registradas</li>
            <li>CTA directo a WhatsApp o reserva</li>
            <li>Permisos y auditoría por empleado</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="xp-section xp-wrap">
      <div class="xp-section-head">
        <span class="xp-kicker">PARA NEGOCIOS CON RECURRENCIA</span>
        <h2>Si un cliente puede volver, Exponenta puede tener sentido.</h2>
      </div>
      <div class="xp-chips">
        <span>Cafeterías</span><span>Restaurantes</span><span>Estéticas</span><span>Salones</span><span>Clínicas</span><span>Gimnasios</span><span>Tiendas</span><span>Servicios</span>
      </div>
    </section>

    <section class="xp-final">
      <div class="xp-wrap xp-final-inner">
        <img src="/static/exponenta-logo.webp?v=20260925-4" alt="Exponenta">
        <div>
          <span class="xp-kicker">EXPONENTA</span>
          <h2>Tu cliente ya tiene un celular. Haz que tu negocio viva ahí.</h2>
          <p>Una experiencia para que te recomienden, regresen y puedas medirlo.</p>
        </div>
        {% if user %}<a class="xp-btn xp-btn-light-solid" href="/panel">Abrir mi panel</a>{% else %}<a class="xp-btn xp-btn-light-solid" href="/login">Ingresar</a>{% endif %}
      </div>
    </section>
  </main>

  <footer class="xp-footer xp-wrap">
    <img src="/static/exponenta-logo.webp?v=20260925-4" alt="Exponenta">
    <span>Exponenta · Tecnología para negocios que quieren clientes recurrentes.</span>
  </footer>
</div>
{% endblock %}
"""
Path("/app/app/templates/landing.html").write_text(landing, encoding="utf-8")

css_path = Path("/app/app/static/app.css")
css = css_path.read_text(encoding="utf-8")
css += r"""
/* EXPONENTA LANDING MOBILE-FIRST V3 */
.xp-page{--xp-bg:#f6f3ee;--xp-ink:#15130f;--xp-muted:#706c64;--xp-line:#ded8ce;--xp-card:#fff;--xp-brown:#6d3d1f;--xp-copper:#a96131;--xp-copper2:#cf7c43;background:var(--xp-bg);color:var(--xp-ink);overflow:hidden}.xp-page *{box-sizing:border-box}.xp-page img{max-width:100%;height:auto}.xp-wrap{width:min(1160px,calc(100% - 32px));margin-inline:auto}.xp-nav{position:sticky;top:0;z-index:40;background:rgba(246,243,238,.94);backdrop-filter:blur(16px);border-bottom:1px solid rgba(222,216,206,.75)}.xp-nav-inner{height:74px;display:flex;align-items:center;justify-content:space-between;gap:16px}.xp-logo{display:flex;align-items:center;min-width:0}.xp-logo img{width:126px;display:block}.xp-nav-links{display:none}.xp-btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 20px;border-radius:999px;font-size:.9rem;font-weight:850;border:1px solid transparent;white-space:nowrap}.xp-btn-small{min-height:42px;padding:0 16px;font-size:.82rem}.xp-btn-dark{background:#15130f;color:#fff}.xp-btn-light{background:#fff;border-color:var(--xp-line)}.xp-btn-outline{border-color:#2a2722;color:#1a1814}.xp-btn-copper{background:linear-gradient(135deg,var(--xp-brown),var(--xp-copper2));color:#fff}.xp-btn-light-solid{background:#fff;color:#1d1712}.xp-kicker{display:block;font-size:.67rem;letter-spacing:.18em;font-weight:900;color:#8d6c54;text-transform:uppercase}.xp-hero{padding:58px 0 72px;display:grid;gap:48px}.xp-hero-copy h1{font-size:clamp(3rem,14vw,5rem);line-height:.92;letter-spacing:-.062em;margin:12px 0 20px;max-width:850px}.xp-hero-copy h1 span{color:var(--xp-copper)}.xp-lead{font-size:1.07rem;line-height:1.55;color:#565149;max-width:700px}.xp-hero-actions{display:grid;gap:10px;margin:28px 0 18px}.xp-noapp{font-size:.82rem;color:var(--xp-muted);margin:0}.xp-hero-visual{position:relative;min-height:560px;display:grid;place-items:center}.xp-phone{width:min(100%,360px);background:#111;border-radius:38px;padding:12px;box-shadow:0 30px 90px rgba(55,32,17,.24);transform:rotate(-1.5deg)}.xp-phone-bar{height:36px;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 14px;font-size:.7rem}.xp-pass{min-height:470px;border-radius:28px;padding:22px;background:linear-gradient(145deg,#4f2c19 0%,#9b572e 55%,#d1844c 100%);color:#fff;display:flex;flex-direction:column;gap:24px}.xp-pass-top{display:flex;justify-content:space-between;gap:12px;font-size:.65rem}.xp-pass small{font-size:.58rem;letter-spacing:.12em;opacity:.78}.xp-pass h3{font-size:1.6rem;margin:2px 0}.xp-pass h2{font-size:2rem;margin:2px 0;letter-spacing:-.04em}.xp-stamps{display:grid;grid-template-columns:repeat(5,1fr);gap:9px}.xp-stamps i{aspect-ratio:1;border-radius:50%;border:2px solid rgba(255,255,255,.42)}.xp-stamps i.on{background:#fff;border-color:#fff}.xp-reward{margin-top:auto;background:rgba(24,11,4,.24);border-radius:15px;padding:14px;display:grid;gap:4px}.xp-pass-cta{background:#fff;color:#2a180e;border-radius:999px;text-align:center;padding:12px;font-weight:900;font-size:.83rem}.xp-float{position:absolute;background:#fff;border:1px solid var(--xp-line);box-shadow:0 16px 40px rgba(32,25,20,.12);border-radius:16px;padding:12px 14px;display:grid;grid-template-columns:auto 1fr;column-gap:9px;min-width:165px}.xp-float span{grid-row:1/3;width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:#efe2d7;color:var(--xp-brown);font-weight:900}.xp-float b{font-size:.76rem}.xp-float small{font-size:.68rem;color:var(--xp-muted)}.xp-float-a{right:-4px;top:60px}.xp-float-b{left:-6px;bottom:68px}.xp-proof{background:#fff;border-block:1px solid var(--xp-line)}.xp-proof-grid{display:grid}.xp-proof-grid>div{padding:20px 0;border-bottom:1px solid var(--xp-line);display:grid;gap:4px}.xp-proof-grid>div:last-child{border-bottom:0}.xp-proof b{font-size:.93rem}.xp-proof span{font-size:.79rem;color:var(--xp-muted)}.xp-section{padding:76px 0}.xp-section-head{max-width:820px;margin-bottom:32px}.xp-section-head h2,.xp-offer h2,.xp-final h2{font-size:clamp(2.2rem,10vw,4.5rem);line-height:.98;letter-spacing:-.05em;margin:10px 0 14px}.xp-section-head p,.xp-offer-copy p{font-size:1rem;line-height:1.6;color:var(--xp-muted);max-width:700px}.xp-three{display:grid;gap:14px}.xp-card{background:#fff;border:1px solid var(--xp-line);border-radius:22px;padding:24px;min-height:250px;display:flex;flex-direction:column}.xp-card-dark{background:#1c1915;color:#fff;border-color:#1c1915}.xp-card .xp-index{font-size:.68rem;font-weight:900;opacity:.55}.xp-card h3{font-size:1.65rem;margin:auto 0 8px;letter-spacing:-.035em}.xp-card p{font-size:.9rem;line-height:1.55;color:#746f67;margin:0}.xp-card-dark p{color:#c8c0b7}.xp-band{background:#171410;color:#fff}.xp-section-head-light p{color:#c0b8ae}.xp-section-head-light .xp-kicker{color:#c78b62}.xp-steps{display:grid;gap:12px}.xp-steps article{display:grid;grid-template-columns:46px 1fr;gap:15px;padding:20px;border:1px solid #37312b;border-radius:20px;background:#201c18}.xp-steps article>span{width:40px;height:40px;border-radius:50%;background:#fff;color:#1a1714;display:grid;place-items:center;font-size:.72rem;font-weight:900}.xp-steps h3{margin:2px 0 6px;font-size:1.25rem}.xp-steps p{margin:0;color:#bfb7ad;font-size:.88rem;line-height:1.5}.xp-feature-grid{display:grid;gap:12px}.xp-feature-grid article{background:#fff;border:1px solid var(--xp-line);border-radius:20px;padding:22px;min-height:205px;display:flex;flex-direction:column}.xp-icon{width:38px;height:38px;border-radius:11px;background:#f0e4da;color:var(--xp-brown);display:grid;place-items:center;font-weight:900}.xp-feature-grid h3{font-size:1.2rem;margin:auto 0 6px}.xp-feature-grid p{color:var(--xp-muted);font-size:.86rem;line-height:1.5;margin:0}.xp-offer{background:#fff;border:1px solid var(--xp-line);border-radius:26px;padding:24px;display:grid;gap:30px;box-shadow:0 18px 55px rgba(55,40,28,.06)}.xp-stack{display:grid;border:1px solid var(--xp-line);border-radius:18px;overflow:hidden}.xp-stack div{display:flex;justify-content:space-between;gap:15px;padding:15px 16px;border-bottom:1px solid var(--xp-line);font-size:.82rem}.xp-stack div:last-child{border-bottom:0}.xp-stack span{color:var(--xp-copper);font-weight:850}.xp-compare{display:grid;gap:14px}.xp-compare-col{background:#fff;border:1px solid var(--xp-line);border-radius:22px;padding:22px}.xp-compare-col h3{font-size:1.35rem;margin:0 0 15px}.xp-compare-col ul{list-style:none;padding:0;margin:0;display:grid;gap:12px}.xp-compare-col li{font-size:.88rem;color:#5f5a52;display:flex;gap:10px}.xp-compare-col li:before{content:"—";font-weight:900;color:#9d958b}.xp-compare-good{background:#1c1915;color:#fff;border-color:#1c1915}.xp-compare-good li{color:#d0c7bd}.xp-compare-good li:before{content:"✓";color:#d99262}.xp-chips{display:flex;flex-wrap:wrap;gap:9px}.xp-chips span{background:#fff;border:1px solid var(--xp-line);border-radius:999px;padding:11px 15px;font-size:.82rem;font-weight:800}.xp-final{background:linear-gradient(135deg,#3f2416,#7a4426 55%,#a8643a);color:#fff;padding:70px 0}.xp-final-inner{display:grid;gap:28px}.xp-final-inner>img{width:160px;filter:brightness(1.25)}.xp-final .xp-kicker{color:#e7c2a7}.xp-final p{color:#ead9cc;max-width:620px}.xp-footer{padding:28px 0 42px;display:flex;flex-direction:column;gap:12px;align-items:flex-start;color:#766f67}.xp-footer img{width:112px}.xp-footer span{font-size:.72rem}

@media(min-width:680px){.xp-hero-actions{display:flex}.xp-proof-grid{grid-template-columns:1fr 1fr}.xp-proof-grid>div{padding:22px;border-bottom:1px solid var(--xp-line)}.xp-proof-grid>div:nth-child(odd){border-right:1px solid var(--xp-line)}.xp-three{grid-template-columns:repeat(3,1fr)}.xp-feature-grid{grid-template-columns:repeat(2,1fr)}.xp-compare{grid-template-columns:1fr 1fr}.xp-footer{flex-direction:row;justify-content:space-between;align-items:center}}
@media(min-width:920px){.xp-wrap{width:min(1180px,calc(100% - 64px))}.xp-nav-inner{height:84px}.xp-logo img{width:150px}.xp-nav-links{display:flex;align-items:center;gap:24px}.xp-nav-links a{font-size:.8rem;font-weight:800;color:#5b554e}.xp-hero{grid-template-columns:minmax(0,1.05fr) minmax(420px,.75fr);align-items:center;gap:80px;padding:90px 0 110px}.xp-hero-copy h1{font-size:clamp(4.6rem,7vw,7.1rem)}.xp-hero-visual{min-height:620px}.xp-phone{width:390px}.xp-float-a{right:0}.xp-float-b{left:0}.xp-proof-grid{grid-template-columns:repeat(4,1fr)}.xp-proof-grid>div{border-bottom:0!important;border-right:1px solid var(--xp-line)!important}.xp-proof-grid>div:last-child{border-right:0!important}.xp-section{padding:105px 0}.xp-steps{grid-template-columns:repeat(3,1fr)}.xp-steps article{grid-template-columns:1fr;min-height:270px}.xp-steps article>span{margin-bottom:auto}.xp-feature-grid{grid-template-columns:repeat(4,1fr)}.xp-offer{grid-template-columns:1.2fr .8fr;padding:42px;align-items:center}.xp-final-inner{grid-template-columns:180px 1fr auto;align-items:center}.xp-final-inner>img{width:160px}}
"""
css_path.write_text(css, encoding="utf-8")
print("Exponenta landing V3 mobile-first installed")
