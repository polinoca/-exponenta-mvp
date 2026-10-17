from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK CLIENT PANEL BRAND V1'

if marker not in s:
    override=r'''
# XP PET CLINIK CLIENT PANEL BRAND V1
def xp_survey_business_theme(title, body, survey):
    name=str(survey.get("name") or "Tu negocio")
    logo=str(survey.get("logo_data") or survey.get("logo_url") or "")
    esc=lambda v: xp_html.escape(str(v),quote=True)
    brand=survey.get("brand_color") if xp_survey_re.fullmatch(r"#[0-9A-Fa-f]{6}",str(survey.get("brand_color") or "")) else "#2D71B1"
    logo_html=('<span class="xp-client-logo"><img src="'+esc(logo)+'" alt="Logotipo de '+esc(name)+'"></span>' if logo else '<span class="xp-client-name">'+esc(name)+'</span>')
    style="""<style>
    header,footer,.footer{display:none!important}
    body{background:#f4fafd!important}
    main{max-width:1080px!important;margin:0 auto!important;padding:16px 14px 56px!important}
    .xp-client-brandbar{display:flex!important;align-items:center!important;gap:12px!important;background:#fff!important;border:1px solid #d7e8f2!important;border-radius:18px!important;padding:11px 14px!important;margin:0 0 18px!important;box-shadow:0 8px 24px rgba(23,76,112,.07)!important}
    .xp-client-logo{display:flex;width:52px;height:52px;align-items:center;justify-content:center;border-radius:50%;background:#fff;border:1px solid #e0edf4;padding:6px;overflow:hidden;flex:0 0 auto}
    .xp-client-logo img{display:block;max-width:100%;max-height:100%;object-fit:contain}
    .xp-client-name{color:var(--client-brand);font-size:20px;font-weight:850;letter-spacing:-.03em}
    .xp-client-brandcopy{min-width:0;display:grid;gap:3px}.xp-client-brandcopy b{font-size:15px;line-height:1.1;color:#17324d}.xp-client-brandcopy small{font-size:11px;color:#6f879a;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
    @media(max-width:540px){main{padding:12px 11px 45px!important}.xp-client-brandbar{border-radius:15px;padding:9px 11px;margin-bottom:13px!important}.xp-client-logo{width:45px;height:45px}.xp-client-brandcopy b{font-size:14px}}
    </style>"""
    shell=style.replace("--client-brand",brand)+'<div class="xp-client-brandbar">'+logo_html+'<div class="xp-client-brandcopy"><b>'+esc(name)+'</b><small>Panel de experiencia</small></div></div>'+body
    return xp_survey_page(title,shell)
'''
    p.write_text(s+'\n'+override+'\n'+marker+'\n',encoding='utf-8')

print('PET Clinik brand header is enforced throughout the client survey panel')
