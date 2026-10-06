from pathlib import Path

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SUPERADMIN ROLE NORMALIZATION V2"
if marker not in s:
    start=s.rfind("def control_superadmin(")
    if start < 0:
        raise SystemExit("control_superadmin not found")
    end=s.find("\n\n", start)
    if end < 0:
        raise SystemExit("control_superadmin end not found")
    replacement='''def control_superadmin(request, db):
    # Reuse the established production auth path so SessionMiddleware order is preserved.
    return require_superadmin(request, db)
'''
    s=s[:start]+replacement+s[end:]
    s+="\n"+marker+"\n"
    p.write_text(s,encoding="utf-8")
print("Superadmin auth restored to production helper")
