from pathlib import Path
p=Path("/app/app/templates/admin/connect_material.html")
s=p.read_text(encoding="utf-8")
s=s.replace('onclick="downloadQR()">Descargar QR PNG</button>', 'onclick="downloadQR()">Descargar QR PNG</button>')
s=s.replace('onclick="window.print()">Imprimir / Guardar PDF</button>', 'onclick="saveMaterialPDF()">Imprimir / Guardar PDF</button>')
start=s.find('function downloadQR(){')
end=s.find('\n}',start)
if start<0 or end<0: raise SystemExit("QR function not found")
s=s[:start]+'''function downloadQR(){
  const url="/admin/connect/{{ profile.slug }}/download-qr.png";
  const a=document.createElement("a");
  a.href=url;
  a.download="{{ profile.slug }}-exponenta-connect-qr.png";
  document.body.appendChild(a);
  a.click();
  a.remove();
}
function saveMaterialPDF(){
  window.location.href="/admin/connect/{{ profile.slug }}/download-material.pdf";
}'''+s[end+2:]
p.write_text(s,encoding="utf-8")

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
anchor='@app.get("/admin/connect/{slug}/material", response_class=HTMLResponse)'
if anchor not in s: raise SystemExit("Material route missing")
routes=r'''
@app.get("/admin/connect/{slug}/download-qr.png")
def xp_connect_download_qr(slug: str, request: Request, db: Session = Depends(get_db)):
    import io, qrcode
    from fastapi.responses import Response
    control_superadmin(request, db)
    xp_connect_ensure(db)
    row=db.execute(xp_sql_text("SELECT slug FROM exponenta_connect_profiles WHERE slug=:slug"), {"slug":slug}).first()
    if not row: raise HTTPException(404)
    payload=str(request.base_url).rstrip("/") + "/connect/" + slug
    qr=qrcode.QRCode(box_size=14,border=4,error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(payload)
    qr.make(fit=True)
    out=io.BytesIO()
    qr.make_image(fill_color="black",back_color="white").save(out,format="PNG")
    return Response(content=out.getvalue(),media_type="image/png",headers={"Content-Disposition":f'attachment; filename="{slug}-exponenta-connect-qr.png"',"Cache-Control":"no-store"})

@app.get("/admin/connect/{slug}/download-material.pdf")
def xp_connect_download_material(slug: str, request: Request, db: Session = Depends(get_db)):
    import io, qrcode
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from fastapi.responses import Response
    control_superadmin(request, db)
    xp_connect_ensure(db)
    row=db.execute(xp_sql_text("SELECT name,slug FROM exponenta_connect_profiles WHERE slug=:slug"), {"slug":slug}).mappings().first()
    if not row: raise HTTPException(404)
    payload=str(request.base_url).rstrip("/") + "/connect/" + slug
    qr=qrcode.QRCode(box_size=12,border=4,error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(payload)
    qr.make(fit=True)
    img=io.BytesIO()
    qr.make_image(fill_color="black",back_color="white").save(img,format="PNG")
    img.seek(0)
    buf=io.BytesIO()
    c=canvas.Canvas(buf,pagesize=(595,842))
    c.setFillColorRGB(.985,.975,.96)
    c.rect(0,0,595,842,fill=1,stroke=0)
    c.setFillColorRGB(.72,.52,.26)
    c.rect(0,825,595,17,fill=1,stroke=0)
    c.setFillColorRGB(.12,.11,.10)
    c.setFont("Helvetica-Bold",23)
    c.drawCentredString(297,747,str(row["name"])[:42])
    c.setFillColorRGB(.60,.40,.19)
    c.setFont("Helvetica-Bold",12)
    c.drawCentredString(297,696,"EXPONENTA CONNECT")
    c.setFillColorRGB(.10,.10,.10)
    c.setFont("Helvetica-Bold",25)
    c.drawCentredString(297,646,"Conectate con nosotros")
    c.setFont("Helvetica",12)
    c.drawCentredString(297,612,"Resenas  |  WhatsApp  |  Instagram  |  Ubicacion")
    c.drawImage(ImageReader(img),132,235,width=330,height=330)
    c.setFont("Helvetica",12)
    c.drawCentredString(297,202,"Acerca tu celular o escanea el QR")
    c.setFont("Helvetica",11)
    c.drawCentredString(297,95,"Powered by Exponenta")
    c.showPage()
    c.save()
    return Response(content=buf.getvalue(),media_type="application/pdf",headers={"Content-Disposition":f'attachment; filename="{slug}-exponenta-connect.pdf"',"Cache-Control":"no-store"})

'''
s=s.replace(anchor,routes+anchor,1)
p.write_text(s,encoding="utf-8")
print("Connect mobile download endpoints and buttons patched")
