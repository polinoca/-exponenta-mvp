from pathlib import Path
import re

main = Path("/app/app/main.py")
s = main.read_text()

message = "El destino debe ser una URL http/https válida"
pattern = re.compile(
    r'(?P<i>[ \t]+)if not (?P<expr>[^\n]+):\n(?P=i)[ \t]+raise HTTPException\(422, ["\']El destino debe ser una URL http/https válida["\']\)'
)
m = pattern.search(s)
if not m:
    raise SystemExit("campaign destination validation not found")

indent = m.group("i")
expr = m.group("expr")
var_match = re.search(r'([A-Za-z_]\w*)\.startswith', expr)
if not var_match:
    raise SystemExit("campaign destination variable not found")
v = var_match.group(1)

replacement = (
    f"{indent}{v} = ({v} or '').strip()\n"
    f"{indent}if {v} and not {v}.startswith(('http://', 'https://')):\n"
    f"{indent}    {v} = 'https://' + {v}\n"
    f"{indent}if not {v}:\n"
    f"{indent}    return RedirectResponse('/negocio/marketing?campaign_error=destination', status_code=303)"
)
s = s[:m.start()] + replacement + s[m.end():]
main.write_text(s)

tpl = Path("/app/app/templates/business/marketing.html")
if tpl.exists():
    t = tpl.read_text()
    if "xp-campaign-error" not in t:
        marker = "{% block body %}"
        alert = """{% if request.query_params.get("campaign_error") == "destination" %}
<div class="xp-campaign-error" role="alert">Agrega un destino para la campaña. Puede ser una página web, un enlace de WhatsApp o Google; si escribes <b>wa.me/...</b> o <b>google.com/...</b>, Exponenta agregará <b>https://</b> automáticamente.</div>
{% endif %}"""
        if marker in t:
            t = t.replace(marker, marker + "\n" + alert, 1)
            tpl.write_text(t)

css = Path("/app/app/static/app.css")
c = css.read_text()
if ".xp-campaign-error" not in c:
    c += "\n.xp-campaign-error{width:min(1180px,calc(100% - 28px));margin:16px auto;padding:13px 15px;border:1px solid #efc0b8;border-radius:14px;background:#fff2ef;color:#8c2f20;font-size:.78rem;line-height:1.45}.xp-campaign-error b{color:#6f2218}\n"
    css.write_text(c)

print("campaign destination UX fixed")
