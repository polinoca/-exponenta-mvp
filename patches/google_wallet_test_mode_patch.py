from pathlib import Path

main_path = Path("/app/app/main.py")
main = main_path.read_text(encoding="utf-8")

# The original Google Wallet helper refers to wallet_branding; accept it explicitly.
old_signature = '''    organization: Organization,
) -> tuple[str, str]:
'''
new_signature = '''    organization: Organization,
    wallet_branding=None,
) -> tuple[str, str]:
'''
if old_signature in main:
    main = main.replace(old_signature, new_signature, 1)
elif "wallet_branding=None" not in main:
    raise SystemExit("Google Wallet helper signature not found")

# Never allow a real Google Wallet save link until the operator explicitly enables test integration.
config_path = Path("/app/app/config.py")
config = config_path.read_text(encoding="utf-8")
if "google_wallet_test_enabled" not in config:
    source = '    google_wallet_service_account_json: str = os.getenv("GOOGLE_WALLET_SERVICE_ACCOUNT_JSON", "").strip()\n'
    target = source + '    google_wallet_test_enabled: bool = os.getenv("GOOGLE_WALLET_TEST_ENABLED", "false").strip().lower() in {"1", "true", "yes"}\n'
    if source not in config:
        raise SystemExit("Google Wallet config anchor not found")
    config_path.write_text(config.replace(source, target, 1), encoding="utf-8")

main = main_path.read_text(encoding="utf-8")
main = main.replace(
    '    if provider == "google" and settings.google_wallet_ready:\n',
    '    if provider == "google" and settings.google_wallet_ready and settings.google_wallet_test_enabled:\n',
    1,
)
main = main.replace(
    '        "configured": settings.google_wallet_ready,\n        "mode": "real" if settings.google_wallet_ready else "mock",\n',
    '        "configured": settings.google_wallet_ready,\n        "test_enabled": settings.google_wallet_test_enabled,\n        "mode": "test" if (settings.google_wallet_ready and settings.google_wallet_test_enabled) else "mock",\n',
    1,
)
main_path.write_text(main, encoding="utf-8")
print("Google Wallet test-mode safety patch applied")
