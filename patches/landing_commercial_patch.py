from pathlib import Path

logo_svg = Path("/bootstrap/patches/exponenta-logo.svg").read_text(encoding="utf-8")
Path("/app/app/static/exponenta-logo.svg").write_text(logo_svg, encoding="utf-8")

base = Path("/app/app/templates/base.html")
base.write_text("""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="description" content="Exponenta ayuda a negocios locales a convertir visitas en clientes recurrentes, recompensas, reseñas y datos útiles.">
  <meta name="theme-color" content="#f6f1ea">
  <title>{% block title %}Exponenta{% endblock %}</title>
  <link rel="stylesheet" href="/static/app.css?v=20260925-8">
</head>
<body>
  {% block body %}{% endblock %}
  <script src="/static/app.js?v=20260925-3" defer></script>
</body>
</html>
""", encoding="utf-8")

landing = r"""{% extends "base.html" %}
{% block title %}Exponenta — Clientes que vuelven{% endblock %}
{% block body %}
<div class="xp4">
  <div class="xp4-top">Convierte cada visita en una relación que puede crecer.</div>

  <header class="xp4-nav">
    <div class="xp4-wrap xp4-navin">
      <a class="xp4-logo" href="/" aria-label="Exponenta"><img src="/static/exponenta-logo.svg?v=20260925-8" alt="Exponenta"></a>
      <nav>
        <a href="#beneficios">Beneficios</a>
        <a href="#programa">Fidelización</a>
        <a href="#como">Cómo funciona</a>
        <a href="#faq">Preguntas</a>
      </nav>
      {% if user %}<a class="xp4-btn xp4-btn-dark xp4-small" href="/panel">Abrir panel</a>{% else %}<a class="xp4-btn xp4-btn-ghost xp4-small" href="/login">Ingresar</a>{% endif %}
    </div>
  </header>

  <main>
    <section class="xp4-hero xp4-wrap">
      <span class="xp4-kicker">FIDELIZACIÓN PARA NEGOCIOS LOCALES</span>
      <h1>Haz que tus clientes<br><em>quieran volver.</em></h1>
      <p>Exponenta convierte una visita en una relación: tus clientes acumulan beneficios, regresan con más facilidad y tú entiendes mejor qué está funcionando en tu negocio.</p>
      <div class="xp4-actions">
        <a class="xp4-btn xp4-btn-dark" href="#como">Ver cómo funciona</a>
        {% if user %}<a class="xp4-btn xp4-btn-ghost" href="/panel">Ir a mi panel</a>{% else %}<a class="xp4-btn xp4-btn-ghost" href="/login">Ya soy cliente</a>{% endif %}
      </div>
      <div class="xp4-stage" aria-label="Ejemplo de experiencia de fidelización Exponenta">
        <div class="xp4-mini xp4-mini-left"><span>★</span><b>Nueva reseña</b><small>Cliente satisfecho</small></div>
        <div class="xp4-phone">
          <div class="xp4-phonebar"><span>9:41</span><span>● ● ●</span></div>
          <div class="xp4-pass">
            <div class="xp4-passhead"><strong>CAFÉ CENTRAL</strong><small>MI CLUB</small></div>
            <div><small>HOLA, DIEGO</small><h3>Tu próxima recompensa está cerca.</h3></div>
            <div class="xp4-count"><strong>6</strong><span>de 9 visitas</span></div>
            <div class="xp4-dots">{% for i in range(9) %}<i class="{% if i < 6 %}on{% endif %}"></i>{% endfor %}</div>
            <div class="xp4-reward"><small>PRÓXIMO BENEFICIO</small><b>Tu café va por la casa</b></div>
            <div class="xp4-passbtn">Volver al negocio</div>
          </div>
        </div>
        <div class="xp4-mini xp4-mini-right"><span>+1</span><b>Visita registrada</b><small>Progreso actualizado</small></div>
      </div>
    </section>

    <section class="xp4-intro" id="beneficios">
      <div class="xp4-wrap">
        <span class="xp4-kicker">LO QUE IMPORTA</span>
        <h2>Tus clientes vuelven una y otra vez.</h2>
        <p class="xp4-sub">Nos concentramos en tres cosas que un negocio local sí puede aprovechar todos los días.</p>
        <div class="xp4-benefits">
          <article>
            <div class="xp4-copy"><span>01</span><h3>Más recurrencia.</h3><p>Una tarjeta digital de tu propia marca mantiene visible el progreso del cliente y le da una razón concreta para regresar.</p><ul><li>Visitas y sellos</li><li>Recompensas claras</li><li>Experiencia desde el celular</li></ul></div>
            <div class="xp4-visual xp4-visual-card"><div class="xp4-loyalty"><small>PROGRESO</small><b>6 de 9</b><div class="xp4-dots">{% for i in range(9) %}<i class="{% if i < 6 %}on{% endif %}"></i>{% endfor %}</div><p>3 visitas para tu recompensa</p></div></div>
          </article>
          <article class="reverse">
            <div class="xp4-copy"><span>02</span><h3>Datos que sí sirven.</h3><p>No necesitas otro sistema lleno de información que nadie consulta. Exponenta te ayuda a ver actividad real de tus clientes.</p><ul><li>Quién está regresando</li><li>Cuántas visitas acumula</li><li>Qué recompensas se entregan</li></ul></div>
            <div class="xp4-visual"><div class="xp4-metrics"><div><small>CLIENTES ACTIVOS</small><b>128</b></div><div><small>VISITAS</small><b>342</b></div><div class="wide"><small>ACTIVIDAD RECIENTE</small><p>Mariana volvió · +1 visita</p><p>Jorge obtuvo recompensa</p><p>Ana dejó una reseña</p></div></div></div>
          </article>
          <article>
            <div class="xp4-copy"><span>03</span><h3>Reputación conectada.</h3><p>La relación no termina al cobrar. Puedes facilitar que los clientes satisfechos compartan su experiencia y vuelvan a contactar al negocio.</p><ul><li>Acceso a reseñas</li><li>Contacto directo</li><li>Actividad medible</li></ul></div>
            <div class="xp4-visual"><div class="xp4-review"><div class="stars">★★★★★</div><b>¿Cómo fue tu experiencia?</b><p>Comparte tu opinión y ayuda a otros a conocernos.</p><button>Dejar mi reseña</button></div></div>
          </article>
        </div>
      </div>
    </section>

    <section class="xp4-program" id="programa">
      <div class="xp4-wrap">
        <span class="xp4-kicker light">TU PROGRAMA DE FIDELIZACIÓN</span>
        <h2>Simple para tu cliente.<br>Útil para tu negocio.</h2>
        <p>Empieza con una mecánica que todos entienden: visitar, acumular y recibir una recompensa.</p>
        <div class="xp4-programgrid">
          <article class="active"><span>01</span><h3>Tarjeta de visitas</h3><p>Cada compra o visita acerca al cliente a un beneficio definido por tu negocio.</p></article>
          <article><span>02</span><h3>Recompensas</h3><p>Define el incentivo que tenga sentido para tu margen y para el comportamiento que quieres repetir.</p></article>
          <article><span>03</span><h3>Experiencia de marca</h3><p>El cliente ve tu negocio, su progreso y su beneficio desde una experiencia móvil sencilla.</p></article>
        </div>
      </div>
    </section>

    <section class="xp4-how xp4-wrap" id="como">
      <span class="xp4-kicker">ASÍ FUNCIONA</span>
      <h2>Tu cliente lo entiende en segundos.</h2>
      <div class="xp4-steps">
        <article><b>1</b><div class="xp4-stepmock"><span>Bienvenido</span><strong>Únete al club</strong><i>Continuar</i></div><h3>Entra a tu club</h3><p>El cliente accede desde el punto de contacto de tu negocio, sin descargar una aplicación.</p></article>
        <article><b>2</b><div class="xp4-stepmock"><span>Tu tarjeta</span><strong>3 de 9 visitas</strong><i>Ver progreso</i></div><h3>Acumula progreso</h3><p>Tu equipo registra la visita y el cliente ve cómo se acerca a su siguiente beneficio.</p></article>
        <article><b>3</b><div class="xp4-stepmock"><span>Recompensa</span><strong>¡La conseguiste!</strong><i>Usar beneficio</i></div><h3>Recibe y vuelve</h3><p>La recompensa crea una razón visible para regresar y mantener la relación activa.</p></article>
      </div>
    </section>

    <section class="xp4-tools">
      <div class="xp4-wrap">
        <span class="xp4-kicker">MÁS QUE UNA TARJETA</span>
        <h2>Todo conectado alrededor del cliente.</h2>
        <div class="xp4-toolgrid">
          <article><span>★</span><h3>Reseñas</h3><p>Facilita que clientes satisfechos compartan su experiencia.</p></article>
          <article><span>↻</span><h3>Recurrencia</h3><p>Visitas, progreso, recompensas y canjes en un mismo flujo.</p></article>
          <article><span>◎</span><h3>Clientes</h3><p>Consulta actividad e historial útil para entender quién vuelve.</p></article>
          <article><span>✓</span><h3>Equipo</h3><p>Permisos y trazabilidad para operar el programa con control.</p></article>
        </div>
      </div>
    </section>

    <section class="xp4-compare xp4-wrap">
      <span class="xp4-kicker">ANTES Y DESPUÉS</span>
      <h2>De una visita aislada a una relación medible.</h2>
      <div class="xp4-comparegrid">
        <div><h3>Sin un sistema</h3><p>El cliente compra y se va</p><p>La tarjeta física se pierde</p><p>No sabes quién regresó</p><p>Pedir reseñas depende del momento</p><p>Las recompensas son difíciles de seguir</p></div>
        <div class="good"><h3>Con Exponenta</h3><p>El cliente conserva su progreso</p><p>La experiencia vive en su celular</p><p>Ves actividad y recurrencia</p><p>La reputación forma parte del flujo</p><p>Tu equipo opera con trazabilidad</p></div>
      </div>
    </section>

    <section class="xp4-faq xp4-wrap" id="faq">
      <span class="xp4-kicker">PREGUNTAS FRECUENTES</span>
      <h2>Lo esencial, sin complicarlo.</h2>
      <details open><summary>¿Qué es Exponenta?</summary><p>Una plataforma de fidelización para negocios locales que conecta recurrencia, recompensas, reseñas y datos de clientes en una sola experiencia.</p></details>
      <details><summary>¿El cliente tiene que descargar una app?</summary><p>No. La experiencia está diseñada para funcionar desde el navegador del celular.</p></details>
      <details><summary>¿Cómo entra el cliente a su tarjeta?</summary><p>El negocio puede darle acceso mediante un enlace y puntos de contacto físicos como QR o NFC. La tecnología queda detrás; para el cliente lo importante es entrar, ver su progreso y usar sus beneficios.</p></details>
      <details><summary>¿Puedo controlar lo que hacen mis empleados?</summary><p>Sí. Exponenta contempla permisos, límites operativos y trazabilidad para acciones sensibles como otorgar visitas o gestionar recompensas.</p></details>
    </section>

    <section class="xp4-final">
      <div class="xp4-wrap">
        <img src="/static/exponenta-logo.svg?v=20260925-8" alt="Exponenta">
        <span class="xp4-kicker light">CLIENTES QUE VUELVEN</span>
        <h2>Tu próxima venta puede empezar con alguien que ya te conoce.</h2>
        <p>Convierte la visita de hoy en una razón para regresar mañana.</p>
        {% if user %}<a class="xp4-btn xp4-btn-white" href="/panel">Abrir mi panel</a>{% else %}<a class="xp4-btn xp4-btn-white" href="/login">Ingresar</a>{% endif %}
      </div>
    </section>
  </main>

  <footer class="xp4-footer xp4-wrap">
    <img src="/static/exponenta-logo.svg?v=20260925-8" alt="Exponenta">
    <span>Fidelización y recurrencia para negocios locales.</span>
    <span>© 2026 Exponenta</span>
  </footer>
</div>
{% endblock %}
"""
Path("/app/app/templates/landing.html").write_text(landing, encoding="utf-8")

