from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK COOLDOWN BRAND V1'
if marker not in s:
    a=s.index('def xp_survey_public('); b=s.index('\n@app.',a); part=s[a:b]
    old='''        page=xp_survey_page("Opinión registrada",'<div class="card" style="text-align:center"><h1>Ya recibimos tu opinión</h1><p>Gracias por ayudarnos a mejorar.</p><p class="muted">Podrás responder una nueva encuesta después de 60 minutos.</p></div>')'''
    new='''        logo=(''<img src="'+xp_html.escape(str(p.get("logo_url") or ""),quote=True)+'" alt="'+xp_html.escape(str(p.get("name") or "Negocio"),quote=True)+'" style="display:block;width:76px;height:76px;object-fit:contain;margin:0 auto 17px;border-radius:50%;background:#fff;padding:5px;box-shadow:0 3px 14px rgba(20,72,106,.12)">'' if p.get("logo_url") else '')
        page=xp_survey_page("Opinión registrada",'<div class="card" style="text-align:center;max-width:520px;margin:30px auto;padding:clamp(28px,7vw,46px) 22px">'+logo+'<h1>Ya recibimos tu opinión</h1><p>Gracias por ayudarnos a mejorar.</p><p class="muted">Podrás responder una nueva encuesta después de 60 minutos.</p></div>')'''
    assert old in part
    part=part.replace(old,new,1)
    s=s[:a]+part+s[b:]
    p.write_text(s+'\n'+marker+'\n',encoding='utf-8')
print('Pet Clinik cooldown page now uses business logo')
