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


    # Composite a truly circular logo thumbnail, then draw the ring last.
    # This prevents opaque white corners in uploaded logos from hiding the ring.
    from PIL import ImageChops
    center_x,center_y=600,300
    radius=270
    logo=str(profile.get("logo_data") or "")
    if ";base64," in logo and logo.startswith("data:image/"):
        try:
            raw=base64.b64decode(logo.split(";base64,",1)[1])
            source=Image.open(io.BytesIO(raw)).convert("RGBA")
            # Fit the full artwork with a 24px breathing margin.
            max_side=2*(radius-24)
            source.thumbnail((max_side,max_side),Image.Resampling.LANCZOS)
            layer=Image.new("RGBA",(2*radius,2*radius),(255,255,255,0))
            layer.alpha_composite(source,((2*radius-source.width)//2,(2*radius-source.height)//2))
            mask=Image.new("L",layer.size,0)
            ImageDraw.Draw(mask).ellipse((10,10,2*radius-11,2*radius-11),fill=255)
            layer.putalpha(ImageChops.multiply(layer.getchannel("A"),mask))
            img.paste(layer,(center_x-radius,center_y-radius),layer)
        except Exception: pass
    # Ring on top, not behind the image: fully visible even for opaque logos.
    draw=ImageDraw.Draw(img)
    draw.ellipse((center_x-radius,center_y-radius,center_x+radius,center_y+radius),outline=brand,width=8)
    buf=io.BytesIO()
    img.save(buf,format="JPEG",quality=91,optimize=True)
    return Response(content=buf.getvalue(),media_type="image/jpeg",headers={"Cache-Control":"public, max-age=300"})
'''
s=s.replace(anchor,route+"\n"+anchor,1)
p.write_text(s,encoding="utf-8")
print("Connect business branded WhatsApp share preview installed")
