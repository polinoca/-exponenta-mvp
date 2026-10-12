from pathlib import Path
p=Path("/app/app/templates/connect/profile.html")
s=p.read_text(encoding="utf-8")
s=s.replace('<title>{{ profile.name }} · Exponenta Connect</title>','''<title>{{ profile.name | replace('\\n', ' ') }}{% if profile.subtitle %} | {{ profile.subtitle | replace('\\n', ' ') }}{% endif %}</title>
  <meta name="description" content="{{ (profile.subtitle or profile.name) | replace('\\n', ' ') }} · Reseñas, redes sociales y contacto.">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{{ profile.name | replace('\\n', ' ') }}">
  <meta property="og:title" content="{{ profile.name | replace('\\n', ' ') }}">
  <meta property="og:description" content="{{ (profile.subtitle or 'Conéctate con nosotros. Todo lo que necesitas, en un solo lugar.') | replace('\\n', ' ') }}">
  <meta property="og:url" content="{{ request.url.scheme }}://{{ request.url.netloc }}/connect/{{ profile.slug }}">
  <meta property="og:image" content="{{ request.url.scheme }}://{{ request.url.netloc }}/connect/{{ profile.slug }}/compartir.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{ profile.name | replace('\\n', ' ') }}">
  <meta name="twitter:description" content="{{ (profile.subtitle or 'Conéctate con nosotros.') | replace('\\n', ' ') }}">
  <meta name="twitter:image" content="{{ request.url.scheme }}://{{ request.url.netloc }}/connect/{{ profile.slug }}/compartir.jpg">''')
p.write_text(s,encoding="utf-8")

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
anchor='@app.get("/connect/{slug}/go/{kind}")'
assert anchor in s
route=r'''
@app.get("/connect/{slug}/compartir.jpg")
def xp_connect_share_image(slug: str, db: Session = Depends(get_db)):
    import io, base64, re
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    from fastapi.responses import Response
    profile=xp_connect_profile(db,slug)
    if not profile: raise HTTPException(404)
    w,h=1200,630
    img=Image.new("RGB",(w,h),"#FFFFFF")
    draw=ImageDraw.Draw(img)
    brand=str(profile.get("brand_color") or "#A88448")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}",brand): brand="#A88448"
    draw.rounded_rectangle((24,24,1176,606),radius=32,outline=brand,width=5)
    draw.rounded_rectangle((40,40,1160,590),radius=24,outline="#F0F0F0",width=2)
    draw.ellipse((100,115,460,475),fill="white",outline=brand,width=9)
    logo=str(profile.get("logo_data") or "")
    if ";base64," in logo and logo.startswith("data:image/"):
        try:
            raw=base64.b64decode(logo.split(";base64,",1)[1])
            source=Image.open(io.BytesIO(raw)).convert("RGBA")
            source.thumbnail((305,305),Image.Resampling.LANCZOS)
            img.paste(source,(280-source.width//2,295-source.height//2),source)
        except Exception: pass
    def font(size,bold=False):
        paths=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
               "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
        for path in paths:
            try: return ImageFont.truetype(path,size)
            except OSError: pass
        return ImageFont.load_default()
    def wrap(text,max_width,ft):
        result=[]
        for explicit in str(text).splitlines():
            words=explicit.split()
            line=""
            for word in words:
                trial=(line+" "+word).strip()
                if line and draw.textbbox((0,0),trial,font=ft)[2]>max_width:
                    result.append(line);line=word
                else: line=trial
            if line: result.append(line)
        return result
    name=str(profile["name"]).strip()
    subtitle=str(profile.get("subtitle") or "").strip()
    f=font(48,True)
    lines=wrap(name,620,f)
    while len(lines)>3 and f.size>28:
        f=font(f.size-2,True);lines=wrap(name,620,f)
    y=190
    for line in lines[:3]:
        draw.text((505,y),line,fill="#1B1B1B",font=f)
        y+=f.size+12
    if subtitle:
        sf=font(27)
        for line in wrap(subtitle,620,sf)[:3]:
            draw.text((505,y+8),line,fill=brand,font=sf)
            y+=36
    draw.text((505,490),"Conéctate con nosotros",fill="#333333",font=font(25))
    buf=io.BytesIO()
    img.save(buf,format="JPEG",quality=91,optimize=True)
    return Response(content=buf.getvalue(),media_type="image/jpeg",headers={"Cache-Control":"public, max-age=300"})
'''
s=s.replace(anchor,route+"\n"+anchor,1)
p.write_text(s,encoding="utf-8")
print("Connect business branded WhatsApp share preview installed")
