from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK QUESTIONNAIRE V1'
assert marker not in s
# Only the Pet Clinik survey uses the revised wording and new metrics.
helper='''
def xp_pet_questions(db,slug):
    defaults={
      "reception":"¿Cómo calificarías la atención recibida desde tu llegada (en recepción)?",
      "veterinarian":"¿Qué médico veterinario atendió a tu mascota?",
      "overall":"¿Cómo calificarías el trato y atención del médico hacia ti y tu mascota?",
      "clarity":"¿La explicación del médico fue clara y te generó confianza?",
      "cleanliness":"¿Cómo calificarías la limpieza, comodidad y condiciones de nuestras instalaciones?",
      "recommend":"¿Qué tan probable es que recomiendes Pet Clinik a familiares o amigos?",
      "comment":"¿Hay algo que podamos mejorar o que quisieras reconocer de nuestro servicio?"
    }
    db.execute(xp_survey_sql("""CREATE TABLE IF NOT EXISTS xp_survey_question_texts (
        slug VARCHAR(100) NOT NULL, field VARCHAR(32) NOT NULL,
        prompt VARCHAR(240) NOT NULL, PRIMARY KEY(slug,field))"""))
    db.commit()
    rows=db.execute(xp_survey_sql("SELECT field,prompt FROM xp_survey_question_texts WHERE slug=:slug"),{"slug":slug}).mappings().all()
    defaults.update({r["field"]:r["prompt"] for r in rows if r["field"] in defaults})
    return defaults

def xp_pet_extra_init(db):
    db.execute(xp_survey_sql("""CREATE TABLE IF NOT EXISTS xp_pet_clinik_extras (
        response_id BIGINT PRIMARY KEY, reception INTEGER NOT NULL,
        recommendation INTEGER NOT NULL,
        CHECK (reception BETWEEN 1 AND 5),
        CHECK (recommendation BETWEEN 1 AND 5))"""))
'''
route_marker='@app.get("/encuesta/{slug}"'
pos=s.index(route_marker)
s=s[:pos]+helper+'\n'+s[pos:]
a=s.index('def xp_survey_public(');b=s.index('\n@app.',a);part=s[a:b]
# Apply to current five-star mobile survey.
needle="    content+='<label>1. ¿Cómo calificarías la atención recibida?</label>'+star_scale('overall',['1 ★','2 ★','3 ★','4 ★','5 ★'])"
assert needle in part
part=part.replace(needle,'''    pet=(slug=='pet-clinick')
    q=xp_pet_questions(db,slug) if pet else {}
    if pet:
        content+='<label>'+xp_html.escape(q['reception'])+'</label>'+star_scale('reception')
    content+='<label>'+(xp_html.escape(q['overall']) if pet else '1. ¿Cómo calificarías la atención recibida?')+'</label>'+star_scale('overall',['1 ★','2 ★','3 ★','4 ★','5 ★'])''',1)
for label,key in [('2. ¿Qué te pareció la limpieza de nuestras instalaciones?','cleanliness'),('3. ¿La explicación sobre la atención de tu mascota fue clara?','clarity'),('4. ¿Quién te atendió? (opcional)','veterinarian'),('5. ¿Quieres compartir algún comentario? (opcional)','comment')]:
    part=part.replace(label,"'+xp_html.escape(q['"+key+"'])+'",1) if False else part
part=part.replace("'<label>2. ¿Qué te pareció la limpieza de nuestras instalaciones?</label>'","'<label>'+(xp_html.escape(q['cleanliness']) if pet else '2. ¿Qué te pareció la limpieza de nuestras instalaciones?')+'</label>'",1)
part=part.replace("'<label>3. ¿La explicación sobre la atención de tu mascota fue clara?</label>'","'<label>'+(xp_html.escape(q['clarity']) if pet else '3. ¿La explicación sobre la atención de tu mascota fue clara?')+'</label>'",1)
part=part.replace("'<label for=\"attendant\">4. ¿Quién te atendió? (opcional)</label>'","'<label for=\"attendant\">'+(xp_html.escape(q['veterinarian']) if pet else '4. ¿Quién te atendió? (opcional)')+'</label>'",1)
part=part.replace("'<label for=\"comment\">5. ¿Quieres compartir algún comentario? (opcional)</label>'","'<label for=\"comment\">'+(xp_html.escape(q['comment']) if pet else '5. ¿Quieres compartir algún comentario? (opcional)')+'</label>'",1)
needle='    questions=db.execute('
assert needle in part
part=part.replace(needle,'''    if pet:
        content+='<label>'+xp_html.escape(q['recommend'])+'</label><div class="xp-nps">'+''.join('<label><input type="radio" name="recommendation" value="'+str(i)+'" required><span>'+str(i)+'</span></label>' for i in range(1,6))+'</div><p class="muted">1 = Nada probable · 5 = Muy probable</p>'
        content='<style>.xp-nps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:5px}.xp-nps label{min-width:0}.xp-nps span{display:flex;align-items:center;justify-content:center;padding:12px 2px;border:1px solid #CBDFEC;border-radius:10px}.xp-nps input:checked+span{background:#2D71B1;color:#fff}@media(min-width:720px){.xp-nps{grid-template-columns:repeat(5,minmax(0,1fr))}}</style>'+content
    questions=db.execute(''',1)
