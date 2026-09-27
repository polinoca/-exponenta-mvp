from pathlib import Path
import re

path=Path("/app/app/main.py")
text=path.read_text(encoding="utf-8")
pattern=r'def control_superadmin\(request,db\):\n(?:    .*\n)+?    return user\n'
replacement='''def control_superadmin(request, db):
    # Use the production authentication path used by every existing /admin route.
    return require_superadmin(request, db)
'''
text2,count=re.subn(pattern,replacement,text,count=1)
if count != 1:
    raise SystemExit("control_superadmin function not found")
path.write_text(text2,encoding="utf-8")
print("Control Center now uses the existing Superadmin authentication context")
