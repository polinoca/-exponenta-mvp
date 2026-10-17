from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK FULL STAFF RESPONSES V1'
if marker not in s:
    a=s.index('def xp_survey_business_results(')
    b=s.index('\n@app.',a)
    part=s[a:b]
    old_select='''SELECT created_at,overall,cleanliness,clarity,attendant,comment
        FROM xp_survey_responses WHERE slug=:slug'''
    new_select='''SELECT r.created_at,r.overall,r.cleanliness,r.clarity,r.attendant,r.comment,e.reception,e.recommendation
        FROM xp_survey_responses r LEFT JOIN xp_pet_clinik_extras e ON e.response_id=r.id WHERE r.slug=:slug'''
    assert old_select in part
    part=part.replace(old_select,new_select,1)
    old_limit='ORDER BY created_at DESC LIMIT 30'
    assert old_limit in part
    part=part.replace(old_limit,'ORDER BY created_at DESC LIMIT 5000',1)
    old_head='<th>Fecha</th><th>Atención</th><th>Limpieza</th><th>Claridad</th><th>Colaborador</th><th>Comentario</th>'
    new_head='<th>Fecha</th><th>Recepción</th><th>Trato médico</th><th>Instalaciones</th><th>Claridad</th><th>Recomendación</th><th>Colaborador</th><th>Comentario</th>'
    assert old_head in part
    part=part.replace(old_head,new_head,1)
    old_row='''<td data-label="Atención">'+stars(r["overall"])+'</td><td data-label="Limpieza">'+stars(r["cleanliness"])+'</td><td data-label="Claridad">'+stars(r["clarity"])+'</td><td data-label="Colaborador">'''
    new_row='''<td data-label="Recepción">'+(stars(r["reception"]) if r["reception"] is not None else '—')+'</td><td data-label="Trato médico">'+stars(r["overall"])+'</td><td data-label="Instalaciones">'+stars(r["cleanliness"])+'</td><td data-label="Claridad">'+stars(r["clarity"])+'</td><td data-label="Recomendación">'+(stars(r["recommendation"]) if r["recommendation"] is not None else '—')+'</td><td data-label="Colaborador">'''
    assert old_row in part
    part=part.replace(old_row,new_row,1)
    part=part.replace('Comentarios y respuestas recientes','Detalle de respuestas recibidas',1)
    part=part.replace('Últimas 30 respuestas del periodo seleccionado','Historial completo del periodo seleccionado · al elegir un colaborador verás todas sus respuestas detalladas',1)
    s=s[:a]+part+s[b:]
    p.write_text(s+'\n'+marker+'\n',encoding='utf-8')
print('Full staff response detail ready')
