from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY ACCESS GUARDS V1"
if marker not in s:
    anchor='# XP SURVEYS MULTITENANT V1'
    if anchor not in s: raise SystemExit("Survey module not installed")
    guard=r'''
# XP SURVEY ACCESS GUARDS V1
def xp_survey_same_origin(request):
    # Reject cross-site form submissions using the browser's Origin / Referer.
    from urllib.parse import urlparse
    base=urlparse(str(request.base_url))
    origin=request.headers.get("origin") or request.headers.get("referer") or ""
    incoming=urlparse(origin)
    if not origin or incoming.netloc!=base.netloc or incoming.scheme not in ("https","http"):
        raise HTTPException(403,"Solicitud no autorizada")

def xp_survey_business(request,db,slug):
    user,org=business_admin_context(request,db)
    p=xp_survey_lookup(db,slug)
    if not p or p["organization_id"]!=org.id:
        raise HTTPException(403,"Sin acceso a esta encuesta")
    return user,org,p

'''
    s=s.replace(anchor,guard+anchor,1)
    # Enforce same-origin on privileged admin POSTs
    for name in ("xp_survey_create","xp_survey_config"):
        start=s.find('def '+name+'(')
        end=s.find('\n@app.',start)
        if start<0: raise SystemExit("Handler not found "+name)
        if end<0:end=len(s)
        sec=s[start:end]
        sec=sec.replace('xp_survey_admin(request,db);xp_survey_init(db)','xp_survey_admin(request,db);xp_survey_same_origin(request);xp_survey_init(db)',1)
        s=s[:start]+sec+s[end:]
    # Also protect public POST from browser cross-site forgery (can be completed from same origin only)
    start=s.find('def xp_survey_submit(')
    end=s.find('\n@app.',start)
    sec=s[start:end]
    sec=sec.replace('slug:str,overall:int=Form(...)','slug:str,request:Request,overall:int=Form(...)')
    sec=sec.replace('xp_survey_init(db)','xp_survey_same_origin(request);xp_survey_init(db)',1)
    s=s[:start]+sec+s[end:]
    # Extend Superadmin form to associate business account by existing organization id.
    sec_start=s.find('def xp_survey_details(')
    sec_end=s.find('\n@app.',sec_start)
    sec=s[sec_start:sec_end]
    sec=sec.replace('body+=\'<label>Promoción después de responder</label>','''orgs=db.execute(xp_survey_sql("SELECT id,name FROM organizations ORDER BY name")).mappings().all()
    body+='<label>Negocio con acceso a los resultados</label><select name="organization_id"><option value="">Solo Superadmin</option>'
    for org in orgs:
        body+='<option value="'+str(org["id"])+'"'+(' selected' if p["organization_id"]==org["id"] else '')+'>'+xp_html.escape(org["name"])+'</option>'
    body+='</select>'
    body+='<label>Promoción después de responder</label>''')
    s=s[:sec_start]+sec+s[sec_end:]
    sec_start=s.find('def xp_survey_config(')
    sec_end=s.find('\n@app.',sec_start)
    sec=s[sec_start:sec_end]
    sec=sec.replace('name:str=Form(...),promo_enabled:', 'name:str=Form(...),organization_id:str=Form(""),promo_enabled:')
    sec=sec.replace('    db.execute(xp_survey_sql("""\n      UPDATE xp_surveys', '''    org_id=int(organization_id) if organization_id.strip().isdigit() else None
    if org_id and not db.execute(xp_survey_sql("SELECT id FROM organizations WHERE id=:id"),{"id":org_id}).first():raise HTTPException(422,"Negocio no existe")
    db.execute(xp_survey_sql("""
      UPDATE xp_surveys''')
    sec=sec.replace('SET name=:name,promo_enabled=', 'SET name=:name,organization_id=:org_id,promo_enabled=')
    sec=sec.replace('{"name":name.strip()[:220],"promo":', '{"org_id":org_id,"name":name.strip()[:220],"promo":')
    s=s[:sec_start]+sec+s[sec_end:]
    # Secure business dashboard; reuse the same summary UI by redirecting to a dedicated scoped view.
    route=r'''
@app.get("/negocio/encuestas",response_class=HTMLResponse)
def xp_survey_business_list(request:Request,db:Session=Depends(get_db)):
    user,org=business_admin_context(request,db)
    xp_survey_init(db)
    rows=db.execute(xp_survey_sql("SELECT slug,name FROM xp_surveys WHERE organization_id=:org_id ORDER BY name"),{"org_id":org.id}).mappings().all()
    body='<h1>Encuestas</h1><p class="muted">Opiniones internas de tus clientes.</p><div class="card">'
    for r in rows:
        body+='<p><a class="btn" href="/negocio/encuestas/'+xp_html.escape(r["slug"])+'">'+xp_html.escape(r["name"])+'</a></p>'
    if not rows:body+='<p>Aún no hay encuestas asignadas a este negocio.</p>'
    return xp_survey_page("Encuestas",body+'</div>')

@app.get("/negocio/encuestas/{slug}",response_class=HTMLResponse)
def xp_survey_business_results(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_init(db)
    _,_,p=xp_survey_business(request,db,slug)
    summary=db.execute(xp_survey_sql("""SELECT COUNT(*) n,ROUND(AVG(overall)::numeric,2) avg_o,
    ROUND(AVG(cleanliness)::numeric,2) avg_c,ROUND(AVG(clarity)::numeric,2) avg_cl
    FROM xp_survey_responses WHERE slug=:slug"""),{"slug":slug}).mappings().first()
    rows=db.execute(xp_survey_sql("SELECT * FROM xp_survey_responses WHERE slug=:slug ORDER BY created_at DESC LIMIT 100"),{"slug":slug}).mappings().all()
    body='<h1>'+xp_html.escape(p["name"])+'</h1><a class="btn secondary" href="/encuesta/'+slug+'" target="_blank">Ver encuesta</a>'
    body+='<div class="grid">'
    for k,v in [('Respuestas',summary["n"]),('Atención',summary["avg_o"] or '—'),('Limpieza',summary["avg_c"] or '—'),('Claridad',summary["avg_cl"] or '—')]:
        body+='<div class="metric"><strong>'+str(v)+'</strong>'+k+'</div>'
    body+='</div><div class="card"><h2>Comentarios y calificaciones</h2><div class="scroll"><table><thead><tr><th>Fecha</th><th>Atención</th><th>Limpieza</th><th>Claridad</th><th>Atendió</th><th>Comentario</th></tr></thead><tbody>'
    for r in rows:
        body+='<tr>'+''.join('<td>'+xp_html.escape(str(r[k] or ""))+'</td>' for k in ('created_at','overall','cleanliness','clarity','attendant','comment'))+'</tr>'
    return xp_survey_page("Resultados",body+'</tbody></table></div></div>')
'''
    at='@app.get("/admin/encuestas",response_class=HTMLResponse)'
    if at not in s:raise SystemExit("Admin surveys anchor missing")
    s=s.replace(at,route+'\n'+at,1)
    p.write_text(s,encoding="utf-8")
    print("Tenant isolation, same-origin checks and business dashboard installed")
