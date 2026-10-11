from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY ACCESS LOOP FIX V25"
if marker not in s:
    a=s.index("def xp_survey_simple_access(")
    b=s.index("\n@app.",a)
    sec=s[a:b]
    old='''        if rows:return RedirectResponse("/negocio/encuestas",status_code=303)
    except Exception:pass'''
    new='''        if rows:return RedirectResponse("/negocio/encuestas",status_code=303)
        return HTMLResponse('<!doctype html><html lang="es"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Encuestas · Exponenta</title><body style="font-family:system-ui;max-width:540px;margin:12vh auto;padding:24px"><h1>Encuestas no está activado para este negocio</h1><p>Tu cuenta no tiene encuestas asignadas. Puedes volver a tus servicios o contactar a Exponenta.</p><a href="/accesos">Volver a servicios</a></body></html>',status_code=403)
    except HTTPException:pass'''
    assert old in sec,"Access route unexpectedly changed"
    sec=sec.replace(old,new,1)
    s=s[:a]+sec+s[b:]
    s=s.replace('''    response.set_cookie("xp_survey_login_return","1",max_age=600,httponly=True,secure=True,samesite="lax",path="/")
''','',1)
    a=s.index('@app.middleware("http")\nasync def xp_survey_login_return_middleware(')
    b=s.find('\n@app.',a)
    if b<0:b=len(s)
    s=s[:a]+s[b:]
    s+='\n'+marker+'\n'
    p.write_text(s,encoding="utf-8")
print("Survey loop fixed: authenticated users without surveys get 403, not login redirect")
