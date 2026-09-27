from pathlib import Path

config_path = Path("/app/app/config.py")
config = config_path.read_text(encoding="utf-8")
old_field = '    google_wallet_test_emails: set[str] = {item.strip().lower() for item in os.getenv("GOOGLE_WALLET_TEST_EMAILS", "").split(",") if item.strip()}\n'
new_field = '    google_wallet_test_emails: str = os.getenv("GOOGLE_WALLET_TEST_EMAILS", "").strip().lower()\n'
if old_field not in config:
    raise SystemExit("Mutable test emails config field not found")
config_path.write_text(config.replace(old_field, new_field, 1), encoding="utf-8")

main_path = Path("/app/app/main.py")
main = main_path.read_text(encoding="utf-8")
old_check = '        and customer.email.strip().lower() in settings.google_wallet_test_emails\n'
new_check = '        and customer.email.strip().lower() in {item.strip() for item in settings.google_wallet_test_emails.split(",") if item.strip()}\n'
if old_check not in main:
    raise SystemExit("Test email gate check not found")
main_path.write_text(main.replace(old_check, new_check, 1), encoding="utf-8")
print("Google Wallet test accounts config fixed")
