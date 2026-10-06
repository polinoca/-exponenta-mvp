from pathlib import Path

main = Path("/app/app/main.py")
s = main.read_text(encoding="utf-8")
marker = "# XP EXPONENTA CONNECT V1"

if marker not in s:
    anchor = '@app.get("/negocio/lealtad", response_class=HTMLResponse)'
    if anchor not in s:
        anchor = "@app."
    if anchor not in s:
        raise SystemExit("FastAPI route anchor not found")

    routes = r'''
# XP EXPONENTA CONNECT V1
import base64 as xp_base64
import re as xp_re
from sqlalchemy import text as xp_sql_text

def xp_connect_ensure(db):
    db.execute(xp_sql_text("""
        CREATE TABLE IF NOT EXISTS exponenta_connect_profiles (
            slug VARCHAR(80) PRIMARY KEY,
            name TEXT NOT NULL,
            subtitle TEXT,
            brand_color VARCHAR(16),
            logo_data TEXT,
            google_url TEXT,
            whatsapp TEXT,
            instagram_url TEXT,
            maps_url TEXT,
            phone TEXT,
            booking_url TEXT,
            website_url TEXT,
            menu_url TEXT,
            facebook_url TEXT,
            contact_email TEXT,
            address TEXT,
            active INTEGER NOT NULL DEFAULT 1
        )
    """))
    db.execute(xp_sql_text("""
        CREATE TABLE IF NOT EXISTS exponenta_connect_clicks (
            slug VARCHAR(80) NOT NULL,
            kind VARCHAR(40) NOT NULL,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    db.commit()

def xp_connect_slug(value: str) -> str:
    value = (value or "").strip().lower()
    value = xp_re.sub(r"[^a-z0-9-]+", "-", value)
    value = xp_re.sub(r"-+", "-", value).strip("-")
    return value[:80]

def xp_connect_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value

def xp_connect_instagram(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith("@"):
        return "https://instagram.com/" + value[1:]
    if "/" not in value and "." not in value:
        return "https://instagram.com/" + value
    return xp_connect_url(value)

def xp_connect_whatsapp(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) == 10:
        digits = "52" + digits
    return "https://wa.me/" + digits if digits else ""

def xp_connect_profile(db, slug: str):
    xp_connect_ensure(db)
    return db.execute(
        xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug AND active=1"),
        {"slug": slug},
    ).mappings().first()

@app.get("/connect/{slug}", response_class=HTMLResponse)
def exponenta_connect_public(slug: str, request: Request, db: Session = Depends(get_db)):
    profile = xp_connect_profile(db, slug)
    if not profile:
        raise HTTPException(404, "Perfil Connect no encontrado")
    return render(request, "connect/profile.html", {"profile": profile})

@app.get("/connect/{slug}/go/{kind}")
def exponenta_connect_go(slug: str, kind: str, db: Session = Depends(get_db)):
    profile = xp_connect_profile(db, slug)
    if not profile:
        raise HTTPException(404, "Perfil Connect no encontrado")
    field_map = {
        "google": "google_url",
        "whatsapp": "whatsapp",
        "instagram": "instagram_url",
        "maps": "maps_url",
        "call": "phone",
        "booking": "booking_url",
        "website": "website_url",
        "menu": "menu_url",
        "facebook": "facebook_url",
    }
    field = field_map.get(kind)
    if not field:
        raise HTTPException(404)
    target = (profile.get(field) or "").strip()
    if kind == "call" and target:
        target = "tel:" + "".join(ch for ch in target if ch.isdigit() or ch == "+")
    if not target:
        raise HTTPException(404, "Acción no configurada")
    db.execute(xp_sql_text("INSERT INTO exponenta_connect_clicks(slug,kind) VALUES (:slug,:kind)"), {"slug": slug, "kind": kind})
    db.commit()
    return RedirectResponse(target, status_code=302)

@app.get("/connect/{slug}/contact.vcf")
def exponenta_connect_vcard(slug: str, db: Session = Depends(get_db)):
    profile = xp_connect_profile(db, slug)
    if not profile:
        raise HTTPException(404)
    phone = (profile.get("phone") or "").strip()
    wa = (profile.get("whatsapp") or "").strip()
    email = (profile.get("contact_email") or "").strip()
    website = (profile.get("website_url") or "").strip()
    address = (profile.get("address") or "").strip()
    lines = ["BEGIN:VCARD","VERSION:3.0",f"FN:{profile['name']}"]
    if phone: lines.append(f"TEL;TYPE=CELL:{phone}")
    if email: lines.append(f"EMAIL:{email}")
    if website: lines.append(f"URL:{website}")
    if address: lines.append(f"ADR:;;{address};;;;")
    if wa: lines.append(f"NOTE:WhatsApp: {wa}")
    lines.append("END:VCARD")
    db.execute(xp_sql_text("INSERT INTO exponenta_connect_clicks(slug,kind) VALUES (:slug,'contact')"), {"slug": slug})
    db.commit()
    return Response("\r\n".join(lines), media_type="text/vcard", headers={"Content-Disposition": f'attachment; filename="{slug}.vcf"'})

@app.get("/admin/connect", response_class=HTMLResponse)
def exponenta_connect_admin(request: Request, db: Session = Depends(get_db)):
    user = control_superadmin(request, db)
    xp_connect_ensure(db)
    profiles = db.execute(xp_sql_text("""
        SELECT p.*,
               COALESCE((SELECT COUNT(*) FROM exponenta_connect_clicks c WHERE c.slug=p.slug),0) AS clicks
        FROM exponenta_connect_profiles p ORDER BY p.name
    """)).mappings().all()
    return render(request, "admin/connect.html", {"user": user, "profiles": profiles})

@app.get("/admin/connect/nuevo", response_class=HTMLResponse)
def exponenta_connect_new(request: Request, db: Session = Depends(get_db)):
    user = control_superadmin(request, db)
    return render(request, "admin/connect_edit.html", {"user": user, "profile": None})

@app.get("/admin/connect/{slug}/editar", response_class=HTMLResponse)
def exponenta_connect_edit(slug: str, request: Request, db: Session = Depends(get_db)):
    user = control_superadmin(request, db)
    xp_connect_ensure(db)
    profile = db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug"), {"slug": slug}).mappings().first()
    if not profile:
        raise HTTPException(404)
    return render(request, "admin/connect_edit.html", {"user": user, "profile": profile})

@app.post("/admin/connect/guardar")
async def exponenta_connect_save(
    request: Request,
    original_slug: str = Form(""),
    slug: str = Form(""),
    name: str = Form(...),
    subtitle: str = Form(""),
    brand_color: str = Form("#6b3b22"),
    google_url: str = Form(""),
    whatsapp: str = Form(""),
    instagram_url: str = Form(""),
    maps_url: str = Form(""),
    phone: str = Form(""),
    booking_url: str = Form(""),
    website_url: str = Form(""),
    menu_url: str = Form(""),
    facebook_url: str = Form(""),
    contact_email: str = Form(""),
    address: str = Form(""),
    active: str = Form("1"),
    logo_file: UploadFile|None = File(None),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    control_superadmin(request, db)
    verify_csrf(request, csrf_token)
    xp_connect_ensure(db)
    slug = xp_connect_slug(slug or name)
    if not slug:
        raise HTTPException(422, "Slug inválido")
    if len(brand_color) != 7 or not brand_color.startswith("#"):
        brand_color = "#6b3b22"
    logo_data = None
    if original_slug:
        old = db.execute(xp_sql_text("SELECT logo_data FROM exponenta_connect_profiles WHERE slug=:slug"), {"slug": original_slug}).mappings().first()
        if old:
            logo_data = old.get("logo_data")
    if logo_file and logo_file.filename:
        data = await logo_file.read()
        if len(data) > 2*1024*1024:
            raise HTTPException(422, "Logo máximo 2 MB")
        mime = logo_file.content_type or "image/png"
        if mime not in {"image/png","image/jpeg","image/webp"}:
            raise HTTPException(422, "Logo debe ser PNG, JPG o WebP")
        logo_data = "data:" + mime + ";base64," + xp_base64.b64encode(data).decode("ascii")
    values = {
        "slug": slug, "name": name.strip(), "subtitle": subtitle.strip(),
        "brand_color": brand_color, "logo_data": logo_data,
        "google_url": xp_connect_url(google_url), "whatsapp": xp_connect_whatsapp(whatsapp),
        "instagram_url": xp_connect_instagram(instagram_url), "maps_url": xp_connect_url(maps_url),
        "phone": phone.strip(), "booking_url": xp_connect_url(booking_url),
        "website_url": xp_connect_url(website_url), "menu_url": xp_connect_url(menu_url),
        "facebook_url": xp_connect_url(facebook_url), "contact_email": contact_email.strip(),
        "address": address.strip(), "active": 1 if active=="1" else 0,
    }
    if original_slug and original_slug != slug:
        db.execute(xp_sql_text("DELETE FROM exponenta_connect_profiles WHERE slug=:slug"), {"slug": original_slug})
    db.execute(xp_sql_text("""
        INSERT INTO exponenta_connect_profiles
        (slug,name,subtitle,brand_color,logo_data,google_url,whatsapp,instagram_url,maps_url,phone,booking_url,website_url,menu_url,facebook_url,contact_email,address,active)
        VALUES (:slug,:name,:subtitle,:brand_color,:logo_data,:google_url,:whatsapp,:instagram_url,:maps_url,:phone,:booking_url,:website_url,:menu_url,:facebook_url,:contact_email,:address,:active)
        ON CONFLICT (slug) DO UPDATE SET
        name=EXCLUDED.name, subtitle=EXCLUDED.subtitle, brand_color=EXCLUDED.brand_color, logo_data=COALESCE(EXCLUDED.logo_data, exponenta_connect_profiles.logo_data),
        google_url=EXCLUDED.google_url, whatsapp=EXCLUDED.whatsapp, instagram_url=EXCLUDED.instagram_url, maps_url=EXCLUDED.maps_url,
        phone=EXCLUDED.phone, booking_url=EXCLUDED.booking_url, website_url=EXCLUDED.website_url, menu_url=EXCLUDED.menu_url,
        facebook_url=EXCLUDED.facebook_url, contact_email=EXCLUDED.contact_email, address=EXCLUDED.address, active=EXCLUDED.active
    """), values)
    db.commit()
    return RedirectResponse("/admin/connect", status_code=303)

'''
    s = s.replace(anchor, routes + anchor, 1)
    main.write_text(s, encoding="utf-8")

