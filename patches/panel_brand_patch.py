from pathlib import Path
import re

base = Path("/app/app/templates/base.html")
text = base.read_text(encoding="utf-8")
old = '<body>\n  {% block body %}{% endblock %}'
new = '''<body class="{% if request.url.path == '/' %}xp-public{% elif request.url.path == '/login' %}xp-auth{% else %}xp-app-shell{% endif %}">
  {% if request.url.path != '/' and request.url.path != '/login' %}
  <header class="xp-app-topbar">
    <div class="xp-app-topbar-inner">
      <a class="xp-app-brand" href="/panel" aria-label="Exponenta panel">
        <img src="/static/exponenta-logo.svg?v=20260925-6" alt="Exponenta">
      </a>
      <div class="xp-app-context">
        <span>{% if request.url.path.startswith('/admin') %}Administración{% elif request.url.path.startswith('/operar') %}Operación{% else %}Panel de negocio{% endif %}</span>
        <small>Exponenta</small>
      </div>
      <a class="xp-app-site-link" href="/">Ver sitio</a>
    </div>
  </header>
  {% endif %}
  {% block body %}{% endblock %}'''
if old not in text:
    raise SystemExit("Expected base body block not found")
base.write_text(text.replace(old, new), encoding="utf-8")

css_path = Path("/app/app/static/app.css")
css = css_path.read_text(encoding="utf-8")
css += r"""
/* EXPONENTA MOBILE QA V4 */
.xp-auth .auth-shell{padding:18px;background:#f6f3ee}
.xp-auth .auth-card{gap:22px}
.xp-auth-brand{display:block;width:104px;line-height:0}
.xp-auth-brand img{display:block;width:100%;height:auto}
@media(max-width:560px){
  .xp-logo img{width:82px;max-height:58px;object-fit:contain}
  .xp-nav-inner{height:68px}
  .xp-hero{padding:44px 0 62px;gap:38px}
  .xp-hero-copy h1{font-size:clamp(2.75rem,12vw,3.25rem);line-height:.94;letter-spacing:-.055em}
  .xp-lead{font-size:1rem;line-height:1.52}
  .xp-section{padding:64px 0}
  .xp-final{padding:58px 0}
  .xp-footer img{width:92px}
}
"""
css += r"""
/* EXPONENTA APP SHELL V1 — shared visual system with commercial landing */
.xp-app-shell{--xp-bg:#f6f3ee;--xp-surface:#fff;--xp-ink:#15130f;--xp-muted:#706c64;--xp-line:#ded8ce;--xp-brown:#6d3d1f;--xp-copper:#a96131;--xp-copper2:#c47a47;background:var(--xp-bg)!important;color:var(--xp-ink)!important;min-height:100vh}
.xp-app-shell *{box-sizing:border-box}
.xp-app-topbar{position:sticky;top:0;z-index:100;background:rgba(246,243,238,.95);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-bottom:1px solid var(--xp-line)}
.xp-app-topbar-inner{width:min(1180px,calc(100% - 28px));height:70px;margin:auto;display:flex;align-items:center;gap:13px}
.xp-app-brand{display:flex;align-items:center;flex:0 0 auto}
.xp-app-brand img{display:block;width:112px;height:auto;max-height:46px;object-fit:contain}
.xp-app-context{min-width:0;padding-left:12px;border-left:1px solid var(--xp-line);display:grid;line-height:1.05}
.xp-app-context span{font-size:.78rem;font-weight:900;letter-spacing:-.01em;color:var(--xp-ink)}
.xp-app-context small{margin-top:4px;font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:#96735b;font-weight:850}
.xp-app-site-link{margin-left:auto;display:inline-flex;align-items:center;justify-content:center;min-height:38px;padding:0 14px;border:1px solid var(--xp-line);border-radius:999px;background:#fff;color:var(--xp-ink)!important;font-size:.72rem;font-weight:850;text-decoration:none!important}

/* Existing internal navigation */
.xp-app-shell nav{background:transparent}
.xp-app-shell nav a,.xp-app-shell .nav a,.xp-app-shell .tabs a{border-radius:999px;text-decoration:none}
.xp-app-shell nav a:hover,.xp-app-shell .nav a:hover,.xp-app-shell .tabs a:hover{color:var(--xp-copper)}

/* Content rhythm */
.xp-app-shell main,.xp-app-shell .container,.xp-app-shell .page,.xp-app-shell .content{width:min(1180px,calc(100% - 28px));margin-left:auto;margin-right:auto}
.xp-app-shell main{padding-top:24px;padding-bottom:52px}
.xp-app-shell h1,.xp-app-shell h2,.xp-app-shell h3{color:var(--xp-ink);letter-spacing:-.035em}
.xp-app-shell h1{font-size:clamp(2rem,9vw,3.5rem);line-height:.98;margin-bottom:12px}
.xp-app-shell h2{line-height:1.05}
.xp-app-shell p,.xp-app-shell small,.xp-app-shell .muted,.xp-app-shell .help{color:var(--xp-muted)}

/* Cards and dashboard surfaces */
.xp-app-shell .card,.xp-app-shell .panel,.xp-app-shell .box,.xp-app-shell .stat,.xp-app-shell .metric,.xp-app-shell section:not(.xp-app-topbar){border-color:var(--xp-line);border-radius:20px}
.xp-app-shell .card,.xp-app-shell .panel,.xp-app-shell .box,.xp-app-shell .stat,.xp-app-shell .metric{background:var(--xp-surface);box-shadow:0 10px 32px rgba(55,40,28,.045)}
.xp-app-shell .grid{gap:14px}
.xp-app-shell hr{border:0;border-top:1px solid var(--xp-line)}

/* Forms */
.xp-app-shell label{font-size:.76rem;font-weight:850;color:#4f4942}
.xp-app-shell input,.xp-app-shell select,.xp-app-shell textarea{width:100%;min-height:46px;border:1px solid #d8d1c7!important;border-radius:13px!important;background:#fff!important;color:var(--xp-ink)!important;padding:11px 13px!important;outline:none;box-shadow:none!important}
.xp-app-shell textarea{min-height:110px}
.xp-app-shell input:focus,.xp-app-shell select:focus,.xp-app-shell textarea:focus{border-color:var(--xp-copper)!important;box-shadow:0 0 0 3px rgba(169,97,49,.10)!important}

/* Buttons */
.xp-app-shell button,.xp-app-shell .button,.xp-app-shell .btn,.xp-app-shell input[type=submit]{min-height:44px;border-radius:999px!important;padding:0 18px;font-weight:850;border:1px solid transparent;cursor:pointer}
.xp-app-shell button:not(.secondary):not(.danger),.xp-app-shell .button:not(.secondary):not(.danger),.xp-app-shell .btn:not(.secondary):not(.danger),.xp-app-shell input[type=submit]{background:#171410;color:#fff}
.xp-app-shell .secondary,.xp-app-shell .btn-secondary{background:#fff!important;color:var(--xp-ink)!important;border-color:var(--xp-line)!important}
.xp-app-shell .danger,.xp-app-shell .btn-danger{background:#fff5f3!important;color:#8a2f25!important;border-color:#e8c7c1!important}
.xp-app-shell a{color:var(--xp-brown)}
.xp-app-shell a:hover{color:var(--xp-copper)}

/* Tables */
.xp-app-shell table{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid var(--xp-line);border-radius:16px;overflow:hidden}
.xp-app-shell th{font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;color:#827a71;background:#f2eee8;text-align:left}
.xp-app-shell th,.xp-app-shell td{padding:13px 14px;border-bottom:1px solid #ebe5dc}
.xp-app-shell tr:last-child td{border-bottom:0}
.xp-app-shell td{font-size:.84rem;color:#3f3a34}

/* Status / pills */
.xp-app-shell .badge,.xp-app-shell .pill,.xp-app-shell .tag{border-radius:999px!important;background:#efe4da;color:var(--xp-brown);font-size:.68rem;font-weight:850;padding:6px 9px}

/* Make existing dense admin tables usable on phones */
@media(max-width:720px){
  .xp-app-topbar-inner{height:66px}
  .xp-app-brand img{width:96px}
  .xp-app-context{display:none}
  .xp-app-site-link{min-height:36px;padding:0 12px}
  .xp-app-shell main,.xp-app-shell .container,.xp-app-shell .page,.xp-app-shell .content{width:min(100% - 24px,1180px)}
  .xp-app-shell main{padding-top:18px}
  .xp-app-shell h1{font-size:2.25rem}
  .xp-app-shell .grid{grid-template-columns:1fr!important}
  .xp-app-shell table{display:block;overflow-x:auto;-webkit-overflow-scrolling:touch;white-space:nowrap}
  .xp-app-shell form{max-width:100%}
  .xp-app-shell button,.xp-app-shell .button,.xp-app-shell .btn,.xp-app-shell input[type=submit]{min-height:46px}
}
@media(min-width:900px){
  .xp-app-topbar-inner{height:78px}
  .xp-app-brand img{width:132px}
  .xp-app-shell main{padding-top:34px}
}
"""

