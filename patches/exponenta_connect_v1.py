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
        CREATE TABLE IF NOT EXISTS exponenta_connect_feedback (
            id BIGSERIAL PRIMARY KEY,
            slug VARCHAR(80) NOT NULL,
            rating INTEGER,
            attendant TEXT,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS button_border_color VARCHAR(16)"))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS wifi_enabled INTEGER NOT NULL DEFAULT 0"))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS wifi_ssid TEXT"))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS wifi_note TEXT"))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS wifi_portal_url TEXT"))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS feedback_enabled INTEGER NOT NULL DEFAULT 0"))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS feedback_prompt TEXT"))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS organization_id INTEGER"))
    db.execute(xp_sql_text("CREATE INDEX IF NOT EXISTS ix_exponenta_connect_profiles_org ON exponenta_connect_profiles(organization_id)"))
    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_feedback ADD COLUMN IF NOT EXISTS attendant TEXT"))
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


@app.get("/connect/{slug}/wifi", response_class=HTMLResponse)
def exponenta_connect_wifi_page(slug: str, request: Request, db: Session = Depends(get_db)):
    profile = xp_connect_profile(db, slug)
    if not profile or not profile.get("wifi_enabled") or not (profile.get("wifi_ssid") or "").strip():
        raise HTTPException(404, "Wi-Fi no configurado")
    return render(request, "connect/wifi.html", {"profile": profile})

@app.get("/connect/{slug}/experiencia", response_class=HTMLResponse)
def exponenta_connect_feedback_page(slug: str, request: Request, db: Session = Depends(get_db)):
    profile = xp_connect_profile(db, slug)
    if not profile or not profile.get("feedback_enabled"):
        raise HTTPException(404, "Experiencia no configurada")
    return render(request, "connect/feedback.html", {"profile": profile, "saved": False})

@app.post("/connect/{slug}/experiencia")
def exponenta_connect_feedback_save(
    slug: str,
    request: Request,
    rating: int = Form(...),
    attendant: str = Form(""),
    comment: str = Form(""),
    db: Session = Depends(get_db),
):
    profile = xp_connect_profile(db, slug)
    if not profile or not profile.get("feedback_enabled"):
        raise HTTPException(404, "Experiencia no configurada")
    if rating < 1 or rating > 5:
        raise HTTPException(422, "Calificación inválida")
    db.execute(
        xp_sql_text("INSERT INTO exponenta_connect_feedback(slug,rating,attendant,comment) VALUES (:slug,:rating,:attendant,:comment)"),
        {"slug": slug, "rating": rating, "attendant": attendant.strip()[:120], "comment": comment.strip()[:2000]},
    )
    db.execute(xp_sql_text("INSERT INTO exponenta_connect_clicks(slug,kind) VALUES (:slug,'feedback')"), {"slug": slug})
    db.commit()
    return render(request, "connect/feedback.html", {"profile": profile, "saved": True})

@app.get("/admin/connect", response_class=HTMLResponse)
def exponenta_connect_admin(request: Request, db: Session = Depends(get_db)):
    user = control_superadmin(request, db)
    xp_connect_ensure(db)
    profiles = db.execute(xp_sql_text("""
        SELECT p.*,
               COALESCE((SELECT COUNT(*) FROM exponenta_connect_clicks c WHERE c.slug=p.slug),0) AS clicks,
               COALESCE((SELECT COUNT(*) FROM exponenta_connect_feedback f WHERE f.slug=p.slug),0) AS feedback_count
        FROM exponenta_connect_profiles p ORDER BY p.name
    """)).mappings().all()
    return render(request, "admin/connect.html", {"user": user, "profiles": profiles})

@app.get("/admin/connect/nuevo", response_class=HTMLResponse)
def exponenta_connect_new(request: Request, db: Session = Depends(get_db)):
    user = control_superadmin(request, db)
    return render(request, "admin/connect_edit.html", {"user": user, "profile": None, "csrf": request.state.session["csrf"]})