tpldir = Path("/app/app/templates/connect")
tpldir.mkdir(parents=True, exist_ok=True)
(tpldir / "profile.html").write_text(r'''{% extends "base.html" %}
{% block title %}{{ profile.name }} · Exponenta Connect{% endblock %}
{% block body %}
<main class="xp-connect-public" style="--xp-brand:{{ profile.brand_color or '#6b3b22' }}">
  <section class="xp-connect-card">
    <div class="xp-connect-brand">
      <div class="xp-connect-logo">{% if profile.logo_data %}<img src="{{ profile.logo_data }}" alt="{{ profile.name }}">{% else %}<b>{{ profile.name[:1] }}</b>{% endif %}</div>
      <div><span>EXPONENTA CONNECT</span><h1>{{ profile.name }}</h1>{% if profile.subtitle %}<p>{{ profile.subtitle }}</p>{% endif %}</div>
    </div>
    <div class="xp-connect-actions">
      {% if profile.google_url %}<a class="primary" href="/connect/{{ profile.slug }}/go/google">★ <span><b>Dejar una reseña en Google</b><small>Tu opinión nos ayuda a crecer</small></span><i>›</i></a>{% endif %}
      {% if profile.whatsapp %}<a href="/connect/{{ profile.slug }}/go/whatsapp">💬 <span><b>WhatsApp</b><small>Escríbenos directamente</small></span><i>›</i></a>{% endif %}
      {% if profile.instagram_url %}<a href="/connect/{{ profile.slug }}/go/instagram">◎ <span><b>Instagram</b><small>Síguenos y conoce más</small></span><i>›</i></a>{% endif %}
      {% if profile.booking_url %}<a href="/connect/{{ profile.slug }}/go/booking">◷ <span><b>Agendar cita</b><small>Reserva en línea</small></span><i>›</i></a>{% endif %}
      {% if profile.maps_url %}<a href="/connect/{{ profile.slug }}/go/maps">⌖ <span><b>Cómo llegar</b><small>Abrir ubicación</small></span><i>›</i></a>{% endif %}
      {% if profile.phone %}<a href="/connect/{{ profile.slug }}/go/call">☎ <span><b>Llamar</b><small>Contacto directo</small></span><i>›</i></a>{% endif %}
      {% if profile.menu_url %}<a href="/connect/{{ profile.slug }}/go/menu">☰ <span><b>Menú / servicios</b><small>Ver información</small></span><i>›</i></a>{% endif %}
      {% if profile.website_url %}<a href="/connect/{{ profile.slug }}/go/website">↗ <span><b>Sitio web</b><small>Visitar página</small></span><i>›</i></a>{% endif %}
      {% if profile.facebook_url %}<a href="/connect/{{ profile.slug }}/go/facebook">f <span><b>Facebook</b><small>Visitar perfil</small></span><i>›</i></a>{% endif %}
      <a href="/connect/{{ profile.slug }}/contact.vcf">＋ <span><b>Guardar contacto</b><small>Agrega el negocio a tu celular</small></span><i>›</i></a>
    </div>
    <footer>Conectado por <b>Exponenta</b></footer>
  </section>
</main>
{% endblock %}''', encoding="utf-8")

