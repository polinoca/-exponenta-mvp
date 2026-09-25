from pathlib import Path

base = Path("/app/app/templates/base.html")
text = base.read_text(encoding="utf-8")
old = '<body>\n  {% block body %}{% endblock %}'
new = '''<body class="{% if request.url.path == '/' %}xp-public{% elif request.url.path == '/login' %}xp-auth{% else %}xp-app-shell{% endif %}">
  {% if request.url.path != '/' and request.url.path != '/login' %}
  <header class="xp-app-topbar">
    <div class="xp-app-topbar-inner">
      <a class="xp-app-brand" href="/panel" aria-label="Exponenta panel">
        <img src="/static/exponenta-logo.webp?v=20260925-5" alt="Exponenta">
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
css_path.write_text(css, encoding="utf-8")
print("Exponenta internal panel visual system installed")
