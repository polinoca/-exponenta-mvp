from pathlib import Path
p=Path("/app/app/templates/connect/profile.html")
s=p.read_text(encoding="utf-8")
s=s.replace('<title>{{ profile.name }} · Exponenta Connect</title>','''<title>{{ profile.name | replace('\\n', ' ') }}</title>
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


    draw.ellipse((322,22,878,578),fill="white",outline=brand,width=7)
    logo=str(profile.get("logo_data") or "")
    if ";base64," in logo and logo.startswith("data:image/"):
        try:
            raw=base64.b64decode(logo.split(";base64,",1)[1])
            source=Image.open(io.BytesIO(raw)).convert("RGBA")
            source.thumbnail((490,490),Image.Resampling.LANCZOS)
            img.paste(source,(600-source.width//2,300-source.height//2),source)
        except Exception: pass
    buf=io.BytesIO()
    img.save(buf,format="JPEG",quality=91,optimize=True)
    return Response(content=buf.getvalue(),media_type="image/jpeg",headers={"Cache-Control":"public, max-age=300"})
'''
s=s.replace(anchor,route+"\n"+anchor,1)
p.write_text(s,encoding="utf-8")
print("Connect business branded WhatsApp share preview installed")
