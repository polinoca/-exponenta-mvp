from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK PROMOTION BRAND NAV V1'

if marker not in s:
    start=s.index('@app.get("/negocio/encuestas/{slug}/promocion", response_class=HTMLResponse)')
    end=s.index('@app.post("/negocio/encuestas/{slug}/promocion")',start)
    replacement=r'''@app.get("/negocio/encuestas/{slug}/promocion", response_class=HTMLResponse)
def xp_business_survey_promotion(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_extended(db)
    _,_,p=xp_survey_business(request,db,slug)
    body='''+"'''"+r'''<style>
      .xp-promo-return{display:inline-flex;align-items:center;min-height:42px;padding:0 14px;border:1px solid #c9dfec;border-radius:12px;color:#2d71b1!important;background:#fff;text-decoration:none!important;font-weight:800;font-size:14px;margin:0 0 16px}
      .xp-promo-form-title{margin:0 0 5px;color:#17324d}.xp-promo-form-sub{margin:0 0 20px;color:#637d91}
    </style>'''+"'''"+r'''+'<a class="xp-promo-return" href="/negocio/encuestas/'+xp_html.escape(slug,quote=True)+'">← Volver al panel</a>'
    body+='<h1 class="xp-promo-form-title">Promoción y comunicación</h1><p class="xp-promo-form-sub">Configura el beneficio que verá tu cliente al terminar la encuesta.</p><div class="card"><form method="post" enctype="multipart/form-data">'
    if p['promotion_image']:body+='<img alt="Promoción" src="'+p['promotion_image']+'" style="max-height:180px;max-width:100%;object-fit:contain">'
    body+='<label>Imagen del producto o promoción</label><input type="file" name="promotion_file" accept="image/png,image/jpeg,image/webp">'
    for key,label in [('promo_title','Título del beneficio'),('promo_details','Vigencia y condiciones'),('promo_code','Código de promoción'),('thanks_text','Mensaje de agradecimiento')]:
        body+='<label>'+label+'</label><input maxlength="400" name="'+key+'" value="'+xp_html.escape(p[key] or '',quote=True)+'">'
    body+='<label>Estado</label><select name="promo_enabled"><option value="0">Desactivada</option><option value="1"'+(' selected' if p['promo_enabled'] else '')+'>Activada</option></select><button class="btn" type="submit">Guardar promoción</button></form></div>'
    return xp_survey_business_theme('Promoción · '+str(p['name']),body,p)

'''
    s=s[:start]+replacement+s[end:]
    p.write_text(s+'\n'+marker+'\n',encoding='utf-8')

print('PET Clinik promotion page now has branding and return navigation')
