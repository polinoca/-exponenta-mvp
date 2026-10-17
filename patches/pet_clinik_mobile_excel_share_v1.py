from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK MOBILE EXCEL SHARE V1'
if marker not in s:
    s=s.replace('''    xp_survey_extended(db)
    try:
        _,_,brand=xp_survey_business(request,db,slug)''','''    xp_survey_extended(db)
    if slug=='pet-clinick':
        xp_pet_extra_init(db)
    try:
        _,_,brand=xp_survey_business(request,db,slug)''',1)
    old_query='''SELECT id,created_at,overall,cleanliness,clarity,
        attendant,comment FROM xp_survey_responses WHERE slug=:slug'''
    new_query='''SELECT r.id,r.created_at,r.overall,r.cleanliness,r.clarity,r.attendant,r.comment,e.reception,e.recommendation
        FROM xp_survey_responses r LEFT JOIN xp_pet_clinik_extras e ON e.response_id=r.id WHERE r.slug=:slug'''
    assert old_query in s
    s=s.replace(old_query,new_query,1)
    old_titles='''titles=["Fecha","Atención","Limpieza","Claridad","Quién atendió","Comentario"]
    rows=[titles]
    for r in responses:
        rows.append([str(r["created_at"])[:19],r["overall"],r["cleanliness"],r["clarity"],r["attendant"] or "",r["comment"] or ""])'''
    new_titles='''titles=["Fecha","Recepción","Trato médico","Instalaciones","Claridad","Recomendación","Quién atendió","Comentario"]
    rows=[titles]
    for r in responses:
        rows.append([str(r["created_at"])[:19],r["reception"] or "",r["overall"],r["cleanliness"],r["clarity"],r["recommendation"] or "",r["attendant"] or "",r["comment"] or ""])'''
    assert old_titles in s
    s=s.replace(old_titles,new_titles,1)
    s=s.replace('''<col min="5" max="5" width="25" customWidth="1"/><col min="6" max="6" width="65" customWidth="1"/>''','''<col min="5" max="6" width="17" customWidth="1"/><col min="7" max="7" width="25" customWidth="1"/><col min="8" max="8" width="65" customWidth="1"/>''',1)
    s=s.replace("'<autoFilter ref=\"A1:F'+str(max(1,len(rows)))+'\"/></worksheet>'","'<autoFilter ref=\"A1:H'+str(max(1,len(rows)))+'\"/></worksheet>'",1)
    a=s.index('def xp_survey_business_results('); b=s.index('\n@app.',a); part=s[a:b]
    mobile_css='@media(max-width:540px){.xp-db-actions{display:grid!important;grid-template-columns:1fr 1fr!important;width:100%;gap:8px}.xp-db-actions a,.xp-db-actions button{width:100%;min-height:48px!important;padding:10px 8px!important;font-size:12px!important;white-space:normal}.xp-db-tabs{overflow-x:auto;flex-wrap:nowrap;padding-bottom:4px}.xp-db-tabs a{white-space:nowrap;flex:0 0 auto}}'
    assert '    body=style+' in part
    part=part.replace('    body=style+',"    body=style.replace('</style>',mobile_css+'</style>')+",1)
    anchor="    body+='<nav class=\"xp-db-tabs\""
    assert anchor in part
    share_fix="""    body+=\"\"\"<script>(function(){var btn=document.getElementById('xp-share-excel'),link=document.getElementById('xp-export-excel');if(!btn||!link)return;btn.addEventListener('click',async function(e){e.preventDefault();e.stopImmediatePropagation();var filename='pet-clinik-resultados.xlsx';try{if(navigator.share&&window.isSecureContext&&window.File){var response=await fetch(link.href,{credentials:'same-origin'});if(!response.ok)throw new Error('download');var file=new File([await response.blob()],filename,{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});if(!navigator.canShare||navigator.canShare({files:[file]})){await navigator.share({files:[file],title:'Resultados PET Clinik'});return;}}}catch(err){if(err&&err.name==='AbortError')return;}link.click();},true);})();</script>\"\"\"
"""
    part=part.replace(anchor,share_fix+anchor,1)
    s=s[:a]+part+s[b:]
    p.write_text(s+'\n'+marker+'\n',encoding='utf-8')
print('Mobile-first PET Clinik Excel export and share ready')
