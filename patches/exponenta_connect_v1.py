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
    return render(request, "admin/connect_edit.html", {"user": user, "profile": None, "csrf": request.state.session["csrf"]})

@app.get("/admin/connect/{slug}/editar", response_class=HTMLResponse)
def exponenta_connect_edit(slug: str, request: Request, db: Session = Depends(get_db)):
    user = control_superadmin(request, db)
    xp_connect_ensure(db)
    profile = db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug"), {"slug": slug}).mappings().first()
    if not profile:
        raise HTTPException(404)
    return render(request, "admin/connect_edit.html", {"user": user, "profile": profile, "csrf": request.state.session["csrf"]})

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
        "brand_color": brand_color, "button_border_color": button_border_color, "logo_data": logo_data,
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
        (slug,name,subtitle,brand_color,button_border_color,logo_data,google_url,whatsapp,instagram_url,maps_url,phone,booking_url,website_url,menu_url,facebook_url,contact_email,address,active)
        VALUES (:slug,:name,:subtitle,:brand_color,:button_border_color,:logo_data,:google_url,:whatsapp,:instagram_url,:maps_url,:phone,:booking_url,:website_url,:menu_url,:facebook_url,:contact_email,:address,:active)
        ON CONFLICT (slug) DO UPDATE SET
        name=EXCLUDED.name, subtitle=EXCLUDED.subtitle, brand_color=EXCLUDED.brand_color, button_border_color=EXCLUDED.button_border_color, logo_data=COALESCE(EXCLUDED.logo_data, exponenta_connect_profiles.logo_data),
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
(tpldir / "profile.html").write_text(r'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="theme-color" content="{{ profile.brand_color or '#6b3b22' }}">
  <title>{{ profile.name }} · Exponenta Connect</title>
  <style>
    :root{
      --brand:{{ profile.brand_color or '#6b3b22' }};
      --border:{{ profile.button_border_color or '#e4ddd7' }};
      --bg:#f7f4f0;--card:#ffffff;--ink:#171513;--muted:#756d67;--soft:#eee7e1;
      --shadow:0 8px 24px rgba(34,24,17,.055);
    }
    *{box-sizing:border-box}html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text",Inter,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
    body{min-height:100dvh;-webkit-font-smoothing:antialiased}
    a{-webkit-tap-highlight-color:transparent}
    .xp-page{width:100%;max-width:620px;margin:0 auto;padding:max(24px,env(safe-area-inset-top)) 18px max(34px,env(safe-area-inset-bottom))}
    .xp-head{display:flex;align-items:center;gap:15px;padding:6px 4px 21px;position:relative}
    .xp-head:after{content:"";position:absolute;left:4px;right:4px;bottom:8px;height:3px;border-radius:999px;background:var(--brand);opacity:.9}
    .xp-logo{width:78px;height:78px;border-radius:23px;overflow:hidden;background:#fff;display:grid;place-items:center;box-shadow:var(--shadow);border:1px solid rgba(0,0,0,.05);flex:0 0 auto}
    .xp-logo img{width:100%;height:100%;object-fit:contain}.xp-logo b{font-size:2rem;color:var(--brand)}
    .xp-eyebrow{display:block;font-size:11px;line-height:1;letter-spacing:.17em;font-weight:850;color:var(--brand);margin-bottom:7px}
    .xp-head h1{font-size:34px;line-height:.98;letter-spacing:-.035em;margin:0 0 7px;font-weight:850}
    .xp-head p{font-size:16px;line-height:1.25;margin:0;color:var(--muted);font-weight:520}
    .xp-actions{display:grid;gap:12px;margin-top:10px}
    .xp-action{display:grid;grid-template-columns:48px minmax(0,1fr) 24px;align-items:center;gap:14px;min-height:88px;padding:15px 17px;background:var(--card);border:1.5px solid var(--border);border-radius:23px;text-decoration:none;color:var(--ink);box-shadow:var(--shadow);transition:transform .12s ease,box-shadow .12s ease}
    .xp-action:active{transform:scale(.986);box-shadow:0 3px 12px rgba(34,24,17,.05)}
    .xp-icon{width:46px;height:46px;border-radius:14px;background:#faf8f6;display:grid;place-items:center}
    .xp-icon svg,.xp-icon img{width:29px;height:29px;display:block}
    .xp-copy{min-width:0}.xp-copy b{display:block;font-size:18px;line-height:1.08;letter-spacing:-.012em}.xp-copy small{display:block;margin-top:5px;color:var(--muted);font-size:13.5px;line-height:1.2;font-weight:520}
    .xp-arrow{font-size:30px;line-height:1;color:#aaa19a;text-align:right}
    .xp-google{border:2px solid var(--brand);background:#fff;box-shadow:0 10px 28px rgba(34,24,17,.07)}
    .xp-google .xp-copy b{color:var(--brand)}
    .xp-stars{display:flex;gap:2px;margin-top:7px}
    .xp-stars svg{width:15px;height:15px;fill:#f4b400}
    .xp-whatsapp .xp-icon{background:#eefbf3}.xp-instagram .xp-icon{background:#fff5fb}
    .xp-save .xp-icon,.xp-map .xp-icon,.xp-call .xp-icon,.xp-web .xp-icon,.xp-booking .xp-icon,.xp-menu .xp-icon,.xp-facebook .xp-icon{color:var(--brand)}
    .xp-foot{text-align:center;padding:25px 6px 4px;color:#958c85;font-size:12px}.xp-foot b{color:#6f665f}
    @media(max-width:420px){
      .xp-page{padding-left:14px;padding-right:14px}.xp-logo{width:72px;height:72px}.xp-head{gap:13px}.xp-head h1{font-size:31px}.xp-action{min-height:84px;padding:14px 14px;border-radius:21px}.xp-icon{width:44px;height:44px}.xp-copy b{font-size:17px}.xp-copy small{font-size:13px}
    }
    @media(min-width:621px){body{padding:24px 0}.xp-page{border-radius:30px}}
  </style>
</head>
<body>
<main class="xp-page">
  <header class="xp-head">
    <div class="xp-logo">{% if profile.logo_data %}<img src="{{ profile.logo_data }}" alt="{{ profile.name }}">{% else %}<b>{{ profile.name[:1] }}</b>{% endif %}</div>
    <div>
      <span class="xp-eyebrow">EXPONENTA CONNECT</span>
      <h1>{{ profile.name }}</h1>
      {% if profile.subtitle %}<p>{{ profile.subtitle }}</p>{% endif %}
    </div>
  </header>

  <section class="xp-actions">
    {% if profile.google_url %}
    <a class="xp-action xp-google" href="/connect/{{ profile.slug }}/go/google" aria-label="Dejar una reseña en Google">
      <span class="xp-icon" aria-hidden="true">
        <svg viewBox="0 0 48 48">
          <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.2-.1-2.3-.4-3.5z"/>
          <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15 18.9 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4c-7.7 0-14.4 4.3-17.7 10.7z"/>
          <path fill="#4CAF50" d="M24 44c5.2 0 9.8-2 13.3-5.2l-6.2-5.2C29.1 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.2-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/>
          <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.3-2.3 4.2-4.2 5.6l6.2 5.2C36.9 39.2 44 34 44 24c0-1.2-.1-2.3-.4-3.5z"/>
        </svg>
      </span>
      <span class="xp-copy"><b>Dejar una reseña en Google</b><small>Tu opinión nos ayuda a crecer</small><span class="xp-stars" aria-label="5 estrellas">{% for _ in range(5) %}<svg viewBox="0 0 24 24"><path d="M12 2.8l2.8 5.7 6.3.9-4.6 4.5 1.1 6.3-5.6-3-5.6 3 1.1-6.3-4.6-4.5 6.3-.9z"/></svg>{% endfor %}</span></span><span class="xp-arrow">›</span>
    </a>
    {% endif %}

    {% if profile.whatsapp %}
    <a class="xp-action xp-whatsapp" href="/connect/{{ profile.slug }}/go/whatsapp">
      <span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="#25D366"/><path fill="#fff" d="M23.6 19.4c-.4-.2-2.2-1.1-2.6-1.2-.3-.1-.6-.2-.8.2-.2.4-.9 1.2-1.1 1.4-.2.3-.4.3-.8.1-2.2-1.1-3.7-2-5.2-4.5-.4-.7.4-.7 1.1-2.2.1-.3 0-.5-.1-.7-.1-.2-.8-2-1.1-2.8-.3-.7-.6-.6-.8-.6h-.7c-.2 0-.7.1-1 .5-.3.4-1.3 1.3-1.3 3.2s1.4 3.7 1.6 4c.2.3 2.7 4.1 6.5 5.7.9.4 1.6.6 2.2.8.9.3 1.8.2 2.4.1.7-.1 2.2-.9 2.5-1.8.3-.9.3-1.7.2-1.8-.2-.1-.5-.2-.9-.4z"/><path fill="#fff" d="M26.8 5.2A15.2 15.2 0 003.1 23.5L1 31l7.7-2A15.3 15.3 0 1026.8 5.2zm-10.7 23a12.2 12.2 0 01-6.2-1.7l-.4-.2-4.6 1.2 1.2-4.5-.3-.5A12.3 12.3 0 1116.1 28.2z"/></svg></span>
      <span class="xp-copy"><b>WhatsApp</b><small>Escríbenos directamente</small></span><span class="xp-arrow">›</span>
    </a>
    {% endif %}

    {% if profile.instagram_url %}
    <a class="xp-action xp-instagram" href="/connect/{{ profile.slug }}/go/instagram">
      <span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 32 32"><defs><linearGradient id="ig" x1="0" y1="32" x2="32" y2="0"><stop stop-color="#feda75"/><stop offset=".28" stop-color="#fa7e1e"/><stop offset=".52" stop-color="#d62976"/><stop offset=".78" stop-color="#962fbf"/><stop offset="1" stop-color="#4f5bd5"/></linearGradient></defs><rect x="3" y="3" width="26" height="26" rx="8" fill="url(#ig)"/><circle cx="16" cy="16" r="6.3" fill="none" stroke="#fff" stroke-width="2.3"/><circle cx="23.2" cy="8.9" r="1.6" fill="#fff"/></svg></span>
      <span class="xp-copy"><b>Instagram</b><small>Síguenos y conoce más</small></span><span class="xp-arrow">›</span>
    </a>
    {% endif %}

    {% if profile.maps_url %}
    <a class="xp-action xp-map" href="/connect/{{ profile.slug }}/go/maps"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M12 21s6-5.2 6-11a6 6 0 10-12 0c0 5.8 6 11 6 11z"/><circle cx="12" cy="10" r="2.2"/></svg></span><span class="xp-copy"><b>Cómo llegar</b><small>Abrir ubicación</small></span><span class="xp-arrow">›</span></a>
    {% endif %}
    {% if profile.phone %}
    <a class="xp-action xp-call" href="/connect/{{ profile.slug }}/go/call"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M7 3h3l1.5 4-2 1.6a15 15 0 006 6l1.6-2L21 14v3c0 2-1.6 4-3.7 4C10 21 3 14 3 6.7 3 4.6 5 3 7 3z"/></svg></span><span class="xp-copy"><b>Llamar</b><small>Contacto directo</small></span><span class="xp-arrow">›</span></a>
    {% endif %}
    {% if profile.website_url %}
    <a class="xp-action xp-web" href="/connect/{{ profile.slug }}/go/website"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.4 2.5 3.6 5.5 3.6 9S14.4 18.5 12 21M12 3c-2.4 2.5-3.6 5.5-3.6 9s1.2 6.5 3.6 9"/></svg></span><span class="xp-copy"><b>Sitio web</b><small>Visitar página</small></span><span class="xp-arrow">›</span></a>
    {% endif %}
    {% if profile.booking_url %}
    <a class="xp-action xp-booking" href="/connect/{{ profile.slug }}/go/booking"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/><path d="M8 14h3v3H8z"/></svg></span><span class="xp-copy"><b>Agendar cita</b><small>Reserva en línea</small></span><span class="xp-arrow">›</span></a>
    {% endif %}
    {% if profile.menu_url %}
    <a class="xp-action xp-menu" href="/connect/{{ profile.slug }}/go/menu"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M8 6h13M8 12h13M8 18h13"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/></svg></span><span class="xp-copy"><b>Menú / servicios</b><small>Ver información</small></span><span class="xp-arrow">›</span></a>
    {% endif %}
    {% if profile.facebook_url %}
    <a class="xp-action xp-facebook" href="/connect/{{ profile.slug }}/go/facebook"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="#1877F2"/><path fill="#fff" d="M18.1 27V17.2h3.3l.5-3.8h-3.8V11c0-1.1.3-1.8 1.9-1.8h2V5.8c-.4-.1-1.6-.2-3-.2-3 0-5.1 1.9-5.1 5.3v2.5h-3.4v3.8h3.4V27z"/></svg></span><span class="xp-copy"><b>Facebook</b><small>Conoce más del negocio</small></span><span class="xp-arrow">›</span></a>
    {% endif %}
    <a class="xp-action xp-save" href="/connect/{{ profile.slug }}/contact.vcf"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="12" cy="8" r="3.5"/><path d="M5 21c0-4 3-7 7-7s7 3 7 7"/><path d="M19 4v5M16.5 6.5h5"/></svg></span><span class="xp-copy"><b>Guardar contacto</b><small>Agrega el negocio a tu celular</small></span><span class="xp-arrow">›</span></a>
  </section>
  <footer class="xp-foot">Conectado por <b>Exponenta</b></footer>
</main>
</body>
</html>''', encoding="utf-8")

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
      <label>Color de marca<input type="color" name="brand_color" value="{{ profile.brand_color if profile and profile.brand_color else '#6b3b22' }}"></label>\n      <label>Color del marco de botones<input type="color" name="button_border_color" value="{{ profile.button_border_color if profile and profile.button_border_color else '#e4ddd7' }}"></label>
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
.xp-connect-public{min-height:100vh;background:linear-gradient(160deg,#f5f1ed,#fff);padding:28px 16px 48px;color:#211d1a}.xp-connect-card{max-width:560px;margin:0 auto}.xp-connect-brand{display:flex;align-items:center;gap:16px;padding:20px 8px 18px}.xp-connect-logo{width:74px;height:74px;border-radius:22px;background:#fff;box-shadow:0 8px 24px rgba(0,0,0,.1);overflow:hidden;display:grid;place-items:center;color:var(--xp-brand)}.xp-connect-logo img{width:100%;height:100%;object-fit:contain}.xp-connect-logo b{font-size:2rem}.xp-connect-brand span{font-size:.58rem;letter-spacing:.16em;font-weight:900;color:var(--xp-brand)}.xp-connect-brand:after{content:"";display:block;position:absolute;left:8px;right:8px;bottom:0;height:3px;border-radius:999px;background:var(--xp-brand);opacity:.9}.xp-connect-brand{position:relative}.xp-connect-brand h1{margin:4px 0 2px;font-size:2rem;line-height:1}.xp-connect-brand p{margin:0;color:#71665e;font-size:.82rem}.xp-connect-actions{display:grid;gap:10px}.xp-connect-actions a{display:grid;grid-template-columns:34px 1fr auto;align-items:center;gap:12px;min-height:76px;padding:12px 16px;border:1px solid var(--xp-button-border);border-radius:19px;background:#fff;color:#201c19!important;text-decoration:none!important;box-shadow:0 8px 22px rgba(47,33,22,.05);font-size:1.05rem}.xp-connect-actions a.primary{background:#fff;color:#201c19!important;border:2px solid var(--xp-brand);box-shadow:0 10px 26px color-mix(in srgb,var(--xp-brand) 18%,transparent)}.xp-connect-actions a.primary b{color:var(--xp-brand)}.xp-connect-actions a.primary i{color:var(--xp-brand);opacity:.8}.xp-connect-actions a span{display:grid}.xp-connect-actions a b{font-size:.95rem}.xp-connect-actions a small{font-size:.67rem;opacity:.68;margin-top:2px}.xp-connect-actions a i{font-style:normal;font-size:1.6rem;opacity:.45}.xp-connect-card footer{text-align:center;padding:24px 0 0;color:#8a817a;font-size:.68rem}.xp-connect-admin-head{display:flex;justify-content:space-between;gap:18px;align-items:end;margin:28px 0}.xp-connect-table{display:grid;gap:9px}.xp-connect-table article{display:grid;grid-template-columns:46px 1fr auto auto;gap:12px;align-items:center;padding:12px;border:1px solid #e7ded6;border-radius:15px;background:#fff}.xp-connect-table article>div{width:46px;height:46px;border-radius:12px;background:#f4ede8;display:grid;place-items:center;overflow:hidden}.xp-connect-table img{width:100%;height:100%;object-fit:contain}.xp-connect-table section{display:grid}.xp-connect-table small{color:#7a7068}.xp-connect-table a{font-weight:800;font-size:.72rem}.xp-connect-editor{max-width:900px!important;padding-top:28px}.xp-connect-editor form{margin-top:18px}.xp-connect-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px}.xp-connect-grid label{display:grid;gap:5px;font-size:.72rem;font-weight:800}.xp-connect-grid .wide{grid-column:1/-1}.xp-connect-grid input,.xp-connect-grid select{min-height:44px;padding:9px 11px;border:1px solid #d8cec6;border-radius:11px;background:#fff}@media(max-width:640px){.xp-connect-grid{grid-template-columns:1fr}.xp-connect-grid .wide{grid-column:auto}.xp-connect-admin-head{align-items:flex-start;flex-direction:column}.xp-connect-table article{grid-template-columns:44px 1fr}.xp-connect-table article>a{grid-column:auto}.xp-connect-brand h1{font-size:1.7rem}}
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
    _s = _s.replace(_anchor, _block + "\n" + _anchor, 1)
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
.xp-material-toolbar{display:flex;justify-content:space-between;align-items:center;gap:14px;margin:24px 0}.xp-material-toolbar>div{display:flex;gap:8px}.xp-material-sheet{display:grid;grid-template-columns:minmax(320px,430px) 1fr;gap:28px;align-items:start}.xp-material-sheet aside{padding:24px;border:1px solid #e3d8cf;border-radius:20px;background:#fff}.xp-material-sheet code{display:block;overflow-wrap:anywhere;padding:10px;background:#f5f1ed;border-radius:10px}.xp-material-banner{aspect-ratio:105/148;background:#fff;border:1px solid #e4ddd6;border-radius:18px;padding:26px 24px;display:flex;flex-direction:column;align-items:center;text-align:center;box-shadow:0 18px 45px rgba(45,31,20,.1);position:relative;overflow:hidden}.xp-material-banner:before{content:"";position:absolute;inset:0 0 auto;height:12px;background:var(--xp-brand)}.xp-material-banner header{width:100%;display:flex;align-items:center;justify-content:center;gap:10px;margin-top:6px}.xp-material-banner header img,.xp-material-logo{width:54px;height:54px;border-radius:15px;object-fit:contain;background:#fff;border:1px solid #eee;display:grid;place-items:center;font-weight:900}.xp-material-banner header strong{font-size:1.05rem}.xp-material-copy{margin:22px 0 14px}.xp-material-copy span{font-size:.54rem;letter-spacing:.17em;font-weight:900;color:var(--xp-brand)}.xp-material-copy h1{font-size:1.7rem!important;line-height:1.02;margin:7px 0!important}.xp-material-copy p{font-size:.72rem;color:#6f655e;margin:0}.xp-material-qr{background:#fff;padding:10px;border-radius:14px;border:1px solid #eee}.xp-material-qr canvas{display:block!important;width:210px!important;height:210px!important}.xp-material-qr img{display:none!important}.xp-material-tap{display:grid;gap:2px;margin-top:12px}.xp-material-tap b{font-size:.78rem;color:var(--xp-brand)}.xp-material-tap span{font-size:.62rem;color:#796e67}.xp-material-banner footer{margin-top:auto;font-size:.58rem;color:#847a73}@media(max-width:760px){.xp-material-sheet{grid-template-columns:1fr}.xp-material-toolbar{align-items:flex-start;flex-direction:column}.xp-material-banner{max-width:430px;margin:auto}}@media print{body{background:#fff!important}.no-print,.xp-app-topbar,.xp-business-nav{display:none!important}.xp-connect-material-page{padding:0!important;margin:0!important;max-width:none!important}.xp-material-sheet{display:block}.xp-material-banner{width:105mm;height:148mm;box-sizing:border-box;border:0;border-radius:0;box-shadow:none;margin:0;page-break-after:avoid}.xp-material-qr canvas{width:52mm!important;height:52mm!important}.xp-material-qr img{display:none!important}}
'''
    _cssp.write_text(_css,encoding="utf-8")

print("Exponenta Connect print material installed")

# XP BUSINESS CONNECT ACCESS V1
from pathlib import Path as _XpPath2
_p=_XpPath2("/app/app/main.py")
_s=_p.read_text(encoding="utf-8")
_anchor='@app.get("/negocio/lealtad", response_class=HTMLResponse)'
if "def business_connect_page" not in _s:
    _block=r'''
def xp_connect_ensure_org_column(db):
    xp_connect_ensure(db)
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS organization_id INTEGER"))
    db.execute(xp_sql_text("CREATE INDEX IF NOT EXISTS idx_exponenta_connect_org ON exponenta_connect_profiles(organization_id)"))
    db.commit()

@app.get("/negocio/connect", response_class=HTMLResponse)
def business_connect_page(request: Request, db: Session = Depends(get_db)):
    current_user = require_user(request, db)
    if current_user.role == Role.SUPERADMIN:
        return RedirectResponse("/admin/connect", status_code=303)
    user, org = business_admin_context(request, db)
    xp_connect_ensure_org_column(db)
    profile = db.execute(
        xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE organization_id=:org_id ORDER BY slug LIMIT 1"),
        {"org_id": org.id},
    ).mappings().first()
    return render(request, "business/connect.html", {"user": user, "organization": org, "profile": profile, "csrf": request.state.session["csrf"]})

@app.post("/negocio/connect")
async def business_connect_save(
    request: Request,
    slug: str = Form(""),
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
    logo_file: UploadFile|None = File(None),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    user, org = business_admin_context(request, db)
    verify_csrf(request, csrf_token)
    xp_connect_ensure_org_column(db)
    existing = db.execute(
        xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE organization_id=:org_id ORDER BY slug LIMIT 1"),
        {"org_id": org.id},
    ).mappings().first()
    clean_slug = xp_connect_slug(slug or (existing["slug"] if existing else org.slug or org.name))
    if not clean_slug:
        raise HTTPException(422, "Slug inválido")
    if len(brand_color)!=7 or not brand_color.startswith("#"):
        brand_color = getattr(org,"brand_color",None) or "#6b3b22"
    logo_data = existing.get("logo_data") if existing else None
    if logo_file and logo_file.filename:
        data = await logo_file.read()
        if len(data) > 2*1024*1024:
            raise HTTPException(422, "Logo máximo 2 MB")
        mime = logo_file.content_type or "image/png"
        if mime not in {"image/png","image/jpeg","image/webp"}:
            raise HTTPException(422, "Logo debe ser PNG, JPG o WebP")
        logo_data = "data:" + mime + ";base64," + xp_base64.b64encode(data).decode("ascii")
    vals={
      "organization_id":org.id,"slug":clean_slug,"name":org.name,"subtitle":subtitle.strip(),
      "brand_color":brand_color,"button_border_color":button_border_color,"logo_data":logo_data,"google_url":xp_connect_url(google_url),
      "whatsapp":xp_connect_whatsapp(whatsapp),"instagram_url":xp_connect_instagram(instagram_url),
      "maps_url":xp_connect_url(maps_url),"phone":phone.strip(),"booking_url":xp_connect_url(booking_url),
      "website_url":xp_connect_url(website_url),"menu_url":xp_connect_url(menu_url),
      "facebook_url":xp_connect_url(facebook_url),"contact_email":contact_email.strip(),"address":address.strip()
    }
    if existing and existing["slug"] != clean_slug:
        db.execute(xp_sql_text("DELETE FROM exponenta_connect_profiles WHERE organization_id=:org_id"),{"org_id":org.id})
    db.execute(xp_sql_text("""
      INSERT INTO exponenta_connect_profiles
      (organization_id,slug,name,subtitle,brand_color,button_border_color,logo_data,google_url,whatsapp,instagram_url,maps_url,phone,booking_url,website_url,menu_url,facebook_url,contact_email,address,active)
      VALUES (:organization_id,:slug,:name,:subtitle,:brand_color,:button_border_color,:logo_data,:google_url,:whatsapp,:instagram_url,:maps_url,:phone,:booking_url,:website_url,:menu_url,:facebook_url,:contact_email,:address,1)
      ON CONFLICT (slug) DO UPDATE SET
      organization_id=EXCLUDED.organization_id,name=EXCLUDED.name,subtitle=EXCLUDED.subtitle,brand_color=EXCLUDED.brand_color,button_border_color=EXCLUDED.button_border_color,
      logo_data=COALESCE(EXCLUDED.logo_data,exponenta_connect_profiles.logo_data),google_url=EXCLUDED.google_url,
      whatsapp=EXCLUDED.whatsapp,instagram_url=EXCLUDED.instagram_url,maps_url=EXCLUDED.maps_url,phone=EXCLUDED.phone,
      booking_url=EXCLUDED.booking_url,website_url=EXCLUDED.website_url,menu_url=EXCLUDED.menu_url,facebook_url=EXCLUDED.facebook_url,
      contact_email=EXCLUDED.contact_email,address=EXCLUDED.address,active=1
    """),vals)
    db.commit()
    return RedirectResponse("/negocio/connect?message=Connect+actualizado", status_code=303)
'''
    _s=_s.replace(_anchor,_block+"\n"+_anchor,1)
    _p.write_text(_s,encoding="utf-8")

_bt=_XpPath2("/app/app/templates/business/connect.html")
_bt.write_text(r'''{% extends "base.html" %}
{% block title %}Connect · {{ organization.name }}{% endblock %}
{% block body %}
<main class="business-shell xp-connect-business">
  <nav class="xp-business-nav">
    <a href="/negocio">Inicio</a><a href="/negocio/operacion">Operación</a><a href="/negocio/lealtad">Clientes</a><a href="/negocio/marketing">Reseñas</a><a class="active" href="/negocio/connect">Connect</a><a href="/negocio/marca">Marca</a><a href="/negocio/configuracion">Más</a>
  </nav>
  <header class="xp-connect-biz-head"><span class="eyebrow">EXPONENTA CONNECT</span><h1>Tu negocio completo en un solo toque.</h1><p>Configura los accesos que verá tu cliente al escanear el QR o acercar el NFC.</p></header>
  {% if request.query_params.get("message") %}<div class="xp-brand-alert success">✓ Connect actualizado</div>{% endif %}
  <form method="post" enctype="multipart/form-data" class="xp-connect-biz-form">
    <input type="hidden" name="csrf_token" value="{{ csrf }}">
    <section>
      <h2>Identidad</h2>
      <label>URL corta<input name="slug" placeholder="{{ organization.slug }}" value="{{ profile.slug if profile else organization.slug }}"></label>
      <label>Descripción corta<input name="subtitle" placeholder="Ej. Podología profesional" value="{{ profile.subtitle if profile else '' }}"></label>
      <label>Color de marca<input type="color" name="brand_color" value="{{ profile.brand_color if profile and profile.brand_color else organization.brand_color or '#6b3b22' }}"></label>\n      <label>Color del marco de botones<input type="color" name="button_border_color" value="{{ profile.button_border_color if profile and profile.button_border_color else '#e4ddd7' }}"></label>
      <label>Logo<input type="file" name="logo_file" accept="image/png,image/jpeg,image/webp"></label>
    </section>
    <section>
      <h2>Acciones</h2>
      <label>Reseña de Google<input name="google_url" placeholder="https://..." value="{{ profile.google_url if profile else '' }}"></label>
      <label>WhatsApp<input name="whatsapp" placeholder="3312345678" value="{{ profile.whatsapp if profile else '' }}"></label>
      <label>Instagram<input name="instagram_url" placeholder="@usuario" value="{{ profile.instagram_url if profile else '' }}"></label>
      <label>Google Maps<input name="maps_url" placeholder="https://maps..." value="{{ profile.maps_url if profile else '' }}"></label>
      <label>Teléfono<input name="phone" value="{{ profile.phone if profile else '' }}"></label>
      <label>Agenda<input name="booking_url" placeholder="https://..." value="{{ profile.booking_url if profile else '' }}"></label>
      <label>Sitio web<input name="website_url" placeholder="https://..." value="{{ profile.website_url if profile else '' }}"></label>
      <label>Menú / servicios<input name="menu_url" placeholder="https://..." value="{{ profile.menu_url if profile else '' }}"></label>
      <label>Facebook<input name="facebook_url" placeholder="https://..." value="{{ profile.facebook_url if profile else '' }}"></label>
      <label>Correo<input name="contact_email" value="{{ profile.contact_email if profile else '' }}"></label>
      <label>Dirección<input name="address" value="{{ profile.address if profile else '' }}"></label>
    </section>
    <div class="xp-connect-biz-actions">
      <button class="btn btn-primary" type="submit">Guardar Connect</button>
      {% if profile %}<a class="btn btn-secondary" href="/connect/{{ profile.slug }}" target="_blank">Ver perfil público</a><a class="btn btn-secondary" href="/admin/connect/{{ profile.slug }}/material">QR / banner</a>{% endif %}
    </div>
  </form>
</main>
{% endblock %}''',encoding="utf-8")

_cssp=_XpPath2("/app/app/static/app.css")
_css=_cssp.read_text(encoding="utf-8")
if "/* XP BUSINESS CONNECT ACCESS V1 */" not in _css:
    _css+=r'''
/* XP BUSINESS CONNECT ACCESS V1 */
.xp-connect-business{max-width:1050px!important}.xp-connect-biz-head{margin:24px 0 18px}.xp-connect-biz-head h1{font-size:clamp(2rem,4vw,3.2rem)!important;margin:5px 0}.xp-connect-biz-head p{color:#71675f;max-width:700px}.xp-connect-biz-form{display:grid;grid-template-columns:1fr 1fr;gap:18px}.xp-connect-biz-form>section{background:#fff;border:1px solid #e4dbd3;border-radius:20px;padding:20px;display:grid;gap:11px}.xp-connect-biz-form h2{margin:0 0 4px}.xp-connect-biz-form label{display:grid;gap:5px;font-size:.72rem;font-weight:800}.xp-connect-biz-form input{min-height:44px;padding:9px 11px;border:1px solid #d8cec6;border-radius:11px;background:#fff}.xp-connect-biz-actions{grid-column:1/-1;display:flex;gap:8px;flex-wrap:wrap}@media(max-width:720px){.xp-connect-biz-form{grid-template-columns:1fr}.xp-connect-biz-actions{grid-column:auto}}
'''
    _cssp.write_text(_css,encoding="utf-8")

# Surface Connect in existing business navigation.
for _f in _XpPath2("/app/app/templates/business").glob("*.html"):
    _t=_f.read_text(encoding="utf-8")
    if 'xp-business-nav' in _t and 'href="/negocio/connect"' not in _t:
        _t=_t.replace('<a href="/negocio/marca">Marca</a>','<a href="/negocio/connect">Connect</a><a href="/negocio/marca">Marca</a>')
        _t=_t.replace('<a href="/negocio/configuracion">Más</a>','<a href="/negocio/connect">Connect</a><a href="/negocio/configuracion">Más</a>')
        _f.write_text(_t,encoding="utf-8")

print("Business Connect access installed")