css_path = Path("/app/app/static/app.css")
css = css_path.read_text(encoding="utf-8")
css += r"""
/* EXPONENTA LANDING V4 — editorial loyalty layout */
.xp4{--bg:#f6f1ea;--paper:#fffdf9;--ink:#16120f;--muted:#746c64;--line:#dfd5ca;--brown:#6b3b22;--copper:#aa6338;--copper2:#ca8152;background:var(--bg);color:var(--ink);overflow:hidden}.xp4 *{box-sizing:border-box}.xp4 img{max-width:100%;height:auto}.xp4-wrap{width:min(1120px,calc(100% - 32px));margin-inline:auto}.xp4-top{background:#1a1512;color:#fff;text-align:center;padding:9px 16px;font-size:.72rem;font-weight:800;letter-spacing:.02em}.xp4-nav{position:sticky;top:0;z-index:50;background:rgba(246,241,234,.94);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid rgba(223,213,202,.8)}.xp4-navin{height:72px;display:flex;align-items:center;gap:18px}.xp4-logo{display:flex;align-items:center}.xp4-logo img{display:block;width:92px}.xp4-nav nav{display:none}.xp4-navin>.xp4-btn{margin-left:auto}.xp4-btn{min-height:48px;padding:0 21px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;font-size:.86rem;font-weight:900;border:1px solid transparent;text-decoration:none}.xp4-small{min-height:40px;padding:0 16px;font-size:.78rem}.xp4-btn-dark{background:#171310;color:#fff}.xp4-btn-ghost{background:rgba(255,255,255,.66);border-color:var(--line);color:var(--ink)}.xp4-btn-white{background:#fff;color:#23160f}.xp4-kicker{font-size:.65rem;letter-spacing:.2em;font-weight:900;color:#98735d;text-transform:uppercase}.xp4-kicker.light{color:#e7c2a8}.xp4-hero{text-align:center;padding:66px 0 70px}.xp4-hero h1{font-size:clamp(3.15rem,14vw,6.6rem);line-height:.89;letter-spacing:-.065em;margin:16px auto 22px;max-width:950px}.xp4-hero h1 em{font-style:normal;color:var(--copper)}.xp4-hero>p{max-width:720px;margin:0 auto;color:#5f5851;font-size:1.05rem;line-height:1.6}.xp4-actions{display:grid;gap:10px;max-width:420px;margin:28px auto 48px}.xp4-stage{position:relative;min-height:570px;display:grid;place-items:center;margin-top:10px}.xp4-phone{width:min(100%,355px);background:#16120f;border-radius:42px;padding:11px;box-shadow:0 32px 90px rgba(64,39,24,.2);transform:rotate(-1deg);position:relative;z-index:2}.xp4-phonebar{height:35px;color:#fff;display:flex;justify-content:space-between;align-items:center;padding:0 14px;font-size:.65rem}.xp4-pass{min-height:475px;background:linear-gradient(150deg,#4e2c1b,#96562f 58%,#c47b4b);border-radius:31px;color:#fff;text-align:left;padding:23px;display:flex;flex-direction:column;gap:23px}.xp4-passhead{display:flex;justify-content:space-between;font-size:.65rem;letter-spacing:.04em}.xp4-pass small,.xp4-loyalty small{font-size:.58rem;letter-spacing:.14em;opacity:.75}.xp4-pass h3{font-size:1.55rem;line-height:1.04;margin:5px 0;letter-spacing:-.035em}.xp4-count{display:flex;align-items:baseline;gap:8px}.xp4-count strong{font-size:3.1rem;line-height:1}.xp4-count span{font-size:.8rem;opacity:.8}.xp4-dots{display:grid;grid-template-columns:repeat(5,1fr);gap:9px}.xp4-dots i{aspect-ratio:1;border-radius:50%;border:2px solid rgba(255,255,255,.45)}.xp4-dots i.on{background:#fff;border-color:#fff}.xp4-reward{margin-top:auto;background:rgba(30,14,7,.24);border-radius:15px;padding:14px;display:grid;gap:4px}.xp4-passbtn{background:#fff;color:#2d1a10;text-align:center;padding:12px;border-radius:999px;font-weight:900;font-size:.78rem}.xp4-mini{position:absolute;background:#fff;border:1px solid var(--line);border-radius:17px;padding:12px 14px;box-shadow:0 18px 48px rgba(43,31,22,.11);display:none;grid-template-columns:auto 1fr;gap:2px 9px;text-align:left;z-index:3}.xp4-mini span{grid-row:1/3;width:36px;height:36px;display:grid;place-items:center;background:#f1e4da;border-radius:11px;color:var(--brown);font-weight:900}.xp4-mini b{font-size:.76rem}.xp4-mini small{font-size:.65rem;color:var(--muted)}.xp4-intro{background:var(--paper);padding:78px 0}.xp4-intro h2,.xp4-program h2,.xp4-how h2,.xp4-tools h2,.xp4-compare h2,.xp4-faq h2,.xp4-final h2{font-size:clamp(2.45rem,10vw,5rem);line-height:.94;letter-spacing:-.055em;margin:12px 0 16px}.xp4-sub{color:var(--muted);max-width:650px;font-size:1rem;line-height:1.6}.xp4-benefits{display:grid;gap:20px;margin-top:46px}.xp4-benefits>article{display:grid;gap:24px;padding:26px 0;border-top:1px solid var(--line)}.xp4-copy>span{font-size:.65rem;font-weight:900;color:var(--copper)}.xp4-copy h3{font-size:2rem;letter-spacing:-.04em;margin:9px 0}.xp4-copy p{color:var(--muted);line-height:1.6}.xp4-copy ul{list-style:none;padding:0;margin:20px 0 0;display:grid;gap:9px}.xp4-copy li{font-size:.82rem;font-weight:800}.xp4-copy li:before{content:"✓";color:var(--copper);margin-right:8px}.xp4-visual{min-height:320px;border-radius:28px;background:#efe5db;display:grid;place-items:center;padding:24px;overflow:hidden}.xp4-loyalty{width:min(100%,300px);background:linear-gradient(145deg,#4b2a19,#a45f36);border-radius:24px;color:#fff;padding:24px;box-shadow:0 24px 55px rgba(64,36,20,.22)}.xp4-loyalty b{display:block;font-size:2.5rem;margin:5px 0 20px}.xp4-loyalty p{font-size:.75rem;margin:18px 0 0;opacity:.82}.xp4-metrics{width:min(100%,330px);display:grid;grid-template-columns:1fr 1fr;gap:10px}.xp4-metrics>div{background:#fff;border-radius:18px;padding:18px;box-shadow:0 12px 35px rgba(40,30,22,.06)}.xp4-metrics .wide{grid-column:1/-1}.xp4-metrics small{font-size:.55rem;letter-spacing:.1em;color:#8b8178}.xp4-metrics b{display:block;font-size:2rem;margin-top:5px}.xp4-metrics p{font-size:.7rem;padding:8px 0;margin:0;border-bottom:1px solid #eee6de}.xp4-review{width:min(100%,330px);background:#fff;border-radius:22px;padding:25px;box-shadow:0 18px 50px rgba(40,30,22,.08)}.xp4-review .stars{color:var(--copper);letter-spacing:.12em;margin-bottom:18px}.xp4-review b{font-size:1.25rem}.xp4-review p{color:var(--muted);font-size:.8rem;line-height:1.5}.xp4-review button{width:100%;border:0;background:#171310;color:#fff;border-radius:999px;padding:12px;font-weight:850}.xp4-program{background:#1b1511;color:#fff;padding:78px 0}.xp4-program>div>p{color:#c7bcb2;max-width:650px}.xp4-programgrid{display:grid;gap:12px;margin-top:36px}.xp4-programgrid article{border:1px solid #41342b;border-radius:22px;padding:23px;min-height:205px;display:flex;flex-direction:column;background:#211a16}.xp4-programgrid article.active{background:linear-gradient(145deg,#6b3b22,#a96138);border-color:#a96138}.xp4-programgrid span{font-size:.62rem;opacity:.65}.xp4-programgrid h3{font-size:1.5rem;margin:auto 0 7px}.xp4-programgrid p{font-size:.83rem;line-height:1.5;color:#cfc5bc;margin:0}.xp4-programgrid .active p{color:#f2e7df}.xp4-how{padding:80px 0}.xp4-steps{display:grid;gap:14px;margin-top:40px}.xp4-steps article{background:#fff;border:1px solid var(--line);border-radius:24px;padding:20px}.xp4-steps article>b{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;background:#eee1d6;color:var(--brown);font-size:.7rem}.xp4-stepmock{height:190px;margin:18px 0;background:#f1e7de;border-radius:18px;padding:20px;display:flex;flex-direction:column;justify-content:center;text-align:center}.xp4-stepmock span{font-size:.6rem;letter-spacing:.12em;color:#8d7768}.xp4-stepmock strong{font-size:1.25rem;margin:8px 0 18px}.xp4-stepmock i{font-style:normal;background:#fff;border-radius:999px;padding:10px;font-size:.68rem;font-weight:900}.xp4-steps h3{font-size:1.35rem;margin:10px 0 6px}.xp4-steps p{color:var(--muted);font-size:.84rem;line-height:1.55;margin:0}.xp4-tools{background:#eee5dc;padding:78px 0}.xp4-toolgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:36px}.xp4-toolgrid article{background:#fff;border-radius:20px;padding:18px;min-height:175px;display:flex;flex-direction:column}.xp4-toolgrid article>span{font-size:1.15rem;color:var(--copper)}.xp4-toolgrid h3{font-size:1.1rem;margin:auto 0 5px}.xp4-toolgrid p{font-size:.75rem;line-height:1.45;color:var(--muted);margin:0}.xp4-compare{padding:80px 0}.xp4-comparegrid{display:grid;gap:12px;margin-top:36px}.xp4-comparegrid>div{background:#fff;border:1px solid var(--line);border-radius:24px;padding:23px}.xp4-comparegrid .good{background:#1c1713;color:#fff;border-color:#1c1713}.xp4-comparegrid h3{font-size:1.4rem;margin:0 0 18px}.xp4-comparegrid p{font-size:.83rem;padding:11px 0;margin:0;border-bottom:1px solid #ece4dc;color:#6f675f}.xp4-comparegrid .good p{color:#d6ccc3;border-color:#3b312a}.xp4-faq{padding:30px 0 90px}.xp4-faq details{border-top:1px solid var(--line);padding:18px 0}.xp4-faq details:last-child{border-bottom:1px solid var(--line)}.xp4-faq summary{font-weight:850;cursor:pointer;list-style:none}.xp4-faq summary::-webkit-details-marker{display:none}.xp4-faq summary:after{content:"+";float:right;color:var(--copper);font-size:1.3rem}.xp4-faq details[open] summary:after{content:"–"}.xp4-faq details p{color:var(--muted);line-height:1.55;font-size:.88rem;max-width:760px}.xp4-final{background:linear-gradient(135deg,#482817,#754226 55%,#a8643a);color:#fff;text-align:center;padding:76px 0}.xp4-final img{width:120px;filter:brightness(1.35);margin-bottom:28px}.xp4-final p{color:#ead9cd;max-width:620px;margin:0 auto 28px}.xp4-footer{padding:30px 0 42px;display:grid;gap:9px;color:#776e66}.xp4-footer img{width:94px}.xp4-footer span{font-size:.7rem}
@media(min-width:680px){.xp4-actions{display:flex;justify-content:center;max-width:none}.xp4-mini{display:grid}.xp4-mini-left{left:4%;top:130px}.xp4-mini-right{right:4%;bottom:130px}.xp4-benefits>article{grid-template-columns:1fr 1fr;align-items:center;gap:50px;padding:45px 0}.xp4-benefits>article.reverse .xp4-copy{order:2}.xp4-programgrid,.xp4-steps{grid-template-columns:repeat(3,1fr)}.xp4-comparegrid{grid-template-columns:1fr 1fr}.xp4-footer{grid-template-columns:auto 1fr auto;align-items:center}.xp4-footer span:nth-child(2){text-align:center}}
@media(min-width:900px){.xp4-wrap{width:min(1120px,calc(100% - 64px))}.xp4-navin{height:82px}.xp4-logo img{width:112px}.xp4-nav nav{display:flex;gap:24px;margin-left:auto}.xp4-nav nav a{font-size:.78rem;font-weight:800;color:#5e554e}.xp4-navin>.xp4-btn{margin-left:0}.xp4-hero{padding:88px 0 95px}.xp4-hero>p{font-size:1.15rem}.xp4-stage{min-height:620px}.xp4-phone{width:385px}.xp4-mini-left{left:10%;top:155px}.xp4-mini-right{right:10%;bottom:150px}.xp4-intro,.xp4-program,.xp4-how,.xp4-tools,.xp4-compare{padding-top:105px;padding-bottom:105px}.xp4-benefits>article{gap:80px}.xp4-copy h3{font-size:2.5rem}.xp4-visual{min-height:390px}.xp4-toolgrid{grid-template-columns:repeat(4,1fr)}.xp4-toolgrid article{min-height:210px}.xp4-faq{padding-bottom:120px}}
"""
css_path.write_text(css, encoding="utf-8")
print("Exponenta landing V4 installed")
