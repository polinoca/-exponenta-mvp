from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY BUSINESS DASHBOARD V19"
if marker not in s:
    a=s.index("def xp_survey_business_results(")
    b=s.index("\n@app.",a)
    replacement=r'''def xp_survey_business_results(slug:str,request:Request,db:Session=Depends(get_db)):
    xp_survey_extended(db)
    try:
        _,_,p=xp_survey_business(request,db,slug)
    except HTTPException:
        xp_survey_admin(request,db)
        p=xp_survey_lookup(db,slug)
        if not p:raise HTTPException(404)
    selected=str(request.query_params.get("period","30"))
    days=int(selected) if selected in ("7","30","90") else 0
    condition=(" AND created_at >= CURRENT_TIMESTAMP - INTERVAL '"+str(days)+" days'") if days else ""
    params={"slug":slug}
    result=db.execute(xp_survey_sql("""SELECT COUNT(*) AS n,
        ROUND(AVG(overall)::numeric,2) AS attention,
        ROUND(AVG(cleanliness)::numeric,2) AS cleanliness,
        ROUND(AVG(clarity)::numeric,2) AS clarity,
        COUNT(*) FILTER (WHERE overall >= 4) AS happy,
        COUNT(*) FILTER (WHERE overall <= 2) AS low,
        COUNT(*) FILTER (WHERE NULLIF(TRIM(comment),'') IS NOT NULL) AS comments
        FROM xp_survey_responses WHERE slug=:slug"""+condition),params).mappings().first()
    count=int(result["n"] or 0)
    distribution=db.execute(xp_survey_sql("""SELECT overall AS score, COUNT(*) AS n FROM xp_survey_responses
        WHERE slug=:slug"""+condition+" GROUP BY overall ORDER BY overall DESC"),params).mappings().all()
    volumes={int(r["score"]):int(r["n"]) for r in distribution}
    trend=db.execute(xp_survey_sql("""SELECT created_at::date AS day,COUNT(*) AS n
        FROM xp_survey_responses WHERE slug=:slug"""+condition+"""
        GROUP BY created_at::date ORDER BY created_at::date DESC LIMIT 14"""),params).mappings().all()
    comments=db.execute(xp_survey_sql("""SELECT created_at,overall,cleanliness,clarity,attendant,comment
        FROM xp_survey_responses WHERE slug=:slug"""+condition+"""
        ORDER BY created_at DESC LIMIT 30"""),params).mappings().all()
    team=db.execute(xp_survey_sql("""SELECT TRIM(attendant) AS person,COUNT(*) AS n,
        ROUND(AVG(overall)::numeric,1) AS score FROM xp_survey_responses
        WHERE slug=:slug"""+condition+"""
        AND NULLIF(TRIM(attendant),'') IS NOT NULL
        GROUP BY TRIM(attendant) ORDER BY n DESC,score DESC LIMIT 8"""),params).mappings().all()
    def esc(v):
        return xp_html.escape(str(v if v is not None else ""),quote=True)
    def num(v):
        return ("%.1f" % float(v)) if v is not None else "—"
    def stars(n):
        n=max(0,min(5,int(n or 0)))
        return '<span class="xp-db-stars" aria-label="'+str(n)+' de 5 estrellas">'+('★'*n)+'</span><span class="xp-db-empty">'+('☆'*(5-n))+'</span>'
    labels={1:"Nada bueno",2:"No muy bueno",3:"Bueno",4:"Excelente",5:"Excepcional"}
    style="""<style>
    :root{--primary:#2D71B1!important;--secondary:#4BB8DE!important}
    body{background:#F4FAFD!important;color:#17324D!important}
    header{background:#fff!important;color:#17324D!important;border-bottom:1px solid #DCECF5}
    header a{color:#2D71B1!important}
    main{max-width:1080px!important;padding-top:20px!important}
    .xp-db-head{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin:15px 0 22px}
    .xp-db-head h1{color:#17324D;font-size:clamp(26px,5vw,36px);margin:5px 0 6px;letter-spacing:-.03em}
    .xp-db-kicker{font-size:12px;color:#2D71B1;font-weight:800;letter-spacing:.09em}
    .xp-db-sub{color:#5F7690;margin:0;font-size:14px}
    .xp-db-actions{display:flex;gap:9px;flex-wrap:wrap}
    .xp-db-actions a,.xp-db-tabs a{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;font-weight:750;border-radius:12px;padding:10px 14px;border:1px solid #CBDFEC;color:#2D71B1;background:white}
    .xp-db-actions a:first-child{background:#2D71B1;color:white;border-color:#2D71B1}
    .xp-db-tabs{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 20px}
    .xp-db-tabs a{font-size:13px;padding:8px 13px}
    .xp-db-tabs a.selected{background:#2D71B1;color:white}
    .xp-db-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
    .xp-db-stat,.xp-db-panel{background:white;border:1px solid #DDEBF4;border-radius:21px;box-shadow:0 7px 24px rgba(25,80,124,.045)}
    .xp-db-stat{padding:20px 18px}
    .xp-db-stat small{display:block;color:#5F7690;font-size:13px;font-weight:650}
    .xp-db-stat strong{display:block;color:#2D71B1;font-size:clamp(25px,4vw,34px);line-height:1.4;letter-spacing:-.04em}
    .xp-db-stat span{color:#72899A;font-size:12px}
    .xp-db-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:16px}
    .xp-db-panel{padding:22px;margin:0;min-width:0}
    .xp-db-panel h2{font-size:18px;margin:0 0 5px;color:#17324D}
    .xp-db-caption{font-size:12px;color:#748A9B;margin:0 0 18px}
    .xp-db-dist-row{display:grid;grid-template-columns:104px 1fr 44px;gap:10px;align-items:center;margin:12px 0}
    .xp-db-dist-row .rating{font-size:12px;color:#355770}
    .xp-db-bar-track{height:11px;background:#E8F2F8;border-radius:30px;overflow:hidden}
    .xp-db-bar-fill{height:100%;background:#4BB8DE;border-radius:30px}
    .xp-db-count{font-size:13px;text-align:right;color:#536F83}
    .xp-db-trend{height:160px;display:flex;align-items:flex-end;gap:8px;border-bottom:1px solid #E2EDF4;padding:10px 0 0}
    .xp-db-trend-item{height:100%;flex:1;min-width:0;display:flex;align-items:center;justify-content:end;flex-direction:column;gap:5px}
    .xp-db-trend-item .xp-db-column{width:min(80%,27px);min-height:3px;background:#4BB8DE;border-radius:7px 7px 0 0}
    .xp-db-trend-item .xp-db-day{font-size:10px;color:#6F879A;white-space:nowrap}
    .xp-db-stars{color:#4BB8DE;letter-spacing:1px}.xp-db-empty{color:#CFDCE5;letter-spacing:1px}
    .xp-db-table{width:100%;border-collapse:collapse}
    .xp-db-table th{text-align:left;color:#6C8799;font-size:12px;padding:13px 8px;border-bottom:1px solid #E2EDF4}
    .xp-db-table td{vertical-align:top;padding:13px 8px;border-bottom:1px solid #EDF3F7;font-size:13px;color:#35536B;overflow-wrap:anywhere}
    .xp-db-table tr:last-child td{border:0}
    .xp-db-comments{grid-column:1/-1}
    .xp-db-empty-state{padding:25px 10px;text-align:center;color:#6E8798}
    .xp-db-badge{display:inline-block;border-radius:30px;padding:4px 9px;background:#EAF6FC;color:#2D71B1;font-size:11px;font-weight:800}
    @media(max-width:800px){.xp-db-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.xp-db-grid{grid-template-columns:1fr}.xp-db-comments{grid-column:auto}}
    @media(max-width:540px){main{padding:13px 12px 60px!important}.xp-db-head{margin-top:8px}.xp-db-actions{width:100%}.xp-db-actions a{flex:1;font-size:13px}.xp-db-stat{padding:15px 13px;border-radius:17px}.xp-db-panel{padding:17px 14px;border-radius:18px}.xp-db-dist-row{grid-template-columns:90px 1fr 30px;gap:7px}.xp-db-table thead{display:none}.xp-db-table tr{display:block;margin-bottom:12px;border:1px solid #E3EDF4;border-radius:13px;padding:10px}.xp-db-table td{display:block;border:0;padding:4px 3px}.xp-db-table td:before{content:attr(data-label);font-weight:800;color:#2D71B1;font-size:11px;display:block}}
    </style>"""
    body=style+'<section class="xp-db-head"><div><div class="xp-db-kicker">TABLERO DE EXPERIENCIA</div><h1>'+esc(p["name"])+'</h1><p class="xp-db-sub">Opiniones de clientes y desempeño de atención</p></div>'
    body+='<div class="xp-db-actions"><a href="/negocio/encuestas/'+esc(slug)+'/promocion">Editar promoción</a><a target="_blank" rel="noopener" href="/encuesta/'+esc(slug)+'">Ver encuesta ↗</a></div></section>'
    body+='<nav class="xp-db-tabs" aria-label="Periodo">'
    for name,value in (("7 días","7"),("30 días","30"),("90 días","90"),("Todo","all")):
        body+='<a class="'+("selected" if selected==value or (days==0 and value=="all") else "")+'" href="/negocio/encuestas/'+esc(slug)+'?period='+value+'">'+name+'</a>'
    body+='</nav>'
    cards=[("Respuestas",str(count),"Opiniones registradas"),
       ("Atención",num(result["attention"])+"/5","Promedio de atención"),
       ("Limpieza",num(result["cleanliness"])+"/5","Promedio de limpieza"),
       ("Claridad",num(result["clarity"])+"/5","Explicación al cliente")]
    body+='<div class="xp-db-stats">'
    for title,value,sub in cards:
        body+='<article class="xp-db-stat"><small>'+title+'</small><strong>'+value+'</strong><span>'+sub+'</span></article>'
    body+='</div><div class="xp-db-grid">'
    body+='<section class="xp-db-panel"><h2>Distribución de calificaciones</h2><p class="xp-db-caption">Calificación de la atención recibida · 1 a 5 estrellas</p>'
    for score in range(5,0,-1):
        n=volumes.get(score,0);percent=100*n/count if count else 0
        body+='<div class="xp-db-dist-row"><span class="rating">'+str(score)+' ★ · '+labels[score]+'</span><div class="xp-db-bar-track" role="meter" aria-label="'+labels[score]+'" aria-valuenow="'+str(n)+'" aria-valuemin="0" aria-valuemax="'+str(max(count,1))+'"><div class="xp-db-bar-fill" style="width:'+str(round(percent,1))+'%"></div></div><span class="xp-db-count">'+str(n)+'</span></div>'
    body+='</section>'
    body+='<section class="xp-db-panel"><h2>Evolución de respuestas</h2><p class="xp-db-caption">Últimos 14 días con actividad dentro del periodo</p>'
    if trend:
        chronological=list(reversed(trend));top=max(int(r["n"]) for r in chronological)
        body+='<div class="xp-db-trend" role="img" aria-label="Respuestas por fecha">'
        for r in chronological:
            v=int(r["n"]);h=max(5,round(120*v/max(top,1)))
            date=str(r["day"]);label=date[5:10]
            body+='<div class="xp-db-trend-item" title="'+esc(date)+': '+str(v)+' respuestas"><strong style="font-size:10px;color:#2D71B1">'+str(v)+'</strong><div class="xp-db-column" style="height:'+str(h)+'px"></div><span class="xp-db-day">'+esc(label)+'</span></div>'
        body+='</div>'
    else:body+='<div class="xp-db-empty-state">Sin respuestas registradas en este periodo.</div>'
    body+='</section>'
    body+='<section class="xp-db-panel"><h2>Indicadores de experiencia</h2><p class="xp-db-caption">Se calculan únicamente con las respuestas recibidas</p>'
    for title,value in (("Evaluaciones excelentes o excepcionales",int(result["happy"] or 0)),("Calificaciones bajas (1–2 estrellas)",int(result["low"] or 0)),("Opiniones con comentario",int(result["comments"] or 0))):
        pct=(100*value/count) if count else 0
        body+='<div style="display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid #EBF2F7"><span style="font-size:13px;color:#4D6A7D">'+esc(title)+'</span><strong style="color:#2D71B1;white-space:nowrap">'+str(value)+' · '+str(round(pct))+'%</strong></div>'
    body+='</section>'
    body+='<section class="xp-db-panel"><h2>Colaboradores mencionados</h2><p class="xp-db-caption">Según el nombre escrito por los clientes</p>'
    if team:
        for t in team:
            body+='<div style="display:flex;justify-content:space-between;gap:14px;padding:11px 0;border-bottom:1px solid #EBF2F7"><span style="font-size:13px;color:#35536B">'+esc(t["person"])+' <small style="color:#8294A3">('+str(t["n"])+')</small></span><strong style="white-space:nowrap;color:#2D71B1">'+num(t["score"])+' ★</strong></div>'
    else:body+='<div class="xp-db-empty-state">Aún no hay nombres registrados.</div>'
    body+='</section>'
    body+='<section class="xp-db-panel xp-db-comments"><h2>Comentarios y respuestas recientes</h2><p class="xp-db-caption">Últimas 30 respuestas del periodo seleccionado</p>'
    if comments:
        body+='<table class="xp-db-table"><thead><tr><th>Fecha</th><th>Atención</th><th>Limpieza</th><th>Claridad</th><th>Colaborador</th><th>Comentario</th></tr></thead><tbody>'
        for r in comments:
            body+='<tr><td data-label="Fecha">'+esc(str(r["created_at"])[:16])+'</td><td data-label="Atención">'+stars(r["overall"])+'</td><td data-label="Limpieza">'+stars(r["cleanliness"])+'</td><td data-label="Claridad">'+stars(r["clarity"])+'</td><td data-label="Colaborador">'+(esc(r["attendant"]) if r["attendant"] else '—')+'</td><td data-label="Comentario">'+(esc(r["comment"]) if r["comment"] else '—')+'</td></tr>'
        body+='</tbody></table>'
    else:body+='<div class="xp-db-empty-state">Todavía no hay comentarios ni calificaciones para este periodo.</div>'
    body+='</section></div>'
    return xp_survey_business_theme("Resultados · "+str(p["name"]),body,p)
'''
    s=s[:a]+replacement+s[b:]
    p.write_text(marker+"\n"+s,encoding="utf-8")
print("Business survey analytics dashboard updated")
