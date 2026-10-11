from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# EXPONENTA BUSINESS PRODUCT ROUTE GUARD V1"
if marker not in s:
    start=s.find("def business_admin_context(")
    assert start>=0,"business_admin_context missing"
    end=s.find("\ndef ",start+4)
    assert end>start,"context function boundary missing"
    sec=s[start:end]
    import re
    matches=list(re.finditer(r"(?m)^([ \t]+)return user,\s*org[ \t]*$",sec))
    assert len(matches)==1,"Expected one business context return"
    guard='''    # Enforce product access on the server, not just in the navigation.
    path=request.url.path.rstrip("/")
    if path=="/panel" or (path.startswith("/negocio") and not path.startswith("/negocio/encuestas")):
        key="connect" if path.startswith("/negocio/connect") else "wallet"
        require_org_feature(db,org,key)
'''
    m=matches[0]
    indent=m.group(1)
    import textwrap
    guard="\n".join(indent+line if line else "" for line in textwrap.dedent(guard).strip().splitlines())+"\n"
    sec=sec[:m.start()]+guard+sec[m.start():]
    s=s[:start]+sec+s[end:]
    p.write_text(s+"\n"+marker+"\n",encoding="utf-8")
print("Server-side business access guard enabled for wallet and connect paths")
