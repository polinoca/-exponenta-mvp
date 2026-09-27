from pathlib import Path
import re
text=Path("/app/app/main.py").read_text(encoding="utf-8")
for match in re.finditer(r"^def ([A-Za-z_][A-Za-z0-9_]*)\(", text, re.M):
    name=match.group(1).lower()
    if any(word in name for word in ("auth","user","admin","login","current","context","token","session")):
        print("AUTH_CANDIDATE", match.group(1))
print("ADMIN_ROUTE_CONTEXT")
start=text.find('@app.get("/admin")')
print(text[start:start+3500])
