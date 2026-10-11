from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
marker="# XP SURVEY THANK YOU BRAND FINISH V15"
if marker not in s:
 a=s.index("def xp_survey_thanks(");b=s.index("\n@app.",a)
 part=s[a:b]
 start=part.index("    body=");end=part.index("    return xp_survey_page(",start)
 replacement=r'''    brand=p["brand_color"] if xp_survey_re.fullmatch(r"#[0-9A-Fa-f]{6}",p["brand_color"] or "") else "#2D71B1"
    accent=p["secondary_color"] if xp_survey_re.fullmatch(r"#[0-9A-Fa-f]{6}",p["secondary_color"] or "") else "#4BB8DE"
    style="""<style>
    :root{--pet-primary:__MAIN__;--pet-accent:__ACCENT__;--pet-text:#17324D;--pet-muted:#5F7690;--pet-bg:#F4FAFD}
    body{background:var(--pet-bg);color:var(--pet-text);font-family:Inter,system-ui,-apple-system,sans-serif}
    header{display:none}main{max-width:560px;padding:26px 14px 60px;margin:auto}
    .xp-thanks-logo{display:block;max-width:178px;max-height:94px;object-fit:contain;margin:0 auto 25px}
    .xp-thanks-card{background:#fff;border:1px solid #CFE6F3;box-shadow:0 16px 44px rgba(27,89,142,.08);border-radius:25px;padding:30px 25px;text-align:center}
    .xp-thanks-check{width:72px;height:72px;margin:0 auto 20px;background:var(--pet-primary);color:#fff;font-size:39px;display:grid;place-items:center;border-radius:50%;box-shadow:0 8px 20px rgba(28,91,162,.16)}
    .xp-thanks-card h1{color:var(--pet-primary);font-weight:750;font-size:clamp(27px,7vw,36px);letter-spacing:-.04em;margin:0 0 11px}
    .xp-thanks-card>.xp-thanks-sub{color:var(--pet-muted);line-height:1.6;font-size:16px;margin:0 auto;max-width:320px}
    .xp-promo{margin-top:28px;background:#EAF6FC;border:1px solid #CFE6F3;border-radius:20px;padding:13px;text-align:left}
    .xp-promo-image{width:100%;height:195px;object-fit:cover;display:block;border-radius:13px;background:#DCEEF8}
    .xp-promo-copy{padding:15px 9px 8px}.xp-promo-copy h2{color:var(--pet-primary);font-size:22px;line-height:1.24;letter-spacing:-.02em;margin:0 0 7px}
    .xp-promo-copy p{color:#405c75;margin:7px 0;line-height:1.5}
    .xp-promo-code{color:var(--pet-primary);border:1.5px dashed var(--pet-accent);background:white;border-radius:13px;font-size:18px;font-weight:800;padding:14px;margin:15px 0;word-break:break-word;text-align:center}
    .xp-promo-note{color:var(--pet-muted);font-size:12px;line-height:1.45;margin:17px auto 0;max-width:320px}
    .footer{font-size:11px;color:#7C96AC;margin-top:26px}
    @media(max-width:600px){main{padding:18px 12px 50px}.xp-thanks-card{padding:25px 16px;border-radius:21px}.xp-promo{padding:11px;margin-top:24px}.xp-promo-image{height:180px}}
    @media(prefers-reduced-motion:no-preference){.xp-thanks-check{animation:popin .4s ease both}@keyframes popin{from{opacity:0;transform:scale(.84)}to{opacity:1;transform:scale(1)}}}
    </style>""".replace("__MAIN__",brand).replace("__ACCENT__",accent)
    body=style
    if p["logo_data"]:
        body+='<img class="xp-thanks-logo" alt="Logotipo de '+xp_html.escape(p["name"],quote=True)+'" src="'+xp_html.escape(p["logo_data"],quote=True)+'">'
    else:
        body+='<div style="color:'+brand+';font-size:25px;font-weight:800;text-align:center;margin:0 0 23px">'+xp_html.escape(p["name"])+'</div>'
    body+='<section class="xp-thanks-card"><div class="xp-thanks-check" aria-hidden="true">✓</div>'
    body+='<h1>¡Gracias por tu opinión!</h1><p class="xp-thanks-sub">'+xp_html.escape(p["thanks_text"] or "Tu experiencia nos ayuda a seguir mejorando.")+'</p>'
    if p["promo_enabled"] and p["promo_title"]:
        # The built-in default image can always be replaced by uploading a promotional image in Superadmin.
        fallback="https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?auto=format&fit=crop&w=1000&q=82"
        img=p["promotion_image"] or fallback
        body+='<section class="xp-promo"><img class="xp-promo-image" src="'+xp_html.escape(img,quote=True)+'" alt="Atención y cuidado de mascotas" loading="lazy" referrerpolicy="no-referrer">'
        body+='<div class="xp-promo-copy"><h2>'+xp_html.escape(p["promo_title"])+'</h2>'
        if p["promo_details"]:body+='<p>'+xp_html.escape(p["promo_details"])+'</p>'
        if p["promo_code"]:body+='<div class="xp-promo-code">Código: '+xp_html.escape(p["promo_code"])+'</div>'
        body+='</div></section><p class="xp-promo-note">Muestra este beneficio al personal. Aplican las condiciones indicadas.</p>'
    body+='</section>'
'''
 part=part[:start]+replacement+part[end:]
 s=s[:a]+part+s[b:]
 p.write_text(marker+"\n"+s,encoding="utf-8")
print("Brand-consistent mobile thank-you and replaceable promotion image enabled")
