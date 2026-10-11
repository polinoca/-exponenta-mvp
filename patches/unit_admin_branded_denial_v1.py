from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# EXPONENTA UNIT ADMIN AND BRANDED DENIAL V1"
if marker not in s:
    # Preserve HTTP status and avoid raw JSON for service authorization failures.
    addition=r'''
# EXPONENTA UNIT ADMIN AND BRANDED DENIAL V1
from fastapi.exception_handlers import http_exception_handler as xp_default_http_exception_handler

@app.exception_handler(HTTPException)
async def xp_branded_product_denial(request:Request,exc:HTTPException):
    if exc.status_code==403 and str(exc.detail)=="Servicio no contratado para esta organización.":
        return HTMLResponse("""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Acceso restringido · Exponenta</title><style>*{box-sizing:border-box}body{margin:0;min-height:100vh;background:#f7f4ef;color:#251e19;font:16px system-ui,-apple-system,sans-serif;display:grid;place-items:center;padding:24px}.card{width:100%;max-width:480px;background:white;border:1px solid #e5dcd2;border-radius:24px;padding:36px;box-shadow:0 18px 60px #3d261014;text-align:center}.icon{font-size:38px;background:#f7eee5;width:80px;height:80px;display:grid;place-items:center;border-radius:50%;margin:0 auto 22px}h1{font-size:29px;letter-spacing:-.04em;margin:0 0 12px}p{line-height:1.6;color:#71665d;margin:0 0 25px}a.btn{display:inline-block;padding:14px 22px;background:#80563c;color:white;text-decoration:none;border-radius:12px;font-weight:750}a.other{display:block;margin-top:20px;color:#80563c;text-decoration:none;font-size:14px}</style></head><body><main class="card"><img src="/static/exponenta-logo.svg" alt="Exponenta" style="width:148px;max-height:60px;object-fit:contain;margin-bottom:25px"><div class="icon" aria-hidden="true">🔒</div><h1>Este servicio no está incluido en tu cuenta</h1><p>Tu negocio tiene acceso únicamente a los servicios contratados. Puedes volver a Satisfacción del cliente o consultar los demás servicios de Exponenta.</p><a class="btn" href="/encuestas/acceso">Ir a mis encuestas</a><a class="other" href="/accesos">Ver servicios</a></main></body></html>""",status_code=403)
    return await xp_default_http_exception_handler(request,exc)

@app.get("/admin/unidades/{unit}",response_class=HTMLResponse)
def xp_admin_business_unit(unit:str,request:Request,db:Session=Depends(get_db)):
    control_superadmin(request,db)
    if unit not in ("wallet","connect"):raise HTTPException(404,"Unidad no encontrada")
    from html import escape as esc
    orgs=db.scalars(select(Organization).order_by(Organization.name)).all()
    title="Wallet / Club" if unit=="wallet" else "Connect"
    cards=[]
    for org in orgs:
        states=feature_states(db,org.id)
        if not states.get(unit,False):continue
        cards.append('<a class="item" href="/admin/control/'+str(org.id)+'"><strong>'+esc(org.name)+'</strong><span>Administrar cliente →</span></a>')
    body=''.join(cards) or '<p>No hay clientes con este servicio activado.</p>'
    return HTMLResponse('<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+' · Exponenta</title><style>body{background:#f7f4ef;color:#2a211b;font:16px system-ui;padding:24px;margin:0}main{max-width:900px;margin:35px auto}h1{font-size:40px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}.item{background:#fff;border:1px solid #e5dcd2;border-radius:16px;padding:20px;text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:12px}.item span,a.back{color:#80563c}.actions{display:flex;gap:18px;flex-wrap:wrap;margin:24px 0}a{font-weight:600}</style><main><img src="/static/exponenta-logo.svg" alt="Exponenta" style="width:140px"><h1>'+title+'</h1><p>Clientes con este servicio activo. Selecciona uno para configurar accesos y funciones.</p><div class="actions"><a class="back" href="/accesos">← Unidades de negocio</a><a class="back" href="/admin/control">Administrar todos los clientes / agregar nuevo</a></div><div class="grid">'+body+'</div></main></html>')

'''
    s+="\n"+addition
    old='def xp_product_access_portal():'
    assert old in s,"Portal signature missing"
    s=s.replace(old,'def xp_product_access_portal(request:Request,db:Session=Depends(get_db)):',1)
    needle='    body=\'\'.join(\'<a class="xp-unit"'
    assert needle in s,"Portal cards missing"
    insertion='''    uid=request.session.get("user_id") or request.session.get("uid")
    if uid:
        user=db.get(User,int(uid))
        role=str(getattr(getattr(user,"role",None),"value",getattr(user,"role",""))).lower() if user else ""
        if "superadmin" in role:
            cards=[
              ("Wallet","Administrar Wallet / Club","Clientes, lealtad y configuración.","/admin/unidades/wallet"),
              ("Connect","Administrar Connect","Clientes, QR/NFC y perfiles.","/admin/unidades/connect"),
              ("Satisfacción del cliente","Administrar Encuestas","Clientes, encuestas y resultados.","/admin/encuestas")
            ]
'''
    s=s.replace(needle,insertion+needle,1)
    p.write_text(s+"\n"+marker+"\n",encoding="utf-8")
print("Branded 403 and superadmin business-unit destinations installed")
