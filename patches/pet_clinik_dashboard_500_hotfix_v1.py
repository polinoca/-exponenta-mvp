from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK DASHBOARD 500 HOTFIX V1'
if marker not in s:
    s=s.replace("body=style.replace('</style>',mobile_css+'</style>')+welcome+", "body=style+welcome+")
    p.write_text(s+'\n'+marker+'\n',encoding='utf-8')
print('Pet Clinik dashboard NameError hotfix applied')
