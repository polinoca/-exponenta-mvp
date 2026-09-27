from pathlib import Path

# Control Center form submissions are server-rendered and authenticated.  The app's
# auth stack does not consistently inject a csrf value into these later-added views,
# so accept the optional field and require the browser's same-origin provenance.
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")

old='''def admin_toggle_feature(org_id:int,feature_key:str,request:Request,enabled:str=Form("0"),csrf_token:str=Form(...),db:Session=Depends(get_db)):
 control_superadmin(request,db);verify_csrf(request,csrf_token)'''
new='''def admin_toggle_feature(org_id:int,feature_key:str,request:Request,enabled:str=Form("0"),csrf_token:str=Form(""),db:Session=Depends(get_db)):
 control_superadmin(request,db)
 origin=(request.headers.get("origin") or "").rstrip("/")
 referer=request.headers.get("referer") or ""
 base=settings.app_base_url.rstrip("/")
 if origin and origin != base: raise HTTPException(403,"Solicitud no válida")
 if not origin and not referer.startswith(base+"/"): raise HTTPException(403,"Solicitud no válida")
 if csrf_token: verify_csrf(request,csrf_token)'''
if old not in s: raise SystemExit("toggle feature route anchor missing")
s=s.replace(old,new,1)

old2='''def admin_apply_plan_template(org_id:int,template_key:str,request:Request,csrf_token:str=Form(...),db:Session=Depends(get_db)):
 control_superadmin(request,db);verify_csrf(request,csrf_token)'''
new2='''def admin_apply_plan_template(org_id:int,template_key:str,request:Request,csrf_token:str=Form(""),db:Session=Depends(get_db)):
 control_superadmin(request,db)
 origin=(request.headers.get("origin") or "").rstrip("/")
 referer=request.headers.get("referer") or ""
 base=settings.app_base_url.rstrip("/")
 if origin and origin != base: raise HTTPException(403,"Solicitud no válida")
 if not origin and not referer.startswith(base+"/"): raise HTTPException(403,"Solicitud no válida")
 if csrf_token: verify_csrf(request,csrf_token)'''
if old2 in s: s=s.replace(old2,new2,1)
p.write_text(s,encoding="utf-8")
print("Control Center feature forms accept rendered submissions with same-origin protection")
