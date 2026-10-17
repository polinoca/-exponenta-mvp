from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK DASHBOARD LOGO ONLY V1'
assert marker not in s
a=s.index('def xp_survey_business_results(')
b=s.index('\n@app.',a)
part=s[a:b]
needle='    return xp_survey_business_theme("Resultados · "+str(p["name"]),body,p)'
assert needle in part
part=part.replace(needle,'''    if slug=='pet-clinick':
        # Keep the circular white-background logo, without duplicated brand labels.
        body='<style>header{display:none!important}.xp-db-welcome{display:none!important}.xp-db-kicker,.xp-db-head h1,.xp-db-sub{display:none!important}.xp-db-head{margin-top:0!important}.xp-business-logo-badge{width:150px!important;height:150px!important;padding:17px!important;margin:16px auto 24px!important;border-radius:50%!important;background:white!important}.xp-business-logo-badge img{object-fit:contain!important}</style>'+body
    return xp_survey_business_theme("Resultados · "+str(p["name"]),body,p)''',1)
s=s[:a]+part+s[b:]
p.write_text(s+'\n'+marker+'\n',encoding='utf-8')
print('Pet Clinik dashboard: centered original logo, no repeated brand headings')
