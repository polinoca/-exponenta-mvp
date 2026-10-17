from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK LOGO CIRCLE V1'

if marker not in s:
    block=r'''
# XP PET CLINIK LOGO CIRCLE V1
_xp_pet_client_theme_base = xp_survey_business_theme

def xp_survey_business_theme(title, body, survey):
    page = _xp_pet_client_theme_base(title, body, survey)
    circle_style = """<style>
    .xp-client-brandbar .xp-client-logo{
      width:138px!important;height:138px!important;
      border-radius:50%!important;background:#fff!important;
      border:1px solid #d7e8f2!important;padding:12px!important;
      overflow:hidden!important;box-shadow:0 9px 25px rgba(26,83,119,.13)!important;
    }
    .xp-client-brandbar .xp-client-logo img{
      max-width:112px!important;max-height:112px!important;
      width:auto!important;height:auto!important;object-fit:contain!important;
    }
    @media(max-width:540px){
      .xp-client-brandbar .xp-client-logo{width:116px!important;height:116px!important;padding:10px!important}
      .xp-client-brandbar .xp-client-logo img{max-width:94px!important;max-height:94px!important}
    }
    </style>"""
    return page.replace("</head>", circle_style+"</head>", 1)
'''
    p.write_text(s+'\n'+block+'\n'+marker+'\n',encoding='utf-8')

print('PET Clinik logo restored in centered white circular base')
