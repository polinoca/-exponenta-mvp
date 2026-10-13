from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP CONNECT PAY BRAND FINISH V2"
if marker not in s:
    # Reuse the existing Connect Pay routes, preserving account data.
    a=s.index('@app.get("/pagar/{slug}",response_class=HTMLResponse)')
    b=s.index('@app.get("/admin/connect/{slug}/pagos",response_class=HTMLResponse)',a)
    block=s[a:b]
    block=block.replace('    xp_pay_setup(db)\n    profile=', '''    xp_pay_setup(db)
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_bank_accounts ADD COLUMN IF NOT EXISTS bank_logo_data TEXT"))
    db.commit()
    profile=''',1)
    block=block.replace('        cards+=f\'<section class="card"><h2>{h(a["bank"])}</h2>{fields}</section>\'', '''        bank_logo=a.get("bank_logo_data") or ""
        bank_icon=f'<img class="bank-logo" alt="" src="{h(bank_logo)}">' if str(bank_logo).startswith("data:image/") else '<span class="bank-logo-empty" aria-hidden="true"></span>'
        cards+=f'<section class="card"><div class="bank-heading">{bank_icon}<h2>{h(a["bank"])}</h2></div>{fields}</section>\\''''.replace("\\'","'"))
    block=block.replace('<h1>NAME</h1>','')
    block=block.replace('button{background:#222;color:white;', 'button{background:var(--brand);color:white;')
    block=block.replace('.notice{font-size:12px;', '.bank-heading{display:flex;align-items:center;gap:14px;margin-bottom:12px}.bank-heading h2{margin:0}.bank-logo{width:64px;height:55px;object-fit:contain;flex:none}.bank-logo-empty{display:none}.notice{font-size:12px;')
    block=block.replace('<meta name="robots" content="noindex">', '<meta name="robots" content="noindex"><meta property="og:type" content="website"><meta property="og:title" content="NAME · Datos para pagar"><meta property="og:description" content="Copia los datos bancarios de NAME para realizar tu transferencia."><meta property="og:image" content="OGIMAGE"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">')
    block=block.replace('page=page.replace("BRAND",color)', '''page=page.replace("OGIMAGE",h(str(request.base_url).rstrip("/")+"/pagar/"+slug+"/compartir.jpg")).replace("BRAND",color)''')
    s=s[:a]+block+s[b:]
    # Admin: include bank logo upload in a separate form, to avoid nested forms.
    a=s.index('@app.get("/admin/connect/{slug}/pagos",response_class=HTMLResponse)')
    b=s.index('@app.post("/admin/connect/{slug}/pagos/guardar")',a)
    block=s[a:b]
    block=block.replace('    accounts=db.execute(','''    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_bank_accounts ADD COLUMN IF NOT EXISTS bank_logo_data TEXT"))
    db.commit()
    accounts=db.execute(''',1)
    needle='    rows+=f\\'\\'\\'<form method="post"'
    # Attach upload form after existing account forms, not nested.
    anchor='    rows+=f\\'\\'\\'<form method="post" action="/admin/connect/{h(slug)}/pagos/guardar" class="card"><input type="hidden" name="csrf_token" value="{h(request.state.session["csrf"])}"><h2>Agregar cuenta'
    insertion='''    for a in accounts:
        rows+=f\\'''<form method="post" enctype="multipart/form-data" action="/admin/connect/{h(slug)}/pagos/logo" class="card"><strong>Logotipo · {h(a["bank"])}</strong><input type="hidden" name="csrf_token" value="{h(request.state.session["csrf"])}"><input type="hidden" name="account_id" value="{a["id"]}"><input type="file" name="logo_file" accept="image/png,image/jpeg,image/webp" required><button>Guardar logotipo bancario</button></form>\\'''
'''
    if anchor not in block: raise SystemExit("Admin form anchor missing")
    block=block.replace(anchor,insertion+anchor,1)
    s=s[:a]+block+s[b:]
    # The logo URL serves a branded social sharing card; no Exponenta wording.
    route=r'''
# XP CONNECT PAY BRAND FINISH V2
@app.post("/admin/connect/{slug}/pagos/logo")
async def xp_pay_logo_upload(slug: str,request: Request,account_id: int=Form(...),csrf_token: str=Form(...),logo_file: UploadFile=File(...),db: Session=Depends(get_db)):
    import base64,io
    from PIL import Image
    control_superadmin(request,db)
    verify_csrf(request,csrf_token)
    xp_pay_setup(db)
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_bank_accounts ADD COLUMN IF NOT EXISTS bank_logo_data TEXT"))
    data=await logo_file.read()
    if len(data)>3_000_000:raise HTTPException(422,"Imagen demasiado grande")
    try:
        im=Image.open(io.BytesIO(data))
        if im.format not in ("PNG","JPEG","WEBP"):raise ValueError()
        im.thumbnail((400,400))
        out=io.BytesIO()
        im.convert("RGBA").save(out,format="PNG")
    except Exception:raise HTTPException(422,"Selecciona una imagen PNG, JPG o WEBP")
    encoded="data:image/png;base64,"+base64.b64encode(out.getvalue()).decode()
    res=db.execute(xp_sql_text("UPDATE exponenta_connect_bank_accounts SET bank_logo_data=:logo WHERE slug=:slug AND id=:id"),{"logo":encoded,"slug":slug,"id":account_id})
    if not res.rowcount:raise HTTPException(404)
    db.commit()
    return RedirectResponse("/admin/connect/"+slug+"/pagos",status_code=303)

@app.get("/pagar/{slug}/compartir.jpg")
def xp_pay_share_image(slug: str,db: Session=Depends(get_db)):
    import io,base64
    from PIL import Image,ImageDraw,ImageFont
    profile=xp_pay_profile(db,slug)
    if not profile:raise HTTPException(404)
    img=Image.new("RGB",(1200,630),"white")
    logo=profile.get("logo_data") or ""
    if logo.startswith("data:image/") and ";base64," in logo:
        try:
            artwork=Image.open(io.BytesIO(base64.b64decode(logo.split(";base64,",1)[1]))).convert("RGBA")
            artwork.thumbnail((850,480),Image.Resampling.LANCZOS)
            img.paste(artwork,((1200-artwork.width)//2,(630-artwork.height)//2),artwork)
        except Exception:pass
    out=io.BytesIO();img.save(out,format="JPEG",quality=93)
    return Response(out.getvalue(),media_type="image/jpeg",headers={"Cache-Control":"public,max-age=3600"})

'''
    anchor='@app.get("/admin/connect/{slug}/material", response_class=HTMLResponse)'
    if anchor not in s:raise SystemExit("Material route missing")
    s=s.replace(anchor,route+anchor,1)
    p.write_text(s,encoding="utf-8")
print("Connect Pay branded logos, buttons and social sharing ready")
