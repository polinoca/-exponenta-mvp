from pathlib import Path

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
old='''    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    control_superadmin(request, db)
    verify_csrf(request, csrf_token)
    org = db.get(Organization, org_id)'''
new='''    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    control_superadmin(request, db)
    origin = (request.headers.get("origin") or "").rstrip("/")
    referer = request.headers.get("referer") or ""
    base = settings.app_base_url.rstrip("/")
    if origin and origin != base: raise HTTPException(403, "Solicitud no válida")
    if not origin and not referer.startswith(base + "/"): raise HTTPException(403, "Solicitud no válida")
    if csrf_token: verify_csrf(request, csrf_token)
    org = db.get(Organization, org_id)'''
if old not in s: raise SystemExit("password reset CSRF route anchor missing")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("Admin password reset supports authenticated same-origin form submissions")