adm = Path("/app/app/templates/admin")
(adm / "connect.html").write_text(r'''{% extends "base.html" %}
{% block title %}Exponenta Connect{% endblock %}
{% block body %}
<main class="container xp-connect-admin">
  <div class="xp-connect-admin-head"><div><span class="eyebrow">EXPONENTA CONNECT</span><h1>Perfiles Connect</h1><p>Configura un negocio en minutos y después apunta su QR/NFC a su perfil.</p></div><a class="btn btn-primary" href="/admin/connect/nuevo">+ Nuevo Connect</a></div>
  <div class="xp-connect-table">
    {% for p in profiles %}
    <article><div>{% if p.logo_data %}<img src="{{ p.logo_data }}" alt="">{% else %}<b>{{ p.name[:1] }}</b>{% endif %}</div><section><strong>{{ p.name }}</strong><small>/connect/{{ p.slug }} · {{ p.clicks }} clics</small></section><a href="/connect/{{ p.slug }}" target="_blank">Abrir</a><a href="/admin/connect/{{ p.slug }}/editar">Editar</a></article>
    {% else %}<p>Aún no hay perfiles Connect.</p>{% endfor %}
  </div>
</main>
{% endblock %}''', encoding="utf-8")

(adm / "connect_edit.html").write_text(r'''{% extends "base.html" %}
{% block title %}Configurar Connect{% endblock %}
{% block body %}
<main class="container xp-connect-editor">
  <a href="/admin/connect">← Connect</a><span class="eyebrow">CONFIGURACIÓN RÁPIDA</span><h1>{% if profile %}Editar{% else %}Nuevo{% endif %} Exponenta Connect</h1>
  <form method="post" action="/admin/connect/guardar" enctype="multipart/form-data">
    <input type="hidden" name="csrf_token" value="{{ csrf }}"><input type="hidden" name="original_slug" value="{{ profile.slug if profile else '' }}">
    <div class="xp-connect-grid">
      <label>Nombre<input required name="name" value="{{ profile.name if profile else '' }}"></label>
      <label>Slug<input name="slug" placeholder="nombre-negocio" value="{{ profile.slug if profile else '' }}"></label>
      <label class="wide">Descripción corta<input name="subtitle" placeholder="Ej. Podología profesional" value="{{ profile.subtitle if profile else '' }}"></label>
      <label>Color<input type="color" name="brand_color" value="{{ profile.brand_color if profile and profile.brand_color else '#6b3b22' }}"></label>
      <label>Logo<input type="file" name="logo_file" accept="image/png,image/jpeg,image/webp"></label>
      <label class="wide">Google reseña<input name="google_url" placeholder="https://..." value="{{ profile.google_url if profile else '' }}"></label>
      <label>WhatsApp<input name="whatsapp" placeholder="3312345678" value="{{ profile.whatsapp if profile else '' }}"></label>
      <label>Instagram<input name="instagram_url" placeholder="@usuario" value="{{ profile.instagram_url if profile else '' }}"></label>
      <label>Maps<input name="maps_url" placeholder="https://maps..." value="{{ profile.maps_url if profile else '' }}"></label>
      <label>Teléfono<input name="phone" value="{{ profile.phone if profile else '' }}"></label>
      <label>Agenda<input name="booking_url" placeholder="https://..." value="{{ profile.booking_url if profile else '' }}"></label>
      <label>Sitio web<input name="website_url" placeholder="https://..." value="{{ profile.website_url if profile else '' }}"></label>
      <label>Menú/servicios<input name="menu_url" placeholder="https://..." value="{{ profile.menu_url if profile else '' }}"></label>
      <label>Facebook<input name="facebook_url" placeholder="https://..." value="{{ profile.facebook_url if profile else '' }}"></label>
      <label>Correo<input name="contact_email" value="{{ profile.contact_email if profile else '' }}"></label>
      <label class="wide">Dirección<input name="address" value="{{ profile.address if profile else '' }}"></label>
      <label>Estado<select name="active"><option value="1" {% if not profile or profile.active %}selected{% endif %}>Activo</option><option value="0" {% if profile and not profile.active %}selected{% endif %}>Pausado</option></select></label>
    </div>
    <button class="btn btn-primary" type="submit">Guardar y publicar</button>
  </form>
</main>
{% endblock %}''', encoding="utf-8")

