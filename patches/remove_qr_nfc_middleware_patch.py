from pathlib import Path

path = Path("/app/app/main.py")
text = path.read_text(encoding="utf-8")
start = text.find('@app.middleware("http")\nasync def member_qr_to_operator_scan')
if start < 0:
    raise SystemExit("QR/NFC middleware not found")
end = text.find('\n\n# GOOGLE WALLET LIVE SYNC + OPERATOR SCAN V1', start)
if end < 0:
    raise SystemExit("QR/NFC middleware end marker not found")
text = text[:start] + text[end + 2:]
path.write_text(text, encoding="utf-8")
print("Removed QR/NFC middleware to preserve session middleware order")
