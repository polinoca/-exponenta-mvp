from pathlib import Path
import re

main = Path("/app/app/main.py")
s = main.read_text()

# Patch the shared destination sanitizer instead of one individual endpoint.
m = re.search(r'def safe_destination\([^\n]*\):\n(?P<body>(?:[ \t]+[^\n]*\n)+)', s)
if not m:
    raise SystemExit("safe_destination function not found")

block = m.group(0)
if "XP_CAMPAIGN_DESTINATION_NORMALIZER" not in block:
    lines = block.splitlines()
    indent = "    "
    inject = [
        lines[0],
        indent + "# XP_CAMPAIGN_DESTINATION_NORMALIZER",
        indent + "value = (value or '').strip()",
        indent + "if value and not value.startswith(('http://', 'https://')):",
        indent + "    value = 'https://' + value",
    ]
    # Preserve the original sanitizer logic after normalization, but avoid a duplicate
    # first strip assignment if present.
    rest = lines[1:]
    rest = [ln for ln in rest if not re.match(r'\s*value\s*=\s*\(value\s+or\s+[\'\"]{2}\)\.strip\(\)\s*$', ln)]
    new_block = "\n".join(inject + rest) + "\n"
    s = s[:m.start()] + new_block + s[m.end():]
    main.write_text(s)

tpl = Path("/app/app/templates/business/marketing.html")
if tpl.exists():
    t = tpl.read_text()
    if "xp-campaign-error" not in t:
        marker = "{% block body %}"
        alert = """{% if request.query_params.get("campaign_error") == "destination" %}
<div class="xp-campaign-error" role="alert">Agrega un destino válido. Puedes escribir una URL completa o, por ejemplo, <b>wa.me/...</b>; Exponenta agregará <b>https://</b> automáticamente.</div>
{% endif %}"""
        if marker in t:
            t = t.replace(marker, marker + "\n" + alert, 1)
            tpl.write_text(t)

print("shared destination URL normalizer applied")
