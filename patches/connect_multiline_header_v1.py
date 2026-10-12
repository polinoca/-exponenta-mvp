from pathlib import Path
import re

# Preserve intentional line breaks in public Connect profile.
public = Path("/app/app/templates/connect/profile.html")
s = public.read_text(encoding="utf-8")
if "/* xp-multiline-header-v1 */" not in s:
    s = s.replace("</style>", """/* xp-multiline-header-v1 */
    .xp-head h1,.xp-head p{white-space:pre-line;overflow-wrap:anywhere}
    .xp-head > div:last-child{min-width:0;flex:1}
    </style>""", 1)
    public.write_text(s, encoding="utf-8")

# Textareas allow Enter for title and subtitle in both admin and business editors.
for root in [Path("/app/app/templates/admin"), Path("/app/app/templates/business"), Path("/app/app/templates/negocio")]:
    if not root.exists():
        continue
    for p in root.rglob("*.html"):
        s = p.read_text(encoding="utf-8")
        if 'name="subtitle"' not in s or 'name="name"' not in s:
            continue
        orig = s
        for field in ("name", "subtitle"):
            pattern = r'<input\\b(?=[^>]*\\bname="' + field + r'")[^>]*>'
            def swap(m):
                tag = m.group(0)
                if 'type="hidden"' in tag:
                    return tag
                value = re.search(r'\\bvalue="([^"]*)"', tag)
                if not value:
                    return tag
                attrs = re.sub(r'\\s*value="[^"]*"', '', tag[6:-1])
                attrs = re.sub(r'\\s*type="text"', '', attrs)
                return '<textarea' + attrs + ' rows="2" style="width:100%;min-height:68px;resize:vertical;font:inherit;line-height:1.4;padding:12px" >' + value.group(1) + '</textarea>'
            s = re.sub(pattern, swap, s)
        if s != orig:
            p.write_text(s, encoding="utf-8")
            print("Multiline fields:", p)
print("Connect multiline header ready")
