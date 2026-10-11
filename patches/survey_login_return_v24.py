from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY LOGIN RETURN V24"
if marker not in s:
    start=s.index("def xp_survey_simple_access(")
    end=s.index("\n@app.",start)
    section=s[start:end]
    old='    return RedirectResponse("/login?next=%2Fencuestas%2Facceso",status_code=303)'
    assert old in section,"Survey login entry changed"
    new='''    response=RedirectResponse("/login?next=%2Fencuestas%2Facceso",status_code=303)
    response.set_cookie("xp_survey_login_return","1",max_age=600,httponly=True,secure=True,samesite="lax",path="/")
    return response'''
    section=section.replace(old,new,1)
    s=s[:start]+section+s[end:]
    s+='''
# XP SURVEY LOGIN RETURN V24
@app.middleware("http")
async def xp_survey_login_return_middleware(request:Request,call_next):
    if request.url.path in ("/panel","/negocio") and request.cookies.get("xp_survey_login_return")=="1":
        response=RedirectResponse("/encuestas/acceso",status_code=303)
        response.delete_cookie("xp_survey_login_return",path="/")
        return response
    response=await call_next(request)
    if request.url.path.startswith("/negocio/encuestas/") and request.cookies.get("xp_survey_login_return")=="1":
        response.delete_cookie("xp_survey_login_return",path="/")
    return response
'''
    p.write_text(s,encoding="utf-8")
print("Survey login return navigation installed")
