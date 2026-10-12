from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP CONNECT BANK TRANSFER QR V1"
if marker not in s:
    code=r"""
# XP CONNECT BANK TRANSFER QR V1
import re as xp_pay_re
from fastapi.responses import Response as xp_pay_Response

def xp_pay_setup(db):
    db.execute(xp_sql_text('''
    CREATE TABLE IF NOT EXISTS exponenta_connect_bank_accounts (
      id BIGSERIAL PRIMARY KEY, slug VARCHAR(80) NOT NULL,
      bank TEXT NOT NULL, beneficiary TEXT NOT NULL,
      account TEXT DEFAULT '', clabe TEXT DEFAULT '',
      sort_order INTEGER DEFAULT 0, active INTEGER DEFAULT 1
    )'''))
    db.commit()

def xp_pay_profile(db, slug):
    xp_connect_ensure(db)
    return db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug AND active=1"),{"slug":slug}).mappings().first()

@app.get("/pagar/{slug}",response_class=HTMLResponse)
def xp_pay_public(slug: str,request: Request,db: Session=Depends(get_db)):
    xp_pay_setup(db)
    profile=xp_pay_profile(db,slug)
    if not profile: raise HTTPException(404)
    accounts=db.execute(xp_sql_text("SELECT * FROM exponenta_connect_bank_accounts WHERE slug=:slug AND active=1 ORDER BY sort_order,id"),{"slug":slug}).mappings().all()
    if not accounts: raise HTTPException(404,"Datos bancarios no configurados")
    from html import escape
    def h(v): return escape(str(v or ""),quote=True)
    color=str(profile.get("brand_color") or "#B28C55")
    if not xp_pay_re.fullmatch(r"#[0-9a-fA-F]{6}",color):color="#B28C55"
    cards=""
    for a in accounts:
        fields=""
        for label,value in (("Beneficiario",a["beneficiary"]),("Cuenta",a["account"]),("CLABE",a["clabe"])):
            if value:
                fields+=f'<div class="field"><div><small>{h(label)}</small><strong>{h(value)}</strong></div><button type="button" data-copy="{h(value)}" onclick="copyValue(this)">Copiar</button></div>'
        cards+=f'<section class="card"><h2>{h(a["bank"])}</h2>{fields}</section>'
    logo=profile.get("logo_data") or ""
    logo_html=f'<img class="logo" alt="Logotipo" src="{h(logo)}">' if str(logo).startswith("data:image/") else ""
    page='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Datos para pagar · NAME</title><style>
    :root{--brand:BRAND}*{box-sizing:border-box}body{margin:0;background:#f7f6f3;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#202020}.wrap{max-width:520px;margin:auto;padding:30px 18px 60px;text-align:center}.logo{max-width:170px;max-height:110px;object-fit:contain;margin:0 auto 16px;display:block}h1{font-size:26px;margin:12px 0 8px}p{color:#666;font-size:14px;line-height:1.6}.card{text-align:left;background:#fff;border:1px solid #e9e4dc;border-radius:20px;padding:20px;margin:18px 0;box-shadow:0 5px 25px #00000008}h2{font-size:19px;margin:0 0 16px;color:var(--brand)}.field{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0;border-top:1px solid #eee}.field div{min-width:0}.field small{display:block;color:#777;margin-bottom:5px}.field strong{font-size:15px;overflow-wrap:anywhere}button{background:#222;color:white;border:0;border-radius:10px;padding:11px 14px;cursor:pointer;flex-shrink:0}.notice{font-size:12px;color:#777;margin-top:22px}</style></head><body><main class="wrap">LOGO<h1>NAME</h1><p>Datos para realizar tu transferencia</p>CARDS<p class="notice">Verifica el nombre del beneficiario en tu aplicación bancaria antes de confirmar la transferencia.</p></main><script>async function copyValue(btn){let v=btn.dataset.copy;try{await navigator.clipboard.writeText(v)}catch(e){let el=document.createElement("textarea");el.value=v;document.body.appendChild(el);el.select();document.execCommand("copy");el.remove()}let old=btn.textContent;btn.textContent="¡Copiado!";setTimeout(()=>btn.textContent=old,1800)}</script></body></html>'''
    page=page.replace("BRAND",color).replace("LOGO",logo_html).replace("CARDS",cards).replace("NAME",h(profile["name"]))
    return HTMLResponse(page,headers={"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"})

@app.get("/admin/connect/{slug}/pagos",response_class=HTMLResponse)
def xp_pay_admin(slug: str,request: Request,db: Session=Depends(get_db)):
    control_superadmin(request,db)
    xp_pay_setup(db)
    profile=db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug"),{"slug":slug}).mappings().first()
    if not profile:raise HTTPException(404)
    # Seed confirmed SPACC accounts only on the matching business profile, once.
    normalized=xp_pay_re.sub(r"[^a-z0-9]","",str(profile["name"]).lower())
    if normalized in ("spacc","spaciocc","espaciocc") or slug in ("spacc","spacio-cc","espacio-cc"):
        exists=db.execute(xp_sql_text("SELECT 1 FROM exponenta_connect_bank_accounts WHERE slug=:slug LIMIT 1"),{"slug":slug}).first()
        if not exists:
            for bank,beneficiary,account,clabe,priority in (
                ("Mercado Pago W","Cristina Lepe de Los Angeles","","722969010101260640",1),
                ("BBVA","Carolina Guzman Arroyo","1519061863","012320015190618638",2)
            ):
                db.execute(xp_sql_text("INSERT INTO exponenta_connect_bank_accounts(slug,bank,beneficiary,account,clabe,sort_order,active) VALUES (:slug,:bank,:beneficiary,:account,:clabe,:sort_order,1)"),{"slug":slug,"bank":bank,"beneficiary":beneficiary,"account":account,"clabe":clabe,"sort_order":priority})
            db.commit()
    accounts=db.execute(xp_sql_text("SELECT * FROM exponenta_connect_bank_accounts WHERE slug=:slug ORDER BY sort_order,id"),{"slug":slug}).mappings().all()
    from html import escape
    def h(v):return escape(str(v or ""),quote=True)
    rows=""
    for a in accounts:
        rows+=f'''<form method="post" action="/admin/connect/{h(slug)}/pagos/guardar" class="card"><input type="hidden" name="csrf_token" value="{h(request.state.session["csrf"])}"><input type="hidden" name="account_id" value="{a["id"]}"><label>Banco<input name="bank" value="{h(a["bank"])}" required></label><label>Beneficiario<input name="beneficiary" value="{h(a["beneficiary"])}" required></label><label>Número de cuenta<input name="account" value="{h(a["account"])}" inputmode="numeric"></label><label>CLABE<input name="clabe" value="{h(a["clabe"])}" inputmode="numeric"></label><label>Orden<input type="number" name="sort_order" value="{a["sort_order"]}"></label><label>Visible <input type="checkbox" name="active" value="1" {"checked" if a["active"] else ""}></label><button>Guardar cuenta</button></form>'''
    rows+=f'''<form method="post" action="/admin/connect/{h(slug)}/pagos/guardar" class="card"><input type="hidden" name="csrf_token" value="{h(request.state.session["csrf"])}"><h2>Agregar cuenta</h2><label>Banco<input name="bank" required></label><label>Beneficiario<input name="beneficiary" required></label><label>Número de cuenta<input name="account" inputmode="numeric"></label><label>CLABE<input name="clabe" inputmode="numeric"></label><label>Orden<input type="number" name="sort_order" value="10"></label><label>Visible <input type="checkbox" name="active" value="1" checked></label><button>Agregar</button></form>'''
    page='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Datos para pagar</title><style>body{font:15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f8f8f8;color:#222;margin:0}.wrap{max-width:650px;margin:25px auto;padding:16px}.card{background:#fff;border:1px solid #e6e6e6;border-radius:16px;padding:22px;margin:16px 0;display:grid;gap:12px}label{display:grid;gap:5px;font-weight:600}input{padding:11px;border:1px solid #ccc;border-radius:9px;font:inherit;min-width:0}input[type=checkbox]{width:20px}button,.btn{display:inline-block;background:#222;color:#fff;padding:12px 16px;border:0;border-radius:10px;text-decoration:none;cursor:pointer}a{color:#333}h1{margin-bottom:5px}small{color:#666} .tools{display:flex;gap:9px;flex-wrap:wrap;margin:18px 0}</style></head><body><main class="wrap"><a href="/admin/connect/SLUG/editar">← Volver al panel Connect</a><h1>Datos para pagar</h1><p>NAME · Las cuentas se muestran según el orden indicado.</p><div class="tools"><a class="btn" target="_blank" href="/pagar/SLUG">Ver página de pagos</a><a class="btn" href="/admin/connect/SLUG/pagos/qr.png">Descargar QR PNG</a></div>ROWS</main></body></html>'''
    return HTMLResponse(page.replace("SLUG",h(slug)).replace("NAME",h(profile["name"])).replace("ROWS",rows),headers={"Cache-Control":"no-store"})

@app.post("/admin/connect/{slug}/pagos/guardar")
def xp_pay_save(slug: str,request: Request,account_id: int=Form(0),bank: str=Form(...),beneficiary: str=Form(...),account: str=Form(""),clabe: str=Form(""),sort_order: int=Form(10),active: str=Form("0"),csrf_token: str=Form(...),db: Session=Depends(get_db)):
    control_superadmin(request,db)
    verify_csrf(request,csrf_token)
    xp_pay_setup(db)
    if not db.execute(xp_sql_text("SELECT 1 FROM exponenta_connect_profiles WHERE slug=:slug"),{"slug":slug}).first():raise HTTPException(404)
    account="".join(ch for ch in account if ch.isdigit())
    clabe="".join(ch for ch in clabe if ch.isdigit())
    if not bank.strip() or not beneficiary.strip() or (not account and not clabe):raise HTTPException(422,"Banco, beneficiario y cuenta o CLABE son obligatorios")
    if clabe and len(clabe)!=18:raise HTTPException(422,"La CLABE debe tener 18 dígitos")
    args={"slug":slug,"bank":bank.strip()[:90],"beneficiary":beneficiary.strip()[:150],"account":account[:30],"clabe":clabe,"sort_order":sort_order,"active":1 if active=="1" else 0,"id":account_id}
    if account_id:
        res=db.execute(xp_sql_text("UPDATE exponenta_connect_bank_accounts SET bank=:bank,beneficiary=:beneficiary,account=:account,clabe=:clabe,sort_order=:sort_order,active=:active WHERE id=:id AND slug=:slug"),args)
        if not res.rowcount:raise HTTPException(404)
    else:
        db.execute(xp_sql_text("INSERT INTO exponenta_connect_bank_accounts(slug,bank,beneficiary,account,clabe,sort_order,active) VALUES (:slug,:bank,:beneficiary,:account,:clabe,:sort_order,:active)"),args)
    db.commit()
    return RedirectResponse("/admin/connect/"+slug+"/pagos",status_code=303)

@app.get("/admin/connect/{slug}/pagos/qr.png")
def xp_pay_qr(slug: str,request: Request,db: Session=Depends(get_db)):
    control_superadmin(request,db)
    xp_pay_setup(db)
    if not db.execute(xp_sql_text("SELECT 1 FROM exponenta_connect_profiles WHERE slug=:slug"),{"slug":slug}).first():raise HTTPException(404)
    import io,qrcode
    from fastapi.responses import Response
    url=str(request.base_url).rstrip("/")+"/pagar/"+slug
    qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=18,border=4)
    qr.add_data(url);qr.make(fit=True)
    out=io.BytesIO();qr.make_image(fill_color="black",back_color="white").save(out,format="PNG",dpi=(300,300))
    return Response(out.getvalue(),media_type="image/png",headers={"Content-Disposition":f'attachment; filename="{slug}-pagos-QR.png"',"Cache-Control":"no-store"})

"""
    anchor='@app.get("/admin/connect/{slug}/material", response_class=HTMLResponse)'
    if anchor not in s:raise SystemExit("Connect material route not found")
    s=s.replace(anchor,code+anchor,1)
    p.write_text(s,encoding="utf-8")

# Add a shortcut inside the existing Connect edit panel (no extra top-level product).
t=Path("/app/app/templates/admin/connect_edit.html")
html=t.read_text(encoding="utf-8")
if 'xp-pay-shortcut-v1' not in html:
    shortcut='''{% if profile %}<div class="xp-pay-shortcut-v1" style="margin:18px 0;padding:17px;border:1px solid #e5e7eb;border-radius:14px;background:#fff"><strong>Datos para pagar · QR independiente</strong><p style="font-size:13px;color:#64748b">Configura bancos, beneficiarios y CLABEs. Tus clientes podrán copiar los datos con un toque.</p><a href="/admin/connect/{{ profile.slug }}/pagos" style="display:inline-block;background:#202020;color:#fff;padding:11px 15px;border-radius:10px;text-decoration:none">Administrar cuentas y QR de pagos →</a></div>{% endif %}'''
    if '</form>' not in html:raise SystemExit("Connect editor form not found")
    html=html.replace('</form>','</form>\n'+shortcut,1)
    t.write_text(html,encoding="utf-8")
print("Connect Pay QR module ready")
