from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text()
needle="from app.models import BillingAccount"
if needle not in s:
 lines=s.splitlines()
 pos=0
 for i,line in enumerate(lines):
  if line.startswith("from __future__ import"):
   pos=i+1
 lines.insert(pos,needle)
 s="\n".join(lines)+"\n"
 p.write_text(s)
print("BillingAccount runtime import repaired")
