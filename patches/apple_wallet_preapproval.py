from pathlib import Path

main = Path("/app/app/main.py")
text = main.read_text(encoding="utf-8")

# Apple Wallet pre-approval scaffolding.
# This intentionally does NOT sign or expose a pkpass until Apple credentials are present.

config = Path("/app/app/config.py")
c = config.read_text(encoding="utf-8")
anchor = '    google_wallet_service_account_json: str = os.getenv("GOOGLE_WALLET_SERVICE_ACCOUNT_JSON", "").strip()\n'
if anchor in c and "apple_pass_type_identifier" not in c:
    c = c.replace(anchor, anchor +
        '    apple_wallet_enabled: bool = os.getenv("APPLE_WALLET_ENABLED", "false").lower() in {"1", "true", "yes"}\n'
        '    apple_pass_type_identifier: str = os.getenv("APPLE_PASS_TYPE_IDENTIFIER", "").strip()\n'
        '    apple_team_identifier: str = os.getenv("APPLE_TEAM_IDENTIFIER", "").strip()\n'
        '    apple_pass_cert_p12_b64: str = os.getenv("APPLE_PASS_CERT_P12_B64", "").strip()\n'
        '    apple_pass_cert_password: str = os.getenv("APPLE_PASS_CERT_PASSWORD", "").strip()\n'
        '    apple_wwdr_cert_b64: str = os.getenv("APPLE_WWDR_CERT_B64", "").strip()\n'
        '    apple_wallet_web_service_url: str = os.getenv("APPLE_WALLET_WEB_SERVICE_URL", "https://wallet.exponenta.mx").strip().rstrip("/")\n'
    , 1)
ready_anchor = '    @property\n    def google_wallet_ready(self) -> bool:\n'
if ready_anchor in c and "def apple_wallet_ready" not in c:
    prop = '''    @property
    def apple_wallet_ready(self) -> bool:
        return bool(
            self.apple_wallet_enabled
            and self.apple_pass_type_identifier
            and self.apple_team_identifier
            and self.apple_pass_cert_p12_b64
            and self.apple_pass_cert_password
            and self.apple_wwdr_cert_b64
        )

'''
    c = c.replace(ready_anchor, prop + ready_anchor, 1)
config.write_text(c, encoding="utf-8")

# Status endpoint lets UI/ops know why Apple remains unavailable.
status_anchor = '@app.get("/api/wallet/google/status")\n'
if status_anchor in text and '"/api/wallet/apple/status"' not in text:
    block = '''@app.get("/api/wallet/apple/status")
def apple_wallet_status():
    return {
        "provider": "apple",
        "configured": settings.apple_wallet_ready,
        "enabled": settings.apple_wallet_enabled,
        "mode": "real" if settings.apple_wallet_ready else "pending_apple_approval",
        "missing": [
            name for name, value in {
                "pass_type_identifier": settings.apple_pass_type_identifier,
                "team_identifier": settings.apple_team_identifier,
                "pass_certificate": settings.apple_pass_cert_p12_b64,
                "wwdr_certificate": settings.apple_wwdr_cert_b64,
            }.items() if not value
        ],
    }


'''
    text = text.replace(status_anchor, block + status_anchor, 1)

# Keep Apple route safe before approval: never pretend a mock is installable.
old = '    mode = "mock"\n    redirect_url = f"/wallet/mock/{provider}/{membership.wallet_token}"\n    if provider == "google" and settings.google_wallet_ready:\n'
if old in text:
    new = '''    mode = "mock"
    redirect_url = f"/wallet/mock/{provider}/{membership.wallet_token}"
    if provider == "apple" and not settings.apple_wallet_ready:
        existing.status = "pending_apple_approval"
        db.add(Event(
            organization_id=program.organization_id,
            customer_id=membership.customer_id,
            event_type=EventType.WALLET_ADDED,
            metadata_json=json.dumps({"membership_id": membership.id, "provider": provider, "mode": "pending_apple_approval"}),
        ))
        db.commit()
        return RedirectResponse(f"/wallet/mock/apple/{membership.wallet_token}", status_code=303)
    if provider == "google" and settings.google_wallet_ready:
'''
    text = text.replace(old, new, 1)

main.write_text(text, encoding="utf-8")
print("Apple Wallet pre-approval scaffold applied")
