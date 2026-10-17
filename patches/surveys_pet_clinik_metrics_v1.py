from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK CLIENT METRICS V1'
if marker not in s:
    a=s.index('def xp_survey_business_results('); b=s.index('\n@app.',a); part=s[a:b]
    anchor='    trend=db.execute('
    assert anchor in part
    extra=r'''    pet_summary=None
    if slug=='pet-clinick':
        xp_pet_extra_init(db)
        pet_summary=db.execute(xp_survey_sql("""SELECT ROUND(AVG(e.reception)::numeric,2) AS reception, ROUND(AVG(e.recommendation)::numeric,2) AS recommendation FROM xp_survey_responses r LEFT JOIN xp_pet_clinik_extras e ON e.response_id=r.id WHERE r.slug=:slug"""+condition),params).mappings().first()
        for metric,column in (('reception','reception'),('recommendation','recommendation')):
            rows=db.execute(xp_survey_sql("SELECT e."+column+" AS score,COUNT(*) AS n FROM xp_survey_responses r JOIN xp_pet_clinik_extras e ON e.response_id=r.id WHERE r.slug=:slug"+condition+" GROUP BY e."+column),params).mappings().all()
            breakdown[metric]={int(row['score']):int(row['n']) for row in rows if row['score'] is not None}
'''
    part=part.replace(anchor,extra+anchor,1)
    old_cards='''    cards=[("Respuestas",str(count),"Opiniones registradas"),
       ("Atención",num(result["attention"])+"/5","Promedio de atención"),
       ("Limpieza",num(result["cleanliness"])+"/5","Promedio de limpieza"),
       ("Claridad",num(result["clarity"])+"/5","Explicación al cliente")]'''
    assert old_cards in part
    new_cards='''    cards=[("Respuestas",str(count),"Opiniones registradas"),("Atención",num(result["attention"])+"/5","Promedio de atención"),("Limpieza",num(result["cleanliness"])+"/5","Promedio de limpieza"),("Claridad",num(result["clarity"])+"/5","Explicación al cliente")]
    if slug=='pet-clinick':
        cards=[("Respuestas",str(count),"Opiniones registradas"),("Recepción",num(pet_summary["reception"])+"/5","Atención desde la llegada"),("Trato médico",num(result["attention"])+"/5","Atención a cliente y mascota"),("Instalaciones",num(result["cleanliness"])+"/5","Limpieza y comodidad"),("Claridad",num(result["clarity"])+"/5","Explicación y confianza"),("Recomendación",num(pet_summary["recommendation"])+"/5","Probabilidad de recomendar")]'''
    part=part.replace(old_cards,new_cards,1)
    first="    for key,title in (('overall','Atención'),('cleanliness','Limpieza'),('clarity','Claridad'),('compare','Comparar')):"
    assert first in part
    part=part.replace(first,"""    categories=[('overall','Trato médico'),('cleanliness','Instalaciones'),('clarity','Claridad')]
    if slug=='pet-clinick': categories=[('reception','Recepción')]+categories+[('recommendation','Recomendación')]
    for key,title in categories+[('compare','Comparar')]:""",1)
    second="    for key,title in (('overall','Atención'),('cleanliness','Limpieza'),('clarity','Claridad')):"
    assert second in part
    part=part.replace(second,"    for key,title in categories:",1)
    old_compare="    for title,key in (('Atención','attention'),('Limpieza','cleanliness'),('Claridad','clarity')):"
    assert old_compare in part
    part=part.replace(old_compare,"""    compare_metrics=[('Trato médico','attention'),('Instalaciones','cleanliness'),('Claridad','clarity')]
    if slug=='pet-clinick': compare_metrics=[('Recepción','reception'),('Trato médico','attention'),('Instalaciones','cleanliness'),('Claridad','clarity'),('Recomendación','recommendation')]
    for title,key in compare_metrics:""",1)
    old_value='''        value=result[key]
        width=round(float(value)*20,1) if value is not None else 0'''
    assert old_value in part
    part=part.replace(old_value,'''        value=(pet_summary[key] if slug=='pet-clinick' and key in ('reception','recommendation') else result[key])
        width=round(float(value)*20,1) if value is not None else 0''',1)
    part=part.replace("grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-bottom:18px","grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-bottom:18px",1)
    s=s[:a]+part+s[b:]
    p.write_text(s+'\n'+marker+'\n',encoding='utf-8')
print('Pet Clinik metrics ready')