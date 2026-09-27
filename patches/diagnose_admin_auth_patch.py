from pathlib import Path
text=Path("/app/app/main.py").read_text(encoding="utf-8")
for name in ("business_context", "business_admin_context", "admin_dashboard", "admin_businesses"):
    start=text.find("def "+name+"(")
    print("SOURCE_FOR",name)
    print(text[start:start+2200] if start >= 0 else "NOT_FOUND")
