from pathlib import Path

config_path = Path("/app/app/config.py")
config = config_path.read_text(encoding="utf-8")
if "google_wallet_test_emails" not in config:
    anchor = '    google_wallet_test_enabled: bool = os.getenv("GOOGLE_WALLET_TEST_ENABLED", "false").strip().lower() in {"1", "true", "yes"}\n'
    insert = anchor + '    google_wallet_test_emails: set[str] = {item.strip().lower() for item in os.getenv("GOOGLE_WALLET_TEST_EMAILS", "").split(",") if item.strip()}\n'
    if anchor not in config:
        raise SystemExit("Google Wallet test config anchor not found")
    config_path.write_text(config.replace(anchor, insert, 1), encoding="utf-8")

main_path = Path("/app/app/main.py")
main = main_path.read_text(encoding="utf-8")
old = '    if provider == "google" and settings.google_wallet_ready and settings.google_wallet_test_enabled:\n'
new = '''    google_wallet_test_allowed = (
        settings.google_wallet_test_enabled
        and bool(customer.email)
        and customer.email.strip().lower() in settings.google_wallet_test_emails
    )
    if provider == "google" and settings.google_wallet_ready and google_wallet_test_allowed:
'''
if old not in main:
    raise SystemExit("Google Wallet test gate anchor not found")
main_path.write_text(main.replace(old, new, 1), encoding="utf-8")
print("Google Wallet test accounts gate applied")
