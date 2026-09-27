from pathlib import Path

main=Path("/app/app/main.py")
s=main.read_text(encoding="utf-8")
old='''return render(request,"admin/control_business.html",{"user":user,"organization":org,"billing":b,"feature_catalog":FEATURE_CATALOG,"feature_states":states,"plan_templates":PLAN_TEMPLATES})'''
new='''organization_users = db.scalars(select(User).where(User.organization_id == org.id).order_by(User.email)).all()
    password_error = request.query_params.get("password_error", "")
    return render(request,"admin/control_business.html",{"user":user,"organization":org,"billing":b,"feature_catalog":FEATURE_CATALOG,"feature_states":states,"plan_templates":PLAN_TEMPLATES,"organization_users":organization_users,"password_error":password_error})'''
if old not in s: raise SystemExit("control business context anchor missing")
s=s.replace(old,new,1)

s=s.replace('''    if not org or not target:
        raise HTTPException(404, "Usuario no encontrado")
    if len(temporary_password) < 10:
        raise HTTPException(422, "La contraseña temporal debe tener al menos 10 caracteres.")
    if temporary_password != password_confirmation:
        raise HTTPException(422, "Las contraseñas no coinciden.")''','''    if not org or not target:
        return RedirectResponse(f"/admin/control/{org_id}?password_error=user", status_code=303)
    if len(temporary_password) < 10:
        return RedirectResponse(f"/admin/control/{org_id}?password_error=length", status_code=303)
    if temporary_password != password_confirmation:
        return RedirectResponse(f"/admin/control/{org_id}?password_error=mismatch", status_code=303)''',1)
main.write_text(s,encoding="utf-8")

t=Path("/app/app/templates/admin/control_business.html")
s=t.read_text(encoding="utf-8")
old='''  {% if password_reset_message %}<div class="xp-auth-message success">Contraseña temporal actualizada. Compártela de forma segura y pide que la cambie al ingresar.</div>{% endif %}
  <form method="post" action="/admin/control/{{ organization.id }}/usuario/restablecer-contrasena">
    <input type="hidden" name="csrf_token" value="{{ csrf }}">
    <label>Correo del usuario<input type="email" name="target_email" autocomplete="email" required></label>
    <label>Contraseña temporal<input type="password" name="temporary_password" minlength="10" autocomplete="new-password" required></label>
    <label>Confirmar contraseña temporal<input type="password" name="password_confirmation" minlength="10" autocomplete="new-password" required></label>
    <button class="btn btn-primary" type="submit">Guardar contraseña temporal</button>
  </form>'''
new='''  {% if password_reset_message %}<div class="xp-auth-message success">Contraseña temporal actualizada. Compártela de forma segura y pide que la cambie al ingresar.</div>{% endif %}
  {% if password_error == "user" %}<div class="xp-auth-message warning">Selecciona un usuario válido de esta cuenta.</div>{% endif %}
  {% if password_error == "length" %}<div class="xp-auth-message warning">La contraseña temporal debe tener al menos 10 caracteres.</div>{% endif %}
  {% if password_error == "mismatch" %}<div class="xp-auth-message warning">Las contraseñas no coinciden. Revisa ambos campos.</div>{% endif %}
  <form id="admin-password-reset-form" method="post" action="/admin/control/{{ organization.id }}/usuario/restablecer-contrasena">
    <input type="hidden" name="csrf_token" value="{{ csrf }}">
    <label>Usuario de esta cuenta<select name="target_email" required><option value="">Selecciona un usuario</option>{% for account in organization_users %}<option value="{{ account.email }}">{{ account.email }}</option>{% endfor %}</select></label>
    <label>Contraseña temporal<input id="temporary-password" type="password" name="temporary_password" minlength="10" autocomplete="new-password" required></label>
    <label>Confirmar contraseña temporal<input id="password-confirmation" type="password" name="password_confirmation" minlength="10" autocomplete="new-password" required><small id="password-match-note" aria-live="polite"></small></label>
    <button class="btn btn-primary" type="submit">Guardar contraseña temporal</button>
  </form>
  <script>
  (()=>{const form=document.getElementById("admin-password-reset-form"),a=document.getElementById("temporary-password"),b=document.getElementById("password-confirmation"),note=document.getElementById("password-match-note");if(!form||!a||!b)return;const check=()=>{const bad=!!b.value&&a.value!==b.value;b.setCustomValidity(bad?"Las contraseñas no coinciden.":"");note.textContent=bad?"Las contraseñas no coinciden.":" ";note.className=bad?"is-error":"";};a.addEventListener("input",check);b.addEventListener("input",check);form.addEventListener("submit",check);})();
  </script>'''
if old not in s: raise SystemExit("password form anchor missing")
t.write_text(s.replace(old,new,1),encoding="utf-8")

css=Path("/app/app/static/app.css")
s=css.read_text(encoding="utf-8")
if "ADMIN PASSWORD RESET UX V2" not in s:
 s+='''\n/* ADMIN PASSWORD RESET UX V2 */\n.xp-admin-password small{min-height:16px;font-size:.64rem;color:#b42318}.xp-admin-password small.is-error{font-weight:800}.xp-admin-password select{min-height:43px;padding:0 11px;border:1px solid #d9cec5;border-radius:11px;background:#fff;font:inherit}\n'''
css.write_text(s,encoding="utf-8")
print("Password reset now uses account user selection and inline mismatch validation")
