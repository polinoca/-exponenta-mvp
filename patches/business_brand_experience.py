from pathlib import Path

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP BUSINESS BRAND EXPERIENCE V1"
if marker not in s:
    anchor='@app.get("/negocio/lealtad", response_class=HTMLResponse)'
    if anchor not in s: raise SystemExit("business route anchor missing")
    routes=r'''
# XP BUSINESS BRAND EXPERIENCE V1
def _brand_redirect(kind: str):
    messages={
        "invalid_color":"Elige un color válido.",
        "invalid_logo":"El logotipo debe ser PNG, JPG o WebP y pesar máximo 2 MB.",
        "invalid_cover":"La portada debe ser PNG, JPG o WebP, máximo 3 MB, de al menos 800 × 600 px y con proporción cercana a 5:4.",
    }
    return RedirectResponse("/negocio/marca?error="+kind, status_code=303)

@app.get("/negocio/marca", response_class=HTMLResponse)
def business_brand_page(request: Request, db: Session = Depends(get_db)):
    user, org = business_admin_context(request, db)
    require_org_feature(db, org, "wallet")
    require_org_feature(db, org, "wallet_branding")
    branding=wallet_branding_for(db, org)
    return render(request, "business/brand.html", {
        "user":user, "organization":org, "wallet_branding":branding,
        "message":request.query_params.get("message"), "error":request.query_params.get("error"),
    })

@app.post("/negocio/marca")
async def save_business_brand(
    request: Request,
    brand_color: str = Form("#6b3b22"),
    logo_file: UploadFile|None = File(None),
    cover_image: UploadFile|None = File(None),
    remove_cover: str = Form(""),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    _, org = business_admin_context(request, db)
    verify_csrf(request, csrf_token)
    require_org_feature(db, org, "wallet")
    require_org_feature(db, org, "wallet_branding")
    color=brand_color.strip()
    if len(color)!=7 or not color.startswith("#") or any(ch not in "0123456789abcdefABCDEF" for ch in color[1:]):
        return _brand_redirect("invalid_color")
    branding=wallet_branding_for(db, org)
    if logo_file and logo_file.filename:
        logo=await logo_file.read()
        valid=(
            (logo_file.content_type=="image/png" and logo.startswith(b"\\x89PNG\\r\\n\\x1a\\n"))
            or (logo_file.content_type=="image/jpeg" and logo.startswith(b"\\xff\\xd8\\xff"))
            or (logo_file.content_type=="image/webp" and logo[:4]==b"RIFF" and logo[8:12]==b"WEBP")
        )
        if not valid or len(logo)>2*1024*1024:
            return _brand_redirect("invalid_logo")
        org.logo_blob=logo
        org.logo_mime=logo_file.content_type
        org.logo_url=f"{settings.app_base_url.rstrip('/')}/media/organization/{org.slug}/logo?v={secrets.token_urlsafe(8)}"
    if cover_image and cover_image.filename:
        cover=await cover_image.read()
        valid_type=cover_image.content_type in {"image/png","image/jpeg","image/webp"}
        try:
            image=Image.open(io.BytesIO(cover)); image.verify()
            image=Image.open(io.BytesIO(cover)); width,height=image.size
            ratio=width/height
        except Exception:
            valid_type=False; width=height=0; ratio=0
        if not valid_type or len(cover)>3*1024*1024 or width<800 or height<600 or not 1.15<=ratio<=1.40:
            return _brand_redirect("invalid_cover")
        branding.hero_image=cover
        branding.hero_image_mime=cover_image.content_type
        branding.hero_image_width=width
        branding.hero_image_height=height
    elif remove_cover=="1":
        branding.hero_image=None
        branding.hero_image_mime=None
        branding.hero_image_width=None
        branding.hero_image_height=None
    org.brand_color=color
    branding.background_color=color
    db.add(org); db.add(branding); db.commit()
    return RedirectResponse("/negocio/marca?message=Marca+actualizada", status_code=303)

'''
    s=s.replace(anchor,routes+anchor,1)
    # The former Wallet editor now opens the single brand experience.
    old='''@app.get("/negocio/wallet",response_class=HTMLResponse)
def business_wallet_branding(request:Request,db:Session=Depends(get_db)):
 user,org=business_admin_context(request,db);require_org_feature(db,org,"wallet")
 w=wallet_branding_for(db,org)
 return render(request,"business/wallet_branding.html",{"user":user,"organization":org,"wallet_branding":w,"wallet_customization":org_feature_on(db,org.id,"wallet_branding")})
'''
    new='''@app.get("/negocio/wallet",response_class=HTMLResponse)
def business_wallet_branding(request:Request,db:Session=Depends(get_db)):
 business_admin_context(request,db)
 return RedirectResponse("/negocio/marca",status_code=303)
'''
    if old in s: s=s.replace(old,new,1)
    s=s.replace('headers={"Cache-Control":"public, max-age=3600"})','headers={"Cache-Control":"no-store, max-age=0"})',1)
    p.write_text(s,encoding="utf-8")

