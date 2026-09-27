from pathlib import Path

main=Path("/app/app/main.py")
s=main.read_text(encoding="utf-8")
if "EXPONENTA ADMIN PASSWORD RESET V1" not in s:
    anchor='''@app.post("/admin/control/{org_id}/feature/{feature_key}")'''
    if anchor not in s:
        raise SystemExit("Control password route anchor missing")
    route=r'''# EXPONENTA ADMIN PASSWORD RESET V1
@app.post("/admin/control/{org_id}/usuario/restablecer-contrasena")
def admin_reset_business_password(
    org_id: int,
    request: Request,
    target_email: str = Form(""),
    temporary_password: str = Form(""),
    password_confirmation: str = Form(""),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    control_superadmin(request, db)
    verify_csrf(request, csrf_token)
    org = db.get(Organization, org_id)
    target = db.scalar(select(User).where(User.organization_id == org_id, User.email == target_email.strip().lower()))
    if not org or not target:
        raise HTTPException(404, "Usuario no encontrado")
    if len(temporary_password) < 10:
        raise HTTPException(422, "La contraseña temporal debe tener al menos 10 caracteres.")
    if temporary_password != password_confirmation:
        raise HTTPException(422, "Las contraseñas no coinciden.")
    setattr(target, _PASSWORD_RESET_PASSWORD_FIELD, _PASSWORD_RESET_HASHER.hash(temporary_password))
    db.add(target)
    db.commit()
    return RedirectResponse(f"/admin/control/{org_id}?password_reset=1", status_code=303)

'''
    s=s.replace(anchor,route+anchor,1)
main.write_text(s,encoding="utf-8")

template=Path("/app/app/templates/admin/control_business.html")
t=template.read_text(encoding="utf-8")
if "ADMIN PASSWORD RESET V1" not in t:
    anchor='<section class="xp-feature-control">'
    if anchor not in t:
        raise SystemExit("Control business password form anchor missing")
    block=r'''<!-- EXPONENTA ADMIN PASSWORD RESET V1 -->
<section class="xp-admin-password">
  <span class="eyebrow">RECUPERAR ACCESO</span>
  <h2>Restablecer contraseña de un usuario.</h2>
  <p>La contraseña anterior no se muestra ni se conserva. Crea una temporal y compártela sólo después de verificar al dueño del negocio.</p>
  {% if password_reset_message %}<div class="xp-auth-message success">Contraseña temporal actualizada. Compártela de forma segura y pide que la cambie al ingresar.</div>{% endif %}
  <form method="post" action="/admin/control/{{ organization.id }}/usuario/restablecer-contrasena">
    <input type="hidden" name="csrf_token" value="{{ csrf }}">
    <label>Correo del usuario<input type="email" name="target_email" autocomplete="email" required></label>
    <label>Contraseña temporal<input type="password" name="temporary_password" minlength="10" autocomplete="new-password" required></label>
    <label>Confirmar contraseña temporal<input type="password" name="password_confirmation" minlength="10" autocomplete="new-password" required></label>
    <button class="btn btn-primary" type="submit">Guardar contraseña temporal</button>
  </form>

</section>
'''
    t=t.replace(anchor,block+anchor,1)
template.write_text(t,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "EXPONENTA ADMIN PASSWORD RESET V1" not in c:
    c+=r'''
/* EXPONENTA ADMIN PASSWORD RESET V1 */
.xp-admin-password{background:#fff;border:1px solid #e2d7cd;border-radius:22px;padding:20px;margin-top:14px}.xp-admin-password>p{max-width:680px;color:#70655e;line-height:1.5}.xp-admin-password form{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px}.xp-admin-password label{display:grid;gap:6px;font-size:.66rem;font-weight:850;color:#594d45}.xp-admin-password input,.xp-admin-password select{min-height:43px;padding:0 11px;border:1px solid #d9cec5;border-radius:11px;background:#fff;font:inherit}@media(max-width:720px){.xp-admin-password form{grid-template-columns:1fr}}
'''
css.write_text(c,encoding="utf-8")
print("Exponenta admin password reset installed")
