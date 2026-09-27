from pathlib import Path

css = Path("/app/app/static/app.css")
c = css.read_text()
if "ADMIN SIDEBAR BUTTON CONTRAST V1" not in c:
    c += r'''
/* ADMIN SIDEBAR BUTTON CONTRAST V1 */
.app-shell .sidebar .side-nav a,
.xp-app-shell .app-shell .sidebar .side-nav a{
  display:flex!important;align-items:center!important;justify-content:space-between!important;
  min-height:42px!important;padding:0 14px!important;margin:0 0 8px!important;
  border:1px solid rgba(255,255,255,.42)!important;border-radius:999px!important;
  background:#fff!important;color:#201813!important;font-weight:850!important;
  opacity:1!important;text-shadow:none!important;
}
.app-shell .sidebar .side-nav a:hover,
.xp-app-shell .app-shell .sidebar .side-nav a:hover{
  background:#f2d8c5!important;color:#3b2011!important;border-color:#e7a979!important;
}
.app-shell .sidebar .side-nav a.active,
.xp-app-shell .app-shell .sidebar .side-nav a.active{
  background:#c87643!important;color:#fff!important;border-color:#e5a270!important;
}
.app-shell .sidebar .side-nav a.disabled,
.xp-app-shell .app-shell .sidebar .side-nav a.disabled{
  background:transparent!important;color:#f7e5d9!important;border-color:rgba(255,255,255,.45)!important;
  cursor:default!important;
}
.app-shell .sidebar .side-nav a small,
.xp-app-shell .app-shell .sidebar .side-nav a small{
  color:inherit!important;opacity:.78!important;font-size:.58rem!important;font-weight:900!important;
  text-transform:uppercase!important;letter-spacing:.07em!important;
}
'''
    css.write_text(c)
print("admin sidebar button contrast fixed")