template=Path("/app/app/templates/business/brand.html")
template.write_text(r'''{% extends "base.html" %}
{% block title %}Marca · {{ organization.name }}{% endblock %}
{% block body %}
<main class="business-shell xp-brand-page">
  <nav class="xp-business-nav">
    <a href="/negocio">Inicio</a><a href="/negocio/lealtad">Clientes</a><a href="/negocio/seguridad">Equipo</a><a href="/negocio/marketing">Reseñas</a><a class="active" href="/negocio/marca">Marca</a><a href="/negocio/configuracion">Más</a>
  </nav>
  <header class="xp-brand-head"><span class="eyebrow">MARCA DEL NEGOCIO</span><h1>Tu marca, en una sola pantalla.</h1><p>Sube tu logo, elige tu color y agrega una imagen de cubierta. Así se verá tu tarjeta digital.</p></header>
  {% if message %}<div class="xp-brand-alert success">✓ {{ message }}</div>{% endif %}
  {% if error %}<div class="xp-brand-alert error">{% if error=="invalid_logo" %}El logotipo debe ser PNG, JPG o WebP y pesar máximo 2 MB.{% elif error=="invalid_cover" %}La portada debe ser PNG, JPG o WebP, máximo 3 MB, de al menos 800 × 600 px y proporción cercana a 5:4.{% else %}Revisa el color e inténtalo nuevamente.{% endif %}</div>{% endif %}
  <form method="post" enctype="multipart/form-data" class="xp-brand-layout">
    <input type="hidden" name="csrf_token" value="{{ csrf }}">
    <section class="xp-brand-form">
      <div class="xp-brand-step"><b>1</b><div><strong>Logotipo</strong><small>PNG, JPG o WebP · hasta 2 MB</small></div></div>
      <label class="xp-file-field"><span>Seleccionar logotipo</span><input id="brand-logo-input" type="file" name="logo_file" accept="image/png,image/jpeg,image/webp"></label>
      <div class="xp-brand-step"><b>2</b><div><strong>Color principal</strong><small>El color que identifica a tu negocio.</small></div></div>
      <label class="xp-color-field"><input id="brand-color-input" type="color" name="brand_color" value="{{ wallet_branding.background_color or organization.brand_color or '#6b3b22' }}"><code id="brand-color-value">{{ wallet_branding.background_color or organization.brand_color or '#6b3b22' }}</code></label>
      <div class="xp-brand-step"><b>3</b><div><strong>Imagen de cubierta <em>Opcional</em></strong><small>Se muestra en la tarjeta de Google Wallet.</small></div></div>
      <label class="xp-file-field"><span>Seleccionar imagen de cubierta</span><input id="brand-cover-input" type="file" name="cover_image" accept="image/png,image/jpeg,image/webp"></label>
      <small class="xp-file-help">Horizontal, mínimo 800 × 600 px, PNG/JPG/WebP, hasta 3 MB.</small>
      {% if wallet_branding.hero_image %}<label class="xp-remove-cover"><input type="checkbox" name="remove_cover" value="1"> Quitar imagen actual</label>{% endif %}
      <button class="btn btn-primary xp-brand-save" type="submit">Guardar mi marca</button>
    </section>
    <aside class="xp-brand-preview-wrap"><span>PREVISUALIZACIÓN</span><div id="brand-preview" class="xp-brand-preview" style="--brand:{{ wallet_branding.background_color or organization.brand_color or '#6b3b22' }}">
      <div id="brand-cover" class="xp-brand-cover {% if wallet_branding.hero_image %}has-image{% endif %}" {% if wallet_branding.hero_image %}style="background-image:url('/branding/wallet/{{ organization.id }}/hero?v={{ wallet_branding.updated_at }}')"{% endif %}></div>
      <div class="xp-brand-card"><div id="brand-logo" class="xp-brand-logo">{% if organization.logo_url %}<img src="{{ organization.logo_url }}" alt="Logo de {{ organization.name }}">{% else %}<b>{{ organization.name[:1] }}</b>{% endif %}</div><small>MI TARJETA</small><strong>{{ organization.name }}</strong><p>Lista para tus clientes</p></div>
    </div><p>La previsualización se actualiza antes de guardar.</p></aside>
  </form>
</main>
<script>
(()=>{const color=document.querySelector("#brand-color-input"), value=document.querySelector("#brand-color-value"), preview=document.querySelector("#brand-preview"), logo=document.querySelector("#brand-logo-input"), cover=document.querySelector("#brand-cover-input"), logoBox=document.querySelector("#brand-logo"), coverBox=document.querySelector("#brand-cover");color.addEventListener("input",()=>{preview.style.setProperty("--brand",color.value);value.textContent=color.value.toUpperCase()});const read=(input,done)=>input.addEventListener("change",()=>{const f=input.files[0];if(!f)return;const r=new FileReader();r.onload=e=>done(e.target.result);r.readAsDataURL(f)});read(logo,url=>logoBox.innerHTML='<img src="'+url+'" alt="Nuevo logotipo">');read(cover,url=>{coverBox.style.backgroundImage='url("'+url+'")';coverBox.classList.add("has-image")})})()
</script>
{% endblock %}''',encoding="utf-8")