@app.get("/admin/connect/{slug}/experiencias", response_class=HTMLResponse)
def exponenta_connect_feedback_admin(slug: str, request: Request, db: Session = Depends(get_db)):
    user = control_superadmin(request, db)
    xp_connect_ensure(db)
    profile = db.execute(xp_sql_text("SELECT * FROM exponenta_connect_profiles WHERE slug=:slug"), {"slug": slug}).mappings().first()
    if not profile:
        raise HTTPException(404)
    items = db.execute(
        xp_sql_text("SELECT * FROM exponenta_connect_feedback WHERE slug=:slug ORDER BY created_at DESC LIMIT 200"),
        {"slug": slug},
    ).mappings().all()
    return render(request, "admin/connect_feedback.html", {"user": user, "profile": profile, "items": items})

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
        "brand_color": brand_color, "button_border_color": button_border_color,
        "wifi_enabled": 1 if wifi_enabled=="1" else 0,
        "wifi_ssid": wifi_ssid.strip(),
        "wifi_note": wifi_note.strip(),
        "wifi_portal_url": xp_connect_url(wifi_portal_url),
        "feedback_enabled": 1 if feedback_enabled=="1" else 0,
        "feedback_prompt": (feedback_prompt.strip() or "¿Cómo fue tu experiencia hoy?"),
        "logo_data": logo_data,
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
        (slug,name,subtitle,brand_color,button_border_color,wifi_enabled,wifi_ssid,wifi_note,wifi_portal_url,feedback_enabled,feedback_prompt,logo_data,google_url,whatsapp,instagram_url,maps_url,phone,booking_url,website_url,menu_url,facebook_url,contact_email,address,active)
        VALUES (:slug,:name,:subtitle,:brand_color,:button_border_color,:wifi_enabled,:wifi_ssid,:wifi_note,:wifi_portal_url,:feedback_enabled,:feedback_prompt,:logo_data,:google_url,:whatsapp,:instagram_url,:maps_url,:phone,:booking_url,:website_url,:menu_url,:facebook_url,:contact_email,:address,:active)
        ON CONFLICT (slug) DO UPDATE SET
        name=EXCLUDED.name, subtitle=EXCLUDED.subtitle, brand_color=EXCLUDED.brand_color, button_border_color=EXCLUDED.button_border_color,
        wifi_enabled=EXCLUDED.wifi_enabled,wifi_ssid=EXCLUDED.wifi_ssid,wifi_note=EXCLUDED.wifi_note,wifi_portal_url=EXCLUDED.wifi_portal_url,
        feedback_enabled=EXCLUDED.feedback_enabled,feedback_prompt=EXCLUDED.feedback_prompt,
        logo_data=COALESCE(EXCLUDED.logo_data, exponenta_connect_profiles.logo_data),
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
    .xp-copy{min-width:0}.xp-copy b{display:block;font-size:18px;line-height:1.08;letter-spacing:-.012em;color:var(--ink)}.xp-copy small{display:block;margin-top:5px;color:var(--muted);font-size:13.5px;line-height:1.2;font-weight:520}
    .xp-arrow{font-size:30px;line-height:1;color:#aaa19a;text-align:right}
    .xp-google{border:1.5px solid var(--border);background:#fff;box-shadow:0 10px 28px rgba(34,24,17,.07)}
    .xp-google .xp-copy b{color:var(--ink)}
    .xp-stars{display:flex;gap:2px;margin-top:7px}
    .xp-stars svg{width:15px;height:15px;fill:#f4b400}
    .xp-google .xp-icon{background:#fff}
    .xp-whatsapp .xp-icon{background:#eefbf3}
    .xp-instagram .xp-icon{background:#fff5fb}
    .xp-map .xp-icon{background:#fff1ef;color:#EA4335}
    .xp-call .xp-icon{background:#effaf2;color:#16A34A}
    .xp-web .xp-icon{background:#eff6ff;color:#2563EB}
    .xp-booking .xp-icon{background:#f5f0ff;color:#7C3AED}
    .xp-menu .xp-icon{background:#fff7ed;color:#D97706}
    .xp-wifi .xp-icon{background:#f3f4f6;color:#111827}
    .xp-feedback .xp-icon{background:#f5f0ff;color:#7C3AED}
    .xp-save .xp-icon{background:#ecfdf5;color:#0F766E}
    .xp-facebook .xp-icon{background:#eef5ff;color:#1877F2}
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
    {% if profile.wifi_enabled and profile.wifi_ssid %}
    <a class="xp-action xp-wifi" href="/connect/{{ profile.slug }}/wifi"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M2.8 8.5a14.5 14.5 0 0118.4 0M5.8 12a9.8 9.8 0 0112.4 0M9 15.5a5 5 0 016 0"/><circle cx="12" cy="19" r="1.2" fill="currentColor" stroke="none"/></svg></span><span class="xp-copy"><b>Conectarse al Wi-Fi</b><small>Ver red y acceso</small></span><span class="xp-arrow">›</span></a>
    {% endif %}
    {% if profile.feedback_enabled %}
    <a class="xp-action xp-feedback" href="/connect/{{ profile.slug }}/experiencia"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M4 4h16v12H8l-4 4z"/><path d="M8 9h8M8 12h5"/></svg></span><span class="xp-copy"><b>¿Cómo fue tu experiencia?</b><small>Cuéntanos de forma privada</small></span><span class="xp-arrow">›</span></a>
    {% endif %}
    <a class="xp-action xp-save" href="/connect/{{ profile.slug }}/contact.vcf"><span class="xp-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="12" cy="8" r="3.5"/><path d="M5 21c0-4 3-7 7-7s7 3 7 7"/><path d="M19 4v5M16.5 6.5h5"/></svg></span><span class="xp-copy"><b>Guardar contacto</b><small>Agrega el negocio a tu celular</small></span><span class="xp-arrow">›</span></a>
  </section>
  <footer class="xp-foot">Conectado por <b>Exponenta</b></footer>
</main>
</body>
</html>''', encoding="utf-8")


(Path("/app/app/templates/connect") / "wifi.html").write_text(r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Wi-Fi · {{ profile.name }}</title><style>*{box-sizing:border-box}body{margin:0;background:#f7f4f0;color:#171513;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,Arial,sans-serif}.wrap{max-width:520px;margin:auto;padding:26px 18px}.card{background:#fff;border-radius:26px;padding:24px;border:1px solid #e7dfd8;box-shadow:0 10px 30px rgba(34,24,17,.06)}.back{display:inline-block;margin-bottom:18px;color:#6b625c;text-decoration:none}.k{font-size:11px;letter-spacing:.15em;font-weight:800;color:{{ profile.brand_color or '#6b3b22' }}}h1{font-size:32px;margin:7px 0 8px}.muted{color:#756d67}.row{margin-top:18px;padding:15px;border-radius:18px;background:#f7f4f0}.row small{display:block;color:#80766f;margin-bottom:5px}.row b{font-size:18px;overflow-wrap:anywhere}.btn{display:block;text-align:center;text-decoration:none;width:100%;margin-top:14px;padding:15px;border-radius:16px;background:{{ profile.brand_color or '#6b3b22' }};color:#fff;font-weight:800;font-size:16px}.note{margin-top:14px;color:#756d67;font-size:14px}</style></head><body><main class="wrap"><a class="back" href="/connect/{{ profile.slug }}">← Volver</a><section class="card"><span class="k">WI-FI</span><h1>Conéctate a nuestra red</h1><p class="muted">Busca esta red desde los ajustes de Wi-Fi de tu teléfono.</p><div class="row"><small>Nombre de la red</small><b>{{ profile.wifi_ssid }}</b></div>{% if profile.wifi_note %}<p class="note">{{ profile.wifi_note }}</p>{% endif %}{% if profile.wifi_portal_url %}<a class="btn" href="{{ profile.wifi_portal_url }}" target="_blank" rel="noopener">Abrir portal Wi-Fi</a>{% endif %}</section></main></body></html>''', encoding="utf-8")

(Path("/app/app/templates/connect") / "feedback.html").write_text(r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Tu experiencia · {{ profile.name }}</title><style>*{box-sizing:border-box}body{margin:0;background:#f7f4f0;color:#171513;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,Arial,sans-serif}.wrap{max-width:520px;margin:auto;padding:26px 18px}.card{background:#fff;border-radius:26px;padding:24px;border:1px solid #e7dfd8;box-shadow:0 10px 30px rgba(34,24,17,.06)}.back{display:inline-block;margin-bottom:18px;color:#6b625c;text-decoration:none}.k{font-size:11px;letter-spacing:.15em;font-weight:800;color:{{ profile.brand_color or '#6b3b22' }}}h1{font-size:30px;line-height:1.05;margin:7px 0 10px}.muted{color:#756d67}.scale{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:22px 0}.scale input{display:none}.scale label{display:grid;place-items:center;min-height:52px;border:1px solid #ddd3cb;border-radius:14px;font-size:26px;color:#bbb;cursor:pointer}.scale input:checked+label{background:#fff7d6;border-color:#f4b400;color:#f4b400}textarea{width:100%;min-height:120px;border:1px solid #ddd3cb;border-radius:16px;padding:14px;font:inherit;resize:vertical}.btn{width:100%;margin-top:14px;padding:15px;border:0;border-radius:16px;background:{{ profile.brand_color or '#6b3b22' }};color:#fff;font-weight:800;font-size:16px}.ok{text-align:center;padding:28px 8px}.ok b{font-size:28px}.ok p{color:#756d67}</style></head><body><main class="wrap"><a class="back" href="/connect/{{ profile.slug }}">← Volver</a><section class="card">{% if saved %}<div class="ok"><b>Gracias por contarnos.</b><p>Tu comentario fue enviado de forma privada al negocio.</p></div>{% else %}<span class="k">EXPERIENCIA</span><h1>{{ profile.feedback_prompt or '¿Cómo fue tu experiencia hoy?' }}</h1><p class="muted">Esto se envía directamente al negocio y no se publica en Google.</p><form method="post"><div class="scale">{% for n in range(1,6) %}<input id="r{{ n }}" name="rating" type="radio" value="{{ n }}" {% if n==5 %}required{% endif %}><label for="r{{ n }}">★</label>{% endfor %}</div><input name="attendant" maxlength="120" placeholder="¿Quién te atendió? (opcional)" style="width:100%;height:52px;border:1px solid #ddd3cb;border-radius:16px;padding:0 14px;font:inherit;margin-bottom:12px"><textarea name="comment" maxlength="2000" placeholder="Cuéntanos sobre tu experiencia. ¿Qué te gustó o qué podríamos mejorar?"></textarea><button class="btn" type="submit">Enviar experiencia</button></form>{% endif %}</section></main></body></html>''', encoding="utf-8")

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
      <label>Wi-Fi<select name="wifi_enabled"><option value="0" {% if not profile or not profile.wifi_enabled %}selected{% endif %}>No mostrar</option><option value="1" {% if profile and profile.wifi_enabled %}selected{% endif %}>Mostrar</option></select></label>
      <label>Nombre de red Wi-Fi<input name="wifi_ssid" placeholder="Ej. Linopo Guest" value="{{ profile.wifi_ssid if profile else '' }}"></label>
      <label class="wide">Nota Wi-Fi<input name="wifi_note" placeholder="Ej. Solicita la clave al personal" value="{{ profile.wifi_note if profile else '' }}"></label>
      <label class="wide">Portal Wi-Fi (opcional)<input name="wifi_portal_url" placeholder="https://..." value="{{ profile.wifi_portal_url if profile else '' }}"></label>
      <label>Experiencia privada<select name="feedback_enabled"><option value="0" {% if not profile or not profile.feedback_enabled %}selected{% endif %}>No mostrar</option><option value="1" {% if profile and profile.feedback_enabled %}selected{% endif %}>Mostrar</option></select></label>
      <label class="wide">Pregunta de experiencia<input name="feedback_prompt" placeholder="¿Cómo fue tu experiencia hoy?" value="{{ profile.feedback_prompt if profile else '¿Cómo fue tu experiencia hoy?' }}"></label>
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
    new = '<a href="/connect/{{ p.slug }}" target="_blank">Abrir</a><a href="/admin/connect/{{ p.slug }}/material">QR / banner</a><a href="/admin/connect/{{ p.slug }}/experiencias">Experiencias{% if p.feedback_count %} ({{ p.feedback_count }}){% endif %}</a><a href="/admin/connect/{{ p.slug }}/editar">Editar</a>'
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
      "brand_color":brand_color,"button_border_color":button_border_color,
      "wifi_enabled":1 if wifi_enabled=="1" else 0,"wifi_ssid":wifi_ssid.strip(),"wifi_note":wifi_note.strip(),
      "wifi_portal_url":xp_connect_url(wifi_portal_url),"feedback_enabled":1 if feedback_enabled=="1" else 0,
      "feedback_prompt":(feedback_prompt.strip() or "¿Cómo fue tu experiencia hoy?"),
      "logo_data":logo_data,"google_url":xp_connect_url(google_url),
      "whatsapp":xp_connect_whatsapp(whatsapp),"instagram_url":xp_connect_instagram(instagram_url),
      "maps_url":xp_connect_url(maps_url),"phone":phone.strip(),"booking_url":xp_connect_url(booking_url),
      "website_url":xp_connect_url(website_url),"menu_url":xp_connect_url(menu_url),
      "facebook_url":xp_connect_url(facebook_url),"contact_email":contact_email.strip(),"address":address.strip()
    }
    if existing and existing["slug"] != clean_slug:
        db.execute(xp_sql_text("DELETE FROM exponenta_connect_profiles WHERE organization_id=:org_id"),{"org_id":org.id})
    db.execute(xp_sql_text("""
      INSERT INTO exponenta_connect_profiles
      (organization_id,slug,name,subtitle,brand_color,button_border_color,wifi_enabled,wifi_ssid,wifi_note,wifi_portal_url,feedback_enabled,feedback_prompt,logo_data,google_url,whatsapp,instagram_url,maps_url,phone,booking_url,website_url,menu_url,facebook_url,contact_email,address,active)
      VALUES (:organization_id,:slug,:name,:subtitle,:brand_color,:button_border_color,:wifi_enabled,:wifi_ssid,:wifi_note,:wifi_portal_url,:feedback_enabled,:feedback_prompt,:logo_data,:google_url,:whatsapp,:instagram_url,:maps_url,:phone,:booking_url,:website_url,:menu_url,:facebook_url,:contact_email,:address,1)
      ON CONFLICT (slug) DO UPDATE SET
      organization_id=EXCLUDED.organization_id,name=EXCLUDED.name,subtitle=EXCLUDED.subtitle,brand_color=EXCLUDED.brand_color,button_border_color=EXCLUDED.button_border_color,
      wifi_enabled=EXCLUDED.wifi_enabled,wifi_ssid=EXCLUDED.wifi_ssid,wifi_note=EXCLUDED.wifi_note,wifi_portal_url=EXCLUDED.wifi_portal_url,
      feedback_enabled=EXCLUDED.feedback_enabled,feedback_prompt=EXCLUDED.feedback_prompt,
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
      <label>Wi-Fi<select name="wifi_enabled"><option value="0" {% if not profile or not profile.wifi_enabled %}selected{% endif %}>No mostrar</option><option value="1" {% if profile and profile.wifi_enabled %}selected{% endif %}>Mostrar</option></select></label>
      <label>Red Wi-Fi<input name="wifi_ssid" value="{{ profile.wifi_ssid if profile else '' }}"></label>
      <label>Nota Wi-Fi<input name="wifi_note" value="{{ profile.wifi_note if profile else '' }}"></label>
      <label>Portal Wi-Fi<input name="wifi_portal_url" placeholder="https://..." value="{{ profile.wifi_portal_url if profile else '' }}"></label>
      <label>Experiencia privada<select name="feedback_enabled"><option value="0" {% if not profile or not profile.feedback_enabled %}selected{% endif %}>No mostrar</option><option value="1" {% if profile and profile.feedback_enabled %}selected{% endif %}>Mostrar</option></select></label>
      <label>Pregunta<input name="feedback_prompt" value="{{ profile.feedback_prompt if profile else '¿Cómo fue tu experiencia hoy?' }}"></label>
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


# XP CONNECT UI/SAVE HOTFIX 2026-10-06
from pathlib import Path as _XpFixPath
_m = _XpFixPath("/app/app/main.py")
_ms = _m.read_text(encoding="utf-8")

_old_sig = '''    brand_color: str = Form("#6b3b22"),
    google_url: str = Form(""),'''
_new_sig = '''    brand_color: str = Form("#6b3b22"),
    button_border_color: str = Form("#e4ddd7"),
    wifi_enabled: str = Form("0"),
    wifi_ssid: str = Form(""),
    wifi_note: str = Form(""),
    wifi_portal_url: str = Form(""),
    feedback_enabled: str = Form("0"),
    feedback_prompt: str = Form(""),
    google_url: str = Form(""),'''
if _old_sig in _ms:
    _ms = _ms.replace(_old_sig, _new_sig, 1)
_m.write_text(_ms, encoding="utf-8")

_ed = _XpFixPath("/app/app/templates/admin/connect_edit.html")
if _ed.exists():
    _e = _ed.read_text(encoding="utf-8")
    _e = _e.replace('</label>\\n      <label>Color del marco de botones', '</label>\n      <label>Color del marco de botones')
    _e = _e.replace('Nota Wi-Fi<input name="wifi_note" placeholder="Ej. Solicita la clave al personal"', 'Clave Wi-Fi<input name="wifi_note" placeholder="Ej. linopo2026"')
    _ed.write_text(_e, encoding="utf-8")

_lst = _XpFixPath("/app/app/templates/admin/connect.html")
if _lst.exists():
    _l = _lst.read_text(encoding="utf-8")
    _l = _l.replace('/connect/{{ p.slug }} · {{ p.clicks }} clics', '{{ p.clicks }} clics')
    _lst.write_text(_l, encoding="utf-8")

_wf = _XpFixPath("/app/app/templates/connect/wifi.html")
if _wf.exists():
    _w = _wf.read_text(encoding="utf-8")
    _w = _w.replace('Busca esta red desde los ajustes de Wi-Fi de tu teléfono.', 'Busca esta red desde los ajustes de Wi-Fi de tu teléfono y copia la clave.')
    _w = _w.replace('{% if profile.wifi_note %}<p class="note">{{ profile.wifi_note }}</p>{% endif %}', '''{% if profile.wifi_note %}<div class="row"><small>Clave Wi-Fi</small><b id="wifi-key">{{ profile.wifi_note }}</b></div><button class="btn" type="button" onclick="navigator.clipboard.writeText(document.getElementById('wifi-key').textContent);this.textContent='Clave copiada ✓'">Copiar clave</button>{% endif %}''')
    _wf.write_text(_w, encoding="utf-8")

_css = _XpFixPath("/app/app/static/app.css")
if _css.exists():
    _cs = _css.read_text(encoding="utf-8")
    if "/* XP CONNECT ADMIN HOTFIX */" not in _cs:
        _cs += r'''
/* XP CONNECT ADMIN HOTFIX */
.xp-connect-table article{grid-template-columns:64px minmax(180px,1fr) auto auto auto auto!important;align-items:center;gap:12px}
.xp-connect-table article>a{display:inline-flex!important;align-items:center;justify-content:center;white-space:nowrap;padding:8px 10px;border-radius:10px;text-decoration:none}
@media(max-width:760px){.xp-connect-table article{grid-template-columns:52px 1fr!important}.xp-connect-table article>a{grid-column:auto;justify-content:flex-start;padding:6px 0}}
'''
        _css.write_text(_cs, encoding="utf-8")


# XP CONNECT EXPERIENCES TEMPLATE HOTFIX 2026-10-06
from pathlib import Path as _XpExperiencePath
_exp_dir = _XpExperiencePath("/app/app/templates/admin")
_exp_dir.mkdir(parents=True, exist_ok=True)
(_exp_dir / "connect_feedback.html").write_text(r'''{% extends "base.html" %}
{% block title %}Experiencias · {{ profile.name }}{% endblock %}
{% block body %}
<main class="container xp-connect-admin">
  <div class="xp-connect-admin-head">
    <div>
      <a href="/admin/connect">← Connect</a>
      <span class="eyebrow">BUZÓN PRIVADO</span>
      <h1>Experiencias · {{ profile.name }}</h1>
      <p>Comentarios privados recibidos desde Exponenta Connect. No se publican en Google.</p>
    </div>
  </div>

  <div class="xp-connect-table xp-feedback-list">
    {% for item in items %}
    <article style="grid-template-columns:110px minmax(0,1fr)!important">
      <div style="width:auto;height:auto;background:transparent;display:block">
        <b style="font-size:18px">{{ item.rating }}/5 ★</b>
      </div>
      <section>
        {% if item.attendant %}
        <small style="display:block;margin-bottom:6px"><b>Te atendió:</b> {{ item.attendant }}</small>
        {% endif %}
        <strong style="display:block">{{ item.comment or "Sin comentario" }}</strong>
        <small style="display:block;margin-top:7px">{{ item.created_at }}</small>
      </section>
    </article>
    {% else %}
    <section style="padding:24px 0">
      <strong>Aún no hay experiencias recibidas.</strong>
      <p>Cuando un cliente envíe una calificación o comentario, aparecerá aquí.</p>
    </section>
    {% endfor %}
  </div>
</main>
{% endblock %}''', encoding="utf-8")


# XP CONNECT MOBILE EXPERIENCE/WIFI POLISH 2026-10-06
from pathlib import Path as _XpPolishPath
_polish_connect = _XpPolishPath("/app/app/templates/connect")
_polish_connect.mkdir(parents=True, exist_ok=True)

(_polish_connect / "feedback.html").write_text(r'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Tu experiencia · {{ profile.name }}</title>
<style>
*{box-sizing:border-box}
:root{--brand:{{ profile.brand_color or '#6b3b22' }}}
body{margin:0;background:#f7f4f0;color:#171513;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:520px;margin:auto;padding:26px 18px 40px}
.card{background:#fff;border-radius:26px;padding:24px;border:1px solid #e7dfd8;box-shadow:0 10px 30px rgba(34,24,17,.06)}
.back{display:inline-block;margin-bottom:18px;color:#6b625c;text-decoration:none;font-weight:700}
.k{display:block;font-size:12px;letter-spacing:.16em;font-weight:900;color:#6f655f;margin-bottom:10px}
h1{font-size:31px;line-height:1.03;margin:0 0 14px;letter-spacing:-.025em}
.muted{color:#756d67;font-size:17px;line-height:1.35;margin:0}
.scale{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:24px 0}
.scale input{position:absolute;opacity:0;pointer-events:none}
.scale label{display:grid;place-items:center;min-height:58px;border:1.5px solid #ddd3cb;border-radius:16px;font-size:30px;color:#b9b9b9;cursor:pointer;transition:.12s ease;background:#fff}
.scale label.active{background:#fff7d6;border-color:#f4b400;color:#f4b400;transform:translateY(-1px)}
.field{margin-top:14px}
.field label{display:block;font-size:14px;font-weight:800;color:#5f5751;margin:0 0 8px 3px}
.field input,.field textarea{width:100%;border:1.5px solid #d9cec6;border-radius:16px;padding:14px;font:inherit;color:#171513;background:#fff;outline:none}
.field input{height:54px}
.field textarea{min-height:132px;resize:vertical}
.field input::placeholder,.field textarea::placeholder{color:#9d9590;opacity:1}
.field input:focus,.field textarea:focus{border-color:#8e837b;box-shadow:0 0 0 3px rgba(0,0,0,.04)}
.btn{width:100%;margin-top:18px;padding:17px 16px;border:0;border-radius:17px;background:var(--brand);font-weight:900;font-size:17px;box-shadow:0 8px 20px rgba(0,0,0,.10);cursor:pointer;opacity:.45;transition:.15s ease}
.btn.ready{opacity:1;transform:translateY(-1px)}
.ok{text-align:center;padding:28px 8px}.ok b{font-size:28px}.ok p{color:#756d67}
@media(max-width:420px){.wrap{padding:24px 14px 36px}.card{padding:22px 18px}.scale{gap:6px}.scale label{min-height:54px;font-size:28px}}
</style>
</head>
<body>
<main class="wrap">
<a class="back" href="/connect/{{ profile.slug }}">← Volver</a>
<section class="card">
{% if saved %}
<div class="ok"><b>Gracias por contarnos.</b><p>Tu comentario fue enviado directamente al negocio.</p></div>
{% else %}
<span class="k">EXPERIENCIA</span>
<h1>{{ profile.feedback_prompt or '¿Cómo fue tu experiencia hoy?' }}</h1>
<p class="muted">Esto se envía directamente al negocio y nos ayuda a asegurarnos de ofrecerte un buen servicio.</p>
<form method="post" id="feedback-form">
  <div class="scale" aria-label="Calificación de 1 a 5 estrellas">
    {% for n in range(1,6) %}
    <input id="r{{ n }}" name="rating" type="radio" value="{{ n }}" {% if n==1 %}required{% endif %}>
    <label for="r{{ n }}" data-rating="{{ n }}" aria-label="{{ n }} estrella{% if n != 1 %}s{% endif %}">★</label>
    {% endfor %}
  </div>
  <div class="field">
    <label for="attendant">¿Quién te atendió? <span style="font-weight:600;color:#8d847e">(opcional)</span></label>
    <input id="attendant" name="attendant" maxlength="120" placeholder="Nombre de la persona">
  </div>
  <div class="field">
    <label for="comment">Cuéntanos sobre tu experiencia</label>
    <textarea id="comment" name="comment" maxlength="2000" placeholder="¿Qué te gustó o qué podríamos mejorar?"></textarea>
  </div>
  <button class="btn" id="send-btn" type="submit" data-brand="{{ profile.brand_color or '#6b3b22' }}">Enviar experiencia</button>
</form>
<script>
(function(){
  const radios=[...document.querySelectorAll('.scale input')];
  const labels=[...document.querySelectorAll('.scale label')];
  const btn=document.getElementById('send-btn');

  function paint(value){
    labels.forEach((label,idx)=>label.classList.toggle('active',idx<value));
    if(value>0) btn.classList.add('ready');
  }
  radios.forEach(r=>r.addEventListener('change',()=>paint(Number(r.value))));

  function contrast(hex){
    hex=(hex||'').replace('#','');
    if(hex.length===3) hex=hex.split('').map(x=>x+x).join('');
    if(hex.length!==6) return '#ffffff';
    const r=parseInt(hex.slice(0,2),16),g=parseInt(hex.slice(2,4),16),b=parseInt(hex.slice(4,6),16);
    const yiq=(r*299+g*587+b*114)/1000;
    return yiq>=150?'#171513':'#ffffff';
  }
  btn.style.color=contrast(btn.dataset.brand);
})();
</script>
{% endif %}
</section>
</main>
</body>
</html>''', encoding="utf-8")

(_polish_connect / "wifi.html").write_text(r'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Wi-Fi · {{ profile.name }}</title>
<style>
*{box-sizing:border-box}
:root{--brand:{{ profile.brand_color or '#6b3b22' }}}
body{margin:0;background:#f7f4f0;color:#171513;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:520px;margin:auto;padding:26px 18px 40px}
.card{background:#fff;border-radius:26px;padding:24px;border:1px solid #e7dfd8;box-shadow:0 10px 30px rgba(34,24,17,.06)}
.back{display:inline-block;margin-bottom:18px;color:#6b625c;text-decoration:none;font-weight:700}
.k{display:block;font-size:12px;letter-spacing:.16em;font-weight:900;color:#6f655f;margin-bottom:10px}
h1{font-size:32px;line-height:1.05;margin:0 0 14px;letter-spacing:-.025em}
.muted{color:#756d67;font-size:17px;line-height:1.35;margin:0}
.row{margin-top:18px;padding:16px;border-radius:18px;background:#f7f4f0;border:1px solid #ebe4de}
.row small{display:block;color:#756d67;margin-bottom:5px;font-size:14px;font-weight:700}
.row b{font-size:20px;overflow-wrap:anywhere}
.btn{display:block;text-align:center;text-decoration:none;width:100%;margin-top:16px;padding:17px 16px;border:0;border-radius:17px;background:var(--brand);font-weight:900;font-size:17px;box-shadow:0 8px 20px rgba(0,0,0,.10);cursor:pointer;transition:.15s ease}
.btn:active{transform:scale(.99)}
@media(max-width:420px){.wrap{padding:24px 14px 36px}.card{padding:22px 18px}}
</style>
</head>
<body>
<main class="wrap">
<a class="back" href="/connect/{{ profile.slug }}">← Volver</a>
<section class="card">
<span class="k">WI-FI</span>
<h1>Conéctate a nuestra red</h1>
<p class="muted">Busca esta red desde los ajustes de Wi-Fi de tu teléfono y copia la clave.</p>
<div class="row"><small>Nombre de la red</small><b>{{ profile.wifi_ssid }}</b></div>
{% if profile.wifi_note %}
<div class="row"><small>Clave Wi-Fi</small><b id="wifi-key">{{ profile.wifi_note }}</b></div>
<button class="btn" id="copy-btn" type="button" data-brand="{{ profile.brand_color or '#6b3b22' }}">Copiar clave</button>
<script>
(function(){
  const btn=document.getElementById('copy-btn');
  function contrast(hex){
    hex=(hex||'').replace('#','');
    if(hex.length===3) hex=hex.split('').map(x=>x+x).join('');
    if(hex.length!==6) return '#ffffff';
    const r=parseInt(hex.slice(0,2),16),g=parseInt(hex.slice(2,4),16),b=parseInt(hex.slice(4,6),16);
    return ((r*299+g*587+b*114)/1000)>=150?'#171513':'#ffffff';
  }
  btn.style.color=contrast(btn.dataset.brand);
  btn.addEventListener('click',async function(){
    const value=document.getElementById('wifi-key').textContent.trim();
    try{
      await navigator.clipboard.writeText(value);
      btn.textContent='Clave copiada ✓';
    }catch(e){
      const ta=document.createElement('textarea');ta.value=value;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();
      btn.textContent='Clave copiada ✓';
    }
    setTimeout(()=>btn.textContent='Copiar clave',1800);
  });
})();
</script>
{% endif %}
</section>
</main>
</body>
</html>''', encoding="utf-8")

# Keep Wi-Fi configuration simple: remove the unused portal field from admin/business forms.
for _form_path in [
    _XpPolishPath("/app/app/templates/admin/connect_edit.html"),
    _XpPolishPath("/app/app/templates/business/connect.html"),
]:
    if _form_path.exists():
        _form = _form_path.read_text(encoding="utf-8")
        import re as _xp_polish_re
        _form = _xp_polish_re.sub(r'<label[^>]*>Portal Wi-Fi \(opcional\)<input[^>]*name="wifi_portal_url"[^>]*></label>', '', _form)
        _form = _xp_polish_re.sub(r'<label[^>]*>Portal Wi-Fi<input[^>]*name="wifi_portal_url"[^>]*></label>', '', _form)
        _form_path.write_text(_form, encoding="utf-8")


# XP CONNECT ACTION ORDER EDITOR 2026-10-06
from pathlib import Path as _XpOrderPath
_order_main = _XpOrderPath("/app/app/main.py")
_order_s = _order_main.read_text(encoding="utf-8")

# Persist a simple comma-separated order string.
_order_schema_anchor = 'db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS button_border_color VARCHAR(16)"))'
if 'ADD COLUMN IF NOT EXISTS action_order TEXT' not in _order_s and _order_schema_anchor in _order_s:
    _order_s = _order_s.replace(
        _order_schema_anchor,
        _order_schema_anchor + '\n    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS action_order TEXT"))',
        1,
    )

# Add action_order to both admin and business save signatures.
if 'action_order: str = Form("")' not in _order_s:
    _order_s = _order_s.replace(
        '    feedback_prompt: str = Form(""),\n    google_url:',
        '    feedback_prompt: str = Form(""),\n    action_order: str = Form(""),\n    google_url:',
    )

# Add value to both save dictionaries.
_order_s = _order_s.replace(
    '"feedback_prompt": (feedback_prompt.strip() or "¿Cómo fue tu experiencia hoy?"),\n        "logo_data":',
    '"feedback_prompt": (feedback_prompt.strip() or "¿Cómo fue tu experiencia hoy?"),\n        "action_order": action_order.strip(),\n        "logo_data":',
)
_order_s = _order_s.replace(
    '"feedback_prompt":(feedback_prompt.strip() or "¿Cómo fue tu experiencia hoy?"),\n      "logo_data":',
    '"feedback_prompt":(feedback_prompt.strip() or "¿Cómo fue tu experiencia hoy?"),\n      "action_order":action_order.strip(),\n      "logo_data":',
)

# Extend admin SQL.
_order_s = _order_s.replace(
    '(slug,name,subtitle,brand_color,button_border_color,wifi_enabled,wifi_ssid,wifi_note,wifi_portal_url,feedback_enabled,feedback_prompt,logo_data,',
    '(slug,name,subtitle,brand_color,button_border_color,wifi_enabled,wifi_ssid,wifi_note,wifi_portal_url,feedback_enabled,feedback_prompt,action_order,logo_data,',
)
_order_s = _order_s.replace(
    'VALUES (:slug,:name,:subtitle,:brand_color,:button_border_color,:wifi_enabled,:wifi_ssid,:wifi_note,:wifi_portal_url,:feedback_enabled,:feedback_prompt,:logo_data,',
    'VALUES (:slug,:name,:subtitle,:brand_color,:button_border_color,:wifi_enabled,:wifi_ssid,:wifi_note,:wifi_portal_url,:feedback_enabled,:feedback_prompt,:action_order,:logo_data,',
)
_order_s = _order_s.replace(
    'feedback_enabled=EXCLUDED.feedback_enabled,feedback_prompt=EXCLUDED.feedback_prompt,\n        logo_data=',
    'feedback_enabled=EXCLUDED.feedback_enabled,feedback_prompt=EXCLUDED.feedback_prompt,action_order=EXCLUDED.action_order,\n        logo_data=',
)

# Extend business SQL.
_order_s = _order_s.replace(
    '(organization_id,slug,name,subtitle,brand_color,button_border_color,wifi_enabled,wifi_ssid,wifi_note,wifi_portal_url,feedback_enabled,feedback_prompt,logo_data,',
    '(organization_id,slug,name,subtitle,brand_color,button_border_color,wifi_enabled,wifi_ssid,wifi_note,wifi_portal_url,feedback_enabled,feedback_prompt,action_order,logo_data,',
)
_order_s = _order_s.replace(
    'VALUES (:organization_id,:slug,:name,:subtitle,:brand_color,:button_border_color,:wifi_enabled,:wifi_ssid,:wifi_note,:wifi_portal_url,:feedback_enabled,:feedback_prompt,:logo_data,',
    'VALUES (:organization_id,:slug,:name,:subtitle,:brand_color,:button_border_color,:wifi_enabled,:wifi_ssid,:wifi_note,:wifi_portal_url,:feedback_enabled,:feedback_prompt,:action_order,:logo_data,',
)
_order_s = _order_s.replace(
    'feedback_enabled=EXCLUDED.feedback_enabled,feedback_prompt=EXCLUDED.feedback_prompt,\n      logo_data=',
    'feedback_enabled=EXCLUDED.feedback_enabled,feedback_prompt=EXCLUDED.feedback_prompt,action_order=EXCLUDED.action_order,\n      logo_data=',
)

_order_main.write_text(_order_s, encoding="utf-8")

_order_default = "google,whatsapp,instagram,maps,call,website,booking,menu,facebook,wifi,feedback,save"

_order_editor = r'''
<section class="xp-order-editor">
  <div class="xp-order-head">
    <div><h2>Orden de botones</h2><p>Arrastra para elegir cómo los verá el cliente.</p></div>
  </div>
  <input type="hidden" name="action_order" class="xp-order-value" value="{{ profile.action_order if profile and profile.action_order else 'google,whatsapp,instagram,maps,call,website,booking,menu,facebook,wifi,feedback,save' }}">
  <div class="xp-order-list">
    <div class="xp-order-item" draggable="true" data-key="google"><span>☷</span><b>Reseña de Google</b></div>
    <div class="xp-order-item" draggable="true" data-key="whatsapp"><span>☷</span><b>WhatsApp</b></div>
    <div class="xp-order-item" draggable="true" data-key="instagram"><span>☷</span><b>Instagram</b></div>
    <div class="xp-order-item" draggable="true" data-key="maps"><span>☷</span><b>Cómo llegar</b></div>
    <div class="xp-order-item" draggable="true" data-key="call"><span>☷</span><b>Llamar</b></div>
    <div class="xp-order-item" draggable="true" data-key="website"><span>☷</span><b>Sitio web</b></div>
    <div class="xp-order-item" draggable="true" data-key="booking"><span>☷</span><b>Agendar cita</b></div>
    <div class="xp-order-item" draggable="true" data-key="menu"><span>☷</span><b>Menú / servicios</b></div>
    <div class="xp-order-item" draggable="true" data-key="facebook"><span>☷</span><b>Facebook</b></div>
    <div class="xp-order-item" draggable="true" data-key="wifi"><span>☷</span><b>Wi-Fi</b></div>
    <div class="xp-order-item" draggable="true" data-key="feedback"><span>☷</span><b>Experiencia</b></div>
    <div class="xp-order-item" draggable="true" data-key="save"><span>☷</span><b>Guardar contacto</b></div>
  </div>
</section>
<script>
(function(){
  document.querySelectorAll('.xp-order-editor').forEach(function(editor){
    const list=editor.querySelector('.xp-order-list');
    const hidden=editor.querySelector('.xp-order-value');
    const items=[...list.querySelectorAll('.xp-order-item')];
    const saved=(hidden.value||'').split(',').filter(Boolean);
    const byKey=Object.fromEntries(items.map(el=>[el.dataset.key,el]));
    saved.forEach(k=>{if(byKey[k]) list.appendChild(byKey[k]);});
    items.forEach(el=>{if(!saved.includes(el.dataset.key)) list.appendChild(el);});

    let dragging=null;
    list.addEventListener('dragstart',e=>{
      dragging=e.target.closest('.xp-order-item');
      if(dragging) dragging.classList.add('dragging');
    });
    list.addEventListener('dragend',()=>{
      if(dragging) dragging.classList.remove('dragging');
      dragging=null; sync();
    });
    list.addEventListener('dragover',e=>{
      e.preventDefault();
      if(!dragging) return;
      const after=[...list.querySelectorAll('.xp-order-item:not(.dragging)')].find(el=>{
        const r=el.getBoundingClientRect();
        return e.clientY < r.top+r.height/2;
      });
      if(after) list.insertBefore(dragging,after); else list.appendChild(dragging);
    });
    function sync(){
      hidden.value=[...list.querySelectorAll('.xp-order-item')].map(el=>el.dataset.key).join(',');
    }
    editor.closest('form')?.addEventListener('submit',sync);
    sync();
  });
})();
</script>
'''

# Admin editor.
_admin_order = _XpOrderPath("/app/app/templates/admin/connect_edit.html")
if _admin_order.exists():
    _t = _admin_order.read_text(encoding="utf-8")
    if 'xp-order-editor' not in _t:
        _t = _t.replace(
            '    <button class="btn btn-primary" type="submit">Guardar y publicar</button>',
            _order_editor + '\n    <button class="btn btn-primary" type="submit">Guardar y publicar</button>',
            1,
        )
        _admin_order.write_text(_t, encoding="utf-8")

# Business editor.
_business_order = _XpOrderPath("/app/app/templates/business/connect.html")
if _business_order.exists():
    _t = _business_order.read_text(encoding="utf-8")
    if 'xp-order-editor' not in _t:
        _t = _t.replace(
            '    <div class="xp-connect-biz-actions">',
            _order_editor + '\n    <div class="xp-connect-biz-actions">',
            1,
        )
        _business_order.write_text(_t, encoding="utf-8")

# Public page: reorder rendered buttons without complicating the template.
_public_order = _XpOrderPath("/app/app/templates/connect/profile.html")
if _public_order.exists():
    _t = _public_order.read_text(encoding="utf-8")
    if 'XP_CONNECT_PUBLIC_ORDER' not in _t:
        _public_script = r'''
<script id="XP_CONNECT_PUBLIC_ORDER">
(function(){
  const list=document.querySelector('.xp-actions');
  if(!list) return;
  const order="{{ profile.action_order if profile.action_order else 'google,whatsapp,instagram,maps,call,website,booking,menu,facebook,wifi,feedback,save' }}".split(',');
  const selectors={
    google:'.xp-google',whatsapp:'.xp-whatsapp',instagram:'.xp-instagram',maps:'.xp-map',
    call:'.xp-call',website:'.xp-web',booking:'.xp-booking',menu:'.xp-menu',
    facebook:'.xp-facebook',wifi:'.xp-wifi',feedback:'.xp-feedback',save:'.xp-save'
  };
  order.forEach(key=>{
    const el=list.querySelector(selectors[key]||'__none__');
    if(el) list.appendChild(el);
  });
})();
</script>
'''
        _t = _t.replace('</section>\n  <footer class="xp-foot">', '</section>\n'+_public_script+'\n  <footer class="xp-foot">', 1)
        _public_order.write_text(_t, encoding="utf-8")

# Styling: compact and obvious drag UI.
_order_css = _XpOrderPath("/app/app/static/app.css")
if _order_css.exists():
    _css = _order_css.read_text(encoding="utf-8")
    if '/* XP CONNECT ACTION ORDER */' not in _css:
        _css += r'''
/* XP CONNECT ACTION ORDER */
.xp-order-editor{grid-column:1/-1;background:#fff;border:1px solid #e4dbd3;border-radius:18px;padding:18px;margin:6px 0 18px}
.xp-order-head h2{margin:0;font-size:1.1rem}.xp-order-head p{margin:4px 0 14px;color:#776e67;font-size:.8rem}
.xp-order-list{display:grid;gap:7px}
.xp-order-item{display:flex;align-items:center;gap:10px;min-height:44px;padding:10px 12px;border:1px solid #ded5ce;border-radius:12px;background:#faf8f6;cursor:grab;user-select:none}
.xp-order-item:active{cursor:grabbing}.xp-order-item.dragging{opacity:.45}
.xp-order-item span{font-size:1.2rem;color:#8c8179}.xp-order-item b{font-size:.82rem}
'''
        _order_css.write_text(_css, encoding="utf-8")

print("Exponenta Connect action ordering installed")
