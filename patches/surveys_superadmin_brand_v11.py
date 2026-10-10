from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY SUPERADMIN EXPONENTA BRAND V11"
if marker not in s:
    anchor='@app.get("/admin/encuestas",response_class=HTMLResponse)'
    if anchor not in s: raise SystemExit("Missing surveys admin route")
    add=r'''
# XP SURVEY SUPERADMIN EXPONENTA BRAND V11
_xp_survey_page_original=xp_survey_page
def xp_survey_page(title,body,admin=False):
    page=_xp_survey_page_original(title,body,admin=admin)
    if not admin:
        return page
    theme=r"""<style id="xp-exponenta-admin-theme">
    :root{color-scheme:light}
    body{background:#f7f3ee!important;color:#34251f!important}
    header{background:#fffaf5!important;border-bottom:1px solid #e6d8ce!important;box-shadow:0 5px 26px rgba(64,40,28,.05)}
    header strong{font-size:19px;letter-spacing:.09em;color:#70432e!important}
    header a{color:#995e3d!important}
    h1,h2,h3{color:#4b2e24!important}
    .card{background:#fffdfb!important;border-color:#e8ddd4!important;box-shadow:0 8px 28px rgba(60,35,20,.035)}
    .btn:not(.secondary){background:#73452f!important;color:#fff!important}
    .btn.secondary,.secondary{background:#f1e4da!important;color:#6c3f2b!important}
    .metric{background:#f1e8df!important;color:#513527!important}
    .metric strong{color:#885336!important}
    input:focus,select:focus,textarea:focus{outline:2px solid #b87954;outline-offset:2px;border-color:#b87954}
    a{color:#8b5133}
    .muted,.footer{color:#766a62!important}
    th{color:#553a2c!important;background:#f8f1eb}
    th,td{border-color:#e8ddd4!important}
    .radio-row input:checked+span{background:#e8d3c1!important;border-color:#995e3d!important;color:#563424!important}
    </style>"""
    return page.replace("</head>",theme+"</head>",1)
'''
    s=s.replace(anchor,add+"\n"+anchor,1)
    p.write_text(s,encoding="utf-8")
print("Exponenta copper/coffee palette applied to Surveys Superadmin only")
