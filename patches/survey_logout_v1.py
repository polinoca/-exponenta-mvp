from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# EXPONENTA SURVEY LOGOUT V1"
if marker not in s:
    start=s.index("def xp_survey_business_results(")
    end=s.index("\n@app.",start)
    section=s[start:end]
    needle='    return xp_survey_business_theme("Resultados · "+str(p["name"]),body,p)'
    assert needle in section,"Survey dashboard return changed"
    replacement='''    logout='<div style="display:flex;justify-content:flex-end;gap:12px;align-items:center;margin:10px 0 16px"><a href="/accesos" style="color:#2d71b1;text-decoration:none;font-weight:700">Servicios</a><form method="post" action="/logout" style="margin:0"><button type="submit" style="padding:11px 16px;border:1px solid #c9dce9;border-radius:12px;background:white;color:#2d71b1;font-weight:800;cursor:pointer">Cerrar sesión</button></form></div>'
    body=logout+body
    return xp_survey_business_theme("Resultados · "+str(p["name"]),body,p)'''
    section=section.replace(needle,replacement,1)
    s=s[:start]+section+s[end:]
    p.write_text(marker+"\n"+s,encoding="utf-8")
print("Survey dashboard logout action installed")
