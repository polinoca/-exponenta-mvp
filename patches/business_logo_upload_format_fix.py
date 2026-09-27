from pathlib import Path

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
old='''    allowed = {"image/png", "image/jpeg", "image/webp"}
    if logo_file.content_type not in allowed:
        raise HTTPException(422, "Usa una imagen PNG, JPG o WebP")
    content = await logo_file.read()
    if not content or len(content) > 2 * 1024 * 1024:
        raise HTTPException(422, "El logotipo debe pesar menos de 2 MB")
    signatures_ok = (
        (logo_file.content_type == "image/png" and content.startswith(b"\\x89PNG\\r\\n\\x1a\\n"))
        or (logo_file.content_type == "image/jpeg" and content.startswith(b"\\xff\\xd8\\xff"))
        or (logo_file.content_type == "image/webp" and content[:4] == b"RIFF" and content[8:12] == b"WEBP")
    )
    if not signatures_ok:
        raise HTTPException(422, "El archivo no parece una imagen válida")
    org.logo_blob = content
    org.logo_mime = logo_file.content_type'''
new='''    content = await logo_file.read()
    if not content or len(content) > 2 * 1024 * 1024:
        return RedirectResponse("/negocio/configuracion?logo_error=size", status_code=303)
    probe = content[:2048].lstrip().lower()
    detected = (
        "image/png" if content.startswith(b"\\x89PNG\\r\\n\\x1a\\n") else
        "image/jpeg" if content.startswith(b"\\xff\\xd8\\xff") else
        "image/webp" if content[:4] == b"RIFF" and content[8:12] == b"WEBP" else
        "image/svg+xml" if b"<svg" in probe else ""
    )
    if not detected:
        return RedirectResponse("/negocio/configuracion?logo_error=format", status_code=303)
    org.logo_blob = content
    org.logo_mime = detected'''
if old not in s: raise SystemExit("logo validation anchor missing")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")

t=Path("/app/app/templates/business/settings.html")
s=t.read_text(encoding="utf-8")
needle='<form class="xp-logo-upload" method="post" action="/negocio/configuracion/logo" enctype="multipart/form-data">'
notice='''{% if request.query_params.get("logo_error") == "format" %}<div class="xp-auth-message warning">Ese archivo no es una imagen compatible. Usa PNG, JPG, WebP o SVG.</div>{% endif %}
{% if request.query_params.get("logo_error") == "size" %}<div class="xp-auth-message warning">El logotipo debe pesar menos de 2 MB.</div>{% endif %}
'''
if needle in s and 'logo_error") == "format"' not in s:
 s=s.replace(needle,notice+needle,1)
s=s.replace('accept="image/png,image/jpeg,image/webp"','accept="image/png,image/jpeg,image/webp,image/svg+xml,.svg"',1)
s=s.replace('PNG, JPG o WebP · máximo 2 MB','PNG, JPG, WebP o SVG · máximo 2 MB',1)
t.write_text(s,encoding="utf-8")
print("Business logo upload detects PNG, JPG, WebP and SVG with friendly feedback")
