from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK IDENTITY FINAL V1'

if marker not in s:
    block=r'''
# XP PET CLINIK IDENTITY FINAL V1
_xp_pet_clinik_identity_base = xp_survey_business_theme

def xp_survey_business_theme(title, body, survey):
    page = _xp_pet_clinik_identity_base(title, body, survey)
    name = str(survey.get("name") or "Pet Clinik")
    logo = str(survey.get("logo_data") or survey.get("logo_url") or "")
    esc = lambda value: xp_html.escape(str(value), quote=True)
    logo_html = ('<img src="'+esc(logo)+'" alt="Logotipo de '+esc(name)+'">' if logo else '<span>'+esc(name)+'</span>')
    identity = r"""<style>
      /* Client-facing PET Clinik identity: no platform co-branding */
      header, footer, .footer, .site-header, .site-footer, .brand-header,
      .powered-by, .xp-powered-by { display:none!important; }
      .xp-client-brandbar {
        display:flex!important; justify-content:center!important; align-items:center!important;
        padding:8px 0 14px!important; margin:0!important; background:transparent!important;
        border:0!important; box-shadow:none!important;
      }
      .xp-client-brandbar .xp-client-logo, .xp-pet-clinik-mark {
        box-sizing:border-box!important; display:flex!important; justify-content:center!important;
        align-items:center!important; width:142px!important; height:142px!important;
        padding:12px!important; border-radius:50%!important; overflow:hidden!important;
        background:#fff!important; border:1px solid #d5e5ee!important;
        box-shadow:0 8px 24px rgba(22,73,108,.14)!important;
      }
      .xp-client-brandbar .xp-client-logo img, .xp-pet-clinik-mark img {
        display:block!important; max-width:100%!important; max-height:100%!important;
        width:auto!important; height:auto!important; object-fit:contain!important;
      }
      .xp-client-brandcopy, .xp-client-name { display:none!important; }
      @media(max-width:540px) {
        .xp-client-brandbar { padding:7px 0 11px!important; }
        .xp-client-brandbar .xp-client-logo, .xp-pet-clinik-mark {
          width:124px!important; height:124px!important; padding:10px!important;
        }
      }
    </style>"""
    if 'xp-client-brandbar' not in page:
        mark = '<div class="xp-client-brandbar"><span class="xp-pet-clinik-mark">'+logo_html+'</span></div>'
        page = page.replace('<main>', '<main>'+mark, 1)
    page = page.replace('</head>', identity+'</head>', 1)
    # Do not expose the platform name in any client-facing survey screen.
    page = page.replace('Powered by Exponenta', '').replace('POWERED BY EXPONENTA', '')
    page = page.replace('Exponenta', '').replace('EXPONENTA', '').replace('exponenta', '')
    return page
'''
    p.write_text(s+'\n'+block+'\n'+marker+'\n',encoding='utf-8')

print('PET Clinik identity is centered, circular, and platform-free')
