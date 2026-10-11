from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
marker="# XP SURVEY SOCIAL SHARE V20"
if marker not in s:
    helper=r'''
# XP SURVEY SOCIAL SHARE V20
def xp_survey_share_html(html,request,business,slug):
    root=str(request.base_url).rstrip("/")
    link=root+"/encuesta/"+slug
    preview=link+"/compartir.jpg"
    title="Encuesta de satisfacción | "+str(business["name"])
    summary="Tu opinión nos ayuda a mejorar. Cuéntanos cómo fue tu experiencia en "+str(business["name"])+"."
    def meta(key,value,prop=True):
        attr="property" if prop else "name"
        return '<meta '+attr+'="'+xp_html.escape(key,quote=True)+'" content="'+xp_html.escape(value,quote=True)+'">'
    block=(meta("og:type","website")+meta("og:locale","es_MX")+
        meta("og:site_name",str(business["name"]))+
        meta("og:title",title)+meta("og:description",summary)+
        meta("og:url",link)+meta("og:image",preview)+
        meta("og:image:secure_url",preview)+meta("og:image:type","image/jpeg")+
        meta("og:image:width","1200")+meta("og:image:height","630")+
        meta("og:image:alt","Logotipo de "+str(business["name"]))+
        meta("twitter:card","summary_large_image",False)+
        meta("twitter:title",title,False)+meta("twitter:description",summary,False)+
        meta("twitter:image",preview,False)+meta("description",summary,False)+
        '<link rel="canonical" href="'+xp_html.escape(link,quote=True)+'">')
    return html.replace("</head>",block+"</head>",1)

@app.get("/encuesta/{slug}/compartir.jpg")
def xp_survey_share_photo(slug:str,db:Session=Depends(get_db)):
    from fastapi.responses import Response
    from PIL import Image,ImageDraw,ImageFont
    import base64
    xp_survey_extended(db)
    brand=xp_survey_lookup(db,slug)
    if not brand or not brand["enabled"]:raise HTTPException(404)
    im=Image.new("RGB",(1200,630),"#F2F8FC")
    draw=ImageDraw.Draw(im)
    draw.rounded_rectangle((50,40,1150,590),radius=42,fill="#FFFFFF")
    draw.ellipse((460,75,740,355),fill="#FFFFFF",outline="#DCECF5",width=3)
    logo=brand["logo_data"]
    if logo and logo.startswith("data:image/") and "," in logo:
        try:
            raw=base64.b64decode(logo.split(",",1)[1],validate=True)
            src=Image.open(xp_survey_io.BytesIO(raw)).convert("RGBA")
            src.thumbnail((250,235))
            x=(1200-src.width)//2;y=95+(240-src.height)//2
            im.paste(src,(x,y),src)
        except Exception:pass
    try:
        bold=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",42)
        normal=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",29)
    except Exception:
        bold=ImageFont.load_default();normal=bold
    name=str(brand["name"])[:40]
    draw.text((600,397),name,font=bold,fill="#2D71B1",anchor="mm")
    draw.text((600,467),"Tu opinión nos ayuda a mejorar",font=normal,fill="#17324D",anchor="mm")
    draw.rounded_rectangle((435,510,765,558),radius=24,fill="#4BB8DE")
    draw.text((600,534),"Responder encuesta",font=normal,fill="#FFFFFF",anchor="mm")
    out=xp_survey_io.BytesIO();im.save(out,format="JPEG",quality=86,optimize=True)
    return Response(out.getvalue(),media_type="image/jpeg",headers={"Cache-Control":"public, max-age=3600"})
'''
    anchor='def xp_survey_public('
    assert anchor in s
    s=s.replace(anchor,helper+"\n"+anchor,1)
    a=s.index("def xp_survey_public(");b=s.index("\n@app.",a);sec=s[a:b]
    original="response=HTMLResponse(xp_survey_page('Tu opinión',content))"
    assert original in sec
    sec=sec.replace(original,"response=HTMLResponse(xp_survey_share_html(xp_survey_page('Tu opinión',content),request,p,slug))",1)
    original2='response=HTMLResponse(page)'
    if original2 in sec:sec=sec.replace(original2,'response=HTMLResponse(xp_survey_share_html(page,request,p,slug))',1)
    s=s[:a]+sec+s[b:]
    p.write_text(marker+"\n"+s,encoding="utf-8")
print("WhatsApp Open Graph, Twitter cards and branded preview photo installed")
