from pathlib import Path

icons={
"/negocio":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="m3 10 9-7 9 7"/><path d="M5.5 9.5V20h13V9.5M9.5 20v-6h5v6"/></svg>',
"/negocio/operacion":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8V5h3M16 5h3v3M19 16v3h-3M8 19H5v-3"/><path d="M8 12h8M12 8v8"/></svg>',
"/negocio/lealtad":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 20v-1.5A4.5 4.5 0 0 1 8 14h2a4.5 4.5 0 0 1 4.5 4.5V20M17 8h4M19 6v4"/></svg>',
"/negocio/seguridad":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 20v-1.5A4.5 4.5 0 0 1 8 14h2a4.5 4.5 0 0 1 4.5 4.5V20M17 10a2.5 2.5 0 1 0 0-5M18 14c1.7.2 2.8 1.25 2.8 3V20"/></svg>',
"/negocio/marketing":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 2.7 5.4 6 .9-4.3 4.2 1 5.9-5.4-2.8-5.4 2.8 1-5.9-4.3-4.2 6-.9L12 3z"/></svg>',
"/negocio/marca":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 9h18M7 15h4"/></svg>',
"/negocio/configuracion":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .3 1.8l.1.1-2.4 2.4-.1-.1a1.65 1.65 0 0 0-1.8-.3 1.65 1.65 0 0 0-1 1.5v.1h-3.4v-.1a1.65 1.65 0 0 0-1-1.5 1.65 1.65 0 0 0-1.8.3l-.1.1-2.4-2.4.1-.1A1.65 1.65 0 0 0 6.6 15a1.65 1.65 0 0 0-1.5-1h-.1v-3.4h.1a1.65 1.65 0 0 0 1.5-1 1.65 1.65 0 0 0-.3-1.8l-.1-.1 2.4-2.4.1.1a1.65 1.65 0 0 0 1.8.3 1.65 1.65 0 0 0 1-1.5v-.1h3.4v.1a1.65 1.65 0 0 0 1 1.5 1.65 1.65 0 0 0 1.8-.3l.1-.1 2.4 2.4-.1.1a1.65 1.65 0 0 0-.3 1.8 1.65 1.65 0 0 0 1.5 1h.1V14h-.1a1.65 1.65 0 0 0-1.5 1z"/></svg>',
}
for f in Path("/app/app/templates/business").glob("*.html"):
    t=f.read_text(encoding="utf-8")
    if 'xp-business-nav' not in t:
        continue
    for href,svg in icons.items():
        needle=f'<a href="{href}"><span class="xp-business-label">'
        if needle in t:
            t=t.replace(needle, f'<a href="{href}"><span class="xp-business-icon" aria-hidden="true">{svg}</span><span class="xp-business-label">')
    f.write_text(t,encoding="utf-8")

cssp=Path("/app/app/static/app.css")
css=cssp.read_text(encoding="utf-8")
if "/* XP BUSINESS NAV ICONS + HEADER CLEANUP V1 */" not in css:
    css+=r'''
/* XP BUSINESS NAV ICONS + HEADER CLEANUP V1 */
.xp-app-shell > nav:not(.xp-business-nav),.xp-app-shell > .xp-business-nav{display:none!important}
.xp-app-shell header:not(.xp-app-topbar) nav{display:none!important}
.xp-app-shell main:has(> .xp-business-nav)>.xp-business-nav a:before{display:none!important}
.xp-business-nav .xp-business-icon{display:inline-grid!important;place-items:center!important;width:20px!important;height:20px!important;flex:0 0 20px!important;margin-right:11px!important;color:#7a7269!important}
.xp-business-nav .xp-business-icon svg{display:block!important;width:20px!important;height:20px!important}
.xp-business-nav a.active .xp-business-icon{color:#d99969!important}
@media(max-width:899px){.xp-business-nav .xp-business-icon{margin-right:8px!important;width:18px!important;height:18px!important;flex-basis:18px!important}.xp-business-nav .xp-business-icon svg{width:18px!important;height:18px!important}}
'''
    cssp.write_text(css,encoding="utf-8")
print("Business icons restored and residual header navigation hidden")
