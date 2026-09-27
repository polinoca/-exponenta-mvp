from pathlib import Path

path = Path("/app/app/main.py")
text = path.read_text(encoding="utf-8")
old = '        and request.session.get("user_id")\n'
new = '        and (request.scope.get("session") or {}).get("user_id")\n'
if old not in text:
    raise SystemExit("QR/NFC session middleware anchor not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("QR/NFC middleware now tolerates routes before session middleware")
