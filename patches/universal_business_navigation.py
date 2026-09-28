from pathlib import Path

base=Path("/app/app/templates/base.html")
s=base.read_text(encoding="utf-8")
marker="xp-universal-business-menu"
if marker not in s:
    script=r'''
<script id="xp-universal-business-menu">
(()=> {
  if(!location.pathname.startsWith("/negocio")) return;
  const links=[
    ["/negocio","Inicio","⌂"],
    ["/negocio/operacion","Operación","⌁"],
    ["/negocio/lealtad","Clientes","♧"],
    ["/negocio/seguridad","Equipo","♧"],
    ["/negocio/marketing","Reseñas","☆"],
    ["/negocio/marca","Mi tarjeta","▭"],
    ["/negocio/configuracion","Mi plan","⚙"]
  ];
  const main=document.querySelector("main");
  if(!main) return;
  let nav=document.querySelector(".xp-business-nav");
  if(!nav){
    nav=document.createElement("nav");
    nav.className="xp-business-nav";
    nav.setAttribute("aria-label","Secciones del panel");
  }
  nav.id="xp-universal-business-menu";
  nav.innerHTML=links.map(([href,label,icon])=>'<a href="'+href+'"><span class="xp-business-icon" aria-hidden="true">'+icon+'</span><span class="xp-business-label">'+label+'</span></a>').join("")+'<a class="xp-business-back" href="/negocio"><span aria-hidden="true">←</span><span>Volver al panel</span></a>';
  main.prepend(nav);
  document.querySelectorAll(".xp-business-nav").forEach(item=>{if(item!==nav)item.remove()});
  const exact=links.slice().sort((a,b)=>b[0].length-a[0].length).find(([href])=>location.pathname===href || (href!=="/negocio" && location.pathname.startsWith(href+"/")));
  if(exact){const active=[...nav.querySelectorAll("a")].find(a=>a.getAttribute("href")===exact[0]);if(active)active.classList.add("active")}
})()
</script>
'''
    s=s.replace("</body>",script+"\n</body>",1)
base.write_text(s,encoding="utf-8")

cssp=Path("/app/app/static/app.css")
css=cssp.read_text(encoding="utf-8")
if "/* XP UNIVERSAL BUSINESS NAV V1 */" not in css:
 css+=r'''
/* XP UNIVERSAL BUSINESS NAV V1 */
#xp-universal-business-menu{display:flex!important}
#xp-universal-business-menu .xp-business-icon{font-size:1rem!important;line-height:1!important}
#xp-universal-business-menu .xp-business-back{margin-top:9px!important;border-top:1px solid #e4dfd8!important;border-radius:0!important;padding-top:13px!important;color:#8b6650!important}
#xp-universal-business-menu .xp-business-back span:first-child{font-size:1.1rem!important;margin-right:9px!important}
@media(min-width:900px){
  .xp-app-shell main:has(> #xp-universal-business-menu){display:grid!important;grid-template-columns:218px minmax(0,1fr)!important;column-gap:36px!important;align-items:start!important;width:min(1240px,calc(100% - 32px))!important;margin:0 auto!important;padding-top:28px!important}
  .xp-app-shell main:has(> #xp-universal-business-menu)>#xp-universal-business-menu{grid-column:1!important;grid-row:1 / span 50!important;position:sticky!important;top:102px!important;display:flex!important;flex-direction:column!important;gap:3px!important;width:100%!important;margin:0!important;padding:9px!important;overflow:visible!important;border:1px solid #e2ddd5!important;border-radius:18px!important;background:#fff!important;box-shadow:0 10px 28px rgba(41,29,20,.05)!important}
  .xp-app-shell main:has(> #xp-universal-business-menu)>:not(#xp-universal-business-menu){grid-column:2!important;min-width:0!important}
  #xp-universal-business-menu a{display:flex!important;align-items:center!important;width:100%!important;min-height:45px!important;margin:0!important;padding:0 14px!important;border:0!important;border-radius:11px!important;background:transparent!important;color:#625b54!important;font-size:.78rem!important;font-weight:800!important;text-decoration:none!important}
  #xp-universal-business-menu a:hover{background:#f5f1ec!important;color:#312a25!important}
  #xp-universal-business-menu a.active{background:#211914!important;color:#fff!important}
  #xp-universal-business-menu .xp-business-icon{display:inline-grid!important;place-items:center!important;width:20px!important;height:20px!important;flex:0 0 20px!important;margin-right:11px!important;color:currentColor!important}
}
@media(max-width:899px){
  #xp-universal-business-menu{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important;width:100%!important;margin:0 0 18px!important;padding:0!important;overflow:visible!important;border:0!important;background:transparent!important}
  #xp-universal-business-menu a{display:flex!important;align-items:center!important;min-height:45px!important;padding:0 12px!important;border:1px solid #ded8ce!important;border-radius:12px!important;background:#fff!important;color:#514941!important;font-size:.72rem!important;font-weight:850!important;text-decoration:none!important}
  #xp-universal-business-menu a.active{background:#211914!important;border-color:#211914!important;color:#fff!important}
  #xp-universal-business-menu .xp-business-icon{width:18px!important;margin-right:8px!important}
  #xp-universal-business-menu .xp-business-back{grid-column:1/-1!important;justify-content:center!important;margin-top:2px!important;padding-top:0!important;border-top:0!important}
}
'''
 cssp.write_text(css,encoding="utf-8")
print("Universal business navigation added")
