from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
if "# XP SURVEY BUSINESS PROMOTIONS V3" not in s:
    anchor="# XP SURVEYS CUSTOMIZATION V2"
    routes=r'''
# XP SURVEY BUSINESS PROMOTIONS V3
@app.get("/negocio/encuestas/{slug}/promocion", response_class=HTMLResponse)
def xp_business_survey_promotion(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_extended(db)
    _,_,p=xp_survey_business(request,db,slug)
    body='<h1>Promoción y comunicación</h1><p>'+xp_html.escape(p["name"])+'</p><div class="card"><form method="post" enctype="multipart/form-data">'
    if p['promotion_image']:body+='<img alt="Promoción" src="'+p['promotion_image']+'" style="max-height:180px;max-width:100%;object-fit:contain">'
    body+='<label>Imagen del producto o promoción</label><input type="file" name="promotion_file" accept="image/png,image/jpeg,image/webp">'
    for key,label in [('promo_title','Título del beneficio'),('promo_details','Vigencia y condiciones'),('promo_code','Código de promoción'),('thanks_text','Mensaje de agradecimiento')]:
        body+='<label>'+label+'</label><input maxlength="400" name="'+key+'" value="'+xp_html.escape(p[key] or '',quote=True)+'">'
    body+='<label>Estado</label><select name="promo_enabled"><option value="0">Desactivada</option><option value="1"'+(' selected' if p['promo_enabled'] else '')+'>Activada</option></select><button class="btn" type="submit">Guardar promoción</button></form></div>'
    return xp_survey_page('Promoción',body)

@app.post("/negocio/encuestas/{slug}/promocion")
async def xp_business_survey_promotion_update(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_same_origin(request);xp_survey_extended(db)
    _,_,p=xp_survey_business(request,db,slug)
    form=await request.form()
    updates={'slug':slug,'title':str(form.get('promo_title') or '')[:160],
    'details':str(form.get('promo_details') or '')[:400],
    'code':str(form.get('promo_code') or '')[:32],
    'thanks':str(form.get('thanks_text') or '')[:240],
    'enabled':str(form.get('promo_enabled'))=='1','image':p['promotion_image']}
    file=form.get('promotion_file')
    if file is not None and getattr(file,'filename',None):
        updates['image']=xp_survey_data_image(await file.read(),file.filename)
    db.execute(xp_survey_sql("""UPDATE xp_surveys SET promo_title=:title,promo_details=:details,
      promo_code=:code,thanks_text=:thanks,promo_enabled=:enabled,promotion_image=:image WHERE slug=:slug"""),updates)
    db.commit()
    return RedirectResponse('/negocio/encuestas/'+slug+'/promocion',303)
'''
    s=s.replace(anchor,routes+'\n'+anchor,1)
    a=s.find("def xp_survey_business_results(");b=s.find('\n@app.',a)
    if a<0:raise SystemExit('business dashboard not found')
    frag=s[a:b].replace("body='<h1>'+xp_html.escape(p[\"name\"])", "body='<p><a class=\"btn secondary\" href=\"/negocio/encuestas/'+slug+'/promocion\">Editar promoción</a></p><h1>'+xp_html.escape(p[\"name\"])",1)
    s=s[:a]+frag+s[b:]
    p.write_text(s,encoding="utf-8")
    print("Business-controlled promotions with tenant-scoped image uploads installed")