# Production login: use the approved brand asset and never expose demo credentials.
login_path = Path("/app/app/templates/login.html")
login = login_path.read_text(encoding="utf-8")
login = re.sub(
    r'<a class="brand" href="/">.*?</a>',
    '<a class="brand xp-auth-brand" href="/" aria-label="Exponenta"><img src="/static/exponenta-logo.svg?v=20260925-7" alt="Exponenta"></a>',
    login,
    count=1,
    flags=re.S,
)
login = re.sub(r'<div class="demo-box">.*?</div>', '', login, count=1, flags=re.S)
login_path.write_text(login, encoding="utf-8")


# Business Panel V1 navigation: surface the already-working modules as a coherent SaaS.
templates_dir = Path("/app/app/templates/business")
business_templates = [
    templates_dir / "dashboard.html",
    templates_dir / "loyalty.html",
    templates_dir / "marketing.html",
    templates_dir / "settings.html",
    templates_dir / "security.html",
]
nav = """<nav class="xp-business-nav" aria-label="Panel del negocio">
  <a href="/negocio">Inicio</a>
  <a href="/negocio/lealtad">Clientes y lealtad</a>
  <a href="/negocio/seguridad">Equipo</a>
  <a href="/negocio/marketing">Reseñas</a>
  <a href="/negocio/configuracion">Configuración</a>
</nav>"""
for tpl in business_templates:
    if not tpl.exists():
        continue
    t = tpl.read_text(encoding="utf-8")
    if "xp-business-nav" not in t:
        block_marker = "{% block body %}"
        if block_marker in t:
            t = t.replace(block_marker, block_marker + "\n" + nav, 1)
    tpl.write_text(t, encoding="utf-8")

css += r"""
/* BUSINESS PANEL V1 — mobile-first module navigation */
.xp-business-nav{width:min(1180px,calc(100% - 28px));margin:14px auto 0;display:flex;gap:7px;overflow-x:auto;padding:3px 0 7px;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.xp-business-nav::-webkit-scrollbar{display:none}
.xp-business-nav a{flex:0 0 auto;display:inline-flex;align-items:center;min-height:38px;padding:0 13px;border:1px solid #ded8ce;border-radius:999px;background:#fff;color:#4d443d!important;font-size:.72rem;font-weight:850;text-decoration:none!important}
.xp-business-nav a:hover{border-color:#a96131;color:#6d3d1f!important}
@media(max-width:720px){.xp-business-nav{width:calc(100% - 24px);margin-top:10px}.xp-business-nav a{min-height:36px;padding:0 12px;font-size:.7rem}}
"""

# Remove legacy business navigation buttons now replaced by xp-business-nav.
for tpl in business_templates:
    if not tpl.exists():
        continue
    t = tpl.read_text(encoding="utf-8")
    t = re.sub(
        r'(<header class="site-header">\s*<a class="brand"[^>]*>.*?</a>)\s*<div>.*?</div>(\s*</header>)',
        r'\1\2',
        t,
        count=1,
        flags=re.S,
    )
    tpl.write_text(t, encoding="utf-8")

css += r"""
/* BUSINESS PANEL V1.1 — legacy nav cleanup */
@media(max-width:720px){
  .business-shell .site-header{height:auto;min-height:58px;padding:14px 0 6px}
  .business-shell .site-header .brand{font-size:1.35rem;line-height:1.1}
}
"""

# SELF-SERVICE V1 — make the business panel understandable without training.
dashboard_path = templates_dir / "dashboard.html"
if dashboard_path.exists():
    t = dashboard_path.read_text(encoding="utf-8")
    if "xp-selfservice-start" not in t:
        nav_end = "</nav>"
        guide = r"""
<section class="xp-selfservice-start">
  <div class="xp-ss-head">
    <div><span class="xp-ss-kicker">PRIMEROS PASOS</span><h2>Deja tu programa listo en minutos.</h2></div>
    <span class="xp-ss-badge">Sin conocimientos técnicos</span>
  </div>
  <div class="xp-ss-steps">
    <a href="/negocio/configuracion"><b>1</b><span><strong>Personaliza tu negocio</strong><small>Nombre, color, logo y contacto.</small></span><i>→</i></a>
    <a href="/negocio/lealtad"><b>2</b><span><strong>Define tu recompensa</strong><small>Ejemplo: 9 visitas = 1 café gratis.</small></span><i>→</i></a>
    <a href="/negocio/seguridad"><b>3</b><span><strong>Agrega a tu equipo</strong><small>Ellos podrán registrar visitas.</small></span><i>→</i></a>
    <a href="/negocio/lealtad"><b>4</b><span><strong>Prueba como cliente</strong><small>Registra una visita y revisa la experiencia.</small></span><i>→</i></a>
  </div>
  <p class="xp-ss-note">Exponenta configura la parte técnica por detrás. Tú sólo decides cómo quieres atender y premiar a tus clientes.</p>
</section>
"""
        idx = t.find(nav_end)
        if idx >= 0:
            idx += len(nav_end)
            t = t[:idx] + guide + t[idx:]
    dashboard_path.write_text(t, encoding="utf-8")

