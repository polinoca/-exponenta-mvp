from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
marker="# XP SURVEYS CUSTOMIZATION V2"
if marker not in s:
    anchor="# XP SURVEYS MULTITENANT V1"
    if anchor not in s:raise SystemExit("Survey V1 not installed")
    extra=r'''
# XP SURVEYS CUSTOMIZATION V2
import json as xp_survey_json
import base64 as xp_survey_b64
from PIL import Image as xp_survey_Image
from collections import Counter as xp_survey_Counter

def xp_survey_extended(db):
    xp_survey_init(db)
    for sql in [
        "ALTER TABLE xp_surveys ADD COLUMN IF NOT EXISTS secondary_color VARCHAR(7) DEFAULT '#12304A'",
        "ALTER TABLE xp_surveys ADD COLUMN IF NOT EXISTS logo_data TEXT",
        "ALTER TABLE xp_surveys ADD COLUMN IF NOT EXISTS promotion_image TEXT",
        "ALTER TABLE xp_surveys ADD COLUMN IF NOT EXISTS intro_text VARCHAR(240) DEFAULT 'Tu opinión nos ayuda a mejorar'",
        "ALTER TABLE xp_surveys ADD COLUMN IF NOT EXISTS thanks_text VARCHAR(240) DEFAULT 'Gracias por compartir tu opinión'",
        "CREATE TABLE IF NOT EXISTS xp_survey_questions (id BIGSERIAL PRIMARY KEY, slug VARCHAR(100) NOT NULL, prompt VARCHAR(240) NOT NULL, kind VARCHAR(16) NOT NULL DEFAULT 'scale', position INTEGER NOT NULL DEFAULT 10, enabled BOOLEAN NOT NULL DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS xp_survey_answers (response_id BIGINT NOT NULL, question_id BIGINT NOT NULL, score INTEGER NOT NULL, PRIMARY KEY(response_id,question_id))",
    ]:db.execute(xp_survey_sql(sql))
    db.commit()

def xp_survey_color_from_logo(data):
    im=xp_survey_Image.open(xp_survey_io.BytesIO(data)).convert("RGBA")
    im.thumbnail((128,128))
    pix=[]
    for r,g,b,a in im.getdata():
        hi=max(r,g,b);lo=min(r,g,b)
        if a<190 or hi>242 or hi<30 or hi-lo<28:continue
        pix.append((r//24*24,g//24*24,b//24*24))
    if not pix:return '#0D9D9E'
    r,g,b=xp_survey_Counter(pix).most_common(1)[0][0]
    # constrain color contrast for buttons with white text
    lum=.2126*r+.7152*g+.0722*b
    if lum>145: r=int(r*.63);g=int(g*.63);b=int(b*.63)
    return '#%02X%02X%02X'%(r,g,b)

def xp_survey_data_image(filedata,filename,maximum=2*1024*1024):
    if len(filedata)>maximum:raise HTTPException(422,'Imagen demasiado grande (máximo 2 MB)')
    image=xp_survey_Image.open(xp_survey_io.BytesIO(filedata))
    if image.format not in ('PNG','JPEG','WEBP'):raise HTTPException(422,'Utiliza PNG, JPG o WebP')
    image.thumbnail((900,900))
    dst=xp_survey_io.BytesIO();image.convert('RGB').save(dst,format='JPEG',quality=83,optimize=True)
    return 'data:image/jpeg;base64,'+xp_survey_b64.b64encode(dst.getvalue()).decode('ascii')

@app.get("/admin/encuestas/{slug}/personalizar",response_class=HTMLResponse)
def xp_survey_customize(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_extended(db)
    p=xp_survey_lookup(db,slug)
    if not p:raise HTTPException(404)
    questions=db.execute(xp_survey_sql("SELECT * FROM xp_survey_questions WHERE slug=:slug ORDER BY position,id"),{'slug':slug}).mappings().all()
    body='<h1>Personalizar · '+xp_html.escape(p['name'])+'</h1><p class="muted">Logotipo, colores, comunicación, promoción y preguntas adicionales.</p>'
    body+='<div class="card"><h2>Marca y promoción</h2><form method="post" enctype="multipart/form-data" action="/admin/encuestas/'+slug+'/personalizar">'
    for key,label in [('logo_file','Logotipo PNG, JPG o WebP'),('promotion_file','Imagen de promoción (opcional)')]:
        body+='<label>'+label+'</label><input type="file" accept="image/png,image/jpeg,image/webp" name="'+key+'">'
    if p['logo_data']:body+='<img alt="Logotipo actual" style="max-width:100px;max-height:80px;object-fit:contain" src="'+p['logo_data']+'">'
    body+='<p class="muted">Al subir un logotipo detectamos automáticamente su color predominante. Siempre podrás modificarlo.</p>'
    for key,label in [('brand_color','Color principal'),('secondary_color','Color secundario')]:
        body+='<label>'+label+'</label><input type="color" name="'+key+'" value="'+xp_html.escape(p[key] or "#0D9D9E")+'">'
    for key,label in [('intro_text','Texto de bienvenida'),('thanks_text','Texto de agradecimiento'),('promo_title','Título de la promoción'),('promo_details','Condiciones y vigencia'),('promo_code','Código promocional')]:
        body+='<label>'+label+'</label><input name="'+key+'" maxlength="400" value="'+xp_html.escape(p[key] or "",quote=True)+'">'
    body+='<label>Promoción activa</label><select name="promo_enabled"><option value="0">No</option><option value="1"'+(' selected' if p['promo_enabled'] else '')+'>Sí</option></select><button class="btn">Guardar cambios</button></form></div>'
    body+='<div class="card"><h2>Preguntas adicionales</h2><p class="muted">Las preguntas generales de atención, limpieza y claridad se conservan. Puedes agregar otras con evaluación de 1 a 5.</p><form method="post" action="/admin/encuestas/'+slug+'/preguntas"><label>Nueva pregunta</label><input name="prompt" maxlength="240" placeholder="Ej. ¿Cómo calificarías el tiempo de espera?" required><button class="btn">Agregar pregunta</button></form>'
    for q in questions:
        body+='<form method="post" action="/admin/encuestas/'+slug+'/preguntas/'+str(q['id'])+'/estado" style="display:flex;justify-content:space-between;gap:12px;align-items:center"><span>'+xp_html.escape(q['prompt'])+' · '+('Activa' if q['enabled'] else 'Inactiva')+'</span><button class="btn secondary">'+('Desactivar' if q['enabled'] else 'Activar')+'</button></form>'
    body+='</div><p><a class="btn secondary" href="/admin/encuestas/'+slug+'/analisis">Ver analítica</a></p>'
    return xp_survey_page('Personalizar',body,True)

@app.post("/admin/encuestas/{slug}/personalizar")
async def xp_survey_customize_save(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_same_origin(request);xp_survey_extended(db)
    p=xp_survey_lookup(db,slug)
    if not p:raise HTTPException(404)
    form=await request.form()
    updates={'slug':slug,'color':str(form.get('brand_color') or p['brand_color'])[:7],
    'secondary':str(form.get('secondary_color') or p['secondary_color'])[:7],
    'intro':str(form.get('intro_text') or '')[:240],'thanks':str(form.get('thanks_text') or '')[:240],
    'title':str(form.get('promo_title') or '')[:160],'details':str(form.get('promo_details') or '')[:400],
    'code':str(form.get('promo_code') or '')[:32],'promo':str(form.get('promo_enabled'))=='1',
    'logo':p['logo_data'],'image':p['promotion_image']}
    for key in ['color','secondary']:
        if not xp_survey_re.fullmatch(r'#[0-9a-fA-F]{6}',updates[key]):raise HTTPException(422,'Color inválido')
    for key,dest in [('logo_file','logo'),('promotion_file','image')]:
        obj=form.get(key)
        if obj is not None and getattr(obj,'filename',None):
            data=await obj.read()
            updates[dest]=xp_survey_data_image(data,obj.filename)
            if dest=='logo':updates['color']=xp_survey_color_from_logo(data)
    db.execute(xp_survey_sql("""UPDATE xp_surveys SET brand_color=:color,secondary_color=:secondary,
    intro_text=:intro,thanks_text=:thanks,promo_title=:title,promo_details=:details,promo_code=:code,
    promo_enabled=:promo,logo_data=:logo,promotion_image=:image WHERE slug=:slug"""),updates)
    db.commit()
    return RedirectResponse('/admin/encuestas/'+slug+'/personalizar',status_code=303)

@app.post("/admin/encuestas/{slug}/preguntas")
def xp_survey_add_question(slug:str,request:Request,prompt:str=Form(...),db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_same_origin(request);xp_survey_extended(db)
    if not xp_survey_lookup(db,slug):raise HTTPException(404)
    if not (5<=len(prompt.strip())<=240):raise HTTPException(422)
    db.execute(xp_survey_sql("""INSERT INTO xp_survey_questions (slug,prompt,position)
    VALUES(:slug,:prompt,(SELECT COALESCE(MAX(position),0)+10 FROM xp_survey_questions WHERE slug=:slug))"""),{'slug':slug,'prompt':prompt.strip()})
    db.commit();return RedirectResponse('/admin/encuestas/'+slug+'/personalizar',303)

@app.post("/admin/encuestas/{slug}/preguntas/{qid}/estado")
def xp_survey_toggle_question(slug:str,qid:int,request:Request,db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_same_origin(request);xp_survey_extended(db)
    db.execute(xp_survey_sql("UPDATE xp_survey_questions SET enabled=NOT enabled WHERE slug=:slug AND id=:qid"),{'slug':slug,'qid':qid})
    db.commit();return RedirectResponse('/admin/encuestas/'+slug+'/personalizar',303)

@app.get("/admin/encuestas/{slug}/analisis",response_class=HTMLResponse)
def xp_survey_analytics(slug:str,request:Request,attendant:str='',month:str='',db:Session=Depends(get_db)):
    xp_survey_admin(request,db);xp_survey_extended(db)
    p=xp_survey_lookup(db,slug)
    if not p:raise HTTPException(404)
    if not xp_survey_re.fullmatch(r'\d{4}-\d{2}',month):month=''
    params={'slug':slug,'att':'%'+attendant.strip()[:120]+'%','month':month}
    condition="slug=:slug AND (:att='' OR lower(attendant) LIKE lower(:att)) AND (:month='' OR to_char(created_at,'YYYY-MM')=:month)"
    # empty field in UI maps to empty filter, not %%
    if not attendant.strip():params['att']=''
    summary=db.execute(xp_survey_sql("SELECT COUNT(*) n,ROUND(AVG(overall)::numeric,2) rating,ROUND(AVG(cleanliness)::numeric,2) clean,ROUND(AVG(clarity)::numeric,2) clarity FROM xp_survey_responses WHERE "+condition),params).mappings().first()
    months=db.execute(xp_survey_sql("""SELECT to_char(created_at,'YYYY-MM') mon,COUNT(*) n,ROUND(AVG(overall)::numeric,2) score FROM xp_survey_responses WHERE slug=:slug GROUP BY 1 ORDER BY 1 DESC LIMIT 12"""),{'slug':slug}).mappings().all()
    employees=db.execute(xp_survey_sql("SELECT COALESCE(NULLIF(trim(attendant),''),'Sin nombre') employee,COUNT(*) n,ROUND(AVG(overall)::numeric,2) score FROM xp_survey_responses WHERE "+condition+" GROUP BY 1 ORDER BY n DESC LIMIT 40"),params).mappings().all()
    recent=db.execute(xp_survey_sql("SELECT attendant,comment,overall,created_at FROM xp_survey_responses WHERE "+condition+" ORDER BY created_at DESC LIMIT 100"),params).mappings().all()
    body='<h1>Análisis · '+xp_html.escape(p['name'])+'</h1><div class="card"><form method="get"><div class="grid"><div><label>Colaborador</label><input name="attendant" value="'+xp_html.escape(attendant,quote=True)+'" placeholder="Nombre"></div><div><label>Mes (AAAA-MM)</label><input name="month" placeholder="2026-10" value="'+xp_html.escape(month,quote=True)+'"></div></div><button class="btn">Filtrar</button><a class="btn secondary" href="/admin/encuestas/'+slug+'/analisis">Limpiar</a></form></div>'
    body+='<div class="grid">'+''.join('<div class="metric"><strong>'+str(v or '—')+'</strong>'+k+'</div>' for k,v in [('Respuestas',summary['n']),('Atención',summary['rating']),('Limpieza',summary['clean']),('Claridad',summary['clarity'])])+'</div>'
    body+='<div class="card"><h2>Evolución mensual</h2>'
    for m in reversed(months):
        width=max(0,min(100,float(m['score'] or 0)*20))
        body+='<p>'+m['mon']+' · '+str(m['n'])+' respuestas · '+str(m['score'] or '—')+'/5</p><div style="height:18px;border-radius:10px;background:#e5eeee"><div style="background:#0d9d9e;border-radius:10px;height:18px;width:'+str(width)+'%"></div></div>'
    body+='</div><div class="card"><h2>Por colaborador</h2><div class="scroll"><table><tr><th>Colaborador</th><th>Respuestas</th><th>Promedio</th></tr>'
    for r in employees:body+='<tr><td>'+xp_html.escape(r['employee'])+'</td><td>'+str(r['n'])+'</td><td>'+str(r['score'])+'</td></tr>'
    body+='</table></div></div><div class="card"><h2>Comentarios</h2>'
    for r in recent:
        if r['comment']:body+='<p><strong>'+xp_html.escape(r['attendant'] or 'Sin nombre')+' · '+str(r['overall'])+'/5</strong> · '+str(r['created_at'])+'<p>'+xp_html.escape(r['comment'])+'</p></p>'
    body+='</div>'
    return xp_survey_page('Analítica',body,True)
'''
    s=s.replace(anchor,extra+'\n'+anchor,1)
    # Integrate uploads and dynamic questions in existing client survey and POST
    a=s.find('def xp_survey_public(');b=s.find('\n@app.',a)
    fragment=s[a:b]
    fragment=fragment.replace('xp_survey_init(db)','xp_survey_extended(db)',1)
    fragment=fragment.replace("content='<p class=\"muted\">Tu opinión nos ayuda a mejorar</p>", """content=('<div style="text-align:center"><img style="max-width:180px;max-height:100px;object-fit:contain" alt="Logotipo" src="'+p['logo_data']+'"></div>' if p['logo_data'] else '')+'<p class="muted">'+xp_html.escape(p['intro_text'] or 'Tu opinión nos ayuda a mejorar')+'</p>'""")
    fragment=fragment.replace("content+='<button class=\"btn\" type=\"submit\">Enviar mi opinión</button></form></div>'", """questions=db.execute(xp_survey_sql("SELECT id,prompt FROM xp_survey_questions WHERE slug=:slug AND enabled=TRUE ORDER BY position,id"),{'slug':slug}).mappings().all()
    for q in questions:
        content+='<label>'+xp_html.escape(q['prompt'])+'</label>'+scale('q_'+str(q['id']),['1','2','3','4','5'])
    content+='<button class="btn" type="submit">Enviar mi opinión</button></form></div>'
    content='<style>.btn,.radio-row input:checked+span{background:'+xp_html.escape(p['brand_color'])+'!important;color:white!important}</style>'+content""")
    s=s[:a]+fragment+s[b:]
    a=s.find('def xp_survey_submit(');b=s.find('\n@app.',a);frag=s[a:b]
    frag=frag.replace('xp_survey_init(db)','xp_survey_extended(db)',1)
    frag=frag.replace('slug:str,request:Request,overall:', 'slug:str,request:Request,overall:')
    frag=frag.replace('    db.execute(xp_survey_sql("""\n      INSERT INTO xp_survey_responses', '''    submission=None
    # Insert response and collect the inserted primary key for additional scores.
    submission=db.execute(xp_survey_sql("""
      INSERT INTO xp_survey_responses''')
    frag=frag.replace('VALUES (:slug,:overall,:cleanliness,:clarity,:attendant,:comment)\n    """)','VALUES (:slug,:overall,:cleanliness,:clarity,:attendant,:comment) RETURNING id\n    """)')
    frag=frag.replace('    db.commit()\n    return RedirectResponse', '''    form=await request.form() if False else None
    db.commit()
    return RedirectResponse''')
    # Don't introduce async request.form into sync handler; extra answers submitted via a separate handler to add transaction-safe responses
    frag=frag.replace('    form=await request.form() if False else None\n','')
    s=s[:a]+frag+s[b:]
    # To persist extra questions read form via async route conversion
    a=s.find('def xp_survey_submit(');b=s.find('\n@app.',a);frag=s[a:b]
    frag=frag.replace('def xp_survey_submit(', 'async def xp_survey_submit(')
    frag=frag.replace('    db.commit()\n    return RedirectResponse', '''    form=await request.form()
    questions=db.execute(xp_survey_sql("SELECT id FROM xp_survey_questions WHERE slug=:slug AND enabled=TRUE"),{'slug':slug}).all()
    for row in questions:
        qid=row[0]
        try: score=int(form.get('q_'+str(qid),''))
        except (ValueError,TypeError):raise HTTPException(422,'Falta responder una pregunta')
        if score<1 or score>5:raise HTTPException(422,'Calificación no válida')
        db.execute(xp_survey_sql("INSERT INTO xp_survey_answers (response_id,question_id,score) VALUES(:r,:q,:score)"),{'r':submission.scalar_one(),'q':qid,'score':score})
    db.commit()
    return RedirectResponse''')
    frag=frag.replace("submission.scalar_one()","submission_id")
    frag=frag.replace('    form=await request.form()', '    submission_id=submission.scalar_one()\n    form=await request.form()')
    s=s[:a]+frag+s[b:]
    a=s.find('def xp_survey_thanks(');b=s.find('\n@app.',a);frag=s[a:b]
    frag=frag.replace('xp_survey_init(db)','xp_survey_extended(db)',1)
    frag=frag.replace("body='<div class=\"card\" style=\"text-align:center\"><div style=\"font-size:62px\">✓</div><h1>¡Gracias por tu opinión!</h1><p>Nos ayudas a seguir mejorando.</p>'","body='<div class=\"card\" style=\"text-align:center\"><div style=\"font-size:62px\">✓</div><h1>'+xp_html.escape(p['thanks_text'] or '¡Gracias por tu opinión!')+'</h1><p>Nos ayudas a seguir mejorando.</p>'")
    frag=frag.replace("body+='<div class=\"metric\"><h2>'", "body+='<div class=\"metric\">'+('<img alt=\"Promoción\" src=\"'+p['promotion_image']+'\" style=\"width:100%;max-height:220px;object-fit:contain\">' if p['promotion_image'] else '')+'<h2>'")
    s=s[:a]+frag+s[b:]
    # Add action links to admin details
    a=s.find('def xp_survey_details(');b=s.find('\n@app.',a);frag=s[a:b]
    frag=frag.replace("body='<h1>'+xp_html.escape(p['name'])+'</h1>", "body='<h1>'+xp_html.escape(p['name'])+'</h1><p><a class=\"btn secondary\" href=\"/admin/encuestas/'+slug+'/personalizar\">Personalizar</a><a class=\"btn secondary\" href=\"/admin/encuestas/'+slug+'/analisis\">Análisis y gráficas</a></p>'")
    s=s[:a]+frag+s[b:]
    p.write_text(s,encoding='utf-8')
    print("Advanced surveys branding, editable ratings, promotion media and analytics installed")
