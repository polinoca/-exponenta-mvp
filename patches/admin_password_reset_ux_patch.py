from pathlib import Path

main=Path("/app/app/main.py")
s=main.read_text(encoding="utf-8")
context_from='b=get_billing(db,org);states=feature_states(db,org.id)'
context_to='b=get_billing(db,org);states=feature_states(db,org.id);organization_users=db.scalars(select(User).where(User.organization_id==org.id).order_by(User.email)).all();password_error=request.query_params.get("password_error","")'
if context_from in s and "organization_users=db.scalars" not in s:
    s=s.replace(context_from,context_to,1)
render_from='"plan_templates":PLAN_TEMPLATES})'
render_to='"plan_templates":PLAN_TEMPLATES,"organization_users":organization_users,"password_error":password_error})'
if render_from in s and '"organization_users":organization_users' not in s:
    s=s.replace(render_from,render_to,1)
errors_from='''    if not org or not target:
        raise HTTPException(404, "Usuario no encontrado")
    if len(temporary_password) < 10:
        raise HTTPException(422, "La contraseña temporal debe tener al menos 10 caracteres.")
    if temporary_password != password_confirmation:
        raise HTTPException(422, "Las contraseñas no coinciden.")'''
errors_to='''    if not org or not target:
        return RedirectResponse(f"/admin/control/{org_id}?password_error=user", status_code=303)
    if len(temporary_password) < 10:
        return RedirectResponse(f"/admin/control/{org_id}?password_error=length", status_code=303)
    if temporary_password != password_confirmation:
        return RedirectResponse(f"/admin/control/{org_id}?password_error=mismatch", status_code=303)'''
if errors_from in s:
    s=s.replace(errors_from,errors_to,1)
main.write_text(s,encoding="utf-8")

template=Path("/app/app/templates/admin/control_business.html")
t=template.read_text(encoding="utf-8")
old='<label>Correo del usuario<input type="email" name="target_email" autocomplete="email" required></label>'
new='<label>Usuario de esta cuenta<select name="target_email" required><option value="">Selecciona un usuario</option>{% for account in organization_users %}<option value="{{ account.email }}">{{ account.email }}</option>{% endfor %}</select></label>'
if old in t:
    t=t.replace(old,new,1)
needle='  <form method="post" action="/admin/control/{{ organization.id }}/usuario/restablecer-contrasena">'
alerts='''  {% if password_error == "user" %}<div class="xp-auth-message warning">Selecciona un usuario válido de esta cuenta.</div>{% endif %}
  {% if password_error == "length" %}<div class="xp-auth-message warning">La contraseña temporal debe tener al menos 10 caracteres.</div>{% endif %}
  {% if password_error == "mismatch" %}<div class="xp-auth-message warning">Las contraseñas no coinciden. Revisa ambos campos.</div>{% endif %}
'''
if needle in t and 'password_error == "mismatch"' not in t:
    t=t.replace(needle,alerts+needle,1)
if 'id="admin-password-reset-form"' not in t:
    t=t.replace('<form method="post" action="/admin/control/{{ organization.id }}/usuario/restablecer-contrasena">','<form id="admin-password-reset-form" method="post" action="/admin/control/{{ organization.id }}/usuario/restablecer-contrasena">',1)
    t=t.replace('name="temporary_password" minlength="10"','id="temporary-password" name="temporary_password" minlength="10"',1)
    t=t.replace('name="password_confirmation" minlength="10"','id="password-confirmation" name="password_confirmation" minlength="10"',1)
    t=t.replace('<button class="btn btn-primary" type="submit">Guardar contraseña temporal</button>','<small id="password-match-note" aria-live="polite"></small><button class="btn btn-primary" type="submit">Guardar contraseña temporal</button><script>(()=>{const f=document.getElementById("admin-password-reset-form"),a=document.getElementById("temporary-password"),b=document.getElementById("password-confirmation"),n=document.getElementById("password-match-note");if(!f||!a||!b)return;const c=()=>{const bad=!!b.value&&a.value!==b.value;b.setCustomValidity(bad?"Las contraseñas no coinciden.":"");n.textContent=bad?"Las contraseñas no coinciden.":" ";};a.oninput=c;b.oninput=c;f.onsubmit=c;})();</script>',1)
template.write_text(t,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "ADMIN PASSWORD RESET UX V2" not in c:
 c+='\n/* ADMIN PASSWORD RESET UX V2 */\n.xp-admin-password small{min-height:16px;font-size:.64rem;color:#b42318;font-weight:800}.xp-admin-password select{min-height:43px;padding:0 11px;border:1px solid #d9cec5;border-radius:11px;background:#fff;font:inherit}\n'
css.write_text(c,encoding="utf-8")
print("Password reset UX patch applied safely")
