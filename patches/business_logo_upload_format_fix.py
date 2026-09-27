from pathlib import Path
import re

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
pattern=r'    allowed = \{.*?    org\.logo_mime = logo_file\.content_type'
replacement='''    content = await logo_file.read()
    if not content or len(content) > 2 * 1024 * 1024:
        return RedirectResponse("/negocio/configuracion?logo_error=size", status_code=303)
    probe = content[:2048].lstrip().lower()
    detected = "image/png" if content.startswith(bytes([137,80,78,71,13,10,26,10])) else "image/jpeg" if content.startswith(bytes([255,216,255])) else "image/webp" if content[:4] == b"RIFF" and content[8:12] == b"WEBP" else "image/svg+xml" if b"<svg" in probe else ""
    if not detected:
        return RedirectResponse("/negocio/configuracion?logo_error=format", status_code=303)
    org.logo_blob = content
    org.logo_mime = detected'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n==0: print("Logo handler already updated or route not found")
p.write_text(s,encoding="utf-8")

t=Path("/app/app/templates/business/settings.html")
html=t.read_text(encoding="utf-8")
needle='<form class="xp-logo-upload" method="post" action="/negocio/configuracion/logo" enctype="multipart/form-data">'
notice='{% if request.query_params.get("logo_error") == "format" %}<div class="xp-auth-message warning">Ese archivo no es una imagen compatible. Usa PNG, JPG, WebP o SVG.</div>{% endif %}{% if request.query_params.get("logo_error") == "size" %}<div class="xp-auth-message warning">El logotipo debe pesar menos de 2 MB.</div>{% endif %}'
if needle in html and "logo_error" not in html: html=html.replace(needle,notice+needle,1)
html=html.replace('accept="image/png,image/jpeg,image/webp"','accept="image/png,image/jpeg,image/webp,image/svg+xml,.svg"',1).replace('PNG, JPG o WebP · máximo 2 MB','PNG, JPG, WebP o SVG · máximo 2 MB',1)
t.write_text(html,encoding="utf-8")
print("Logo upload format support applied")