# Add a simple live Wallet-brand preview to Settings using fields already used by Google Wallet.
settings_path = templates_dir / "settings.html"
if settings_path.exists():
    t = settings_path.read_text(encoding="utf-8")
    if "xp-wallet-branding" not in t:
        wallet_branding = r"""
<section class="xp-wallet-branding">
  <div class="xp-wallet-copy">
    <span class="xp-ss-kicker">TU TARJETA DIGITAL</span>
    <h2>Haz que se sienta como tu negocio.</h2>
    <p>Con tu logo y un color principal ya puedes tener una tarjeta reconocible. No necesitas diseñar nada.</p>
    <div class="xp-wallet-levels">
      <div class="active"><b>Simple</b><span>Logo + color de marca. Recomendado para empezar.</span></div>
      <div><b>Personalizado</b><span>Imagen de portada y arte especial. Lo habilitaremos como opción avanzada.</span></div>
    </div>
    <p class="xp-wallet-help">Consejo: usa un color oscuro o medio para que el texto se lea bien. Puedes cambiarlo después.</p>
  </div>
  <div class="xp-wallet-preview" style="--wallet-brand: {{ organization.brand_color or '#6b3b22' }}">
    <div class="xp-wallet-preview-top">
      {% if organization.logo_url %}<img src="{{ organization.logo_url }}" alt="Logo de {{ organization.name }}">{% else %}<span class="xp-wallet-logo-placeholder">{{ organization.name[:1] }}</span>{% endif %}
      <small>MI CLUB</small>
    </div>
    <h3>{{ organization.name }}</h3>
    <div class="xp-wallet-preview-progress"><strong>6</strong><span>de 9 visitas</span></div>
    <div class="xp-wallet-preview-dots">{% for i in range(9) %}<i class="{% if i < 6 %}on{% endif %}"></i>{% endfor %}</div>
    <div class="xp-wallet-preview-reward"><small>PRÓXIMA RECOMPENSA</small><b>Tu beneficio</b></div>
    <span class="xp-wallet-preview-label">Vista previa</span>
  </div>
</section>
"""
        idx = t.find("</header>")
        if idx >= 0:
            idx += len("</header>")
            t = t[:idx] + wallet_branding + t[idx:]
        else:
            block = "{% block body %}"
            t = t.replace(block, block + "\n" + wallet_branding, 1)
    settings_path.write_text(t, encoding="utf-8")

css += r"""
/* SELF-SERVICE V1 */
.xp-selfservice-start{width:min(1180px,calc(100% - 28px));margin:18px auto 26px!important;padding:22px!important;background:#fff!important;border:1px solid var(--xp-line)!important;border-radius:24px!important;box-shadow:0 12px 34px rgba(55,40,28,.05)}
.xp-ss-head{display:flex;gap:18px;justify-content:space-between;align-items:flex-start}.xp-ss-kicker{font-size:.58rem;letter-spacing:.16em;font-weight:950;color:#9a6746}.xp-ss-head h2,.xp-wallet-copy h2{font-size:1.65rem!important;margin:6px 0 0!important;letter-spacing:-.04em}.xp-ss-badge{background:#f2e8df;border-radius:999px;padding:7px 10px;font-size:.62rem;font-weight:850;color:#754426;white-space:nowrap}.xp-ss-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:20px}.xp-ss-steps a{min-width:0;display:grid;grid-template-columns:34px 1fr auto;align-items:center;gap:9px;padding:13px;border:1px solid #e3dcd3;border-radius:16px;background:#fff;color:#29231e!important;text-decoration:none!important}.xp-ss-steps a:hover{border-color:#b8784d;background:#fffaf6}.xp-ss-steps a>b{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;background:#efe1d6;color:#784425;font-size:.7rem}.xp-ss-steps a span{display:grid;min-width:0}.xp-ss-steps strong{font-size:.76rem}.xp-ss-steps small{font-size:.64rem;line-height:1.35;margin-top:3px}.xp-ss-steps i{font-style:normal;color:#a15e35}.xp-ss-note{font-size:.72rem!important;margin:14px 0 0!important;color:#81776f!important}
.xp-wallet-branding{display:grid;gap:24px;width:min(1180px,calc(100% - 28px));margin:18px auto 28px!important;padding:24px!important;background:#efe5dc!important;border:0!important;border-radius:26px!important;align-items:center}.xp-wallet-copy>p{line-height:1.55;max-width:560px}.xp-wallet-levels{display:grid;gap:8px;margin:18px 0}.xp-wallet-levels>div{display:grid;gap:2px;padding:12px 14px;border:1px solid #d9cfc5;border-radius:14px;background:rgba(255,255,255,.55)}.xp-wallet-levels>div.active{border-color:#a8643a;background:#fff}.xp-wallet-levels b{font-size:.75rem}.xp-wallet-levels span{font-size:.66rem;color:#756c64}.xp-wallet-help{font-size:.68rem!important}.xp-wallet-preview{--wallet-brand:#6b3b22;width:min(100%,320px);min-height:390px;justify-self:center;background:linear-gradient(145deg,var(--wallet-brand),color-mix(in srgb,var(--wallet-brand),#fff 24%));color:#fff;border-radius:27px;padding:21px;box-shadow:0 25px 60px rgba(63,39,25,.22);display:flex;flex-direction:column}.xp-wallet-preview-top{display:flex;align-items:center;justify-content:space-between}.xp-wallet-preview-top img{max-width:100px;max-height:42px;object-fit:contain}.xp-wallet-preview-top small{font-size:.55rem;letter-spacing:.12em}.xp-wallet-logo-placeholder{width:36px;height:36px;border-radius:11px;background:rgba(255,255,255,.92);color:var(--wallet-brand);display:grid;place-items:center;font-weight:950}.xp-wallet-preview h3{color:#fff!important;font-size:1.5rem!important;margin:30px 0 20px!important}.xp-wallet-preview-progress{display:flex;align-items:baseline;gap:7px}.xp-wallet-preview-progress strong{font-size:2.8rem}.xp-wallet-preview-progress span{font-size:.7rem;opacity:.8}.xp-wallet-preview-dots{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:15px 0}.xp-wallet-preview-dots i{aspect-ratio:1;border:1.5px solid rgba(255,255,255,.55);border-radius:50%}.xp-wallet-preview-dots i.on{background:#fff}.xp-wallet-preview-reward{margin-top:auto;background:rgba(30,15,8,.2);border-radius:13px;padding:12px;display:grid;gap:3px}.xp-wallet-preview-reward small{font-size:.52rem;letter-spacing:.09em;color:#f3e5dc}.xp-wallet-preview-reward b{font-size:.75rem}.xp-wallet-preview-label{text-align:center;font-size:.56rem;opacity:.65;margin-top:12px}
@media(max-width:820px){.xp-ss-steps{grid-template-columns:1fr 1fr}.xp-wallet-branding{width:calc(100% - 24px)}}
@media(max-width:520px){.xp-selfservice-start{width:calc(100% - 24px);padding:17px!important}.xp-ss-head{display:grid}.xp-ss-badge{justify-self:start}.xp-ss-steps{grid-template-columns:1fr}.xp-wallet-branding{padding:18px!important}.xp-wallet-preview{width:min(100%,285px);min-height:350px}}
@media(min-width:760px){.xp-wallet-branding{grid-template-columns:1fr .8fr;padding:34px!important}}
"""

