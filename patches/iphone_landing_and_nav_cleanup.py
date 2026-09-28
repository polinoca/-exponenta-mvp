from pathlib import Path
import re

base=Path("/app/app/templates/base.html")
s=base.read_text(encoding="utf-8")
s=re.sub(r'<script id="xp-universal-business-menu">.*?</script>', '', s, flags=re.S)
s=re.sub(r'<script id="xp-business-nav-failsafe-v2">.*?</script>', '', s, flags=re.S)
asset_tag='<script defer src="/static/business-navigation.js?v=3"></script>'
if 'business-navigation.js?v=3' not in s:
    if '</head>' in s:
        s=s.replace('</head>',asset_tag+'\n</head>',1)
    else:
        s += asset_tag
base.write_text(s,encoding="utf-8")

js=Path("/app/app/static/business-navigation.js")
js.write_text(r'''(()=>{const run=()=>{if(!location.pathname.startsWith("/negocio"))return;const links=[["/negocio","Inicio","⌂"],["/negocio/operacion","Operación","⊞"],["/negocio/lealtad","Clientes","♙"],["/negocio/seguridad","Equipo","♧"],["/negocio/marketing","Reseñas","☆"],["/negocio/marca","Mi tarjeta","▭"],["/negocio/configuracion","Mi plan","⚙"]];let target=document.querySelector("main")||document.querySelector(".business-shell,.business-page,.business-content,.page-content,.container");if(!target)return;let nav=document.getElementById("xp-universal-business-menu")||document.querySelector(".xp-business-nav");if(!nav){nav=document.createElement("nav");nav.className="xp-business-nav"}nav.id="xp-universal-business-menu";nav.setAttribute("aria-label","Secciones del panel");nav.innerHTML=links.map(function(x){return '<a href="'+x[0]+'"><span class="xp-business-icon" aria-hidden="true">'+x[2]+'</span><span class="xp-business-label">'+x[1]+'</span></a>'}).join("")+'<a class="xp-business-back" href="/negocio"><span aria-hidden="true">←</span><span>Volver al panel</span></a>';target.prepend(nav);document.querySelectorAll(".xp-business-nav").forEach(function(x){if(x!==nav)x.remove()});const current=links.slice().sort(function(a,b){return b[0].length-a[0].length}).find(function(x){return location.pathname===x[0]||(x[0]!=="/negocio"&&location.pathname.startsWith(x[0]+"/"))});if(current){const a=[...nav.querySelectorAll("a")].find(function(x){return x.getAttribute("href")===current[0]});if(a)a.classList.add("active")}if(location.pathname==="/negocio/seguridad")document.querySelectorAll("svg").forEach(function(x){if(!x.closest("#xp-universal-business-menu")&&x.querySelector('path[d*="8.5-6.5"]'))x.classList.add("xp-stray-house")})};document.readyState==="loading"?document.addEventListener("DOMContentLoaded",run):run()})();''',encoding="utf-8")

cssp=Path("/app/app/static/app.css")
css=cssp.read_text(encoding="utf-8")
if "/* XP IPHONE LANDING FIX V1 */" not in css:
    css+=r'''
/* XP IPHONE LANDING FIX V1 */
.xp-stray-house{display:none!important}
@media(max-width:760px){
  .xp-launch-device{min-height:520px!important;overflow:hidden!important}
  .xp-launch-phone{transform:scale(.82)!important;transform-origin:center top!important}
  .xp-launch-float{z-index:3!important;left:20px!important;right:auto!important;max-width:calc(100% - 40px)!important}
  .xp-launch-float.one{top:auto!important;bottom:26px!important}
  .xp-launch-float.two{top:26px!important;bottom:auto!important}
  .xp-launch-automation-visual{min-height:440px!important}
  .xp-launch-message{left:20px!important;right:20px!important;padding:18px!important}
  .xp-launch-message.second{top:28px!important;bottom:auto!important}
  .xp-launch-message:not(.second){top:232px!important;bottom:auto!important}
}
'''
cssp.write_text(css,encoding="utf-8")
print("Inline script cleanup and iPhone landing fixes installed")