cssp=Path("/app/app/static/app.css")
css=cssp.read_text(encoding="utf-8")
if "/* XP BUSINESS BRAND EXPERIENCE V1 */" not in css:
 css+=r'''
/* XP BUSINESS BRAND EXPERIENCE V1 */
.xp-brand-page{max-width:1120px!important}.xp-brand-head{margin:23px 0 18px}.xp-brand-head h1{margin:5px 0;font-size:clamp(2rem,4vw,3.25rem)!important}.xp-brand-head p{max-width:670px;color:#6d635c}.xp-brand-alert{padding:12px 15px;border-radius:12px;margin:12px 0;font-weight:700;font-size:.8rem}.xp-brand-alert.success{background:#e1f3e6;color:#156638}.xp-brand-alert.error{background:#ffe5e3;color:#9b2720}.xp-brand-layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,.82fr);gap:22px;align-items:start}.xp-brand-form,.xp-brand-preview-wrap{border:1px solid #e5dbd2;border-radius:22px;background:#fff;padding:23px;box-shadow:0 9px 24px rgba(64,42,26,.05)}.xp-brand-form{display:grid;gap:12px}.xp-brand-step{display:flex;align-items:center;gap:10px;margin-top:5px}.xp-brand-step>b{display:grid;place-items:center;width:25px;height:25px;border-radius:50%;background:#271e19;color:#fff;font-size:.72rem}.xp-brand-step strong{display:block;font-size:.88rem}.xp-brand-step small,.xp-file-help{font-size:.67rem;color:#746963}.xp-brand-step em{font-size:.58rem;color:#96745d;font-style:normal;font-weight:700}.xp-file-field{border:1px dashed #c8b5a7;background:#fbf8f5;border-radius:13px;padding:12px;display:flex;align-items:center;justify-content:space-between;gap:9px;font-size:.73rem;font-weight:800;cursor:pointer}.xp-file-field input{max-width:185px;font-size:.63rem}.xp-color-field{display:flex;align-items:center;gap:12px;padding:8px 11px;border:1px solid #e5dbd2;border-radius:13px}.xp-color-field input{width:46px;height:34px;border:0;background:transparent;cursor:pointer}.xp-color-field code{font-size:.84rem;font-weight:800;color:#4a3b31}.xp-remove-cover{font-size:.7rem;color:#6a5140}.xp-brand-save{margin-top:5px;justify-content:center}.xp-brand-preview-wrap>span{display:block;font-size:.61rem;letter-spacing:.12em;font-weight:900;color:#806956;margin-bottom:10px}.xp-brand-preview-wrap>p{font-size:.68rem;color:#776c65;margin:11px 0 0}.xp-brand-preview{overflow:hidden;border-radius:23px;background:var(--brand);color:white;box-shadow:0 16px 30px rgba(45,29,18,.18);min-height:400px;position:relative}.xp-brand-cover{height:155px;background:linear-gradient(120deg,rgba(255,255,255,.24),transparent 58%),var(--brand);background-size:cover;background-position:center}.xp-brand-cover.has-image:after{content:"";display:block;height:100%;background:linear-gradient(180deg,transparent,rgba(0,0,0,.28))}.xp-brand-card{padding:20px;min-height:224px;background:linear-gradient(145deg,color-mix(in srgb,var(--brand) 88%,#000),var(--brand));position:relative}.xp-brand-logo{width:48px;height:48px;border-radius:14px;background:#fff;display:grid;place-items:center;overflow:hidden;margin-bottom:23px;color:#382519}.xp-brand-logo img{width:100%;height:100%;object-fit:contain}.xp-brand-logo b{font-size:1.2rem}.xp-brand-card small{display:block;font-size:.56rem;letter-spacing:.12em;font-weight:900;opacity:.8}.xp-brand-card strong{display:block;font-size:1.65rem;line-height:1.05;margin:7px 0;max-width:85%}.xp-brand-card p{font-size:.72rem;margin:0;opacity:.84}@media(max-width:780px){.xp-brand-layout{grid-template-columns:1fr}.xp-brand-preview-wrap{order:-1}.xp-brand-preview{min-height:320px}.xp-brand-cover{height:112px}.xp-brand-card{min-height:190px}.xp-file-field{align-items:flex-start;flex-direction:column}.xp-file-field input{max-width:100%}}
'''
 cssp.write_text(css,encoding="utf-8")

# Surface Marca in the business navigation already injected throughout the business panel.
for file in Path("/app/app/templates").rglob("*.html"):
 t=file.read_text(encoding="utf-8")
 if 'class="xp-business-nav"' in t and 'href="/negocio/marca"' not in t:
  t=t.replace('<a href="/negocio/configuracion">Configuración</a>','<a href="/negocio/marca">Marca</a><a href="/negocio/configuracion">Configuración</a>')
  t=t.replace('<a href="/negocio/configuracion">Más</a>','<a href="/negocio/marca">Marca</a><a href="/negocio/configuracion">Más</a>')
  file.write_text(t,encoding="utf-8")
print("Business brand experience installed")
