from pathlib import Path

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SUPERADMIN ROLE NORMALIZATION V1"
if marker not in s:
    s += r'''

# XP SUPERADMIN ROLE NORMALIZATION V1
# Accept enum/value spellings such as SUPERADMIN, SUPER_ADMIN or super-admin,
# while keeping Connect and Control Center restricted to superadmin accounts.
def control_superadmin(request, db):
    uid = request.session.get("user_id") or request.session.get("uid")
    if not uid:
        raise HTTPException(401, "Inicia sesión")
    user = db.get(User, int(uid))
    raw_role = str(getattr(getattr(user, "role", None), "value", getattr(user, "role", ""))).lower() if user else ""
    normalized_role = raw_role.replace("_", "").replace("-", "").replace(" ", "")
    if "superadmin" not in normalized_role:
        raise HTTPException(403, "Acceso restringido")
    return user
'''
    p.write_text(s,encoding="utf-8")
print("Superadmin role normalization applied")
