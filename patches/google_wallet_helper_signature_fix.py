from pathlib import Path

path = Path("/app/app/main.py")
text = path.read_text(encoding="utf-8")
start = text.find("def google_wallet_save_url(")
if start < 0:
    raise SystemExit("Google Wallet helper not found")
end = text.find(") -> tuple[str, str]:", start)
if end < 0:
    raise SystemExit("Google Wallet helper signature end not found")
end += len(") -> tuple[str, str]:")
header = text[start:end]
if "wallet_branding" not in header:
    anchor = "    organization: Organization,"
    if anchor not in header:
        raise SystemExit("Organization argument missing in Wallet helper")
    header = header.replace(anchor, anchor + "\n    wallet_branding=None,", 1)
    text = text[:start] + header + text[end:]
path.write_text(text, encoding="utf-8")
print("Google Wallet helper accepts branding argument")
