from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SELECTOR SESSION 500 HOTFIX V1"
assert marker not in s
start=s.index("def xp_product_access_portal(")
end=s.index("\n@app.",start)
sec=s[start:end]
old='    uid=request.session.get("user_id") or request.session.get("uid")'
assert old in sec
sec=sec.replace(old,'    session=request.scope.get("session") or {}\n    uid=session.get("user_id") or session.get("uid")',1)
s=s[:start]+sec+s[end:]
p.write_text(s+"\n"+marker+"\n",encoding="utf-8")
print("Service selector no longer crashes when SessionMiddleware is absent")
