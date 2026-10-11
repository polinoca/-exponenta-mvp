from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# SURVEY MANAGEMENT LINK V23"
if marker not in s:
 a=s.index("def xp_survey_details(");b=s.index("\n@app.",a);part=s[a:b]
 key="    body+='<div class=\"grid\">'"
 assert key in part
 part=part.replace(key,'''    if p["organization_id"]:
        body+='<div class="card"><h2>Acceso del negocio</h2><p>El correo y los controles de contraseña están en la administración de usuarios del negocio.</p><a class="btn secondary" href="/admin/control/'+str(p["organization_id"])+'">Ver usuarios y administrar acceso</a></div>'
''' + key,1)
 s=s[:a]+part+s[b:]
 p.write_text(marker+"\n"+s,encoding="utf-8")
print("Survey admin links to existing business access management")
