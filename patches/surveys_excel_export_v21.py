from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY EXCEL EXPORT V21"
if marker not in s:
    route=r'''
# XP SURVEY EXCEL EXPORT V21
@app.get("/negocio/encuestas/{slug}/excel")
def xp_survey_business_excel(slug:str,request:Request,db:Session=Depends(get_db)):
    from fastapi.responses import Response
    from zipfile import ZipFile, ZIP_DEFLATED
    from xml.sax.saxutils import escape as xml_escape
    xp_survey_extended(db)
    try:
        _,_,brand=xp_survey_business(request,db,slug)
    except HTTPException:
        xp_survey_admin(request,db)
        brand=xp_survey_lookup(db,slug)
        if not brand:raise HTTPException(404)
    selected=str(request.query_params.get("period","30"))
    days=int(selected) if selected in ("7","30","90") else 0
    condition=(" AND created_at >= CURRENT_TIMESTAMP - INTERVAL '"+str(days)+" days'") if days else ""
    responses=db.execute(xp_survey_sql("""SELECT id,created_at,overall,cleanliness,clarity,
        attendant,comment FROM xp_survey_responses WHERE slug=:slug"""+condition+
        " ORDER BY created_at DESC"),{"slug":slug}).mappings().all()
    titles=["Fecha","Atención","Limpieza","Claridad","Quién atendió","Comentario"]
    rows=[titles]
    for r in responses:
        rows.append([str(r["created_at"])[:19],r["overall"],r["cleanliness"],r["clarity"],r["attendant"] or "",r["comment"] or ""])
    xml=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
         '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="18"/><cols><col min="1" max="1" width="22" customWidth="1"/><col min="2" max="4" width="15" customWidth="1"/><col min="5" max="5" width="25" customWidth="1"/><col min="6" max="6" width="65" customWidth="1"/></cols><sheetData>']
    def col(i):
        output=""
        while i:
            i,v=divmod(i-1,26);output=chr(65+v)+output
        return output
    for y,row in enumerate(rows,1):
        xml.append('<row r="'+str(y)+'">')
        for x,v in enumerate(row,1):
            ref=col(x)+str(y)
            if isinstance(v,int):
                xml.append('<c r="'+ref+'"><v>'+str(v)+'</v></c>')
            else:
                safe="".join(ch for ch in str(v) if ord(ch)>=32 or ch in "\t\n\r")
                xml.append('<c r="'+ref+'" t="inlineStr"><is><t xml:space="preserve">'+xml_escape(safe)+'</t></is></c>')
        xml.append('</row>')
    xml.append('</sheetData><autoFilter ref="A1:F'+str(max(1,len(rows)))+'"/></worksheet>')
    output=xp_survey_io.BytesIO()
    with ZipFile(output,"w",ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        z.writestr("_rels/.rels",'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml",'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Respuestas" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr("xl/worksheets/sheet1.xml","".join(xml))
    filename="encuesta-"+xp_survey_clean_slug(slug)+"-"+selected+".xlsx"
    return Response(output.getvalue(),media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition":'attachment; filename="'+filename+'"',"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"})

'''
    key='@app.get("/negocio/encuestas/{slug}",response_class=HTMLResponse)'
    assert key in s
    s=s.replace(key,route+key,1)
    a=s.index("def xp_survey_business_results(");b=s.index("\n@app.",a)
    part=s[a:b]
    search="    body+='<nav class=\"xp-db-tabs\""
    assert search in part
    insert='''    body+='<div class="xp-db-actions" style="margin:-5px 0 18px"><a id="xp-export-excel" href="/negocio/encuestas/'+esc(slug)+'/excel?period='+esc(selected)+'" download style="background:#fff;color:#2D71B1;border-color:#CFE6F3">↓ Descargar Excel</a><button id="xp-share-excel" type="button" style="background:#EAF6FC;border:1px solid #CFE6F3;border-radius:12px;padding:10px 14px;min-height:44px;color:#2D71B1;font-size:13px;font-weight:750;cursor:pointer">Compartir Excel ↗</button></div>'
    body+="""<script>(function(){
    var btn=document.getElementById('xp-share-excel'),link=document.getElementById('xp-export-excel');
    if(!btn||!link)return;
    btn.addEventListener('click',async function(){
        btn.disabled=true;
        try{
            var response=await fetch(link.href,{credentials:'same-origin'});
            if(!response.ok)throw new Error('No se pudo generar el archivo');
            var blob=await response.blob();
            var file=new File([blob],'pet-clinik-encuesta.xlsx',{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
            if(navigator.canShare&&navigator.canShare({files:[file]})){
                await navigator.share({files:[file],title:'Resultados de encuesta'});
            }else{
                var url=URL.createObjectURL(blob),a=document.createElement('a');
                a.href=url;a.download=file.name;document.body.appendChild(a);a.click();a.remove();
                setTimeout(function(){URL.revokeObjectURL(url)},30000);
                alert('Archivo descargado. Puedes compartirlo desde Archivos o Descargas.');
            }
        }catch(e){if(e.name!=='AbortError')alert('No fue posible compartir. Prueba Descargar Excel.');}
        finally{btn.disabled=false;}
    });
    })();</script>"""
'''
    part=part.replace(search,insert+search,1)
    s=s[:a]+part+s[b:]
    p.write_text(marker+"\n"+s,encoding="utf-8")
print("Private Excel .xlsx export and native mobile share enabled")
