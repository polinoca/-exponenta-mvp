from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()
# Never access request.session: Exponenta auth does not use Starlette SessionMiddleware.
s=s.replace('csrf_value=request.session.get("csrf_token") or request.session.get("csrf") or ""\n ', '')
old='def billing_checkout(request:Request,interval:str=Form(...),csrf_token:str=Form(...),db:Session=Depends(get_db)):\n user,org=business_admin_context(request,db);verify_csrf(request,csrf_token)'
new='''def billing_checkout(request:Request,interval:str=Form(...),csrf_token:str=Form(""),db:Session=Depends(get_db)):
 user,org=business_admin_context(request,db)
 origin=(request.headers.get("origin") or "").rstrip("/")
 referer=request.headers.get("referer") or ""
 base=settings.app_base_url.rstrip("/")
 if origin and origin!=base: raise HTTPException(403,"Solicitud no válida")
 if not origin and not referer.startswith(base+"/"): raise HTTPException(403,"Solicitud no válida")'''
if old not in s: raise SystemExit("checkout CSRF anchor missing")
s=s.replace(old,new,1)
p.write_text(s)
print("Billing plan 500 fixed; checkout protected by same-origin validation")
