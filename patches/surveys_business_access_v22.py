from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# SURVEYS BUSINESS ACCESS V22"
if marker not in s:
 anchor='@app.get("/negocio/encuestas",response_class=HTMLResponse)'
 block='''@app.get("/encuestas/acceso")
def xp_survey_simple_access(request:Request,db:Session=Depends(get_db)):
    try:
        user,org=business_admin_context(request,db)
        rows=db.execute(xp_survey_sql("SELECT slug FROM xp_surveys WHERE organization_id=:org ORDER BY slug"),{"org":org.id}).mappings().all()
        if len(rows)==1:return RedirectResponse("/negocio/encuestas/"+rows[0]["slug"],status_code=303)
        if rows:return RedirectResponse("/negocio/encuestas",status_code=303)
    except Exception:pass
    return RedirectResponse("/login?next=%2Fencuestas%2Facceso",status_code=303)

'''
 assert anchor in s
 s=s.replace(anchor,block+anchor,1)
 a=s.index("def xp_survey_business_list(");b=s.index("\n@app.",a);part=s[a:b]
 target="    body='<h1>Encuestas</h1>"
 assert target in part
 part=part.replace(target,'    if len(rows)==1:return RedirectResponse("/negocio/encuestas/"+rows[0]["slug"],status_code=303)\n'+target,1)
 s=s[:a]+part+s[b:]
 p.write_text(marker+"\n"+s,encoding="utf-8")
print("Dedicated survey access and automatic single-survey dashboard routing ready")
