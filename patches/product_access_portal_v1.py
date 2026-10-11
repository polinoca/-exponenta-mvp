from pathlib import Path
p=Path("/app/app/templates/landing.html")
s=p.read_text(encoding="utf-8")
if "EXPONENTA PRODUCT ACCESS PORTAL" not in s:
    s=s.replace('href="/login">Ingresar</a>', 'href="/accesos">Ingresar</a>')
    s=s.replace('href="/panel">Abrir panel</a>', 'href="/accesos">Mis accesos</a>')
    anchor='{% block body %}'
    assert anchor in s
    s=s.replace(anchor,anchor+'\n<!-- EXPONENTA PRODUCT ACCESS PORTAL -->',1)
    p.write_text(s,encoding="utf-8")
m=Path("/app/app/main.py")
s=m.read_text(encoding="utf-8")
if "# EXPONENTA PRODUCT ACCESS PORTAL V1" not in s:
    block=r"""
# EXPONENTA PRODUCT ACCESS PORTAL V1
@app.get("/accesos",response_class=HTMLResponse)
def xp_product_access_portal():
    cards=[
      ("Wallet","Programa de lealtad","Visitas, puntos y recompensas.","/login?next=%2Fpanel"),
      ("Connect","Tu negocio en un enlace","QR, NFC, contacto y redes sociales.","/login?next=%2Fnegocio%2Fconnect"),
      ("Satisfacción del cliente","Encuestas y resultados","Opiniones, indicadores y promociones.","/encuestas/acceso")
    ]
    body=''.join('<a class="xp-unit" href="'+link+'"><span>'+name+'</span><strong>'+title+'</strong><small>'+detail+'</small><b>Ingresar →</b></a>' for name,title,detail,link in cards)
    return HTMLResponse('''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ingresar · Exponenta</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f5f8fb;color:#17283c;font-family:system-ui,-apple-system,sans-serif}
    main{max-width:1050px;margin:0 auto;padding:30px 20px 80px}header{padding:20px;border-bottom:1px solid #e3eaf1;background:#fff}
    header a{text-decoration:none;color:#17324d;font-weight:900;font-size:20px}h1{font-size:clamp(32px,6vw,52px);margin:48px 0 12px;letter-spacing:-.04em}
    p{color:#607386;line-height:1.6}.xp-units{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:28px}
    .xp-unit{display:flex;flex-direction:column;gap:14px;text-decoration:none;color:inherit;background:white;border:1px solid #dce6ef;border-radius:20px;padding:28px;min-height:260px;box-shadow:0 10px 35px #132c4410}
    .xp-unit:hover,.xp-unit:focus-visible{border-color:#407bb4;outline:2px solid #b5d6f5}.xp-unit span{font-size:13px;color:#427bb0;font-weight:800;text-transform:uppercase;letter-spacing:.05em}
    .xp-unit strong{font-size:25px}.xp-unit small{font-size:15px;color:#5b7184;line-height:1.5}.xp-unit b{margin-top:auto;color:#2d71b1}
    @media(max-width:750px){.xp-units{grid-template-columns:1fr}.xp-unit{min-height:190px;padding:23px}h1{margin-top:30px}}
    </style></head><body><header><a href="/">EXPONENTA</a></header><main><h1>¿A qué servicio deseas ingresar?</h1><p>Selecciona el servicio que utiliza tu negocio. Inicia sesión con tu cuenta de Exponenta.</p><section class="xp-units">'''+body+'''</section></main></body></html>''')
"""
    s += "\n"+block
    m.write_text(s,encoding="utf-8")
print("Product selection portal added")
