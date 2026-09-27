from pathlib import Path
import re

icons={
"/negocio":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="m3.5 10 8.5-6.5 8.5 6.5"/><path d="M5.5 9.5V20h13V9.5M9.5 20v-6h5v6"/></svg>',
"/negocio/operacion":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8V5.5C4 4.67 4.67 4 5.5 4H8M16 4h2.5c.83 0 1.5.67 1.5 1.5V8M20 16v2.5c0 .83-.67 1.5-1.5 1.5H16M8 20H5.5c-.83 0-1.5-.67-1.5-1.5V16"/><path d="M8 12h8M12 8v8"/></svg>',
"/negocio/lealtad":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 20v-1.5a4.5 4.5 0 0 1 4.5-4.5h2a4.5 4.5 0 0 1 4.5 4.5V20M17 8h4M19 6v4"/></svg>',
"/negocio/seguridad":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 20v-1.5a4.5 4.5 0 0 1 4.5-4.5h2a4.5 4.5 0 0 1 4.5 4.5V20M17 10a2.5 2.5 0 1 0 0-5M18 14c1.7.2 2.8 1.25 2.8 3V20"/></svg>',
"/negocio/marketing":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 2.65 5.37 5.93.86-4.29 4.18 1.01 5.9L12 16.53l-5.3 2.78 1.01-5.9L3.42 9.23l5.93-.86L12 3z"/></svg>',
"/negocio/marca":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5a8.5 8.5 0 1 0 0 17h1.2a1.8 1.8 0 0 0 1.65-2.53 1.8 1.8 0 0 1 1.65-2.53h.5A3.5 3.5 0 0 0 20.5 12 8.5 8.5 0 0 0 12 3.5z"/><circle cx="7.8" cy="11.2" r=".8"/><circle cx="10.5" cy="7.8" r=".8"/><circle cx="14.4" cy="7.8" r=".8"/></svg>',
"/negocio/configuracion":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06-2.33 2.33-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51v.09h-3.3v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06-2.33-2.33.06-.06A1.65 1.65 0 0 0 6.5 15a1.65 1.65 0 0 0-1.51-1H4.9v-3.3h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06 2.33-2.33.06.06a1.65 1.65 0 0 0 1.82.33 1.65 1.65 0 0 0 1-1.51V4.3h3.3v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06 2.33 2.33-.06.06a1.65 1.65 0 0 0-.33 1.82 1.65 1.65 0 0 0 1.51 1h.09V14h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
}
for f in Path("/app/app/templates/business").glob("*.html"):
    t=f.read_text(encoding="utf-8")
    if "xp-business-nav" not in t or "xp-business-icon" in t:
        continue
    for route,icon in icons.items():
        # Replace simple text link only, including links carrying class="active".
        pattern=r'(<a\b(?=[^>]*\bhref=["\']'+re.escape(route)+r'["\'])[^>]*>)([^<]+)(</a>)'
        t=re.sub(pattern,lambda m:m.group(1)+'<span class="xp-business-icon" aria-hidden="true">'+icon+'</span><span class="xp-business-label">'+m.group(2).strip()+'</span>'+m.group(3),t)
    f.write_text(t,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "/* XP BUSINESS SIDEBAR V2 */" not in c:
    c+=r'''
/* XP BUSINESS SIDEBAR V2 */
.xp-business-nav a .xp-business-icon{display:inline-grid;place-items:center;width:21px;height:21px;flex:0 0 21px}.xp-business-nav a .xp-business-icon svg{width:20px;height:20px;display:block}.xp-business-nav a .xp-business-label{min-width:0}
@media(min-width:960px){
  .business-shell:has(.xp-business-nav){display:grid!important;grid-template-columns:214px minmax(0,1fr)!important;column-gap:34px!important;align-items:start!important;max-width:1240px!important}
  .business-shell:has(.xp-business-nav)>.xp-business-nav{grid-column:1!important;grid-row:1 / span 30!important;position:sticky!important;top:101px!important;align-self:start!important;width:100%!important;margin:12px 0 0!important;padding:8px!important;display:grid!important;gap:3px!important;overflow:visible!important;border:1px solid #e3e4e9!important;border-radius:20px!important;background:#fbfbfc!important}
  .business-shell:has(.xp-business-nav)>:not(.xp-business-nav){grid-column:2!important;min-width:0!important}
  .business-shell:has(.xp-business-nav)>.xp-business-nav a{display:flex!important;align-items:center!important;gap:12px!important;min-height:45px!important;margin:0!important;padding:0 11px!important;border:0!important;border-radius:11px!important;background:transparent!important;color:#696e7e!important;font-size:.76rem!important;font-weight:780!important;white-space:normal!important}
  .business-shell:has(.xp-business-nav)>.xp-business-nav a:hover{background:#f0f1f4!important;color:#373c49!important;border-color:transparent!important}
  .business-shell:has(.xp-business-nav)>.xp-business-nav a.active{background:#ebedf3!important;color:#292e39!important;font-weight:900!important;border-color:transparent!important}
  .business-shell:has(.xp-business-nav)>.xp-business-nav a .xp-business-icon{color:#777d8e!important}
  .business-shell:has(.xp-business-nav)>.xp-business-nav a.active .xp-business-icon{color:#414857!important}
}
@media(max-width:959px){
  .xp-business-nav{width:calc(100% - 28px)!important;margin:12px auto 6px!important;padding:0!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important;overflow:visible!important}
  .xp-business-nav a{width:100%!important;min-width:0!important;min-height:47px!important;margin:0!important;padding:0 11px!important;display:flex!important;align-items:center!important;justify-content:flex-start!important;gap:9px!important;border-radius:13px!important;background:#fff!important;border:1px solid #dfd9d1!important;color:#514941!important;font-size:.69rem!important;line-height:1.1!important;white-space:normal!important}
  .xp-business-nav a.active{background:#241c17!important;color:#fff!important;border-color:#241c17!important}
  .xp-business-nav a .xp-business-icon{width:19px!important;height:19px!important;flex-basis:19px!important}
  .xp-business-nav a .xp-business-icon svg{width:19px!important;height:19px!important}
  .xp-business-nav a .xp-business-label{overflow:hidden;text-overflow:ellipsis}
}
@media(max-width:380px){.xp-business-nav{width:calc(100% - 22px)!important;gap:6px!important}.xp-business-nav a{padding:0 8px!important;font-size:.64rem!important;gap:7px!important}}
'''
    css.write_text(c,encoding="utf-8")
print("Business sidebar navigation V2 installed")
