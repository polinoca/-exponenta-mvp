from pathlib import Path

t=Path("/app/app/templates/admin/loyalty.html")
if not t.exists(): raise SystemExit("admin loyalty template missing")
s=t.read_text(encoding="utf-8")

# Legacy admin page: keep its data markup, add a direct stylesheet hook and scoped class.
if "xp-admin-loyalty-v2" not in s:
    # This template is a standalone legacy fragment with no base.html, so it
    # never loads /static/app.css. Inject the stylesheet explicitly.
    link='<link rel="stylesheet" href="/static/app.css?v=20260927-loyalty2">'
    if "<head" in s:
        pos=s.find(">",s.find("<head"))+1
        s=s[:pos]+link+s[pos:]
    else:
        s=link+s
    if "<body" in s:
        tag_start=s.find("<body")
        tag_end=s.find(">",tag_start)
        old=s[tag_start:tag_end+1]
        if "class=" in old:
            new=old.replace('class="','class="xp-app-shell xp-admin-loyalty-v2 ',1)
        else:
            new=old[:-1]+' class="xp-app-shell xp-admin-loyalty-v2">'
        s=s[:tag_start]+new+s[tag_end+1:]
    else:
        s='<div class="xp-app-shell xp-admin-loyalty-v2">'+s+"</div>"
    t.write_text(s,encoding="utf-8")

css=Path("/app/app/static/app.css");c=css.read_text(encoding="utf-8")
if "ADMIN LOYALTY V2" not in c:
 c+=r'''
/* ADMIN LOYALTY V2 */
.xp-admin-loyalty-v2{background:#f6f3ee!important;color:#15130f!important;min-height:100vh;padding:24px!important;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important}
.xp-admin-loyalty-v2 a{color:#6d3d1f;text-decoration:none;font-weight:750}.xp-admin-loyalty-v2 a:hover{color:#a96131}
.xp-admin-loyalty-v2 h1{font-size:clamp(2.3rem,7vw,3.7rem);letter-spacing:-.05em;line-height:.95;margin:24px 0 18px}.xp-admin-loyalty-v2 h2,.xp-admin-loyalty-v2 h3{letter-spacing:-.03em}
.xp-admin-loyalty-v2 nav{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 20px}.xp-admin-loyalty-v2 nav a{display:inline-flex;align-items:center;min-height:38px;padding:0 13px;border:1px solid #ded8ce;border-radius:999px;background:#fff}
.xp-admin-loyalty-v2 table{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid #ded8ce;border-radius:18px;overflow:hidden;margin-top:18px}.xp-admin-loyalty-v2 th{background:#f2eee8;text-transform:uppercase;letter-spacing:.07em;font-size:.68rem;color:#827a71;text-align:left}.xp-admin-loyalty-v2 th,.xp-admin-loyalty-v2 td{padding:13px 14px;border-bottom:1px solid #ebe5dc}.xp-admin-loyalty-v2 tr:last-child td{border-bottom:0}.xp-admin-loyalty-v2 td{font-size:.84rem}
.xp-admin-loyalty-v2 button{min-height:40px;border:1px solid #ded8ce;border-radius:999px;background:#fff;padding:0 14px;font-weight:800}
@media(max-width:720px){.xp-admin-loyalty-v2{padding:16px!important}.xp-admin-loyalty-v2 table{display:block;overflow-x:auto;white-space:nowrap}}
'''
 css.write_text(c,encoding="utf-8")
print("Admin loyalty legacy styling upgraded")
