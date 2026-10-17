from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK EXCEL SHARE CLARITY V2'

if marker not in s:
    old="}catch(err){if(err&&err.name==='AbortError')return;}link.click();},true);})();</script>"
    new="}catch(err){if(err&&err.name==='AbortError')return;}window.alert('Para compartir el Excel usa este botón desde tu celular. En computadora descarga el archivo y adjúntalo en WhatsApp o correo.');},true);})();</script>"
    if old not in s:
        raise SystemExit('Existing share handler not found')
    s=s.replace(old,new,1)
    a=s.index('def xp_survey_business_results(')
    b=s.index('\n@app.',a)
    part=s[a:b]
    if 'Compartir Excel' not in part:
        raise SystemExit('Share button label not found')
    part=part.replace('Compartir Excel','Compartir en celular',1)
    s=s[:a]+part+s[b:]
    p.write_text(s+'\n'+marker+'\n',encoding='utf-8')

print('PET Clinik share behavior now distinguishes mobile share from desktop download')
