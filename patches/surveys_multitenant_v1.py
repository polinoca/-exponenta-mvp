from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEYS MULTITENANT V1"
if marker not in s:
    anchor='@app.get("/admin/connect", response_class=HTMLResponse)'
    routes=r'''
# XP SURVEYS MULTITENANT V1
from sqlalchemy import text as xp_survey_sql
from fastapi.responses import StreamingResponse
from urllib.parse import quote as xp_survey_quote
import re as xp_survey_re
import io as xp_survey_io
import csv as xp_survey_csv

def xp_survey_init(db):
    db.execute(xp_survey_sql("""
      CREATE TABLE IF NOT EXISTS xp_surveys (
        slug VARCHAR(100) PRIMARY KEY, name VARCHAR(220) NOT NULL,
        organization_id INTEGER, enabled BOOLEAN NOT NULL DEFAULT TRUE,
        brand_color VARCHAR(7) NOT NULL DEFAULT '#0D9D9E',
        promo_enabled BOOLEAN NOT NULL DEFAULT FALSE,
        promo_title VARCHAR(160) DEFAULT '',
        promo_details VARCHAR(400) DEFAULT '',
        promo_code VARCHAR(32) DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    """))
    db.execute(xp_survey_sql("""
      CREATE TABLE IF NOT EXISTS xp_survey_responses (
        id BIGSERIAL PRIMARY KEY, slug VARCHAR(100) NOT NULL,
        overall INTEGER NOT NULL, cleanliness INTEGER NOT NULL,
        clarity INTEGER NOT NULL, attendant VARCHAR(120),
        comment VARCHAR(1000), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    """))
    db.execute(xp_survey_sql("CREATE INDEX IF NOT EXISTS xp_surveys_responses_slug ON xp_survey_responses(slug, created_at)"))
    db.execute(xp_survey_sql("""
      INSERT INTO xp_surveys (slug,name,brand_color) VALUES
      ('pet-clinick','Pet Clinik','#0D9D9E')
      ON CONFLICT (slug) DO UPDATE SET name='Pet Clinik' WHERE xp_surveys.name IN ('Pet Clinick','Pet Clinic','Pet Clinik')
    """))
    db.commit()

def xp_survey_lookup(db,slug):
    return db.execute(xp_survey_sql("SELECT * FROM xp_surveys WHERE slug=:slug"),{"slug":slug}).mappings().first()

def xp_survey_admin(request,db):
    return control_superadmin(request,db)

def xp_survey_clean_slug(s):
    v=xp_survey_re.sub(r'[^a-z0-9-]','-',s.strip().lower())
    return xp_survey_re.sub(r'-+','-',v).strip('-')[:80]

def xp_survey_page(title,body,admin=False):
    nav='<a href="/admin/encuestas">← Encuestas</a>' if admin else ''
    return """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>"""+title+""" · Exponenta</title><style>
    :root{font-family:system-ui,-apple-system,sans-serif;color:#122738;background:#f5f8f9}
    *{box-sizing:border-box}body{margin:0}main{max-width:950px;margin:auto;padding:32px 18px 80px}
    header{background:white;padding:20px 24px;border-bottom:1px solid #dce7e9}
    header a{color:#127f82;font-weight:700;text-decoration:none}h1{font-size:clamp(28px,5vw,42px);line-height:1.13;margin:12px 0}
    h2{font-size:21px;margin:0 0 14px}p{line-height:1.5}.muted{color:#62757e}
    .card{background:white;border:1px solid #e3e9eb;border-radius:20px;padding:24px;margin:16px 0}
    label{font-weight:700;display:block;margin:12px 0 7px}
    input,textarea,select{font:inherit;width:100%;padding:13px;border:1px solid #cbd8db;border-radius:11px}
    textarea{min-height:95px;resize:vertical}.btn{display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:12px;padding:14px 19px;font-size:15px;font-weight:750;cursor:pointer;background:#0d8e8e;color:white;text-decoration:none;margin:6px 8px 6px 0}
    .secondary{background:#eef6f6;color:#15575d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
    .metric{background:#e9f8f5;border-radius:15px;padding:18px}.metric strong{font-size:28px;display:block}
    table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #edf1f2;padding:11px 8px;text-align:left;vertical-align:top}
    .scroll{overflow:auto}.radio-row{display:flex;gap:8px}.radio-row label{flex:1;margin:0;text-align:center}
    .radio-row input{position:absolute;opacity:0;width:1px}.radio-row span{display:block;border:1px solid #cbd9da;border-radius:12px;padding:13px 5px;cursor:pointer;font-size:16px}
    .radio-row input:checked+span{background:#dff4ef;border-color:#0d9d9e;color:#0b777b;font-weight:800}
    .footer{text-align:center;font-size:12px;margin-top:28px;color:#7b8e95}
    @media(max-width:600px){main{padding:22px 13px 55px}.card{padding:19px}.radio-row span{padding:13px 1px;font-size:14px}}
    </style></head><body><header><strong>EXPONENTA</strong> &nbsp; """+nav+"""</header><main>"""+body+"""<div class="footer">Powered by Exponenta</div></main></body></html>"""

@app.get("/encuesta/{slug}",response_class=HTMLResponse)
def xp_survey_public(slug: str, db: Session = Depends(get_db)):
    xp_survey_init(db)
    p=xp_survey_lookup(db,slug)
    if not p or not p["enabled"]: raise HTTPException(404,"Encuesta no disponible")
    def scale(field,labels):
        return '<div class="radio-row">'+''.join('<label><input type="radio" name="'+field+'" value="'+str(i)+'" required><span>'+txt+'</span></label>' for i,txt in enumerate(labels,1))+'</div>'
    content='<p class="muted">Tu opinión nos ayuda a mejorar</p><h1>'+xp_html.escape(p["name"])+'</h1><div class="card"><h2>¿Cómo fue tu experiencia?</h2><p class="muted">Te tomará menos de un minuto. Tu evaluación es interna.</p><form action="/encuesta/'+xp_html.escape(slug)+'/enviar" method="post">'
    content+='<label>¿Cómo calificas la atención recibida?</label>'+scale('overall',['1 ★','2 ★','3 ★','4 ★','5 ★'])
    content+='<label>¿Cómo encontraste la limpieza?</label>'+scale('cleanliness',['Muy mal','Mal','Regular','Bien','Excelente'])
    content+='<label>¿Recibiste una explicación clara?</label>'+scale('clarity',['Nada','Poco','Regular','Clara','Muy clara'])
    content+='<label>¿Quién te atendió? (opcional)</label><input name="attendant" maxlength="120" placeholder="Nombre de quien te atendió" autocomplete="off">'
    content+='<label>¿Quieres dejarnos un comentario? (opcional)</label><textarea name="comment" maxlength="1000" placeholder="Escribe tu comentario"></textarea>'
    content+='<button class="btn" type="submit">Enviar mi opinión</button></form></div>'
    return xp_survey_page('Tu opinión',content)

@app.post("/encuesta/{slug}/enviar")
def xp_survey_submit(slug:str,overall:int=Form(...),cleanliness:int=Form(...),clarity:int=Form(...),attendant:str=Form(""),comment:str=Form(""),db:Session=Depends(get_db)):
    xp_survey_init(db)
    p=xp_survey_lookup(db,slug)
    if not p or not p['enabled']:raise HTTPException(404)
    if not all(1 <= x <= 5 for x in [overall,cleanliness,clarity]): raise HTTPException(422,"Calificación no válida")
    db.execute(xp_survey_sql("""
      INSERT INTO xp_survey_responses (slug,overall,cleanliness,clarity,attendant,comment)
      VALUES (:slug,:overall,:cleanliness,:clarity,:attendant,:comment)
    """),{"slug":slug,"overall":overall,"cleanliness":cleanliness,"clarity":clarity,"attendant":attendant.strip()[:120],"comment":comment.strip()[:1000]})
    db.commit()
    return RedirectResponse("/encuesta/"+slug+"/gracias",status_code=303)

@app.get("/encuesta/{slug}/gracias",response_class=HTMLResponse)
def xp_survey_thanks(slug:str,db:Session=Depends(get_db)):
    xp_survey_init(db)
    p=xp_survey_lookup(db,slug)
    if not p:raise HTTPException(404)
    body='<div class="card" style="text-align:center"><div style="font-size:62px">✓</div><h1>¡Gracias por tu opinión!</h1><p>Nos ayudas a seguir mejorando.</p>'
    if p['promo_enabled'] and p['promo_title']:
        body+='<div class="metric"><h2>'+xp_html.escape(p['promo_title'])+'</h2><p>'+xp_html.escape(p['promo_details'] or '')+'</p>'
        if p['promo_code']:body+='<p><strong>Código: '+xp_html.escape(p['promo_code'])+'</strong></p>'
        body+='</div><p class="muted">Muestra este beneficio al personal. Sujeto a las condiciones indicadas.</p>'
    body+='</div>'
    return xp_survey_page('Gracias',body)

@app.get("/admin/encuestas",response_class=HTMLResponse)
def xp_survey_list(request:Request,db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_init(db)
    rows=db.execute(xp_survey_sql("""SELECT s.*, (SELECT COUNT(*) FROM xp_survey_responses r WHERE r.slug=s.slug) n FROM xp_surveys s ORDER BY name""")).mappings().all()
    body='<h1>Encuestas de clientes</h1><p class="muted">Un formulario por negocio, un QR y un panel de resultados. Independiente de Wallet.</p><div class="card"><h2>Nuevo negocio</h2><form action="/admin/encuestas/nueva" method="post"><label>Nombre del negocio</label><input name="name" required maxlength="220" placeholder="Nombre comercial"><button class="btn">Crear encuesta</button></form></div><div class="card"><h2>Negocios</h2>'
    for r in rows:
        body+='<p><a class="btn secondary" href="/admin/encuestas/'+xp_html.escape(r['slug'])+'">'+xp_html.escape(r['name'])+'</a> <span class="muted">'+str(r['n'])+' respuestas</span></p>'
    body+='</div>'
    return xp_survey_page('Encuestas',body,True)

@app.post("/admin/encuestas/nueva")
def xp_survey_create(request:Request,name:str=Form(...),db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_init(db)
    slug=xp_survey_clean_slug(name)
    if not slug or len(name)>220:raise HTTPException(422)
    db.execute(xp_survey_sql("INSERT INTO xp_surveys (slug,name) VALUES(:slug,:name) ON CONFLICT (slug) DO NOTHING"),{"slug":slug,"name":name.strip()})
    db.commit()
    return RedirectResponse("/admin/encuestas/"+slug,status_code=303)

@app.get("/admin/encuestas/{slug}",response_class=HTMLResponse)
def xp_survey_details(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_init(db)
    p=xp_survey_lookup(db,slug)
    if not p:raise HTTPException(404)
    summary=db.execute(xp_survey_sql("""
      SELECT COUNT(*) n,ROUND(AVG(overall)::numeric,2) avg_o,
      ROUND(AVG(cleanliness)::numeric,2) avg_c,ROUND(AVG(clarity)::numeric,2) avg_cl,
      COUNT(*) FILTER (WHERE overall<=2 OR cleanliness<=2 OR clarity<=2) alerts
      FROM xp_survey_responses WHERE slug=:slug
    """),{"slug":slug}).mappings().first()
    rows=db.execute(xp_survey_sql("""
      SELECT * FROM xp_survey_responses WHERE slug=:slug ORDER BY created_at DESC LIMIT 100
    """),{"slug":slug}).mappings().all()
    values=[('Respuestas',summary['n']),('Atención',summary['avg_o'] or '—'),('Limpieza',summary['avg_c'] or '—'),('Claridad',summary['avg_cl'] or '—'),('Alertas',summary['alerts'])]
    body='<h1>'+xp_html.escape(p['name'])+'</h1><p><a class="btn" target="_blank" href="/encuesta/'+slug+'">Abrir encuesta</a><a class="btn secondary" href="/admin/encuestas/'+slug+'/qr.png">Descargar QR</a><a class="btn secondary" href="/admin/encuestas/'+slug+'/csv">Exportar CSV</a></p>'
    body+='<div class="grid">'+''.join('<div class="metric"><strong>'+str(v)+'</strong><span>'+k+'</span></div>' for k,v in values)+'</div>'
    body+='<div class="card"><h2>Configuración</h2><form method="post" action="/admin/encuestas/'+slug+'/guardar">'
    body+='<label>Nombre del negocio</label><input name="name" value="'+xp_html.escape(p['name'],quote=True)+'" required>'
    body+='<label>Promoción después de responder</label><select name="promo_enabled"><option value="0"'+(' selected' if not p['promo_enabled'] else '')+'>Sin promoción</option><option value="1"'+(' selected' if p['promo_enabled'] else '')+'>Activar promoción</option></select>'
    for field,label,limit in [('promo_title','Título del beneficio',160),('promo_details','Condiciones / vigencia',400),('promo_code','Código para mostrar',32)]:
        body+='<label>'+label+'</label><input name="'+field+'" maxlength="'+str(limit)+'" value="'+xp_html.escape(p[field] or '',quote=True)+'">'
    body+='<label>Encuesta habilitada</label><select name="enabled"><option value="1"'+(' selected' if p['enabled'] else '')+'>Activa</option><option value="0"'+(' selected' if not p['enabled'] else '')+'>Pausada</option></select>'
    body+='<button class="btn">Guardar configuración</button></form></div>'
    body+='<div class="card"><h2>Últimas respuestas</h2><div class="scroll"><table><thead><tr><th>Fecha</th><th>Atención</th><th>Limpieza</th><th>Claridad</th><th>Atendió</th><th>Comentario</th></tr></thead><tbody>'
    for r in rows:
        body+='<tr>'+''.join('<td>'+xp_html.escape(str(v or ''))+'</td>' for v in [r['created_at'],r['overall'],r['cleanliness'],r['clarity'],r['attendant'],r['comment']])+'</tr>'
    body+='</tbody></table></div></div>'
    return xp_survey_page('Resultados',body,True)

@app.post("/admin/encuestas/{slug}/guardar")
def xp_survey_config(slug:str,request:Request,name:str=Form(...),promo_enabled:str=Form("0"),promo_title:str=Form(""),promo_details:str=Form(""),promo_code:str=Form(""),enabled:str=Form("1"),db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_init(db)
    if not xp_survey_lookup(db,slug):raise HTTPException(404)
    db.execute(xp_survey_sql("""
      UPDATE xp_surveys SET name=:name,promo_enabled=:promo, promo_title=:title,
      promo_details=:details,promo_code=:code,enabled=:enabled WHERE slug=:slug
    """),{"name":name.strip()[:220],"promo":promo_enabled=="1","title":promo_title.strip()[:160],"details":promo_details.strip()[:400],"code":promo_code.strip()[:32],"enabled":enabled=="1","slug":slug})
    db.commit()
    return RedirectResponse("/admin/encuestas/"+slug,status_code=303)

@app.get("/admin/encuestas/{slug}/qr.png")
def xp_survey_download_qr(slug:str,request:Request,db:Session=Depends(get_db)):
    import qrcode
    from fastapi.responses import Response
    xp_survey_admin(request,db);xp_survey_init(db)
    if not xp_survey_lookup(db,slug):raise HTTPException(404)
    qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=13,border=4)
    qr.add(str(request.base_url).rstrip("/")+"/encuesta/"+slug)
    qr.make(fit=True)
    out=xp_survey_io.BytesIO();qr.make_image(fill_color="black",back_color="white").save(out,format="PNG")
    return Response(out.getvalue(),media_type="image/png",headers={"Content-Disposition":f'attachment; filename="{slug}-encuesta.png"'})

@app.get("/admin/encuestas/{slug}/csv")
def xp_survey_csv_export(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_init(db)
    if not xp_survey_lookup(db,slug):raise HTTPException(404)
    rows=db.execute(xp_survey_sql("SELECT created_at,overall,cleanliness,clarity,attendant,comment FROM xp_survey_responses WHERE slug=:slug ORDER BY created_at DESC"),{"slug":slug}).mappings().all()
    b=xp_survey_io.StringIO();writer=xp_survey_csv.writer(b);writer.writerow(['Fecha','Atención','Limpieza','Claridad','Colaborador','Comentario'])
    for r in rows:
        writer.writerow([str(r[k]) if r[k] is not None else '' for k in ['created_at','overall','cleanliness','clarity','attendant','comment']])
    return Response(content='\ufeff'+b.getvalue(),media_type="text/csv; charset=utf-8",headers={"Content-Disposition":f'attachment; filename="{slug}-respuestas.csv"'})

'''
    # imports needed by routes
    routes=routes.replace('import csv as xp_survey_csv','import csv as xp_survey_csv\nimport html as xp_html')
    if anchor not in s: raise SystemExit("Survey insertion anchor unavailable")
    s=s.replace(anchor,routes+'\n'+anchor,1)
    p.write_text(s,encoding="utf-8")
    print("Reusable standalone surveys module installed")
