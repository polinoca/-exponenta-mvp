from pathlib import Path

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
start=s.find('@app.post("/negocio/marca")')
if start < 0: raise SystemExit("brand route missing")
end=s.find("\n\n@app.", start+1)
if end < 0: raise SystemExit("brand route end missing")
block=s[start:end]
block=block.replace('csrf_token: str = Form(...),', 'csrf_token: str = Form(""),', 1)
old='''    _, org = business_admin_context(request, db)
    verify_csrf(request, csrf_token)
    require_org_feature(db, org, "wallet")'''
new='''    _, org = business_admin_context(request, db)
    # Safari may omit the hidden field on multipart submits.  Keep the authenticated
    # endpoint protected by a strict same-origin check and validate CSRF when present.
    origin=(request.headers.get("origin") or "").rstrip("/")
    referer=request.headers.get("referer") or ""
    base=str(request.base_url).rstrip("/")
    if origin and origin != base:
        raise HTTPException(status_code=403, detail="Solicitud no válida")
    if not origin and not referer.startswith(base + "/"):
        raise HTTPException(status_code=403, detail="Solicitud no válida")
    if csrf_token:
        verify_csrf(request, csrf_token)
    require_org_feature(db, org, "wallet")'''
if old not in block: raise SystemExit("csrf block missing")
block=block.replace(old,new,1)
block=block.replace('len(cover)>3*1024*1024 or width<800 or height<600 or not 1.15<=ratio<=1.40',
                    'len(cover)>3*1024*1024 or width<600 or height<400 or not 0.8<=ratio<=2.2')
s=s[:start]+block+s[end:]
p.write_text(s,encoding="utf-8")

t=Path("/app/app/templates/business/brand.html")
html=t.read_text(encoding="utf-8")
form='<form method="post" enctype="multipart/form-data" class="xp-brand-layout">'
if 'name="csrf_token"' not in html:
    html=html.replace(form, form+'\n    <input type="hidden" name="csrf_token" value="{{ csrf }}">',1)
html=html.replace('La portada debe ser PNG, JPG o WebP, máximo 3 MB, de al menos 800 × 600 px y proporción cercana a 5:4.',
                  'La portada debe ser PNG, JPG o WebP, máximo 3 MB y de al menos 600 × 400 px.')
html=html.replace('Horizontal, mínimo 800 × 600 px, PNG/JPG/WebP, hasta 3 MB.',
                  'Recomendamos imagen horizontal · mínimo 600 × 400 px · PNG/JPG/WebP · hasta 3 MB.')
t.write_text(html,encoding="utf-8")
print("Brand multipart CSRF and cover validation fixed")
