from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY DIRECT MOBILE FLOW V14"
if marker not in s:
    a=s.index("def xp_survey_public("); b=s.index("\n@app.",a)
    part=s[a:b]
    start=part.index("    content=")
    end=part.index("    response=HTMLResponse(",start)
    replacement=r'''    primary=p["brand_color"] if xp_survey_re.fullmatch(r"#[0-9a-fA-F]{6}",p["brand_color"] or "") else "#2D71B1"
    secondary=p["secondary_color"] if xp_survey_re.fullmatch(r"#[0-9a-fA-F]{6}",p["secondary_color"] or "") else "#4BB8DE"
    theme='<style>:root{--survey-primary:'+primary+';--survey-secondary:'+secondary+'}body{background:#f2f8fc;color:#17324d}header{display:none}main{max-width:600px;padding:20px 15px 65px}.card{background:#fff;border:1px solid #e1ebf3;box-shadow:0 10px 32px rgba(18,58,100,.07);border-radius:24px;padding:24px 22px}.btn{background:var(--survey-primary)!important;color:#fff!important;display:flex;width:100%;min-height:54px;align-items:center;justify-content:center;font-weight:750;border-radius:15px}.radio-row{gap:8px}.radio-row span{display:flex;align-items:center;justify-content:center;min-height:53px;border:1px solid #d8e5f0;border-radius:13px;background:#f3f8fc;color:#17324d;font-size:15px;line-height:1.2}.radio-row input:checked+span{background:var(--survey-primary);border-color:var(--survey-primary);color:#fff;font-weight:800}input,textarea{font-size:16px;min-height:50px}label{color:#17324d}.muted{color:#536e85}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--survey-secondary);outline-offset:3px}@media(max-width:600px){main{padding:14px 12px 55px}.card{padding:19px 15px;border-radius:20px}.radio-row{gap:5px}.radio-row span{font-size:14px;min-height:50px}.radio-row label{min-width:0}h1{font-size:26px}}</style>'
    logo=('<img alt="Logotipo de '+xp_html.escape(p["name"],quote=True)+'" src="'+xp_html.escape(p["logo_data"],quote=True)+'" style="display:block;max-width:185px;max-height:95px;object-fit:contain;margin:0 auto 15px">' if p["logo_data"] else '<div style="text-align:center;color:'+primary+';font-size:25px;font-weight:800;margin:10px 0 20px">'+xp_html.escape(p["name"])+'</div>')
    content=theme+logo+'<div class="card"><p style="letter-spacing:.07em;color:'+primary+';font-size:12px;font-weight:800;margin:0 0 8px">TU OPINIÓN NOS AYUDA A MEJORAR</p><h1 style="margin:0 0 10px;font-size:clamp(24px,6vw,32px)">¿Cómo fue tu visita?</h1><p class="muted" style="margin:0 0 19px">Queremos conocer tu experiencia en '+xp_html.escape(p["name"])+'. Responde en menos de 1 minuto.</p><form action="/encuesta/'+xp_html.escape(slug)+'/enviar" method="post">'
    content+='<label>1. ¿Cómo calificarías la atención recibida?</label>'+scale('overall',['1 ★','2 ★','3 ★','4 ★','5 ★'])
    content+='<label>2. ¿Qué te pareció la limpieza de nuestras instalaciones?</label>'+scale('cleanliness',['1','2','3','4','5'])
    content+='<label>3. ¿La explicación sobre la atención de tu mascota fue clara?</label>'+scale('clarity',['1','2','3','4','5'])
    content+='<label for="attendant">4. ¿Quién te atendió? (opcional)</label><input id="attendant" name="attendant" maxlength="120" placeholder="Nombre de quien te atendió" autocomplete="off">'
    content+='<label for="comment">5. ¿Quieres compartir algún comentario? (opcional)</label><textarea id="comment" name="comment" maxlength="1000" placeholder="Escribe tu comentario"></textarea>'
    questions=db.execute(xp_survey_sql("SELECT id,prompt FROM xp_survey_questions WHERE slug=:slug AND enabled=TRUE ORDER BY position,id"),{"slug":slug}).mappings().all()
    for q in questions:
        content+='<label>'+xp_html.escape(q["prompt"])+'</label>'+scale('q_'+str(q["id"]),['1','2','3','4','5'])
    content+='<input type="hidden" name="submission_token" value="'+xp_survey_uuid.uuid4().hex+'">'
    content+='<button class="btn" type="submit" style="margin-top:22px">Enviar mi opinión →</button></form></div><p class="muted" style="font-size:12px;text-align:center">Encuesta interna · Powered by Exponenta</p>'
'''
    part=part[:start]+replacement+part[end:]
    s=s[:a]+part+s[b:]
    a=s.index("def xp_survey_thanks(");b=s.index("\n@app.",a)
    part=s[a:b]
    start=part.index("    body=")
    end=part.index("    return xp_survey_page(",start)
    replacement=r'''    xp_survey_extended(db)
    primary=p["brand_color"] if xp_survey_re.fullmatch(r"#[0-9a-fA-F]{6}",p["brand_color"] or "") else "#2D71B1"
    secondary=p["secondary_color"] if xp_survey_re.fullmatch(r"#[0-9a-fA-F]{6}",p["secondary_color"] or "") else "#4BB8DE"
    body='<style>body{background:#f2f8fc;color:#17324d}header{display:none}main{max-width:600px;padding:25px 14px 60px}.card{border:1px solid #e2ebf1;box-shadow:0 12px 35px rgba(15,53,95,.07);border-radius:24px}.btn{background:'+primary+';color:#fff;width:100%;min-height:52px;display:flex;align-items:center;justify-content:center}.metric{background:#eaf6fd;border:1px solid #d6edf9}.footer{margin-top:32px}@media(max-width:600px){.card{padding:21px 16px}}</style>'
    if p["logo_data"]:
        body+='<img alt="Logotipo" style="display:block;max-width:175px;max-height:85px;object-fit:contain;margin:0 auto 24px" src="'+xp_html.escape(p["logo_data"],quote=True)+'">'
    body+='<div class="card" style="text-align:center"><div style="width:76px;height:76px;border-radius:50%;background:'+secondary+';color:#fff;font-size:44px;line-height:76px;margin:0 auto 20px">✓</div><h1>¡Gracias por tu opinión!</h1><p style="color:#4b6881">Tu experiencia nos ayuda a seguir mejorando.</p>'
    if p["promo_enabled"] and p["promo_title"]:
        body+='<div class="metric" style="margin-top:26px;overflow:hidden;border-radius:18px;padding:14px">'
        if p["promotion_image"]:
            body+='<img alt="Imagen del beneficio" style="width:100%;max-height:210px;object-fit:cover;border-radius:13px;margin-bottom:12px" src="'+xp_html.escape(p["promotion_image"],quote=True)+'">'
        body+='<h2>'+xp_html.escape(p["promo_title"])+'</h2><p>'+xp_html.escape(p["promo_details"] or "")+'</p>'
        if p["promo_code"]:
            body+='<p style="background:#fff;border:1px dashed '+secondary+';border-radius:12px;padding:14px;font-size:18px;font-weight:800;word-break:break-word">'+xp_html.escape(p["promo_code"])+'</p>'
        body+='</div><p class="muted" style="font-size:12px">Muestra este beneficio al personal. Aplican las condiciones indicadas.</p>'
    body+='</div>'
'''
    part=part[:start]+replacement+part[end:]
    s=s[:a]+part+s[b:]
    p.write_text(marker+"\n"+s,encoding="utf-8")
print("Direct QR -> mobile survey -> branded thank-you/promotion UI installed")
