from pathlib import Path
import re

templates=Path("/app/app/templates/business")
links=[
    ("/negocio","Inicio"),
    ("/negocio/operacion","Operación"),
    ("/negocio/lealtad","Clientes"),
    ("/negocio/seguridad","Equipo"),
    ("/negocio/marketing","Reseñas"),
    ("/negocio/marca","Mi tarjeta"),
    ("/negocio/configuracion","Mi plan"),
]
def nav():
    return '<nav class="xp-business-nav" aria-label="Secciones del panel">' + ''.join(
        f'<a href="{href}"><span class="xp-business-label">{label}</span></a>' for href,label in links
    ) + '</nav>'

nav_re=re.compile(r'<nav\b[^>]*class=["\'][^"\']*xp-business-nav[^"\']*["\'][^>]*>.*?</nav>',re.S)
for f in templates.glob("*.html"):
    t=f.read_text(encoding="utf-8")
    # A single canonical navigation is placed *inside* main on every business page.
    # Earlier templates placed it before main, which is why it rendered as a top ribbon.
    t=nav_re.sub("",t)
    m=re.search(r'<main\b[^>]*>',t)
    if not m:
        continue
    t=t[:m.end()]+"\n  "+nav()+t[m.end():]
    f.write_text(t,encoding="utf-8")

base=Path("/app/app/templates/base.html")
t=base.read_text(encoding="utf-8")
t=t.replace('<div class="xp-app-context">', '<div class="xp-app-context"><span id="xp-section-title" class="sr-only"></span>', 1)
# The visible context remains in the header but must never be navigation.
if "xp-business-context-script" not in t:
    t=t.replace('{% block body %}{% endblock %}', '''{% block body %}{% endblock %}
<script id="xp-business-context-script">
(()=>{const p=location.pathname;const names=[
["/negocio/operacion","Operación"],["/negocio/lealtad","Clientes y lealtad"],["/negocio/seguridad","Equipo y seguridad"],["/negocio/marketing","Reseñas"],["/negocio/marca","Mi tarjeta"],["/negocio/configuracion","Mi plan"],["/negocio","Panel"]
];const found=names.find(([path])=>p===path)||names[names.length-1];
document.querySelectorAll(".xp-business-nav a").forEach(a=>{if(a.getAttribute("href")===found[0])a.classList.add("active")});
const context=document.querySelector(".xp-app-context span:not(.sr-only)");if(context&&p.startsWith("/negocio"))context.textContent=found[1];
})()
</script>''',1)
base.write_text(t,encoding="utf-8")

cssp=Path("/app/app/static/app.css")
css=cssp.read_text(encoding="utf-8")
if "/* XP BUSINESS NAVIGATION CONSOLIDATION V1 */" not in css:
    css+=r'''
/* XP BUSINESS NAVIGATION CONSOLIDATION V1 */
.sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
.xp-app-shell main:has(> .xp-business-nav){width:min(1240px,calc(100% - 32px))!important;margin:0 auto!important}
.xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav{box-sizing:border-box}
.xp-app-shell main:has(> .xp-business-nav)>nav:not(.xp-business-nav){display:none!important}
/* An uploaded client logo must stay a logo, never become a page illustration. */
.xp-app-shell main img[src*="/media/organization/"]{display:block!important;max-width:72px!important;max-height:72px!important;width:auto!important;height:auto!important;object-fit:contain!important;position:static!important;transform:none!important}
.xp-app-shell main>img[src*="/media/organization/"]{display:none!important}
@media(min-width:900px){
  .xp-app-shell main:has(> .xp-business-nav){display:grid!important;grid-template-columns:218px minmax(0,1fr)!important;column-gap:36px!important;align-items:start!important;padding-top:28px!important}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav{grid-column:1!important;grid-row:1 / span 50!important;position:sticky!important;top:102px!important;display:flex!important;flex-direction:column!important;gap:3px!important;width:100%!important;margin:0!important;padding:9px!important;overflow:visible!important;border:1px solid #e2ddd5!important;border-radius:18px!important;background:#fff!important;box-shadow:0 10px 28px rgba(41,29,20,.05)!important}
  .xp-app-shell main:has(> .xp-business-nav)>:not(.xp-business-nav){grid-column:2!important;min-width:0!important}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav a{display:flex!important;align-items:center!important;width:100%!important;min-height:45px!important;margin:0!important;padding:0 14px!important;border:0!important;border-radius:11px!important;background:transparent!important;color:#625b54!important;font-size:.78rem!important;font-weight:800!important}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav a:before{content:"";width:7px;height:7px;border-radius:50%;margin-right:11px;background:#d8d1c7!important;flex:none}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav a:hover{background:#f5f1ec!important;color:#312a25!important}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav a.active{background:#211914!important;color:#fff!important}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav a.active:before{background:#c77e4d!important}
}
@media(max-width:899px){
  .xp-app-shell main:has(> .xp-business-nav){padding-top:16px!important}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important;width:100%!important;margin:0 0 18px!important;padding:0!important;overflow:visible!important;border:0!important;background:transparent!important}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav a{display:flex!important;align-items:center!important;min-height:45px!important;padding:0 12px!important;border:1px solid #ded8ce!important;border-radius:12px!important;background:#fff!important;color:#514941!important;font-size:.72rem!important;font-weight:850!important}
  .xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav a.active{background:#211914!important;border-color:#211914!important;color:#fff!important}
}
'''
    cssp.write_text(css,encoding="utf-8")
print("Business navigation consolidated")