# SELF-SERVICE V1.1 — remove internal MVP language and make Wallet preview respond instantly.
for tpl in business_templates:
    if tpl.exists():
        t = tpl.read_text(encoding="utf-8")
        t = t.replace(" · MVP", "").replace("MVP · ", "")
        tpl.write_text(t, encoding="utf-8")

if settings_path.exists():
    t = settings_path.read_text(encoding="utf-8")
    if "xp-wallet-live-script" not in t:
        live_script = r"""
<script id="xp-wallet-live-script">
(() => {
  const color = document.querySelector('input[name="brand_color"]');
  const logo = document.querySelector('input[name="logo_url"]');
  const preview = document.querySelector('.xp-wallet-preview');
  const logoSlot = document.querySelector('.xp-wallet-preview-top img, .xp-wallet-logo-placeholder');
  if (!preview) return;

  if (color) {
    const box = document.createElement('div');
    box.className = 'xp-color-helper';
    box.innerHTML = '<small>Elige un color parecido al de tu negocio</small><div class="xp-color-presets"></div>';
    const presets = [
      ['Café','#6b3b22'],['Negro','#171310'],['Azul','#315187'],['Verde','#315b49'],['Vino','#713b43']
    ];
    const row = box.querySelector('.xp-color-presets');
    presets.forEach(([name,value]) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'xp-color-dot'; b.title = name;
      b.style.background = value; b.setAttribute('aria-label', name);
      b.addEventListener('click', () => { color.value = value; color.dispatchEvent(new Event('input',{bubbles:true})); });
      row.appendChild(b);
    });
    color.insertAdjacentElement('afterend', box);
    const syncColor = () => preview.style.setProperty('--wallet-brand', color.value || '#6b3b22');
    color.addEventListener('input', syncColor); syncColor();
  }

  if (logo) {
    const help = document.createElement('small');
    help.className = 'xp-field-human-help';
    help.textContent = 'Tu logo aparecerá en la tarjeta. Si todavía no lo tienes listo, puedes continuar y agregarlo después.';
    logo.insertAdjacentElement('afterend', help);
    const syncLogo = () => {
      const value = logo.value.trim();
      const current = document.querySelector('.xp-wallet-preview-top img');
      if (value) {
        if (current) current.src = value;
        else if (logoSlot) {
          const img = document.createElement('img'); img.src = value; img.alt = 'Logo del negocio'; logoSlot.replaceWith(img);
        }
      }
    };
    logo.addEventListener('change', syncLogo);
  }
})();
</script>
"""
        endblock = "{% endblock %}"
        if endblock in t:
            t = t.replace(endblock, live_script + "\n" + endblock, 1)
        else:
            t += live_script
    settings_path.write_text(t, encoding="utf-8")

css += r"""
/* SELF-SERVICE V1.1 */
.xp-color-helper{display:grid;gap:7px;margin:8px 0 4px}.xp-color-helper>small,.xp-field-human-help{display:block;font-size:.64rem!important;color:#7c736b!important;line-height:1.4}.xp-color-presets{display:flex;gap:8px;align-items:center}.xp-color-dot{width:31px!important;height:31px!important;min-height:31px!important;padding:0!important;border:3px solid #fff!important;border-radius:50%!important;box-shadow:0 0 0 1px #d5ccc3!important}.xp-color-dot:focus{outline:2px solid #a96131;outline-offset:2px}
"""

# DAILY USE V1 — prioritize the four actions an owner actually needs.
for tpl in business_templates:
    if not tpl.exists():
        continue
    t = tpl.read_text(encoding="utf-8")
    t = t.replace('>Clientes y lealtad</a>', '>Clientes</a>')
    t = t.replace('>Configuración</a>', '>Más</a>')
    tpl.write_text(t, encoding="utf-8")

if dashboard_path.exists():
    t = dashboard_path.read_text(encoding="utf-8")
    if "xp-daily-actions" not in t:
        daily = r"""
<section class="xp-daily-actions">
  <div class="xp-daily-title">
    <span class="xp-ss-kicker">HOY</span>
    <h2>¿Qué quieres hacer?</h2>
  </div>
  <div class="xp-daily-grid">
    <a class="xp-daily-primary" href="/negocio/lealtad"><span class="xp-daily-icon">＋</span><span><b>Registrar visita</b><small>Busca al cliente y suma su visita.</small></span></a>
    <a href="/negocio/lealtad"><span class="xp-daily-icon">⌕</span><span><b>Buscar cliente</b><small>Consulta progreso y recompensas.</small></span></a>
    <a href="/negocio/lealtad"><span class="xp-daily-icon">★</span><span><b>Entregar recompensa</b><small>Canjea un beneficio disponible.</small></span></a>
    <a href="#resultados"><span class="xp-daily-icon">↗</span><span><b>Ver resultados</b><small>Clientes, visitas y actividad.</small></span></a>
  </div>
</section>
"""
        guide_start = t.find('<section class="xp-selfservice-start">')
        if guide_start >= 0:
            t = t[:guide_start] + daily + t[guide_start:]
        else:
            nav_end = t.find("</nav>")
            if nav_end >= 0:
                nav_end += len("</nav>")
                t = t[:nav_end] + daily + t[nav_end:]
    # Give the existing metrics area a stable jump target without depending on its markup.
    if 'id="resultados"' not in t:
        marker_candidates = ['<main', '<div class="dashboard', '<section']
        for mc in marker_candidates:
            pos = t.find(mc)
            if pos >= 0:
                # Don't alter main tag syntax; add an anchor immediately before first content candidate.
                t = t[:pos] + '<span id="resultados" class="xp-anchor"></span>' + t[pos:]
                break
    dashboard_path.write_text(t, encoding="utf-8")

css += r"""
/* DAILY USE V1 */
.xp-daily-actions{width:min(1180px,calc(100% - 28px));margin:18px auto 14px!important;padding:0!important;border:0!important;background:transparent!important}.xp-daily-title{margin-bottom:12px}.xp-daily-title h2{font-size:1.5rem!important;margin:5px 0 0!important}.xp-daily-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.xp-daily-grid>a{display:flex;align-items:center;gap:11px;min-height:84px;padding:14px;border:1px solid #dfd8cf;border-radius:18px;background:#fff;color:#28221d!important;text-decoration:none!important;box-shadow:0 7px 20px rgba(55,40,28,.035)}.xp-daily-grid>a:hover{border-color:#b87549;transform:translateY(-1px)}.xp-daily-grid>a.xp-daily-primary{background:#201914;color:#fff!important;border-color:#201914}.xp-daily-icon{flex:0 0 34px;width:34px;height:34px;display:grid;place-items:center;border-radius:11px;background:#f0e4da;color:#814b2c;font-size:1.05rem;font-weight:700}.xp-daily-primary .xp-daily-icon{background:rgba(255,255,255,.14);color:#fff}.xp-daily-grid a>span:last-child{display:grid;gap:3px}.xp-daily-grid b{font-size:.78rem}.xp-daily-grid small{font-size:.63rem;line-height:1.35;color:#7a7169}.xp-daily-primary small{color:#d6c9c0}.xp-anchor{display:block;position:relative;top:-100px;visibility:hidden}
@media(max-width:760px){.xp-daily-actions{width:calc(100% - 24px);margin-top:14px!important}.xp-daily-grid{grid-template-columns:1fr 1fr}.xp-daily-grid>a{min-height:92px;align-items:flex-start}.xp-daily-grid small{font-size:.61rem}}
@media(max-width:390px){.xp-daily-grid{grid-template-columns:1fr}.xp-daily-grid>a{min-height:72px;align-items:center}}
"""

