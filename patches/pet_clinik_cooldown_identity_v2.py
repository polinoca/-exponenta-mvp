from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK COOLDOWN IDENTITY V2'

if marker not in s:
    a=s.index('def xp_survey_public(')
    b=s.index('\n@app.', a)
    part=s[a:b]
    old='''        logo=('<img src="'+xp_html.escape(str(p.get("logo_url") or ""),quote=True)+'" alt="'+xp_html.escape(str(p.get("name") or "Negocio"),quote=True)+'" style="display:block;width:76px;height:76px;object-fit:contain;margin:0 auto 17px;border-radius:50%;background:#fff;padding:5px;box-shadow:0 3px 14px rgba(20,72,106,.12)">' if p.get("logo_url") else '')
        page=xp_survey_page("Opinión registrada",'<div class="card" style="text-align:center;max-width:520px;margin:30px auto;padding:clamp(28px,7vw,46px) 22px">'+logo+'<h1>Ya recibimos tu opinión</h1><p>Gracias por ayudarnos a mejorar.</p><p class="muted">Podrás responder una nueva encuesta después de 60 minutos.</p></div>')'''
    new='''        brand_name=str(p.get("name") or "PET Clinik")
        logo_src=str(p.get("logo_data") or p.get("logo_url") or "")
        logo_html=('<div class="xp-pet-logo"><img src="'+xp_html.escape(logo_src,quote=True)+'" alt="Logotipo de '+xp_html.escape(brand_name,quote=True)+'"></div>' if logo_src else '<div class="xp-pet-name">'+xp_html.escape(brand_name)+'</div>')
        style='<style>header,.footer,footer{display:none!important}main{max-width:560px!important;margin:0 auto!important;padding:28px 16px 52px!important}.xp-pet-card{background:#fff;border:1px solid #cfe6f3;border-radius:24px;box-shadow:0 16px 44px rgba(27,89,142,.10);padding:38px 22px;text-align:center;color:#17324d}.xp-pet-logo{width:112px;height:112px;border-radius:50%;background:#fff;border:1px solid #dcecf5;display:flex;align-items:center;justify-content:center;padding:15px;box-sizing:border-box;margin:0 auto 22px;box-shadow:0 8px 24px rgba(29,94,148,.10)}.xp-pet-logo img{max-width:100%;max-height:100%;object-fit:contain}.xp-pet-name{font-size:26px;font-weight:800;color:#2d71b1;margin:0 0 22px}.xp-pet-card h1{font-size:clamp(27px,7vw,36px);line-height:1.08;letter-spacing:-.04em;color:#17324d;margin:0 0 14px}.xp-pet-card p{font-size:16px;line-height:1.55;margin:8px auto;max-width:360px;color:#526c84}.xp-pet-card .muted{font-size:14px;color:#71889d;margin-top:19px}@media(max-width:600px){main{padding:20px 13px 40px!important}.xp-pet-card{padding:31px 17px}.xp-pet-logo{width:96px;height:96px;margin-bottom:19px}}</style>'
        content=style+'<section class="xp-pet-card">'+logo_html+'<h1>Ya recibimos tu opinión</h1><p>Gracias por ayudarnos a mejorar.</p><p class="muted">Podrás responder una nueva encuesta después de 60 minutos.</p></section>'
        page=xp_survey_page("Opinión registrada",content)'''
    if old not in part:
        raise SystemExit('Expected PET Clinik cooldown block not found')
    part=part.replace(old,new,1)
    s=s[:a]+part+s[b:]
    p.write_text(s+'\n'+marker+'\n',encoding='utf-8')

print('PET Clinik identity enforced on cooldown screen')
