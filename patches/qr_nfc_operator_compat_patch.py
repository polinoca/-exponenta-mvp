from pathlib import Path

path = Path("/app/app/main.py")
text = path.read_text(encoding="utf-8")

# New Google Wallet passes encode the operator URL directly in their barcode.
helper_start = text.find("def google_wallet_save_url(")
if helper_start < 0:
    raise SystemExit("Google Wallet helper not found")
helper_end = text.find("\n\ndef ", helper_start + 1)
if helper_end < 0:
    helper_end = len(text)
helper = text[helper_start:helper_end]
member_line = '    member_url = f"{settings.app_base_url.rstrip(\'/\')}/m/{membership.wallet_token}"\n'
if member_line not in helper:
    raise SystemExit("Google Wallet member URL anchor not found")
if "scan_url = f" not in helper:
    helper = helper.replace(
        member_line,
        member_line + '    scan_url = f"{settings.app_base_url.rstrip(\'/\')}/s/{membership.wallet_token}"\n',
        1,
    )
helper = helper.replace(
    '"barcode": {"type": "QR_CODE", "value": member_url},',
    '"barcode": {"type": "QR_CODE", "value": scan_url},',
    1,
)
text = text[:helper_start] + helper + text[helper_end:]

# Existing member QR passes stay compatible: when a signed-in operator scans /m/{token},
# redirect to the protected operator page. Customers without a business session still see
# their normal member card.
middleware_anchor = '# GOOGLE WALLET LIVE SYNC + OPERATOR SCAN V1\n'
if middleware_anchor not in text:
    raise SystemExit("Live sync anchor not found")
middleware = r'''@app.middleware("http")
async def member_qr_to_operator_scan(request: Request, call_next):
    path = request.url.path
    parts = path.strip("/").split("/")
    if (
        len(parts) == 2
        and parts[0] == "m"
        and request.session.get("user_id")
    ):
        token = parts[1]
        return RedirectResponse(f"/s/{token}", status_code=307)
    return await call_next(request)


'''
if "async def member_qr_to_operator_scan" not in text:
    text = text.replace(middleware_anchor, middleware + middleware_anchor, 1)

path.write_text(text, encoding="utf-8")
print("QR/NFC operator route compatibility patch applied")