# DAILY USE V1.1 — add plain-language orientation inside the three most-used modules.
module_guides = {
    "loyalty.html": r"""
<section class="xp-module-guide">
  <span class="xp-ss-kicker">CLIENTES</span>
  <h2>Atiende a tus clientes desde aquí.</h2>
  <p>Busca a una persona, registra su visita y entrega su recompensa cuando esté disponible.</p>
  <div class="xp-module-hints"><span><b>1</b> Encuentra al cliente</span><span><b>2</b> Registra la visita</span><span><b>3</b> Canjea cuando corresponda</span></div>
</section>
""",
    "security.html": r"""
<section class="xp-module-guide">
  <span class="xp-ss-kicker">TU EQUIPO</span>
  <h2>Decide quién puede registrar visitas.</h2>
  <p>Agrega a las personas que atienden clientes. Exponenta mantiene las protecciones técnicas por detrás.</p>
</section>
""",
    "marketing.html": r"""
<section class="xp-module-guide">
  <span class="xp-ss-kicker">RESEÑAS</span>
  <h2>Facilita que un cliente satisfecho te recomiende.</h2>
  <p>Conecta tu perfil de Google y deja que Exponenta acerque el acceso a la reseña dentro de la experiencia del cliente.</p>
</section>
"""
}
for filename, guide in module_guides.items():
    p = templates_dir / filename
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8")
    if "xp-module-guide" not in t:
        nav_end = t.find("</nav>")
        if nav_end >= 0:
            nav_end += len("</nav>")
            t = t[:nav_end] + guide + t[nav_end:]
    p.write_text(t, encoding="utf-8")

css += r"""
/* DAILY USE V1.1 — plain-language module orientation */
.xp-module-guide{width:min(1180px,calc(100% - 28px));margin:12px auto 18px!important;padding:18px 20px!important;background:#fff!important;border:1px solid #e1dad1!important;border-radius:20px!important}.xp-module-guide h2{font-size:1.35rem!important;margin:5px 0 6px!important}.xp-module-guide p{font-size:.75rem!important;line-height:1.5;margin:0!important;max-width:720px}.xp-module-hints{display:flex;flex-wrap:wrap;gap:7px;margin-top:13px}.xp-module-hints span{display:inline-flex;align-items:center;gap:6px;padding:7px 9px;border-radius:999px;background:#f3ece5;font-size:.64rem;color:#5e534b}.xp-module-hints b{width:20px;height:20px;display:grid;place-items:center;border-radius:50%;background:#fff;color:#7c4829;font-size:.6rem}
@media(max-width:720px){.xp-module-guide{width:calc(100% - 24px);padding:16px!important}.xp-module-guide h2{font-size:1.2rem!important}.xp-module-hints{display:grid}.xp-module-hints span{border-radius:12px}}
"""

# CLIENT COUNTER V1 — turn the loyalty member list into a simple point-of-sale style workflow.
loyalty_path = templates_dir / "loyalty.html"
if loyalty_path.exists():
    t = loyalty_path.read_text(encoding="utf-8")
    # Human labels only; routes and permissions remain unchanged.
    label_swaps = {
        ">Sumar sello<": ">+ Registrar visita<",
        ">Agregar sello<": ">+ Registrar visita<",
        ">Dar sello<": ">+ Registrar visita<",
        ">Canjear<": ">Entregar recompensa<",
        ">Canjear recompensa<": ">Entregar recompensa<",
    }
    for old, new in label_swaps.items():
        t = t.replace(old, new)
    if "xp-client-counter" not in t:
        counter = r"""
<section class="xp-client-counter">
  <div class="xp-counter-head">
    <div><span class="xp-ss-kicker">ATENCIÓN RÁPIDA</span><h2>Encuentra al cliente.</h2><p>Escribe su nombre, teléfono o correo. Después registra su visita o entrega una recompensa.</p></div>
  </div>
  <label class="xp-client-search">
    <span>Buscar cliente</span>
    <input id="xp-client-search" type="search" inputmode="search" autocomplete="off" placeholder="Nombre, teléfono o correo…" aria-label="Buscar cliente">
  </label>
  <div id="xp-client-empty" class="xp-client-empty" hidden>No encontramos ese cliente. Revisa el nombre o teléfono.</div>
</section>
"""
        guide_pos = t.find('<section class="xp-module-guide">')
        if guide_pos >= 0:
            guide_end = t.find("</section>", guide_pos)
            if guide_end >= 0:
                guide_end += len("</section>")
                t = t[:guide_end] + counter + t[guide_end:]
        else:
            nav_end = t.find("</nav>")
            if nav_end >= 0:
                nav_end += len("</nav>")
                t = t[:nav_end] + counter + t[nav_end:]
    if "xp-client-counter-script" not in t:
        script = r"""
<script id="xp-client-counter-script">
(() => {
  const input = document.getElementById('xp-client-search');
  if (!input) return;
  const tables = [...document.querySelectorAll('table')];
  const table = tables.find(x => /cliente|whatsapp|correo|recompensa|visita/i.test(x.innerText)) || tables[0];
  if (!table) return;
  table.classList.add('xp-client-table');
  const rows = [...table.querySelectorAll('tbody tr')];
  const empty = document.getElementById('xp-client-empty');

  // Mark the two everyday actions without changing any form behavior.
  rows.forEach(row => {
    [...row.querySelectorAll('button, input[type="submit"], a.btn, a.button')].forEach(action => {
      const text = (action.textContent || action.value || '').trim();
      if (/sello|registrar visita|agregar visita/i.test(text)) action.classList.add('xp-visit-action');
      if (/canjear|entregar recompensa/i.test(text)) action.classList.add('xp-reward-action');
    });
  });

  const filter = () => {
    const q = input.value.trim().toLocaleLowerCase('es');
    let visible = 0;
    rows.forEach(row => {
      const show = !q || row.innerText.toLocaleLowerCase('es').includes(q);
      row.hidden = !show;
      if (show) visible++;
    });
    if (empty) empty.hidden = visible !== 0;
  };
  input.addEventListener('input', filter);
})();
</script>
"""
        endblock = "{% endblock %}"
        if endblock in t:
            t = t.replace(endblock, script + "\n" + endblock, 1)
        else:
            t += script
    loyalty_path.write_text(t, encoding="utf-8")

