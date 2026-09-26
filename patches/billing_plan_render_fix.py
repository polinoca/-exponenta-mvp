from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()
old='"test_billing":test_billing and allowed_checkout,"csrf":csrf_value'
new='"test_billing":test_billing and allowed_checkout,"csrf":""'
if old not in s:
    raise SystemExit("billing plan csrf render anchor missing")
s=s.replace(old,new,1)
p.write_text(s)
print("Removed stale csrf_value reference from business plan render")
