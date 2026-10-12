from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text()
marker='# XP CATEGORY DISTRIBUTIONS V1'
assert marker not in s
a=s.index('def xp_survey_business_results(')
b=s.index('\n@app.',a)
part=s[a:b]
needle='    trend=db.execute('
assert needle in part
part=part.replace(needle,'''    breakdown={}
    for metric in ('overall','cleanliness','clarity'):
        rows=db.execute(xp_survey_sql('SELECT '+metric+' AS score,COUNT(*) AS n FROM xp_survey_responses WHERE slug=:slug'+condition+' GROUP BY '+metric),params).mappings().all()
        breakdown[metric]={int(row['score']):int(row['n']) for row in rows if row['score'] is not None}
'''+needle,1)
start=part.index('    body+=\'<section class="xp-db-panel"><h2>Distribución de calificaciones')
end=part.index('    body+=\'<section class="xp-db-panel"><h2>Evolución de respuestas',start)
new='''    body+='<section class="xp-db-panel xp-categories"><h2>Distribución de calificaciones</h2><p class="xp-db-caption">Elige qué aspecto deseas consultar</p>'
    body+='<div class="xp-category-tabs" role="group" aria-label="Categoría">'
    for key,title in (('overall','Atención'),('cleanliness','Limpieza'),('clarity','Claridad'),('compare','Comparar')):
        body+='<button type="button" data-cat="'+key+'" class="'+('active' if key=='overall' else '')+'" aria-pressed="'+('true' if key=='overall' else 'false')+'">'+title+'</button>'
    body+='</div>'
    for key,title in (('overall','Atención'),('cleanliness','Limpieza'),('clarity','Claridad')):
        total=sum(breakdown[key].values())
        body+='<div data-view="'+key+'"'+('' if key=='overall' else ' hidden')+'><p class="xp-db-caption">'+title+' · '+str(total)+' respuestas</p>'
        for score in range(5,0,-1):
            n=breakdown[key].get(score,0)
            percent=100*n/total if total else 0
            body+='<div class="xp-db-dist-row"><span class="rating">'+str(score)+' ★ · '+labels[score]+'</span><div class="xp-db-bar-track"><div class="xp-db-bar-fill" style="width:'+str(round(percent,1))+'%"></div></div><span class="xp-db-count">'+str(n)+'</span></div>'
        body+='</div>'
    body+='<div data-view="compare" hidden><p class="xp-db-caption">Comparación de promedios</p>'
    for title,key in (('Atención','attention'),('Limpieza','cleanliness'),('Claridad','clarity')):
        value=result[key]
        width=round(float(value)*20,1) if value is not None else 0
        body+='<div class="xp-compare-row"><span>'+title+'</span><div class="xp-db-bar-track"><div class="xp-db-bar-fill" style="width:'+str(width)+'%"></div></div><strong>'+num(value)+'/5</strong></div>'
    body+='</div></section>'
    body+='<script>document.querySelectorAll(".xp-categories [data-cat]").forEach(function(btn){btn.addEventListener("click",function(){var box=btn.closest(".xp-categories");box.querySelectorAll("[data-cat]").forEach(function(b){var on=b===btn;b.classList.toggle("active",on);b.setAttribute("aria-pressed",String(on))});box.querySelectorAll("[data-view]").forEach(function(v){v.hidden=v.dataset.view!==btn.dataset.cat})})});</script>'
'''
part=part[:start]+new+part[end:]
needle='    body=style+welcome+'
assert needle in part
part=part.replace(needle,'''    style=style.replace('</style>','.xp-category-tabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-bottom:18px}.xp-category-tabs button{min-height:44px;border:1px solid #CBDFEC;border-radius:11px;background:white;color:#2D71B1;font-weight:750;font-size:12px;padding:8px 3px}.xp-category-tabs button.active{background:#2D71B1;color:white}.xp-categories [hidden]{display:none!important}.xp-compare-row{display:grid;grid-template-columns:75px 1fr 55px;align-items:center;gap:9px;margin:16px 0;font-size:13px}.xp-compare-row strong{color:#2D71B1;text-align:right}@media(max-width:390px){.xp-category-tabs{grid-template-columns:repeat(2,1fr)}}</style>')
'''+needle,1)
s=s[:a]+part+s[b:]
a=s.index('def xp_business_survey_promotion(')
b=s.index('\n@app.',a)
part=s[a:b]
needle="    return xp_survey_page('Promoción',body)"
assert needle in part
part=part.replace(needle,"    body='<style>form button.btn[type=submit]{background:#2D71B1!important;border-color:#2D71B1!important;color:white!important}</style>'+body\n"+needle)
s=s[:a]+part+s[b:]
p.write_text(s+'\n'+marker+'\n')
print('Category charts and blue promotion button ready')