css += r"""
/* CLIENT COUNTER V1 */
.xp-client-counter{width:min(1180px,calc(100% - 28px));margin:10px auto 18px!important;padding:20px!important;background:#201914!important;color:#fff;border:0!important;border-radius:22px!important}.xp-counter-head h2{color:#fff!important;font-size:1.55rem!important;margin:5px 0 5px!important}.xp-counter-head p{color:#cfc2b8!important;font-size:.72rem!important;margin:0 0 15px!important}.xp-client-search{display:grid;gap:6px;color:#fff!important}.xp-client-search>span{font-size:.66rem;font-weight:850}.xp-client-search input{background:#fff!important;color:#17130f!important;border:0!important;min-height:52px!important;border-radius:15px!important;font-size:1rem!important;padding:0 15px!important}.xp-client-empty{margin-top:10px;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.1);font-size:.7rem}.xp-client-table .xp-visit-action{background:#201914!important;color:#fff!important;border-color:#201914!important}.xp-client-table .xp-reward-action{background:#f1e4d9!important;color:#704126!important;border-color:#e3cdbb!important}.xp-client-table tr:not([hidden]){transition:background .15s ease}.xp-client-table tr:hover td{background:#fffaf6}
@media(max-width:720px){.xp-client-counter{width:calc(100% - 24px);padding:17px!important}.xp-client-table{white-space:normal!important}.xp-client-table td{min-width:125px}.xp-client-table button,.xp-client-table .btn,.xp-client-table input[type=submit]{width:100%;white-space:nowrap;margin:3px 0}}
"""

# OPERATOR V1 — make employee mode obvious and safe on a phone.
# Detect the existing operator template by its content/name so the patch stays compatible with the snapshot.
operator_candidates = list(Path("/app/app/templates").rglob("*.html"))
for op in operator_candidates:
    try:
        ot = op.read_text(encoding="utf-8")
    except Exception:
        continue
    is_operator = op.name.lower() in {"operator.html", "operate.html", "operation.html"} or (
        "/operar" in ot and ("sello" in ot.lower() or "visita" in ot.lower()) and "business_staff" not in ot.lower()
    )
    if not is_operator or "xp-operator-simple" in ot:
        continue
    simple = r"""
<section class="xp-operator-simple">
  <span class="xp-ss-kicker">MODO ATENCIÓN</span>
  <h1>Registra la visita del cliente.</h1>
  <p>Escanea su tarjeta o abre al cliente. Exponenta valida los límites y permisos automáticamente.</p>
  <div class="xp-operator-rule"><b>Importante</b><span>Una visita real = un registro. No necesitas hacer ningún cálculo.</span></div>
</section>
"""
    body = "{% block body %}"
    if body in ot:
        ot = ot.replace(body, body + "\n" + simple, 1)
    # Safer wording without changing form endpoints.
    ot = ot.replace(">Dar sello<", ">+ Registrar visita<").replace(">Sumar sello<", ">+ Registrar visita<").replace(">Agregar sello<", ">+ Registrar visita<")
    ot = ot.replace(">Canjear<", ">Entregar recompensa<").replace(">Canjear recompensa<", ">Entregar recompensa<")
    op.write_text(ot, encoding="utf-8")

# Add an explicit confirmation only for reward delivery, never for ordinary visits.
if loyalty_path.exists():
    t = loyalty_path.read_text(encoding="utf-8")
    if "xp-reward-confirm-script" not in t:
        confirm_script = r"""
<script id="xp-reward-confirm-script">
document.addEventListener('click', (event) => {
  const el = event.target.closest('.xp-reward-action');
  if (!el) return;
  if (!window.confirm('¿Entregar esta recompensa ahora? Esta acción quedará registrada.')) event.preventDefault();
});
</script>
"""
        endblock = "{% endblock %}"
        if endblock in t:
            t = t.replace(endblock, confirm_script + "\n" + endblock, 1)
        else:
            t += confirm_script
    loyalty_path.write_text(t, encoding="utf-8")

css += r"""
/* OPERATOR V1 */
.xp-operator-simple{width:min(720px,calc(100% - 24px));margin:16px auto 18px!important;padding:20px!important;border:0!important;border-radius:22px!important;background:#201914!important;color:#fff!important}.xp-operator-simple h1{color:#fff!important;font-size:clamp(1.8rem,8vw,2.6rem)!important;margin:6px 0 8px!important}.xp-operator-simple p{color:#d3c7be!important;font-size:.76rem!important;line-height:1.5}.xp-operator-rule{display:flex;gap:8px;align-items:flex-start;margin-top:15px;padding:11px 12px;border-radius:13px;background:rgba(255,255,255,.09);font-size:.66rem}.xp-operator-rule b{color:#fff}.xp-operator-rule span{color:#d7cbc2}
@media(max-width:520px){.xp-operator-simple{padding:17px!important}}
"""

# CUSTOMER EXPERIENCE V1 — customer-facing club pages must feel like the business, not an admin panel.
base = Path("/app/app/templates/base.html")
bt = base.read_text(encoding="utf-8")
bt = bt.replace(
    '<body class="{% if request.url.path == \'/\' %}xp-public{% elif request.url.path == \'/login\' %}xp-auth{% else %}xp-app-shell{% endif %}">',
    '<body class="{% if request.url.path == \'/\' %}xp-public{% elif request.url.path == \'/login\' %}xp-auth{% elif request.url.path.startswith(\'/club/\') or request.url.path.startswith(\'/m/\') or request.url.path.startswith(\'/wallet/mock/\') %}xp-customer{% else %}xp-app-shell{% endif %}">'
)
bt = bt.replace(
    "{% if request.url.path != '/' and request.url.path != '/login' %}",
    "{% if request.url.path != '/' and request.url.path != '/login' and not request.url.path.startswith('/club/') and not request.url.path.startswith('/m/') and not request.url.path.startswith('/wallet/mock/') %}",
    1,
)
base.write_text(bt, encoding="utf-8")

public_dir = Path("/app/app/templates/public")
join_path = public_dir / "join.html"
member_path = public_dir / "member.html"
wallet_mock_path = public_dir / "wallet_mock.html"

if join_path.exists():
    t = join_path.read_text(encoding="utf-8")
    t = t.replace(">Unirme al club<", ">Crear mi tarjeta<")
    if "xp-customer-join-intro" not in t:
        intro = r"""
<section class="xp-customer-join-intro">
  <span>CLUB DE BENEFICIOS</span>
  <h2>Tu tarjeta en menos de un minuto.</h2>
  <p>Déjanos tus datos básicos. Al terminar podrás ver tu progreso y guardar tu tarjeta digital.</p>
</section>
"""
        block = "{% block body %}"
        if block in t: t = t.replace(block, block + "\n" + intro, 1)
    join_path.write_text(t, encoding="utf-8")

