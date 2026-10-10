from pathlib import Path
p=Path("/app/app/templates/admin/control.html")
s=p.read_text(encoding="utf-8")
marker="XP SURVEY CONTROL LINK V1"
if marker not in s:
    # Preserve all current controls: add a link next to the existing business list, not replace it.
    block='''<!-- XP SURVEY CONTROL LINK V1 -->
<section style="margin:14px 0;padding:18px;background:#eaf8f6;border:1px solid #ccece8;border-radius:18px">
  <strong style="display:block;margin-bottom:6px;font-size:1rem">Encuestas de satisfacción</strong>
  <p style="margin:0 0 12px;font-size:.84rem">Pet Clinick y futuras encuestas, desde el mismo Superadmin. Independientes de Wallet.</p>
  <a href="/admin/encuestas" style="display:inline-block;background:#116969;color:white;text-decoration:none;padding:11px 17px;border-radius:12px;font-size:.88rem;font-weight:750">Administrar encuestas →</a>
</section>
'''
    first=s.find('{% block body %}')
    if first<0: first=s.find('{% block content %}')
    if first>=0:
        first=s.find('\n',first)+1
        s=s[:first]+block+s[first:]
    else:
        raise SystemExit("Unable to place survey link in admin control template")
    p.write_text(s,encoding="utf-8")
print("Unified Superadmin surveys entry installed")