cssp = Path("/app/app/static/app.css")
css = cssp.read_text(encoding="utf-8")
if "/* XP EXPONENTA CONNECT V1 */" not in css:
    css += r'''
/* XP EXPONENTA CONNECT V1 */
.xp-connect-public{min-height:100vh;background:linear-gradient(160deg,#f5f1ed,#fff);padding:28px 16px 48px;color:#211d1a}.xp-connect-card{max-width:560px;margin:0 auto}.xp-connect-brand{display:flex;align-items:center;gap:16px;padding:20px 8px 18px}.xp-connect-logo{width:74px;height:74px;border-radius:22px;background:#fff;box-shadow:0 8px 24px rgba(0,0,0,.1);overflow:hidden;display:grid;place-items:center;color:var(--xp-brand)}.xp-connect-logo img{width:100%;height:100%;object-fit:contain}.xp-connect-logo b{font-size:2rem}.xp-connect-brand span{font-size:.58rem;letter-spacing:.16em;font-weight:900;color:var(--xp-brand)}.xp-connect-brand h1{margin:4px 0 2px;font-size:2rem;line-height:1}.xp-connect-brand p{margin:0;color:#71665e;font-size:.82rem}.xp-connect-actions{display:grid;gap:10px}.xp-connect-actions a{display:grid;grid-template-columns:34px 1fr auto;align-items:center;gap:12px;min-height:76px;padding:12px 16px;border:1px solid #e4ddd7;border-radius:19px;background:#fff;color:#201c19!important;text-decoration:none!important;box-shadow:0 8px 22px rgba(47,33,22,.05);font-size:1.05rem}.xp-connect-actions a.primary{background:var(--xp-brand);color:#fff!important;border-color:transparent}.xp-connect-actions a span{display:grid}.xp-connect-actions a b{font-size:.95rem}.xp-connect-actions a small{font-size:.67rem;opacity:.68;margin-top:2px}.xp-connect-actions a i{font-style:normal;font-size:1.6rem;opacity:.45}.xp-connect-card footer{text-align:center;padding:24px 0 0;color:#8a817a;font-size:.68rem}.xp-connect-admin-head{display:flex;justify-content:space-between;gap:18px;align-items:end;margin:28px 0}.xp-connect-table{display:grid;gap:9px}.xp-connect-table article{display:grid;grid-template-columns:46px 1fr auto auto;gap:12px;align-items:center;padding:12px;border:1px solid #e7ded6;border-radius:15px;background:#fff}.xp-connect-table article>div{width:46px;height:46px;border-radius:12px;background:#f4ede8;display:grid;place-items:center;overflow:hidden}.xp-connect-table img{width:100%;height:100%;object-fit:contain}.xp-connect-table section{display:grid}.xp-connect-table small{color:#7a7068}.xp-connect-table a{font-weight:800;font-size:.72rem}.xp-connect-editor{max-width:900px!important;padding-top:28px}.xp-connect-editor form{margin-top:18px}.xp-connect-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px}.xp-connect-grid label{display:grid;gap:5px;font-size:.72rem;font-weight:800}.xp-connect-grid .wide{grid-column:1/-1}.xp-connect-grid input,.xp-connect-grid select{min-height:44px;padding:9px 11px;border:1px solid #d8cec6;border-radius:11px;background:#fff}@media(max-width:640px){.xp-connect-grid{grid-template-columns:1fr}.xp-connect-grid .wide{grid-column:auto}.xp-connect-admin-head{align-items:flex-start;flex-direction:column}.xp-connect-table article{grid-template-columns:44px 1fr}.xp-connect-table article>a{grid-column:auto}.xp-connect-brand h1{font-size:1.7rem}}
'''
    cssp.write_text(css, encoding="utf-8")

