from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
a=s.index('# EXPONENTA PRODUCT ACCESS PORTAL V1')
section=s[a:]
assert 'def xp_product_access_portal():' in section
section=section.replace('background:#f5f8fb;color:#17283c','background:#f7f4ef;color:#211c18')
section=section.replace('border-bottom:1px solid #e3eaf1','border-bottom:1px solid #e5dcd2')
section=section.replace('color:#17324d;font-weight:900','color:#8b5738;font-weight:900')
section=section.replace('color:#607386','color:#786c63')
section=section.replace('border:1px solid #dce6ef','border:1px solid #e5dcd2')
section=section.replace('border-color:#407bb4;outline:2px solid #b5d6f5','border-color:#a56d46;outline:2px solid #e4c4a6')
section=section.replace('color:#427bb0','color:#95603e')
section=section.replace('color:#5b7184','color:#756b63')
section=section.replace('color:#2d71b1','color:#8b5738')
section=section.replace('<header><a href="/">EXPONENTA</a></header>','<header><a href="/" style="display:inline-flex;align-items:center;gap:10px"><img src="/static/exponenta-logo.svg" alt="" style="width:125px;height:45px;object-fit:contain"></a></header>')
s=s[:a]+section
p.write_text(s,encoding="utf-8")
print("Access portal branded with Exponenta warm brown, cream and logo")
