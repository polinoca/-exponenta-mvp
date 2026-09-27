from pathlib import Path
import re

# Give the existing superadmin navigation a calm, icon-led desktop UI.
root=Path("/app/app/templates")
svg={
"/admin":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="7" height="7" rx="1.2"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.2"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.2"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.2"/></svg>',
"/admin/negocios":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V5.7c0-.7.55-1.2 1.25-1.2h8.5c.7 0 1.25.5 1.25 1.2V21"/><path d="M15 9.5h3.8c.66 0 1.2.54 1.2 1.2V21M8 8h2M8 12h2M8 16h2"/></svg>',
"/admin/codigos":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4z"/><path d="M15 15h1M19 14v2M17 17h3v3h-3zM14 19h1"/></svg>',
"/admin/lealtad":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3v3M17 3v3M5 9h14M6.5 5h11c.83 0 1.5.67 1.5 1.5v12c0 .83-.67 1.5-1.5 1.5h-11c-.83 0-1.5-.67-1.5-1.5v-12C5 5.67 5.67 5 6.5 5z"/><path d="m9.2 14 1.8 1.7 3.8-4"/></svg>',
"/admin/control":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M4 17h16M8 4v6M16 14v6"/></svg>',
}
for f in root.rglob("*.html"):
    t=f.read_text(encoding="utf-8")
    if "side-nav" not in t or "xp-admin-icon" in t:
        continue
    for href,icon in svg.items():
        # Preserve any current CSS classes and label; install an inline, accessible decorative icon.
        pattern=r'(<a\b[^>]*\bhref=["\']'+re.escape(href)+r'["\'][^>]*>)(?!\s*<span class="xp-admin-icon")'
        t=re.sub(pattern,lambda m:m.group(1)+'<span class="xp-admin-icon" aria-hidden="true">'+icon+'</span><span class="xp-admin-label">',t)
        # Close label before closing anchor, only for links just touched (compact matching avoids nested markup changes).
        t=re.sub(r'(<span class="xp-admin-label">(?:.(?!</a>))*?)(</a>)',r'\1</span>\2',t,flags=re.S)
    # Disabled wallet keeps an icon even though it does not have a real route.
    t=re.sub(r'(<a\b[^>]*\bclass=["\'][^"\']*\bdisabled\b[^"\']*["\'][^>]*>)(?!\s*<span class="xp-admin-icon")',
      lambda m:m.group(1)+'<span class="xp-admin-icon xp-icon-wallet" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="6.5" width="17" height="12" rx="2"/><path d="M3.5 10h17M16 14h1"/></svg></span><span class="xp-admin-label">',t)
    t=re.sub(r'(<span class="xp-admin-label">(?:.(?!</a>))*?)(</a>)',r'\1</span>\2',t,flags=re.S)
    f.write_text(t,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "/* XP SUPERADMIN NAV V3 */" not in c:
    c+=r'''
/* XP SUPERADMIN NAV V3 */
.xp-app-shell .app-shell{background:#f7f7f9!important;min-height:calc(100vh - 70px)}
.xp-app-shell .app-shell .sidebar{width:276px!important;background:#fbfbfc!important;border-right:1px solid #e8e9ee!important;color:#686d7d!important;padding:28px 20px 18px!important;box-shadow:none!important}
.xp-app-shell .app-shell .sidebar .brand{display:flex!important;align-items:center!important;min-height:44px!important;margin:0 10px 34px!important;color:#242936!important}
.xp-app-shell .app-shell .sidebar .sidebar-label{margin:0 10px 13px!important;color:#a1a6b5!important;font-size:.64rem!important;letter-spacing:.13em!important;font-weight:900!important}
.xp-app-shell .app-shell .sidebar .side-nav{display:grid!important;gap:3px!important}
.xp-app-shell .app-shell .sidebar .side-nav a{display:flex!important;align-items:center!important;justify-content:flex-start!important;gap:15px!important;min-height:49px!important;margin:0!important;padding:0 12px!important;border:0!important;border-radius:12px!important;background:transparent!important;color:#696e7e!important;font-size:.88rem!important;font-weight:760!important;line-height:1.15!important;text-shadow:none!important}
.xp-app-shell .app-shell .sidebar .side-nav a:hover{background:#f0f1f5!important;color:#303540!important;transform:none!important}
.xp-app-shell .app-shell .sidebar .side-nav a.active{background:#ebedf3!important;color:#292e39!important;font-weight:900!important}
.xp-app-shell .app-shell .sidebar .side-nav a.disabled{background:transparent!important;color:#a9adba!important;cursor:default!important}
.xp-app-shell .app-shell .sidebar .side-nav a .xp-admin-icon{width:25px!important;height:25px!important;display:inline-grid!important;place-items:center!important;flex:0 0 25px!important;color:#74798a!important}
.xp-app-shell .app-shell .sidebar .side-nav a.active .xp-admin-icon{color:#3a4050!important}
.xp-app-shell .app-shell .sidebar .side-nav a .xp-admin-icon svg{display:block!important;width:22px!important;height:22px!important;overflow:visible!important}
.xp-app-shell .app-shell .sidebar .side-nav a .xp-admin-label{display:inline-flex!important;align-items:center!important;gap:7px!important;min-width:0!important}
.xp-app-shell .app-shell .sidebar .side-nav a small{color:#a8acb8!important;font-size:.54rem!important;font-weight:850!important;letter-spacing:.08em!important}
.xp-app-shell .app-shell .sidebar:after{content:"";display:block;height:1px;background:#e7e8ed;margin:28px 8px 18px}
.xp-app-shell .app-shell .sidebar .sidebar-user,.xp-app-shell .app-shell .sidebar .user-block{border-top:1px solid #e7e8ed!important;color:#696e7e!important;padding:19px 10px 0!important}
.xp-app-shell .app-shell .sidebar .sidebar-user strong,.xp-app-shell .app-shell .sidebar .user-block strong{color:#343945!important}
.xp-app-shell .app-shell .sidebar .sidebar-user a,.xp-app-shell .app-shell .sidebar .user-block a{color:#696e7e!important;background:transparent!important;border:0!important;padding:7px 0!important}
@media(max-width:800px){.xp-app-shell .app-shell .sidebar{width:100%!important;border-right:0!important;border-bottom:1px solid #e8e9ee!important;padding:16px!important}.xp-app-shell .app-shell .sidebar .brand{margin:0 8px 14px!important}.xp-app-shell .app-shell .side-nav{grid-template-columns:repeat(2,minmax(0,1fr))!important}.xp-app-shell .app-shell .sidebar:after{display:none}}
'''
 css.write_text(c,encoding="utf-8")
print("Superadmin icon navigation installed")
