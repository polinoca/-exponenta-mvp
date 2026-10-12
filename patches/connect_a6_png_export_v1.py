from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
anchor='@app.get("/admin/connect/{slug}/material", response_class=HTMLResponse)'
if anchor not in s: raise SystemExit("Connect material anchor not found")
route='''
@app.get("/admin/connect/{slug}/download-material-a6.png")
def xp_connect_material_a6_png(slug: str, request: Request, decor: int = 1, db: Session = Depends(get_db)):
    """Full A6 print artwork at 300 DPI, including all branding and text."""
    import fitz
    from fastapi.responses import Response
    pdf=xp_connect_material_pdf_v2(slug=slug,request=request,size="a6",decor=decor,db=db)
    doc=fitz.open(stream=pdf.body,filetype="pdf")
    page=doc[0]
    pix=page.get_pixmap(matrix=fitz.Matrix(300/72,300/72),alpha=False,colorspace=fitz.csRGB)
    png=pix.tobytes("png")
    doc.close()
    return Response(content=png,media_type="image/png",headers={
        "Content-Disposition":f'attachment; filename="{slug}-A6-300dpi.png"',
        "Cache-Control":"no-store",
        "X-Print-Size":"105x148mm; 300dpi"
    })

'''
s=s.replace(anchor,route+anchor,1)
p.write_text(s,encoding="utf-8")
t=Path("/app/app/templates/admin/connect_material.html")
s=t.read_text(encoding="utf-8")
needle='<button class="btn btn-primary" type="button" onclick="xpMaterialPDF(\'a6\')">PDF A6</button>'
if needle not in s: raise SystemExit("PDF A6 button not found")
s=s.replace(needle,needle+'\n      <button class="btn btn-secondary" type="button" onclick="xpMaterialPNG()">Imagen A6 HD (PNG)</button>',1)
needle='function xpMaterialPDF(size){'
if needle not in s: raise SystemExit("PDF JS function not found")
s=s.replace(needle,'''function xpMaterialPNG(){
 const decor=document.getElementById("xp-decor").checked?"1":"0";
 window.location.href="/admin/connect/{{ profile.slug }}/download-material-a6.png?decor="+decor;
}
'''+needle,1)
t.write_text(s,encoding="utf-8")
print("A6 300dpi PNG download enabled")
