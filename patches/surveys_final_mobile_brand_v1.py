from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY FINAL MOBILE BRAND V1"
assert marker not in s
a=s.index("def xp_survey_business_results(")
b=s.index("\n@app.",a)
sec=s[a:b]
assert 'body=style+' in sec
assert 'return xp_survey_business_theme(' in sec
# Preserve original Pet Clinik blue palette from the existing dashboard.
needle='    body=style+\'<section class="xp-db-head">'
assert needle in sec
replacement='''    # Account label is derived from authenticated organization; never from query parameters.
    try:
        account_user,account_org,_=xp_survey_business(request,db,slug)
        account_label=esc(getattr(account_user,"email","") or "Administrador")
        business_label=esc(getattr(account_org,"name","") or p["name"])
    except HTTPException:
        account_label="Superadministrador"
        business_label=esc(p["name"])
    welcome=('<section class="xp-db-welcome" aria-label="Cuenta activa">'
      '<div><small>BIENVENIDO A TU PANEL</small><h2>'+business_label+'</h2>'
      '<p>Administrador · '+account_label+'</p></div>'
      '<span class="xp-db-active"><span aria-hidden="true">●</span> Sesión activa</span></section>')
    style=style.replace('</style>',""".xp-db-welcome{background:#fff;border:1px solid #DDEBF4;border-radius:18px;padding:17px 20px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin:8px 0 16px}.xp-db-welcome small{color:#2D71B1;font-size:11px;font-weight:800;letter-spacing:.07em}.xp-db-welcome h2{font-size:21px;margin:4px 0;color:#17324D}.xp-db-welcome p{font-size:12px;color:#5F7690;margin:0;overflow-wrap:anywhere}.xp-db-active{font-size:12px;font-weight:750;color:#257448;background:#e9f6ed;border-radius:30px;padding:8px 12px;white-space:nowrap}.xp-db-active span{font-size:11px}@media(max-width:650px){.xp-db-welcome{padding:16px;align-items:flex-start}.xp-db-actions a{min-height:44px}.xp-db-tabs a{min-height:42px}.xp-db-head{align-items:flex-start}}</style>""")
    body=style+welcome+'<section class="xp-db-head">'''
sec=sec.replace(needle,replacement,1)
s=s[:a]+sec+s[b:]
p.write_text(s+"\n"+marker+"\n",encoding="utf-8")
print("Survey dashboard branded and account welcome added; existing functionality unchanged")
