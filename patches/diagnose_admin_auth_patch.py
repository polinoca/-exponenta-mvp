from pathlib import Path
text=Path("/app/app/main.py").read_text(encoding="utf-8")
for name in ("business_context", "business_admin_context", "admin_dashboard", "admin_businesses"):
    if text.find("def "+name+"(") < 0:
        raise RuntimeError(f"Required function not found: {name}")
print("Admin authentication source check passed")
