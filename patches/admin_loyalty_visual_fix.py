from pathlib import Path
t=Path("/app/app/templates/admin/loyalty.html")
if not t.exists(): raise SystemExit("admin loyalty template missing")
s=t.read_text(encoding="utf-8")
if "xp-admin-loyalty-v2" not in s:
 b=s.find("{% block body %}"); e=s.rfind("{% endblock %}")
 if b<0 or e<0: raise SystemExit("loyalty body block missing")
 inner=s[b+len("{% block body %}"):e]
 wrapped='''{% block body %}<main class="xp-admin-loyalty-v2"><nav class="xp-admin-nav" aria-label="Administración"><a href="/admin">Resumen</a><a href="/admin/negocios">Negocios</a><a href="/admin/qr">QR / NFC</a><a class="active" href="/admin/lealtad">Lealtad</a><a href="/admin/wallet">Wallet</a><a href="/admin/control">Control de clientes</a></nav><header class="xp-admin-page-head"><div><span class="eyebrow">PLATAFORMA</span><h1>Lealtad</h1><p>Vista general de clientes, membresías, visitas y programas.</p></div></header><div class="xp-admin-loyalty-legacy">'''+inner+'''</div></main>{% endblock %}'''
 s=s[:b]+wrapped+s[e+len("{% endblock %}"):]
 t.write_text(s,encoding="utf-8")
css=Path("/app/app/static/app.css");c=css.read_text(encoding="utf-8")
if "ADMIN LOYALTY V2" not in c:
 c+=r'''/* ADMIN LOYALTY V2 */
.xp-admin-loyalty-v2{width:min(1180px,calc(100% - 28px));margin:auto;padding:20px 0 52px}.xp-admin-nav{display:flex;gap:7px;overflow-x:auto;padding:2px 0 12px;scrollbar-width:none}.xp-admin-nav::-webkit-scrollbar{display:none}.xp-admin-nav a{flex:0 0 auto;display:inline-flex;align-items:center;min-height:38px;padding:0 13px;border:1px solid #ded8ce;border-radius:999px;background:#fff;color:#4d443d!important;font-size:.7rem;font-weight:850;text-decoration:none!important}.xp-admin-nav a.active{background:#9a5a38!important;border-color:#9a5a38!important;color:#fff!important}.xp-admin-page-head{padding:18px 0 14px}.xp-admin-page-head h1{font-size:clamp(2.2rem,7vw,3.5rem);margin:4px 0 8px}.xp-admin-page-head p{margin:0}.xp-admin-loyalty-legacy>header,.xp-admin-loyalty-legacy>nav{display:none!important}.xp-admin-loyalty-legacy table{margin-top:14px}.xp-admin-loyalty-legacy th,.xp-admin-loyalty-legacy td{vertical-align:middle}@media(max-width:720px){.xp-admin-loyalty-v2{width:calc(100% - 24px);padding-top:12px}.xp-admin-page-head{padding-top:10px}.xp-admin-loyalty-legacy table{display:block;overflow-x:auto;white-space:nowrap}}'''
 css.write_text(c,encoding="utf-8")
print("Admin loyalty visual shell upgraded")