if member_path.exists():
    t = member_path.read_text(encoding="utf-8")
    if "xp-customer-ready" not in t:
        ready = r"""
<section class="xp-customer-ready">
  <span>✓ TU TARJETA ESTÁ LISTA</span>
  <p>Muéstrala o usa tu QR cuando visites el negocio. Tus visitas y recompensas se actualizan aquí.</p>
</section>
"""
        block = "{% block body %}"
        if block in t: t = t.replace(block, block + "\n" + ready, 1)
    t = t.replace("MARKETING OPCIONAL", "BENEFICIOS OPCIONALES")
    t = t.replace("Activa beneficios cercanos", "Recibe beneficios cuando estés cerca")
    member_path.write_text(t, encoding="utf-8")

if wallet_mock_path.exists():
    t = wallet_mock_path.read_text(encoding="utf-8")
    t = t.replace("WALLET · DEMO", "TARJETA DIGITAL").replace("WALLET · MOCK", "TARJETA DIGITAL")
    wallet_mock_path.write_text(t, encoding="utf-8")

css += r"""
/* CUSTOMER EXPERIENCE V1 */
.xp-customer{margin:0;background:#f6f3ee;color:#181410;min-height:100vh}.xp-customer main,.xp-customer .container,.xp-customer .page,.xp-customer .content{width:min(620px,calc(100% - 24px));margin-left:auto;margin-right:auto}.xp-customer button,.xp-customer .btn,.xp-customer .button,.xp-customer input[type=submit]{min-height:50px;border-radius:999px!important;font-weight:850}.xp-customer input,.xp-customer select,.xp-customer textarea{min-height:50px;border:1px solid #d9d1c8!important;border-radius:14px!important;background:#fff!important;padding:12px 14px!important}.xp-customer-join-intro,.xp-customer-ready{width:min(620px,calc(100% - 24px));margin:18px auto 14px;padding:18px 19px;border-radius:20px;background:#fff;border:1px solid #e2dbd2}.xp-customer-join-intro>span,.xp-customer-ready>span{font-size:.58rem;letter-spacing:.13em;font-weight:950;color:#8d5532}.xp-customer-join-intro h2{font-size:1.55rem;line-height:1.02;letter-spacing:-.04em;margin:7px 0}.xp-customer-join-intro p,.xp-customer-ready p{font-size:.73rem;line-height:1.5;color:#756c64;margin:6px 0 0}.xp-customer-ready{background:#efe5dc;border-color:#ddcdbf}.xp-customer-ready>span{color:#6f4025}.xp-customer a{color:#6d3d1f}.xp-customer table{width:100%}
@media(max-width:520px){.xp-customer-join-intro,.xp-customer-ready{padding:16px}.xp-customer-join-intro h2{font-size:1.4rem}}
"""

# ONBOARDING V2 — one visible path from account creation to ready-to-operate.
if dashboard_path.exists():
    t = dashboard_path.read_text(encoding="utf-8")
    old_start = '<section class="xp-selfservice-start">'
    start = t.find(old_start)
    if start >= 0:
        end = t.find("</section>", start)
        if end >= 0:
            end += len("</section>")
            onboarding = r"""
<section class="xp-selfservice-start xp-onboarding-v2">
  <div class="xp-ss-head">
    <div><span class="xp-ss-kicker">PON TU CLUB EN MARCHA</span><h2>Configúralo una vez. Después sólo atiende clientes.</h2></div>
    <span class="xp-ss-badge">Guía paso a paso</span>
  </div>
  <div class="xp-onboarding-progress"><i></i><span>Empieza por tu marca y avanza en orden. Puedes volver cuando quieras.</span></div>
  <div class="xp-ss-steps xp-onboarding-steps">
    <a href="/negocio/configuracion"><b>1</b><span><strong>Tu marca</strong><small>Logo, color y datos básicos.</small></span><i>→</i></a>
    <a href="/negocio/lealtad"><b>2</b><span><strong>Tu recompensa</strong><small>Elige cuántas visitas y qué vas a regalar.</small></span><i>→</i></a>
    <a href="/negocio/marketing"><b>3</b><span><strong>Google y contacto</strong><small>Conecta reseñas y la forma de volver a contactarte.</small></span><i>→</i></a>
    <a href="/negocio/seguridad"><b>4</b><span><strong>Tu equipo</strong><small>Agrega a quien registrará visitas.</small></span><i>→</i></a>
    <a href="/club/{{ organization.slug }}" target="_blank" rel="noopener"><b>5</b><span><strong>Prueba como cliente</strong><small>Abre el alta y crea una tarjeta de prueba.</small></span><i>↗</i></a>
    <a href="/operar"><b>6</b><span><strong>Haz una visita de prueba</strong><small>Comprueba el flujo antes de usarlo con clientes.</small></span><i>→</i></a>
  </div>
  <div class="xp-ready-box"><span>Cuando completes estos pasos:</span><strong>Tu negocio queda listo para operar.</strong><small>QR, seguridad, registro y parte técnica quedan funcionando detrás de Exponenta.</small></div>
</section>
"""
            t = t[:start] + onboarding + t[end:]
    dashboard_path.write_text(t, encoding="utf-8")

# Settings should tell the owner exactly what is essential versus optional.
if settings_path.exists():
    t = settings_path.read_text(encoding="utf-8")
    if "xp-essential-note" not in t:
        note = r"""
<div class="xp-essential-note">
  <b>Para empezar sólo necesitas 2 cosas:</b>
  <span>tu logo y un color parecido al de tu negocio. Todo lo demás puede ajustarse después.</span>
</div>
"""
        pos = t.find('<section class="xp-wallet-branding">')
        if pos >= 0:
            insert = t.find(">", pos) + 1
            t = t[:insert] + note + t[insert:]
    settings_path.write_text(t, encoding="utf-8")

css += r"""
/* ONBOARDING V2 */
.xp-onboarding-v2 .xp-ss-steps{grid-template-columns:repeat(3,1fr)}.xp-onboarding-progress{display:flex;align-items:center;gap:9px;margin-top:16px;padding:10px 12px;border-radius:13px;background:#f7f1eb}.xp-onboarding-progress i{width:9px;height:9px;border-radius:50%;background:#a96131;box-shadow:0 0 0 4px #ead8ca}.xp-onboarding-progress span{font-size:.66rem;color:#6e6259}.xp-ready-box{display:grid;gap:3px;margin-top:14px;padding:13px 14px;border-radius:15px;background:#201914;color:#fff}.xp-ready-box span{font-size:.58rem;letter-spacing:.08em;text-transform:uppercase;color:#cdbfb5}.xp-ready-box strong{font-size:.82rem}.xp-ready-box small{font-size:.63rem;color:#cfc2b8}.xp-essential-note{grid-column:1/-1;display:flex;gap:7px;flex-wrap:wrap;padding:11px 13px;border-radius:13px;background:#fff;border:1px solid #dacbbf;margin-bottom:4px}.xp-essential-note b{font-size:.7rem;color:#6f4025}.xp-essential-note span{font-size:.68rem;color:#756b63}
@media(max-width:820px){.xp-onboarding-v2 .xp-ss-steps{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.xp-onboarding-v2 .xp-ss-steps{grid-template-columns:1fr}.xp-onboarding-progress{align-items:flex-start}}
"""

