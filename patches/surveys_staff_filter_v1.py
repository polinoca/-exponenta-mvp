from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text()
marker='# XP STAFF FILTER V1'
assert marker not in s
a=s.index('def xp_survey_business_results(')
b=s.index('\n@app.',a)
part=s[a:b]
part=part.replace('    comments=db.execute(','''    selected_person=str(request.query_params.get('colaborador','')).strip()[:120]
    staff_condition=" AND LOWER(TRIM(attendant))=LOWER(:staff)" if selected_person else ""
    if selected_person:
        params['staff']=selected_person
    comments=db.execute(''',1)
part=part.replace('FROM xp_survey_responses WHERE slug=:slug"""+condition+"""\n        ORDER BY created_at DESC LIMIT 30','FROM xp_survey_responses WHERE slug=:slug"""+condition+staff_condition+"""\n        ORDER BY created_at DESC LIMIT 30',1)
part=part.replace('    body+=\'<section class="xp-db-panel"><h2>Colaboradores mencionados','''    from urllib.parse import quote as xp_staff_quote
    period_url='/negocio/encuestas/'+xp_staff_quote(slug,safe='')+'?period='+str(selected if selected in ('7','30','90') else 'all')
    body+='<section class="xp-db-panel"><h2>Colaboradores mencionados''',1)
part=part.replace('        for t in team:\n            body+=', '''        for t in team:
            active=selected_person.casefold()==str(t["person"]).casefold()
            url=period_url if active else period_url+'&colaborador='+xp_staff_quote(str(t["person"]),safe='')
            body+='<a href="'+esc(url)+'" style="display:block;text-decoration:none;border-radius:9px;'+('background:#E8F2F8;' if active else '')+'" aria-label="Ver encuestas de '+esc(t["person"])+'">'
            body+=''',1)
part=part.replace("+' ★</strong></div>'","+' ★</strong></div></a>'",1)
part=part.replace('    body+=\'<section class="xp-db-panel xp-db-comments"><h2>Comentarios y respuestas recientes</h2>', '''    if selected_person:
        body+='<div style="background:#E8F2F8;border:1px solid #CBDFEC;border-radius:14px;padding:14px;margin:15px 0;color:#17324D"><strong>Encuestas de '+esc(selected_person)+'</strong> · '+str(len(comments))+' resultados mostrados <a href="'+esc(period_url)+'" style="color:#2D71B1;font-weight:750;display:inline-block;margin-left:10px">✕ Ver todos</a></div>'
    body+='<section class="xp-db-panel xp-db-comments"><h2>Comentarios y respuestas recientes</h2>''',1)
s=s[:a]+part+s[b:]
p.write_text(s+'\n'+marker+'\n')
