from pathlib import Path

p = Path("/app/app/main.py")
s = p.read_text()

if "import time\n" not in s:
    marker = "from __future__ import annotations\n"
    if marker in s:
        s = s.replace(marker, marker + "import time\n", 1)
    else:
        s = "import time\n" + s

old_url = 'org.logo_url = f"{settings.app_base_url.rstrip(\'/\')}/media/organization/{org.slug}/logo"'
new_url = 'org.logo_url = f"{settings.app_base_url.rstrip(\'/\')}/media/organization/{org.slug}/logo?v={time.time_ns()}"'
if old_url not in s:
    raise SystemExit("logo URL assignment not found")
s = s.replace(old_url, new_url, 1)

old_cache = 'headers={"Cache-Control": "public, max-age=3600", "X-Content-Type-Options": "nosniff"}'
new_cache = 'headers={"Cache-Control": "no-store, max-age=0", "X-Content-Type-Options": "nosniff"}'
if old_cache not in s:
    raise SystemExit("logo cache header not found")
s = s.replace(old_cache, new_cache, 1)

p.write_text(s)
print("business logo cache bust applied")
