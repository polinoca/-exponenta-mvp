from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
tag="# PRINTED QR REASSIGNMENT ANA BARAJAS"
if tag not in s:
    anchor='@app.get("/connect/{slug}", response_class=HTMLResponse)'
    if anchor not in s: raise SystemExit("Connect public route not found")
    # Place redirect BEFORE the dynamic route, preserving the printed QR.
    code='''# PRINTED QR REASSIGNMENT ANA BARAJAS
@app.get("/connect/armonia-para-tus-pies", include_in_schema=False)
def printed_ana_barajas_qr_redirect():
    # The printed QR contains the old Armonia slug; Ana's banner is already printed.
    # Preserve the old URL, but direct it to Ana's existing profile.
    return RedirectResponse(url="/connect/ana-barajas", status_code=302)

'''
    s=s.replace(anchor,code+anchor,1)
    p.write_text(s,encoding="utf-8")
print("Printed Ana Barajas QR now redirects to her profile")
