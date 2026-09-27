from pathlib import Path

# Render the state color in the page itself so it is not affected by static CSS cache.
p=Path("/app/app/templates/admin/control_business.html")
s=p.read_text(encoding="utf-8")
marker="{% block body %}"
style='''{% block body %}<style>
.xp-feature-grid .xp-toggle.on{background:#16a34a !important;color:#fff !important;border:2px solid #15803d !important}
.xp-feature-grid .xp-toggle.off{background:#dc2626 !important;color:#fff !important;border:2px solid #b91c1c !important}
.xp-feature-grid .xp-toggle.on b,.xp-feature-grid .xp-toggle.off b{color:#fff !important}
.xp-feature-grid .xp-toggle.on i{background:#fff !important}
.xp-feature-grid .xp-toggle.off i{background:#fee2e2 !important}
</style>'''
if marker not in s: raise SystemExit("body block marker missing")
if "Render the state color" not in s:
    s=s.replace(marker,style,1)
p.write_text(s,encoding="utf-8")
print("Control Center uses high-contrast green and red toggle states")