# ONBOARDING STATE V1 — derive completion from real business data, not local browser state.
main_path = Path("/app/app/main.py")
main_src = main_path.read_text(encoding="utf-8")
if '"setup_steps": setup_steps' not in main_src:
    dash_start = main_src.find('@app.get("/negocio", response_class=HTMLResponse)')
    dash_end = main_src.find('@app.get("/negocio/configuracion"', dash_start)
    if dash_start >= 0 and dash_end > dash_start:
        dash = main_src[dash_start:dash_end]
        needle = '    return render(request, "business/dashboard.html", {'
        if needle in dash and 'staff_count = ' not in dash:
            setup_code = '''    staff_count = db.scalar(
        select(func.count()).select_from(User).where(
            User.organization_id == org.id,
            User.role == Role.BUSINESS_STAFF,
            User.active.is_(True),
        )
    ) or 0
    review_connected = db.scalar(
        select(func.count()).select_from(RedirectCode).where(
            RedirectCode.organization_id == org.id,
            RedirectCode.destination_type == DestinationType.GOOGLE_REVIEW,
            RedirectCode.active.is_(True),
        )
    ) or 0
    brand_done = bool(org.logo_url)
    reward_done = bool(program and program.reward_name and program.reward_name.strip() and program.reward_name.strip().lower() != "recompensa")
    contact_done = bool(program and program.primary_cta_url and program.primary_cta_url.strip() not in {"", "https://wa.me/", "https://wa.me"})
    setup_steps = {
        "brand": brand_done,
        "reward": reward_done,
        "contact": bool(contact_done or review_connected),
        "team": staff_count > 0,
        "customer": customers > 0,
        "visit": visits > 0,
    }
    setup_completed = sum(1 for done in setup_steps.values() if done)
'''
            dash = dash.replace(needle, setup_code + needle, 1)
            dash = dash.replace('        "program": program,\n', '        "program": program,\n        "staff_count": staff_count,\n        "review_connected": bool(review_connected),\n        "setup_steps": setup_steps,\n        "setup_completed": setup_completed,\n', 1)
            main_src = main_src[:dash_start] + dash + main_src[dash_end:]
            main_path.write_text(main_src, encoding="utf-8")

# Make onboarding checklist reflect actual completion automatically.
if dashboard_path.exists():
    t = dashboard_path.read_text(encoding="utf-8")
    start = t.find('<section class="xp-selfservice-start xp-onboarding-v2">')
    if start >= 0:
        end = t.find("</section>", start)
        if end >= 0:
            end += len("</section>")
            dynamic_onboarding = r"""
<section class="xp-selfservice-start xp-onboarding-v2">
  <div class="xp-ss-head">
    <div><span class="xp-ss-kicker">PON TU CLUB EN MARCHA</span><h2>{% if setup_completed == 6 %}✓ Tu negocio está listo para operar.{% else %}Te faltan {{ 6 - setup_completed }} pasos para quedar listo.{% endif %}</h2></div>
    <span class="xp-ss-badge">{{ setup_completed }} de 6 listos</span>
  </div>
  <div class="xp-onboarding-meter" aria-label="{{ setup_completed }} de 6 pasos completos"><i style="width:{{ (setup_completed / 6 * 100)|round|int }}%"></i></div>
  <div class="xp-ss-steps xp-onboarding-steps">
    <a class="{% if setup_steps.brand %}done{% endif %}" href="/negocio/configuracion"><b>{% if setup_steps.brand %}✓{% else %}1{% endif %}</b><span><strong>Tu marca</strong><small>{% if setup_steps.brand %}Logo configurado.{% else %}Agrega tu logo y color.{% endif %}</small></span><i>→</i></a>
    <a class="{% if setup_steps.reward %}done{% endif %}" href="/negocio/lealtad"><b>{% if setup_steps.reward %}✓{% else %}2{% endif %}</b><span><strong>Tu recompensa</strong><small>{% if setup_steps.reward %}Recompensa configurada.{% else %}Define visitas y beneficio.{% endif %}</small></span><i>→</i></a>
    <a class="{% if setup_steps.contact %}done{% endif %}" href="/negocio/marketing"><b>{% if setup_steps.contact %}✓{% else %}3{% endif %}</b><span><strong>Google y contacto</strong><small>{% if setup_steps.contact %}Canal conectado.{% else %}Conecta reseñas o tu contacto.{% endif %}</small></span><i>→</i></a>
    <a class="{% if setup_steps.team %}done{% endif %}" href="/negocio/seguridad"><b>{% if setup_steps.team %}✓{% else %}4{% endif %}</b><span><strong>Tu equipo</strong><small>{% if setup_steps.team %}Equipo agregado.{% else %}Agrega a quien registrará visitas.{% endif %}</small></span><i>→</i></a>
    <a class="{% if setup_steps.customer %}done{% endif %}" href="/club/{{ organization.slug }}" target="_blank" rel="noopener"><b>{% if setup_steps.customer %}✓{% else %}5{% endif %}</b><span><strong>Prueba como cliente</strong><small>{% if setup_steps.customer %}Ya existe una tarjeta.{% else %}Crea una tarjeta de prueba.{% endif %}</small></span><i>↗</i></a>
    <a class="{% if setup_steps.visit %}done{% endif %}" href="/operar"><b>{% if setup_steps.visit %}✓{% else %}6{% endif %}</b><span><strong>Visita de prueba</strong><small>{% if setup_steps.visit %}Registro comprobado.{% else %}Registra la primera visita.{% endif %}</small></span><i>→</i></a>
  </div>
  {% if setup_completed == 6 %}
  <div class="xp-ready-box xp-ready-complete"><span>CONFIGURACIÓN COMPLETA</span><strong>✓ Tu negocio está listo para recibir clientes.</strong><small>Desde ahora puedes concentrarte en registrar visitas, entregar recompensas y revisar resultados.</small></div>
  {% else %}
  <div class="xp-ready-box"><span>SIGUIENTE OBJETIVO</span><strong>Completa los pasos pendientes.</strong><small>Exponenta marcará cada uno automáticamente cuando detecte que ya quedó configurado.</small></div>
  {% endif %}
</section>
"""
            t = t[:start] + dynamic_onboarding + t[end:]
    dashboard_path.write_text(t, encoding="utf-8")

css += r"""
/* ONBOARDING STATE V1 */
.xp-onboarding-meter{height:7px;margin:13px 0 15px;border-radius:999px;background:#eadfd5;overflow:hidden}.xp-onboarding-meter i{display:block;height:100%;border-radius:inherit;background:#8a4d2b;transition:width .3s ease}.xp-onboarding-steps>a.done{background:#f3eee8!important;border-color:#d8c6b7!important}.xp-onboarding-steps>a.done>b{background:#6b3b22!important;color:#fff!important}.xp-onboarding-steps>a.done strong{color:#57321f}.xp-ready-complete{background:#57351f!important}
"""
css_path.write_text(css, encoding="utf-8")
print("Exponenta internal panel visual system installed")