print("Exponenta Connect V1 installed")

# EXPONENTA CONNECT PRINT MATERIAL V1
from pathlib import Path as _XpPath
_p = _XpPath("/app/app/main.py")
_s = _p.read_text(encoding="utf-8")
_anchor = '@app.get("/admin/connect/{slug}/editar", response_class=HTMLResponse)'
if "def exponenta_connect_material" not in _s:
    _block = r'''
@app.get("/admin/connect/{slug}/material", response_class=HTMLResponse)
def exponenta_connect_material(slug: str, request: Request, db: Session = Depends(get_db)):
    user = control_superadmin(request, db)
    xp_connect_ensure(db)
    profile = db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug"), {"slug": slug}).mappings().first()
    if not profile:
        raise HTTPException(404)
    return render(request, "admin/connect_material.html", {"user": user, "profile": profile})
'''
    _s = _s.replace(_anchor, _block + "\\n" + _anchor, 1)
    _p.write_text(_s, encoding="utf-8")

_t = _XpPath("/app/app/templates/admin/connect.html")
if _t.exists():
    _x = _t.read_text(encoding="utf-8")
    old = '<a href="/connect/{{ p.slug }}" target="_blank">Abrir</a><a href="/admin/connect/{{ p.slug }}/editar">Editar</a>'
    new = '<a href="/connect/{{ p.slug }}" target="_blank">Abrir</a><a href="/admin/connect/{{ p.slug }}/material">QR / banner</a><a href="/admin/connect/{{ p.slug }}/editar">Editar</a>'
    if old in _x:
        _x = _x.replace(old,new)
        _t.write_text(_x,encoding="utf-8")

