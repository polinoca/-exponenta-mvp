from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK PANEL HEADER QR V2'

if marker not in s:
    block=r'''
# XP PET CLINIK PANEL HEADER QR V2
def xp_survey_business_theme(title, body, survey):
    name=str(survey.get("name") or "Tu negocio")
    logo=str(survey.get("logo_data") or survey.get("logo_url") or "")
    slug=str(survey.get("slug") or "")
    esc=lambda v: xp_html.escape(str(v),quote=True)
    brand=survey.get("brand_color") if xp_survey_re.fullmatch(r"#[0-9A-Fa-f]{6}",str(survey.get("brand_color") or "")) else "#2D71B1"
    if slug and 'xp-db-actions' in body:
        qr='<a class="xp-qr-inline" href="/negocio/encuestas/'+esc(slug)+'/qr.png" download>↓ Descargar QR</a>'
        body=body.replace('<div class="xp-db-actions">','<div class="xp-db-actions">'+qr,1)
    logo_html=('<img src="'+esc(logo)+'" alt="Logotipo de '+esc(name)+'">' if logo else '<span>'+esc(name)+'</span>')
    style="""<style>
    :root{--xp-client-brand:__BRAND__}
    header,footer,.footer{display:none!important}
    body{background:#f4fafd!important}
    main{max-width:1080px!important;margin:0 auto!important;padding:10px 14px 56px!important}
    .xp-client-brandbar{display:flex!important;justify-content:center!important;align-items:center!important;background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0!important;padding:2px!important;margin:0 0 12px!important}
    .xp-client-brandbar .xp-client-logo{display:flex!important;width:136px!important;height:116px!important;align-items:center!important;justify-content:center!important;background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0!important;padding:0!important;overflow:visible!important}
    .xp-client-brandbar .xp-client-logo img{display:block!important;max-width:136px!important;max-height:116px!important;width:auto!important;height:auto!important;object-fit:contain!important}
    .xp-client-brandbar .xp-client-name{font-size:24px;font-weight:850;color:var(--xp-client-brand)}
    .xp-client-brandcopy{display:none!important}
    .xp-db-actions .xp-qr-inline{background:var(--xp-client-brand)!important;color:#fff!important;border-color:var(--xp-client-brand)!important}
    @media(max-width:540px){main{padding:8px 11px 45px!important}.xp-client-brandbar{margin-bottom:8px!important}.xp-client-brandbar .xp-client-logo{width:124px!important;height:100px!important}.xp-client-brandbar .xp-client-logo img{max-width:124px!important;max-height:100px!important}.xp-db-actions{grid-template-columns:1fr 1fr!important}.xp-db-actions .xp-qr-inline{grid-column:span 1!important;font-size:12px!important;padding:10px 7px!important}}
    </style>""".replace("__BRAND__",brand)
    shell=style+'<div class="xp-client-brandbar"><span class="xp-client-logo">'+logo_html+'</span><div class="xp-client-brandcopy"></div></div>'+body
    return xp_survey_page(title,shell)
'''
    p.write_text(s+'\n'+block+'\n'+marker+'\n',encoding='utf-8')

print('PET Clinik centered logo and inline QR action repaired')
