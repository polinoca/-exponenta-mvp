from pathlib import Path

config_path = Path("/app/app/config.py")
config = config_path.read_text(encoding="utf-8")
field = '    google_wallet_test_emails: str = os.getenv("GOOGLE_WALLET_TEST_EMAILS", "").strip().lower()\n'
extra_field = field + '    google_wallet_test_emails_extra: str = os.getenv("GOOGLE_WALLET_TEST_EMAILS_EXTRA", "").strip().lower()\n'
if field not in config:
    raise SystemExit("Google Wallet test email field not found")
if "google_wallet_test_emails_extra:" not in config:
    config = config.replace(field, extra_field, 1)
config_path.write_text(config, encoding="utf-8")

main_path = Path("/app/app/main.py")
main = main_path.read_text(encoding="utf-8")
old = '        and customer.email.strip().lower() in {item.strip() for item in settings.google_wallet_test_emails.split(",") if item.strip()}\n'
new = '        and customer.email.strip().lower() in {item.strip() for item in (settings.google_wallet_test_emails + "," + settings.google_wallet_test_emails_extra).split(",") if item.strip()}\n'
if old not in main and new not in main:
    raise SystemExit("Google Wallet test email gate not found")
if old in main:
    main = main.replace(old, new, 1)
main_path.write_text(main, encoding="utf-8")
print("Additional Google Wallet test accounts supported")
