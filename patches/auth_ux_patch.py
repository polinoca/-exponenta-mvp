from pathlib import Path

main = Path("/app/app/main.py")
s = main.read_text(encoding="utf-8")
if '@app.post("/logout")' not in s:
    marker='@app.get("/login"'
    if marker not in s:
        raise SystemExit("login route anchor missing")
    logout=r'''@app.post("/logout")
def logout(request: Request):
    response=RedirectResponse("/login",status_code=303)
    response.delete_cookie(settings.session_cookie,path="/")
    return response

'''
    s=s.replace(marker,logout+marker,1)
main.write_text(s,encoding="utf-8")

base=Path("/app/app/templates/base.html")
b=base.read_text(encoding="utf-8")
old='<a class="xp-app-site-link" href="/">Ver sitio</a>'
new='''<div class="xp-app-actions"><a class="xp-app-site-link" href="/">Ver sitio</a><form method="post" action="/logout"><button class="xp-app-logout" type="submit">Cerrar sesión</button></form></div>'''
if old not in b:
    raise SystemExit("topbar action anchor missing")
base.write_text(b.replace(old,new,1),encoding="utf-8")

login=Path("/app/app/templates/login.html")
t=login.read_text(encoding="utf-8")
if "EXPONENTA LOGIN UX V1" not in t:
    marker="{% endblock %}"
    i=t.rfind(marker)
    if i<0:
        raise SystemExit("login template endblock anchor missing")
    ux=r'''
<script>
document.addEventListener("DOMContentLoaded",function(){
  const form=document.querySelector('form[action="/login"]')||document.querySelector("form");
  if(!form)return;
  const email=form.querySelector('input[type="email"],input[name="email"]');
  const password=form.querySelector('input[type="password"],input[name="password"]');
  if(!email||!password)return;
  const storageKey="exponenta.remembered_email";
  const remembered=localStorage.getItem(storageKey);
  const row=document.createElement("label");
  row.className="xp-remember-row";
  row.innerHTML='<input type="checkbox" class="xp-remember-check"> <span>Recordar mi correo en este dispositivo</span>';
  const check=row.querySelector("input");
  if(remembered&&!email.value){email.value=remembered;check.checked=true;}
  const passwordWrap=document.createElement("div");
  passwordWrap.className="xp-password-wrap";
  password.parentNode.insertBefore(passwordWrap,password);
  passwordWrap.appendChild(password);
  const toggle=document.createElement("button");
  toggle.type="button";toggle.className="xp-password-toggle";toggle.textContent="Mostrar";
  toggle.addEventListener("click",function(){
    const visible=password.type==="text";
    password.type=visible?"password":"text";
    toggle.textContent=visible?"Mostrar":"Ocultar";
    toggle.setAttribute("aria-pressed",String(!visible));
  });
  passwordWrap.appendChild(toggle);
  passwordWrap.insertAdjacentElement("afterend",row);
  form.addEventListener("submit",function(){
    if(check.checked&&email.value.trim())localStorage.setItem(storageKey,email.value.trim());
    else localStorage.removeItem(storageKey);
  });
});
</script>
<!-- EXPONENTA LOGIN UX V1 -->'''
    t=t[:i]+ux+t[i:]
login.write_text(t,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "EXPONENTA AUTH UX V1" not in c:
    c+=r'''
/* EXPONENTA AUTH UX V1 */
.xp-app-actions{margin-left:auto;display:flex;align-items:center;gap:8px}.xp-app-actions form{margin:0}.xp-app-logout{min-height:38px;padding:0 14px;border:1px solid #d9c7ba;border-radius:999px;background:#fff8f5;color:#743b25;font-size:.72rem;font-weight:850;cursor:pointer}.xp-app-logout:hover{background:#fff0eb}.xp-password-wrap{position:relative}.xp-password-wrap input{padding-right:84px!important}.xp-password-toggle{position:absolute;right:7px;top:50%;transform:translateY(-50%);min-height:32px;border:0;border-radius:9px;background:#f1ebe5;color:#653b25;padding:0 10px;font-size:.68rem;font-weight:850;cursor:pointer}.xp-remember-row{display:flex!important;align-items:center;gap:8px;margin-top:2px;font-size:.72rem!important;font-weight:750!important;color:#5d564f!important;cursor:pointer}.xp-remember-row input{width:17px!important;min-height:auto!important;height:17px!important;margin:0!important;accent-color:#8d502c}@media(max-width:720px){.xp-app-actions{gap:6px}.xp-app-site-link,.xp-app-logout{min-height:36px;padding:0 11px;font-size:.68rem}}
'''
css.write_text(c,encoding="utf-8")
print("Logout and login usability controls installed")
