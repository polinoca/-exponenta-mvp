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
        # Avoid emoji boxes in Helvetica, keep supported Spanish characters.
        text="".join(ch for ch in str(text) if ch.isprintable() and ch.encode("cp1252",errors="ignore") and ord(ch) not in (0x25a0,0x25a1)).strip()
        while fontsize>7 and c.stringWidth(text,font,fontsize)>maxwidth: fontsize-=.5
        c.setFont(font,fontsize)
        c.drawCentredString(w/2,y,text)
    def lines(text,y,maxlines,fontsize,leading,bold=False):
        for ln in str(text or "").splitlines()[:maxlines]:
            txt(ln,y,w*.86,fontsize,bold)
            y-=leading
        return y
    c.setFillColorRGB(1,1,1);c.rect(0,0,w,h,fill=1,stroke=0)
    # Optional single inset brand-color frame, clear of content.
    if decor:
        inset=w*.027
        c.setStrokeColor(color);c.setLineWidth(max(.65,w*.0022))
        c.roundRect(inset,inset,w-2*inset,h-2*inset,min(w*.035,11),fill=0,stroke=1)
    # Circular logo centered, brand-colored outline, image fully contained.
    logo_y=h*.835
    radius=min(w*.145,h*.105)
    # Circular border is drawn on top of the logo.

    logo=row.get("logo_data") or ""
    if logo.startswith("data:image/") and ";base64," in logo:
        try:
            from PIL import Image
            raw=base64.b64decode(logo.split(";base64,",1)[1])
            im=Image.open(io.BytesIO(raw)).convert("RGBA")
            # Keep original uploaded logo unaltered: no crop or circular clipping.
            im.thumbnail((1200,1200),Image.Resampling.LANCZOS)
            available=radius*1.72
            iw,ih=im.size
            scale=min(available/max(iw,1),available/max(ih,1))
            dw,dh=iw*scale,ih*scale
            imbuf=io.BytesIO();im.save(imbuf,format="PNG");imbuf.seek(0)
            c.drawImage(ImageReader(imbuf),w/2-dw/2,logo_y-dh/2,dw,dh,mask="auto")
        except Exception: pass
    c.setStrokeColor(color);c.setLineWidth(1.7)
    c.circle(w/2,logo_y,radius,fill=0,stroke=1)
    c.setFillColorRGB(.12,.12,.12)
    name_lines=str(row["name"]).splitlines()
    if len(name_lines)==1 and " Salón de " in name_lines[0]:
        name_lines=name_lines[0].replace(" Salón de ","\nSalón de ",1).splitlines()
    name_y=h*.692
    for ix,line in enumerate(name_lines[:3]):
        txt(line,name_y-ix*h*.037,w*.86,min(15,w*.047) if ix==0 else min(12,w*.040),ix==0)
    sub_y=name_y-len(name_lines[:3])*h*.037-h*.01
    c.setFillColor(color)
    lines(row.get("subtitle"),sub_y,2,min(9.5,w*.028),h*.025)
    c.setFillColorRGB(.09,.09,.09)
    txt("Conéctate con nosotros",h*.55,w*.90,min(21,w*.069),True)
    c.setFillColor(color)
    txt("Todo lo que necesitas, en un solo lugar.",h*.508,w*.88,min(10,w*.031))
    # QR is generated from actual permanent Connect URL, never an illustrative image.
    payload=str(request.base_url).rstrip("/")+"/connect/"+slug
    qr=qrcode.QRCode(box_size=12,border=4,error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(payload);qr.make(fit=True)
    img=io.BytesIO();qr.make_image(fill_color="black",back_color="white").save(img,format="PNG");img.seek(0)
    qrsize=min(w*.53,h*.265)
    qx=(w-qrsize)/2;qy=h*.215
    c.setStrokeColor(color);c.setLineWidth(1.35)
    c.roundRect(qx-1.5,qy-1.5,qrsize+3,qrsize+3,5,fill=0,stroke=1)
    c.drawImage(ImageReader(img),qx,qy,qrsize,qrsize)
    c.setFillColor(color)
    txt("ESCANEA EL QR",h*.162,w*.75,min(11,w*.037),True)
    # Branded official service favicons, fetched as images with resilient fallback.
    services=[
        ("Google",row.get("google_url"),"google.com","G","#4285F4"),
        ("WhatsApp",row.get("whatsapp"),"whatsapp.com","W","#25D366"),
        ("Instagram",row.get("instagram_url"),"instagram.com","I","#C13584"),
        ("Facebook",row.get("facebook_url"),"facebook.com","f","#1877F2"),
        ("TikTok",row.get("tiktok_url"),"tiktok.com","T","#111111"),
        ("Ubicacion",row.get("maps_url"),"maps.google.com","M","#D64937")
    ]
    enabled=[item for item in services if item[1]]
    if enabled:
        import urllib.request
        from PIL import Image
        n=len(enabled)
        diameter=min(w*.09,w*.82/max(n,1))
        gap=min(w*.16,(w*.88-diameter*n)/max(n-1,1)) if n>1 else 0
        width=n*diameter+(n-1)*gap
        left=(w-width)/2
        icon_y=h*.079
        for idx,(label,url,domain,letter,hexcolor) in enumerate(enabled):
            x=left+idx*(diameter+gap)
            c.setFillColorRGB(1,1,1)
            c.setStrokeColor(color);c.setLineWidth(.7)
            c.circle(x+diameter/2,icon_y+diameter/2,diameter/2,stroke=1,fill=1)
            drawn=False
            try:
                favicon="https://www.google.com/s2/favicons?domain="+domain+"&sz=128"
                req=urllib.request.Request(favicon,headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req,timeout=1.5) as resp: raw=resp.read(120000)
                if label=="WhatsApp" and raw.lstrip().startswith(b"<"):
                    import cairosvg
                    raw=cairosvg.svg2png(bytestring=raw,output_width=128,output_height=128)
                im=Image.open(io.BytesIO(raw)).convert("RGBA")
                if im.width>=24 and im.height>=24:
                    from PIL import ImageDraw, ImageChops
                    im=im.resize((256,256),Image.Resampling.LANCZOS)
                    clip=Image.new("L",(256,256),0)
                    ImageDraw.Draw(clip).ellipse((0,0,255,255),fill=255)
                    im.putalpha(ImageChops.multiply(im.getchannel("A"),clip))
                    b=io.BytesIO();im.save(b,format="PNG");b.seek(0)
                    pad=diameter*.16
                    c.drawImage(ImageReader(b),x+pad,icon_y+pad,diameter-2*pad,diameter-2*pad,mask="auto")
                    drawn=True
            except Exception: pass
            if not drawn and label=="WhatsApp":
                # Retry official WhatsApp artwork, never draw an imitation.
                try:
                    req=urllib.request.Request("https://cdn.simpleicons.org/whatsapp/25D366",headers={"User-Agent":"Mozilla/5.0"})
                    with urllib.request.urlopen(req,timeout=2) as resp: raw=resp.read(120000)
                    import cairosvg
                    icon=cairosvg.svg2png(bytestring=raw,output_width=256,output_height=256)
                    c.drawImage(ImageReader(io.BytesIO(icon)),x+diameter*.16,icon_y+diameter*.16,diameter*.68,diameter*.68,mask="auto")
                    drawn=True
                except Exception: pass
            if not drawn and label!="WhatsApp":
                c.setFillColor(HexColor(hexcolor))
                c.setFont("Helvetica-Bold",diameter*.47)
                c.drawCentredString(x+diameter/2,icon_y+diameter*.31,letter)
            c.setFillColorRGB(.19,.19,.19)
            font_size=min(7,w*.019)
            while font_size>4 and c.stringWidth(label,"Helvetica",font_size)>diameter+gap*.6:font_size-=.25
            c.setFont("Helvetica",font_size)
            c.drawCentredString(x+diameter/2,icon_y-diameter*.25,label)
    c.setFillColorRGB(.64,.64,.64)
    txt("Powered by Exponenta",h*.043,w*.75,min(5.8,w*.017))
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
      <label class="xp-frame-switch" for="xp-decor"><span class="xp-frame-label"><strong>Marco de marca</strong><small>Mostrar en el PDF</small></span><input id="xp-decor" type="checkbox" checked onchange="xpMaterialDecor()"><span class="xp-frame-track" aria-hidden="true"></span></label>
      <button class="btn btn-secondary" type="button" onclick="downloadQR()">Descargar QR PNG</button>
      <button class="btn btn-primary" type="button" onclick="xpMaterialPDF('a6')">PDF A6</button>
      <button class="btn btn-primary" type="button" onclick="xpMaterialPDF('carta')">PDF carta</button>
    </div>
  </div>
'''+s[b:]
a=s.index('    <div class="xp-material-banner"')
b=s.index('    <aside class="no-print">',a)
s=s[:a]+'''    <div class="xp-material-banner xp-material-new" style="--xp-brand:{{ profile.brand_color or '#6b3b22' }}">
      <header style="display:flex;flex-direction:column;gap:10px;margin:8px 0 0">
        <div class="xp-material-roundlogo">{% if profile.logo_data %}<img src="{{ profile.logo_data }}" alt="{{ profile.name }}">{% else %}{{ profile.name[:1] }}{% endif %}</div>
        <strong style="white-space:pre-line;line-height:1.15;font-size:1rem">{{ profile.name }}</strong>
        {% if profile.subtitle %}<small style="white-space:pre-line;color:var(--xp-brand)">{{ profile.subtitle }}</small>{% endif %}
      </header>
      <div class="xp-material-copy" style="margin:12px 0 10px">
        <h1>Conéctate con nosotros</h1>
        <p>Todo lo que necesitas, en un solo lugar.</p>
      </div>
      <div id="connect-qr" class="xp-material-qr" style="border:0;padding:4px"></div>
      <p style="font-weight:800;color:var(--xp-brand);margin:6px 0">ESCANEA EL QR</p>
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
.xp-material-new .xp-material-roundlogo{width:112px;height:112px;border:2px solid var(--xp-brand);outline:none;border-radius:50%;display:grid;place-items:center;background:white;padding:10px}
.xp-material-new .xp-material-roundlogo img{width:100%;height:100%;object-fit:contain;mix-blend-mode:multiply}
.xp-material-new{position:relative}
.xp-material-new.decorated:after{content:"";position:absolute;pointer-events:none;inset:2.7%;border:1.2px solid var(--xp-brand);border-radius:12px}
.xp-frame-switch{display:flex;align-items:center;gap:12px;padding:9px 12px;border:1px solid #e5e7eb;border-radius:12px;background:#fff;cursor:pointer;min-height:48px}
.xp-frame-label{display:flex;flex-direction:column;gap:2px;color:#202124;line-height:1.2}
.xp-frame-label strong{font-size:13px;font-weight:650}
.xp-frame-label small{font-size:11px;color:#737981}
.xp-frame-switch input{position:absolute;opacity:0;width:1px;height:1px}
.xp-frame-track{width:38px;height:22px;border-radius:99px;background:#d2d6db;position:relative;flex:none;transition:background .2s}
.xp-frame-track:after{content:"";position:absolute;top:3px;left:3px;width:16px;height:16px;border-radius:50%;background:white;box-shadow:0 1px 3px #0002;transition:transform .2s}
.xp-frame-switch input:checked+.xp-frame-track{background:#1f2937}
.xp-frame-switch input:checked+.xp-frame-track:after{transform:translateX(16px)}
.xp-frame-switch:focus-within{outline:2px solid #64748b;outline-offset:2px}
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