_XpPath("/app/app/templates/admin/connect_material.html").write_text(r'''{% extends "base.html" %}
{% block title %}Material · {{ profile.name }}{% endblock %}
{% block body %}
<main class="container xp-connect-material-page">
  <div class="xp-material-toolbar no-print">
    <a href="/admin/connect">← Connect</a>
    <div><button class="btn btn-secondary" type="button" onclick="downloadQR()">Descargar QR PNG</button><button class="btn btn-primary" type="button" onclick="window.print()">Imprimir / Guardar PDF</button></div>
  </div>
  <section class="xp-material-sheet">
    <div class="xp-material-banner" style="--xp-brand:{{ profile.brand_color or '#6b3b22' }}">
      <header>
        {% if profile.logo_data %}<img src="{{ profile.logo_data }}" alt="{{ profile.name }}">{% else %}<div class="xp-material-logo">{{ profile.name[:1] }}</div>{% endif %}
        <strong>{{ profile.name }}</strong>
      </header>
      <div class="xp-material-copy">
        <span>EXPONENTA CONNECT</span>
        <h1>Conéctate con nosotros</h1>
        <p>Reseñas · WhatsApp · Instagram · Ubicación</p>
      </div>
      <div id="connect-qr" class="xp-material-qr"></div>
      <div class="xp-material-tap"><b>⌁ NFC</b><span>Acerca tu celular o escanea el QR</span></div>
      <footer>Powered by <b>Exponenta</b></footer>
    </div>
    <aside class="no-print">
      <span class="eyebrow">QR NUEVO</span>
      <h2>{{ profile.name }}</h2>
      <p>Destino permanente:</p>
      <code id="connect-url"></code>
      <p>Este es el QR que debe imprimirse en el nuevo banner. El contenido del perfil puede cambiar después sin volver a imprimirlo.</p>
    </aside>
  </section>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<script>
const target=location.origin+"/connect/{{ profile.slug }}";
document.getElementById("connect-url").textContent=target;
new QRCode(document.getElementById("connect-qr"),{text:target,width:360,height:360,correctLevel:QRCode.CorrectLevel.H});
function downloadQR(){
  const box=document.getElementById("connect-qr");
  const canvas=box.querySelector("canvas");
  const img=box.querySelector("img");
  const url=canvas?canvas.toDataURL("image/png"):img.src;
  const a=document.createElement("a");a.href=url;a.download="{{ profile.slug }}-exponenta-connect-qr.png";a.click();
}
</script>
{% endblock %}''',encoding="utf-8")