s=s[:a]+part+s[b:]
a=s.index('async def xp_survey_submit(');b=s.index('\n@app.',a);part=s[a:b]
# New fields are required only for Pet Clinik, not other tenants.
needle='    submission_id=submission.scalar_one_or_none()'
assert needle in part
part=part.replace(needle,'''    pet_reception=None
    pet_recommendation=None
    if slug=='pet-clinick':
        pet_form=await request.form()
        try:
            pet_reception=int(pet_form.get('reception',''))
            pet_recommendation=int(pet_form.get('recommendation',''))
        except (ValueError,TypeError):
            db.rollback()
            raise HTTPException(422,'Responde todas las preguntas obligatorias')
        if not 1<=pet_reception<=5 or not 1<=pet_recommendation<=5:
            db.rollback()
            raise HTTPException(422,'Calificación fuera de rango')
'''+needle,1)
needle='    db.commit()\n    return RedirectResponse'
assert needle in part
part=part.replace(needle,'''    if slug=='pet-clinick':
        xp_pet_extra_init(db)
        db.execute(xp_survey_sql("""INSERT INTO xp_pet_clinik_extras(response_id,reception,recommendation)
            VALUES (:id,:reception,:recommendation)"""),
            {'id':submission_id,'reception':pet_reception,'recommendation':pet_recommendation})
    db.commit()
    return RedirectResponse''',1)
s=s[:a]+part+s[b:]
# Add admin editable questions, with superadmin guard and same-origin verification.
routes='''
@app.get("/admin/encuestas/{slug}/preguntas-base",response_class=HTMLResponse)
def xp_pet_question_admin(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_admin(request,db)
    if slug!='pet-clinick':raise HTTPException(404)
    q=xp_pet_questions(db,slug)
    fields=[('reception','Recepción'),('veterinarian','Médico veterinario'),
            ('overall','Trato del médico'),('clarity','Explicación'),
            ('cleanliness','Instalaciones'),('recommend','Recomendación (0–10)'),
            ('comment','Comentario')]
    body='<h1>Preguntas de Pet Clinik</h1><p class="muted">Puedes cambiar el texto sin alterar las escalas ni las respuestas existentes.</p>'
    body+='<div class="card"><form method="post" action="/admin/encuestas/pet-clinick/preguntas-base">'
    for key,label in fields:
        body+='<label>'+xp_html.escape(label)+'</label><textarea name="'+key+'" maxlength="240" rows="2" required>'+xp_html.escape(q[key])+'</textarea>'
    body+='<button class="btn" type="submit">Guardar preguntas</button></form></div>'
    body+='<a class="btn secondary" href="/admin/encuestas/pet-clinick/personalizar">Volver a personalización</a>'
    return xp_survey_page('Preguntas de Pet Clinik',body,True)

@app.post("/admin/encuestas/{slug}/preguntas-base")
async def xp_pet_question_admin_save(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_admin(request,db)
    xp_survey_same_origin(request)
    if slug!='pet-clinick':raise HTTPException(404)
    fields=('reception','veterinarian','overall','clarity','cleanliness','recommend','comment')
    form=await request.form()
    xp_pet_questions(db,slug)
    for field in fields:
        prompt=str(form.get(field,'')).strip()
        if not 5<=len(prompt)<=240:raise HTTPException(422,'Revisa la pregunta '+field)
        db.execute(xp_survey_sql("""INSERT INTO xp_survey_question_texts(slug,field,prompt)
            VALUES (:slug,:field,:prompt)
            ON CONFLICT (slug,field) DO UPDATE SET prompt=EXCLUDED.prompt"""),
            {'slug':slug,'field':field,'prompt':prompt})
    db.commit()
    return RedirectResponse('/admin/encuestas/pet-clinick/preguntas-base',303)
'''
s+='\n'+routes
# Make edit link available on the existing customization screen.
a=s.index('def xp_survey_customize(');b=s.index('\n@app.',a);part=s[a:b]
needle="    body+='<div class=\"card\"><h2>Preguntas adicionales</h2>"
assert needle in part
part=part.replace(needle,'''    if slug=='pet-clinick':
        body+='<div class="card"><h2>Preguntas actuales</h2><p>Revisa y modifica las siete preguntas de la encuesta.</p><a class="btn" href="/admin/encuestas/pet-clinick/preguntas-base">Editar preguntas</a></div>'
'''+needle,1)
s=s[:a]+part+s[b:]
p.write_text(s+'\n'+marker+'\n',encoding='utf-8')
print('Pet Clinik survey: reception, doctor care, clarity, cleanliness, NPS, editable prompts')
