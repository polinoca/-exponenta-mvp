from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
anchor='@app.get("/admin/connect/{slug}/download-material.pdf")'
if anchor not in s: raise SystemExit("PDF route missing")
# Override old route by replacing its handler name (keep old route? remove decorator to prevent conflict).
start=s.index(anchor)
end=s.find('\n@app.',start+len(anchor))
if end<0: raise SystemExit("Cannot locate end of PDF route")
s=s[:start]+s[end:]
code=r'''
@app.get("/admin/connect/{slug}/download-material.pdf")
def xp_connect_material_pdf_v2(slug: str, request: Request, size: str = "a6", decor: int = 1, db: Session = Depends(get_db)):
    import io, re, base64, qrcode, math
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.colors import HexColor, Color
    from fastapi.responses import Response
    control_superadmin(request, db)
    xp_connect_ensure(db)
    row=db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug"),{"slug":slug}).mappings().first()
    if not row: raise HTTPException(404)
    size=size.lower()
    if size not in ("a6","carta"): raise HTTPException(400,detail="Tamano no valido")
    mm=72/25.4
    w,h=((105*mm,148*mm) if size=="a6" else (612,792))
    buf=io.BytesIO()
    c=canvas.Canvas(buf,pagesize=(w,h),pageCompression=1)
    c.setTitle("Material imprimible - "+str(row["name"]).replace("\n"," "))
    brand=str(row.get("brand_color") or "#b18a46")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}",brand): brand="#b18a46"
    color=HexColor(brand)
    def txt(text,y,maxwidth,fontsize,bold=False):
        font="Helvetica-Bold" if bold else "Helvetica"
        text=str(text).strip()
        while fontsize>7 and c.stringWidth(text,font,fontsize)>maxwidth: fontsize-=.5
        c.setFont(font,fontsize)
        c.drawCentredString(w/2,y,text)
    def lines(text,y,maxlines,fontsize,leading,bold=False):
        for ln in str(text or "").splitlines()[:maxlines]:
            txt(ln,y,w*.86,fontsize,bold)
            y-=leading
        return y
    c.setFillColorRGB(1,1,1);c.rect(0,0,w,h,fill=1,stroke=0)
    if decor:
        c.setStrokeColor(color);c.setLineWidth(max(1,w*.004))
        c.arc(-w*.16,h*.78,w*.22,h*1.05,0,110)
        c.arc(w*.82,-h*.08,w*1.15,h*.21,90,110)
    # Circular logo centered, brand-colored outline, image fully contained.
    logo_y=h*.835
    radius=min(w*.105,h*.08)
    c.setStrokeColor(color);c.setLineWidth(1.7)
    c.circle(w/2,logo_y,radius,fill=0,stroke=1)
    c.setLineWidth(.5);c.circle(w/2,logo_y,radius+4,fill=0,stroke=1)
    logo=row.get("logo_data") or ""
    if logo.startswith("data:image/") and ";base64," in logo:
        try:
            from PIL import Image
            raw=base64.b64decode(logo.split(";base64,",1)[1])
            im=Image.open(io.BytesIO(raw)).convert("RGBA")
            im.thumbnail((600,600))
            imbuf=io.BytesIO();im.save(imbuf,format="PNG");imbuf.seek(0)
            side=radius*1.52
            c.drawImage(ImageReader(imbuf),w/2-side/2,logo_y-side/2,side,side,mask="auto",preserveAspectRatio=True,anchor="c")
        except Exception: pass
    c.setFillColorRGB(.12,.12,.12)
    name_lines=str(row["name"]).splitlines()
    if len(name_lines)==1 and " Salón de " in name_lines[0]:
        name_lines=name_lines[0].replace(" Salón de ","\nSalón de ",1).splitlines()
    name_y=h*.705
    for ix,line in enumerate(name_lines[:3]):
        txt(line,name_y-ix*h*.037,w*.86,min(19,w*.056) if ix==0 else min(15,w*.047),ix==0)
    sub_y=name_y-len(name_lines[:3])*h*.037-h*.01
    c.setFillColor(color)
    lines(row.get("subtitle"),sub_y,2,min(9.5,w*.028),h*.025)
    c.setFillColorRGB(.09,.09,.09)
    txt("Conectate con nosotros",h*.53,w*.90,min(23,w*.075),True)
    c.setFillColor(color)
    txt("TODO EN UN SOLO LUGAR",h*.493,w*.86,min(10,w*.031),True)
    # QR is generated from actual permanent Connect URL, never an illustrative image.
    payload=str(request.base_url).rstrip("/")+"/connect/"+slug
    qr=qrcode.QRCode(box_size=12,border=4,error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(payload);qr.make(fit=True)
    img=io.BytesIO();qr.make_image(fill_color="black",back_color="white").save(img,format="PNG");img.seek(0)
    qrsize=min(w*.57,h*.315)
    qx=(w-qrsize)/2;qy=h*.145
    c.setStrokeColor(color);c.setLineWidth(2.2)
    c.roundRect(qx-6,qy-6,qrsize+12,qrsize+12,8,fill=0,stroke=1)
    c.drawImage(ImageReader(img),qx,qy,qrsize,qrsize)
    c.setFillColor(color)
    txt("ESCANEA EL QR",qy-h*.043,w*.75,min(14,w*.045),True)
    # Show only enabled services.
    services=[("Resenas",row.get("google_url")),("WhatsApp",row.get("whatsapp")),("Instagram",row.get("instagram_url")),("Facebook",row.get("facebook_url")),("TikTok",row.get("tiktok_url")),("Ubicacion",row.get("maps_url")),("Web",row.get("website_url"))]
    enabled=[label for label,url in services if url]
    if enabled:
        c.setFillColorRGB(.3,.3,.3)
        line="  ·  ".join(enabled[:5])
        txt(line,h*.065,w*.88,min(9,w*.026))
    c.setFillColorRGB(.45,.45,.45)
    txt("Powered by Exponenta",h*.027,w*.75,min(8,w*.024))
    c.showPage();c.save()
    filename=f"{slug}-{size}-{'decorado' if decor else 'blanco'}.pdf"
    return Response(content=buf.getvalue(),media_type="application/pdf",headers={"Content-Disposition":f'attachment; filename="{filename}"',"Cache-Control":"no-store"})
'''
# avoid double escaping source newline string in generated code
s=s.replace('@app.get("/admin/connect/{slug}/material", response_class=HTMLResponse)',code+'\n@app.get("/admin/connect/{slug}/material", response_class=HTMLResponse)',1)
p.write_text(s,encoding="utf-8")
t=Path("/app/app/templates/admin/connect_material.html")
s=t.read_text(encoding="utf-8")
a=s.index('  <div class="xp-material-toolbar')
b=s.index('  <section class="xp-material-sheet">',a)
s=s[:a]+'''  <div class="xp-material-toolbar no-print">
    <a href="/admin/connect">← Connect</a>
    <div style="display:flex;flex-wrap:wrap;align-items:center;gap:10px">
      <label style="display:flex;align-items:center;gap:6px"><input id="xp-decor" type="checkbox" checked onchange="xpMaterialDecor()"> Detalles de fondo</label>
      <button class="btn btn-secondary" type="button" onclick="downloadQR()">Descargar QR PNG</button>
      <button class="btn btn-primary" type="button" onclick="xpMaterialPDF('a6')">PDF A6</button>
      <button class="btn btn-primary" type="button" onclick="xpMaterialPDF('carta')">PDF carta</button>
    </div>
  </div>
'''+s[b:]
a=s.index('    <div class="xp-material-banner"')
b=s.index('    <aside class="no-print">',a)
s=s[:a]+'''    <div class="xp-material-banner xp-material-new" style="--xp-brand:{{ profile.brand_color or '#6b3b22' }}">
      <header style="display:flex;flex-direction:column;gap:10px;margin:18px 0 0">
        <div class="xp-material-roundlogo">{% if profile.logo_data %}<img src="{{ profile.logo_data }}" alt="{{ profile.name }}">{% else %}{{ profile.name[:1] }}{% endif %}</div>
        <strong style="white-space:pre-line;line-height:1.15;font-size:1.2rem">{{ profile.name }}</strong>
        {% if profile.subtitle %}<small style="white-space:pre-line;color:var(--xp-brand)">{{ profile.subtitle }}</small>{% endif %}
      </header>
      <div class="xp-material-copy" style="margin:22px 0 12px">
        <h1>Conéctate con nosotros</h1>
        <p>Todo en un solo lugar</p>
      </div>
      <div id="connect-qr" class="xp-material-qr" style="border:3px solid var(--xp-brand);padding:10px"></div>
      <p style="font-weight:800;color:var(--xp-brand);margin:12px 0">ESCANEA EL QR</p>
      <div class="xp-material-services" style="font-size:.72rem;line-height:1.6">
        {% if profile.google_url %}<span>Reseñas · </span>{% endif %}
        {% if profile.whatsapp %}<span>WhatsApp · </span>{% endif %}
        {% if profile.instagram_url %}<span>Instagram · </span>{% endif %}
        {% if profile.facebook_url %}<span>Facebook · </span>{% endif %}
        {% if profile.tiktok_url %}<span>TikTok · </span>{% endif %}
        {% if profile.maps_url %}<span>Ubicación</span>{% endif %}
      </div>
      <footer>Powered by <b>Exponenta</b></footer>
    </div>
'''+s[b:]
s=s.replace('</main>','''<style>
.xp-material-new:before{display:none}
.xp-material-new .xp-material-roundlogo{width:80px;height:80px;border:2px solid var(--xp-brand);outline:3px solid color-mix(in srgb,var(--xp-brand) 18%,transparent);outline-offset:3px;border-radius:50%;display:grid;place-items:center;background:white;padding:10px}
.xp-material-new .xp-material-roundlogo img{width:100%;height:100%;object-fit:contain}
.xp-material-new.decorated:after{content:"";position:absolute;pointer-events:none;inset:15px;border:1px solid color-mix(in srgb,var(--xp-brand) 22%,transparent);border-radius:18px}
</style>
</main>''',1)
s=s.replace('function saveMaterialPDF(){','''function xpMaterialDecor(){
 document.querySelector(".xp-material-new").classList.toggle("decorated",document.getElementById("xp-decor").checked);
}
function xpMaterialPDF(size){
 const decor=document.getElementById("xp-decor").checked?"1":"0";
 window.location.href="/admin/connect/{{ profile.slug }}/download-material.pdf?size="+size+"&decor="+decor;
}
xpMaterialDecor();
function saveMaterialPDF(){''')
t.write_text(s,encoding="utf-8")
print("Connect A6/Carta brand PDF generator and decor toggle ready")