_cssp=_XpPath("/app/app/static/app.css")
_css=_cssp.read_text(encoding="utf-8")
if "/* XP CONNECT PRINT MATERIAL V1 */" not in _css:
    _css += r'''
/* XP CONNECT PRINT MATERIAL V1 */
.xp-material-toolbar{display:flex;justify-content:space-between;align-items:center;gap:14px;margin:24px 0}.xp-material-toolbar>div{display:flex;gap:8px}.xp-material-sheet{display:grid;grid-template-columns:minmax(320px,430px) 1fr;gap:28px;align-items:start}.xp-material-sheet aside{padding:24px;border:1px solid #e3d8cf;border-radius:20px;background:#fff}.xp-material-sheet code{display:block;overflow-wrap:anywhere;padding:10px;background:#f5f1ed;border-radius:10px}.xp-material-banner{aspect-ratio:105/148;background:#fff;border:1px solid #e4ddd6;border-radius:18px;padding:26px 24px;display:flex;flex-direction:column;align-items:center;text-align:center;box-shadow:0 18px 45px rgba(45,31,20,.1);position:relative;overflow:hidden}.xp-material-banner:before{content:"";position:absolute;inset:0 0 auto;height:12px;background:var(--xp-brand)}.xp-material-banner header{width:100%;display:flex;align-items:center;justify-content:center;gap:10px;margin-top:6px}.xp-material-banner header img,.xp-material-logo{width:54px;height:54px;border-radius:15px;object-fit:contain;background:#fff;border:1px solid #eee;display:grid;place-items:center;font-weight:900}.xp-material-banner header strong{font-size:1.05rem}.xp-material-copy{margin:22px 0 14px}.xp-material-copy span{font-size:.54rem;letter-spacing:.17em;font-weight:900;color:var(--xp-brand)}.xp-material-copy h1{font-size:1.7rem!important;line-height:1.02;margin:7px 0!important}.xp-material-copy p{font-size:.72rem;color:#6f655e;margin:0}.xp-material-qr{background:#fff;padding:10px;border-radius:14px;border:1px solid #eee}.xp-material-qr img,.xp-material-qr canvas{display:block!important;width:210px!important;height:210px!important}.xp-material-tap{display:grid;gap:2px;margin-top:12px}.xp-material-tap b{font-size:.78rem;color:var(--xp-brand)}.xp-material-tap span{font-size:.62rem;color:#796e67}.xp-material-banner footer{margin-top:auto;font-size:.58rem;color:#847a73}@media(max-width:760px){.xp-material-sheet{grid-template-columns:1fr}.xp-material-toolbar{align-items:flex-start;flex-direction:column}.xp-material-banner{max-width:430px;margin:auto}}@media print{body{background:#fff!important}.no-print,.xp-app-topbar,.xp-business-nav{display:none!important}.xp-connect-material-page{padding:0!important;margin:0!important;max-width:none!important}.xp-material-sheet{display:block}.xp-material-banner{width:105mm;height:148mm;box-sizing:border-box;border:0;border-radius:0;box-shadow:none;margin:0;page-break-after:avoid}.xp-material-qr img,.xp-material-qr canvas{width:52mm!important;height:52mm!important}}
'''
    _cssp.write_text(_css,encoding="utf-8")

print("Exponenta Connect print material installed")
