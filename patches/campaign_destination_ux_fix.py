from pathlib import Path
import re

main = Path("/app/app/main.py")
s = main.read_text()

message = 'El destino debe ser una URL http/https válida'
patterns = [
    r'(?P<i> {4,})if not (?P<v>[A-Za-z_]\\w*)\\.startswith\\(\\("http://", "https://"\\)\\):\\n(?P=i)    raise HTTPException\\(422, "El destino debe ser una URL http/https válida"\\)',
    r'(?P<i> {4,})if not \\((?P<v>[A-Za-z_]\\w*)\\.startswith\\("http://"\\) or (?P=v)\\.startswith\\("https://"\\)\\):\\n(?P=i)    raise HTTPException\\(422, "El destino debe ser una URL http/https válida"\\)',
]
count = 0
for pattern in patterns:
    def repl(m):
        i, v = m.group("i"), m.group("v")
        return (
            f"{i}{v} = ({v} or '').strip()\\n"
            f"{i}if {v} and not {v}.startswith(('http://', 'https://')):\\n"
            f"{i}    {v} = 'https://' + {v}\\n"
            f"{i}if not {v}:\\n"
            f"{i}    return RedirectResponse('/negocio/marketing?campaign_error=destination', status_code=303)"
        )
    s, n = re.subn(pattern, repl, s, count=1)
    count += n
    if n:
        break

if not count:
    raise SystemExit("campaign destination validation not found")

main.write_text(s)

tpl = Path("/app/app/templates/business/marketing.html")
if tpl.exists():
    t = tpl.read_text()
    if "xp-campaign-error" not in t:
        marker = "{% block body %}"
        alert = '''{% if request.query_params.get("campaign_error") == "destination" %}
<div class="xp-campaign-error" role="alert">Agrega un destino para la campaña. Puede ser una página web, un enlace de WhatsApp o Google; si escribes <b>wa.me/...</b> o <b>google.com/...</b>, Exponenta agregará <b>https://</b> automáticamente.</div>
{% endif %}'''
        if marker in t:
            t = t.replace(marker, marker + "\\n" + alert, 1)
            tpl.write_text(t)

css = Path("/app/app/static/app.css")
c = css.read_text()
if ".xp-campaign-error" not in c:
    c += "\\n.xp-campaign-error{width:min(1180px,calc(100% - 28px));margin:16px auto;padding:13px 15px;border:1px solid #efc0b8;border-radius:14px;background:#fff2ef;color:#8c2f20;font-size:.78rem;line-height:1.45}.xp-campaign-error b{color:#6f2218}\\n"
    css.write_text(c)

print("campaign destination UX fixed")
