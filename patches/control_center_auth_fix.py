from pathlib import Path

path=Path("/app/app/main.py")
text=path.read_text(encoding="utf-8")
start=text.find("def control_superadmin(")
if start < 0:
    raise SystemExit("control_superadmin function not found")
end=text.find("\n\ndef ", start + 1)
if end < 0:
    raise SystemExit("control_superadmin function end not found")
replacement='''def control_superadmin(request, db):
    # Use the production authentication path used by every existing /admin route.
    return require_superadmin(request, db)
'''
text=text[:start]+replacement+text[end:]
path.write_text(text,encoding="utf-8")
print("Control Center now uses the existing Superadmin authentication context")
