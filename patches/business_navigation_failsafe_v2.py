from pathlib import Path

base=Path("/app/app/templates/base.html")
s=base.read_text(encoding="utf-8")
marker="xp-business-nav-failsafe-v2"
if marker not in s:
    injected=r'''
<script id="xp-business-nav-failsafe-v2">
(()=> {
  const run=()=> {
    if(!location.pathname.startsWith("/negocio")) return;
    const links=[
      ["/negocio","Inicio",'<svg viewBox="0 0 24 24"><path d="m3.5 10 8.5-6.5 8.5 6.5"/><path d="M5.5 9.5V20h13V9.5M9.5 20v-6h5v6"/></svg>'],
      ["/negocio/operacion","Operación",'<svg viewBox="0 0 24 24"><path d="M4 8V5.5C4 4.67 4.67 4 5.5 4H8M16 4h2.5c.83 0 1.5.67 1.5 1.5V8M20 16v2.5c0 .83-.67 1.5-1.5 1.5H16M8 20H5.5c-.83 0-1.5-.67-1.5-1.5V16"/><path d="M8 12h8M12 8v8"/></svg>'],
      ["/negocio/lealtad","Clientes",'<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><path d="M3.5 20v-1.5a4.5 4.5 0 0 1 4.5-4.5h2a4.5 4.5 0 0 1 4.5 4.5V20M17 8h4M19 6v4"/></svg>'],
      ["/negocio/seguridad","Equipo",'<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><path d="M3.5 20v-1.5a4.5 4.5 0 0 1 4.5-4.5h2a4.5 4.5 0 0 1 4.5 4.5V20M17 10a2.5 2.5 0 1 0 0-5M18 14c1.7.2 2.8 1.25 2.8 3V20"/></svg>'],
      ["/negocio/marketing","Reseñas",'<svg viewBox="0 0 24 24"><path d="m12 3 2.65 5.37 5.93.86-4.29 4.18 1.01 5.9L12 16.53l-5.3 2.78 1.01-5.9L3.42 9.23l5.93-.86L12 3z"/></svg>'],
      ["/negocio/marca","Mi tarjeta",'<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18M7 15h4"/></svg>'],
      ["/negocio/configuracion","Mi plan",'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06-2.33 2.33-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51v.09h-3.3v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06-2.33-2.33.06-.06A1.65 1.65 0 0 0 6.5 15a1.65 1.65 0 0 0-1.51-1H4.9v-3.3h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06 2.33-2.33.06.06a1.65 1.65 0 0 0 1.82.33 1.65 1.65 0 0 0 1-1.51V4.3h3.3v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06 2.33 2.33-.06.06a1.65 1.65 0 0 0-.33 1.82 1.65 1.65 0 0 0 1.51 1h.09V14h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>']
    ];
    let target=document.querySelector("main");
    if(!target) target=document.querySelector(".business-shell, .business-page, .business-content, .page-content, .container");
    if(!target) return;
    let nav=document.getElementById("xp-universal-business-menu");
    if(!nav){
      nav=document.querySelector(".xp-business-nav");
      if(!nav){nav=document.createElement("nav");nav.className="xp-business-nav";}
    }
    nav.id="xp-universal-business-menu";
    nav.setAttribute("aria-label","Secciones del panel");
    nav.innerHTML=links.map(([href,label,icon])=>'<a href="'+href+'"><span class="xp-business-icon" aria-hidden="true">'+icon+'</span><span class="xp-business-label">'+label+'</span></a>').join("")+'<a class="xp-business-back" href="/negocio"><span aria-hidden="true">←</span><span>Volver al panel</span></a>';
    target.prepend(nav);
    document.querySelectorAll(".xp-business-nav").forEach(item=>{if(item!==nav)item.remove()});
    const current=links.slice().sort((a,b)=>b[0].length-a[0].length).find(([href])=>location.pathname===href || (href!=="/negocio" && location.pathname.startsWith(href+"/")));
    if(current){const a=[...nav.querySelectorAll("a")].find(x=>x.getAttribute("href")===current[0]); if(a)a.classList.add("active");}
    if(location.pathname==="/negocio/seguridad"){
      document.querySelectorAll("svg").forEach(svg=>{
        if(svg.closest("#xp-universal-business-menu")) return;
        if(svg.querySelector('path[d*="8.5-6.5"]')) svg.classList.add("xp-stray-house");
      });
    }
  };
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",run); else run();
})();
</script>
'''
    s=s.replace("</body>",injected+"\n</body>",1)
base.write_text(s,encoding="utf-8")

cssp=Path("/app/app/static/app.css")
css=cssp.read_text(encoding="utf-8")
if "/* XP BUSINESS NAV FAILSAFE V2 */" not in css:
    css+=r'''
/* XP BUSINESS NAV FAILSAFE V2 */
.xp-stray-house{display:none!important}
#xp-universal-business-menu .xp-business-icon svg{width:19px!important;height:19px!important;display:block!important;fill:none!important;stroke:currentColor!important;stroke-width:1.85!important;stroke-linecap:round!important;stroke-linejoin:round!important}
@media(min-width:900px){
  main:has(> #xp-universal-business-menu),.business-shell:has(> #xp-universal-business-menu),.business-page:has(> #xp-universal-business-menu),.business-content:has(> #xp-universal-business-menu),.page-content:has(> #xp-universal-business-menu),.container:has(> #xp-universal-business-menu){display:grid!important;grid-template-columns:218px minmax(0,1fr)!important;column-gap:36px!important;align-items:start!important;width:min(1240px,calc(100% - 32px))!important;margin:0 auto!important;padding-top:28px!important}
  main:has(> #xp-universal-business-menu)>#xp-universal-business-menu,.business-shell:has(> #xp-universal-business-menu)>#xp-universal-business-menu,.business-page:has(> #xp-universal-business-menu)>#xp-universal-business-menu,.business-content:has(> #xp-universal-business-menu)>#xp-universal-business-menu,.page-content:has(> #xp-universal-business-menu)>#xp-universal-business-menu,.container:has(> #xp-universal-business-menu)>#xp-universal-business-menu{grid-column:1!important;grid-row:1 / span 80!important;position:sticky!important;top:102px!important;display:flex!important;flex-direction:column!important;gap:3px!important;width:100%!important;margin:0!important;padding:9px!important;overflow:visible!important;border:1px solid #e2ddd5!important;border-radius:18px!important;background:#fff!important;box-shadow:0 10px 28px rgba(41,29,20,.05)!important}
  main:has(> #xp-universal-business-menu)>:not(#xp-universal-business-menu),.business-shell:has(> #xp-universal-business-menu)>:not(#xp-universal-business-menu),.business-page:has(> #xp-universal-business-menu)>:not(#xp-universal-business-menu),.business-content:has(> #xp-universal-business-menu)>:not(#xp-universal-business-menu),.page-content:has(> #xp-universal-business-menu)>:not(#xp-universal-business-menu),.container:has(> #xp-universal-business-menu)>:not(#xp-universal-business-menu){grid-column:2!important;min-width:0!important}
}
'''
    cssp.write_text(css,encoding="utf-8")
print("Business navigation failsafe V2 installed")
