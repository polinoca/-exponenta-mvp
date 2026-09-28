from pathlib import Path
js=Path("/app/app/static/business-navigation.js")
s=js.read_text(encoding="utf-8")
marker="xp-business-residual-cleanup-v4"
if marker not in s:
    s+=r'''
/* xp-business-residual-cleanup-v4 */
;(()=>{const clean=()=>{if(!location.pathname.startsWith("/negocio"))return;document.querySelectorAll("body *").forEach(function(el){if(el.children.length)return;const t=(el.textContent||"").replace(/\s+/g," ").trim();if(/^(Café Exponenta prueba|Lealtad MVP)$/i.test(t)){el.style.setProperty("display","none","important")}});document.querySelectorAll("svg").forEach(function(svg){const r=svg.getBoundingClientRect();if(r.width>70&&r.height>70&&!svg.closest("#xp-universal-business-menu"))svg.style.setProperty("display","none","important")})};document.readyState==="loading"?document.addEventListener("DOMContentLoaded",clean):clean()})();
'''
    js.write_text(s,encoding="utf-8")

cssp=Path("/app/app/static/app.css")
css=cssp.read_text(encoding="utf-8")
if "/* XP BUSINESS SIDEBAR ALIGNMENT V4 */" not in css:
    css+=r'''
/* XP BUSINESS SIDEBAR ALIGNMENT V4 */
@media(min-width:900px){
  #xp-universal-business-menu{position:fixed!important;z-index:60!important;top:118px!important;left:max(22px,calc((100vw - 1380px)/2))!important;width:214px!important;margin:0!important;padding:9px!important;display:flex!important;flex-direction:column!important;gap:3px!important;border:1px solid #e2ddd5!important;border-radius:18px!important;background:#fff!important;box-shadow:0 10px 28px rgba(41,29,20,.08)!important}
  #xp-universal-business-menu+.xp-business-nav{display:none!important}
}
'''
    cssp.write_text(css,encoding="utf-8")
print("Business residual cleanup and sidebar alignment installed")
