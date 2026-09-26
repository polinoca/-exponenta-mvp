from pathlib import Path

p=Path("/app/app/main.py");s=p.read_text()
if "EXPONENTA ENTITLEMENT UI V1" not in s:
 anchor='@app.get("/negocio/wallet",response_class=HTMLResponse)'
 if anchor not in s: raise SystemExit("wallet route anchor missing")
 route=r'''# EXPONENTA ENTITLEMENT UI V1
@app.get("/api/negocio/features")
def business_feature_status(request:Request,db:Session=Depends(get_db)):
 user,org=business_admin_context(request,db)
 states=feature_states(db,org.id)
 return {"features":states}

'''
 s=s.replace(anchor,route+anchor,1)
 p.write_text(s)

js=Path("/app/app/static/feature-ui.js")
js.write_text(r'''(() => {
  if (!location.pathname.startsWith("/negocio")) return;
  const map = {
    "/negocio/lealtad": "loyalty",
    "/negocio/seguridad": "staff",
    "/negocio/marketing": "reviews",
    "/negocio/wallet": "wallet"
  };
  fetch("/api/negocio/features", {credentials:"same-origin"})
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      if (!data || !data.features) return;
      document.querySelectorAll("a[href]").forEach(a => {
        const href = a.getAttribute("href") || "";
        const entry = Object.entries(map).find(([prefix]) => href === prefix || href.startsWith(prefix + "/"));
        if (entry && data.features[entry[1]] === false) a.remove();
      });
    }).catch(() => {});
})();
''')

b=Path("/app/app/templates/base.html");t=b.read_text()
if "/static/feature-ui.js" not in t:
 marker="</body>"
 if marker not in t: raise SystemExit("base body close missing")
 t=t.replace(marker,'<script src="/static/feature-ui.js?v=20260926-1" defer></script>\n'+marker,1)
 b.write_text(t)
print("Entitlement UI V1 installed")
