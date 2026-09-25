from pathlib import Path

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"{label}: expected block not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

config = Path("/app/app/config.py")
replace_once(
    config,
    '    web_push_subject: str = os.getenv("WEB_PUSH_SUBJECT", "mailto:soporte@exponenta.mx")\n',
    '    web_push_subject: str = os.getenv("WEB_PUSH_SUBJECT", "mailto:soporte@exponenta.mx")\n'
    '    google_wallet_issuer_id: str = os.getenv("GOOGLE_WALLET_ISSUER_ID", "").strip()\n'
    '    google_wallet_service_account_json: str = os.getenv("GOOGLE_WALLET_SERVICE_ACCOUNT_JSON", "").strip()\n',
    "config wallet fields",
)
replace_once(
    config,
    '    @property\n    def is_production(self) -> bool:\n',
    '    @property\n'
    '    def google_wallet_ready(self) -> bool:\n'
    '        return bool(self.google_wallet_issuer_id and self.google_wallet_service_account_json)\n\n'
    '    @property\n'
    '    def is_production(self) -> bool:\n',
    "config wallet ready",
)

req = Path("/app/requirements.txt")
text = req.read_text(encoding="utf-8")
if "PyJWT" not in text:
    text += "\nPyJWT[crypto]==2.10.1\n"
req.write_text(text, encoding="utf-8")

main = Path("/app/app/main.py")
replace_once(
    main,
    'import io\nimport json\nimport secrets\n',
    'import io\nimport json\nimport re\nimport secrets\nimport time\n\nimport jwt\n',
    "main imports",
)

anchor = '''def safe_destination(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("El destino debe ser una URL http/https válida")
    return url.strip()


'''
helper = '''def safe_destination(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("El destino debe ser una URL http/https válida")
    return url.strip()


def _wallet_suffix(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", value.strip())
    return cleaned[:80] or fallback


def google_wallet_save_url(
    *,
    membership: LoyaltyMembership,
    customer: Customer,
    program: LoyaltyProgram,
    organization: Organization,
) -> tuple[str, str]:
    if not settings.google_wallet_ready:
        raise ValueError("Google Wallet no está configurado")
    try:
        credentials = json.loads(settings.google_wallet_service_account_json)
        client_email = credentials["client_email"]
        private_key = credentials["private_key"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError("Credenciales de Google Wallet inválidas") from exc

    issuer = settings.google_wallet_issuer_id
    org_suffix = _wallet_suffix(organization.slug, f"org{organization.id}")
    token_suffix = _wallet_suffix(membership.wallet_token[:32], f"member{membership.id}")
    class_id = f"{issuer}.exponenta_{org_suffix}"
    object_id = f"{issuer}.exponenta_{org_suffix}_{token_suffix}"
    member_url = f"{settings.app_base_url.rstrip('/')}/m/{membership.wallet_token}"
    qr_url = f"{settings.app_base_url.rstrip('/')}/api/member-qr/{membership.wallet_token}.png"

    wallet_class = {
        "id": class_id,
        "classTemplateInfo": {
            "cardTemplateOverride": {
                "cardRowTemplateInfos": [
                    {
                        "twoItems": {
                            "startItem": {
                                "firstValue": {
                                    "fields": [{"fieldPath": "object.textModulesData['progress']"}]
                                }
                            },
                            "endItem": {
                                "firstValue": {
                                    "fields": [{"fieldPath": "object.textModulesData['reward']"}]
                                }
                            },
                        }
                    }
                ]
            }
        },
    }
    wallet_object = {
        "id": object_id,
        "classId": class_id,
        "state": "ACTIVE",
        "cardTitle": {"defaultValue": {"language": "es-MX", "value": organization.name}},
        "header": {"defaultValue": {"language": "es-MX", "value": program.name}},
        "subheader": {"defaultValue": {"language": "es-MX", "value": customer.name}},
        "hexBackgroundColor": organization.brand_color or "#111111",
        "barcode": {"type": "QR_CODE", "value": member_url},
        "textModulesData": [
            {
                "id": "progress",
                "header": "PROGRESO",
                "body": f"{membership.stamps} / {program.stamps_required} sellos",
            },
            {
                "id": "reward",
                "header": "RECOMPENSA",
                "body": program.reward_name,
            },
        ],
        "linksModuleData": {
            "uris": [
                {
                    "uri": program.primary_cta_url,
                    "description": program.primary_cta_label,
                    "id": "primary_cta",
                },
                {
                    "uri": member_url,
                    "description": "Abrir mi tarjeta Exponenta",
                    "id": "member_card",
                },
                {
                    "uri": qr_url,
                    "description": "Mi QR de cliente",
                    "id": "member_qr",
                },
            ]
        },
    }
    if organization.logo_url:
        wallet_object["logo"] = {
            "sourceUri": {"uri": organization.logo_url},
            "contentDescription": {"defaultValue": {"language": "es-MX", "value": organization.name}},
        }

    claims = {
        "iss": client_email,
        "aud": "google",
        "typ": "savetowallet",
        "iat": int(time.time()),
        "origins": [settings.app_base_url],
        "payload": {
            "genericClasses": [wallet_class],
            "genericObjects": [wallet_object],
        },
    }
    signed = jwt.encode(claims, private_key, algorithm="RS256")
    return f"https://pay.google.com/gp/v/save/{signed}", object_id


'''
replace_once(main, anchor, helper, "wallet helper")

old_wallet = '''@app.get("/m/{token}/wallet/{provider}")
def member_wallet(token: str, provider: str, db: Session = Depends(get_db)):
    if provider not in {"apple", "google"}:
        raise HTTPException(404)
    membership = db.scalar(select(LoyaltyMembership).where(LoyaltyMembership.wallet_token == token, LoyaltyMembership.active.is_(True)))
    if not membership:
        raise HTTPException(404)
    existing = db.scalar(select(WalletPass).where(WalletPass.membership_id == membership.id, WalletPass.provider == provider))
    if not existing:
        existing = WalletPass(
            membership_id=membership.id,
            provider=provider,
            status="mock",
            serial_number=f"{provider}-{membership.id}-{membership.wallet_token[:12]}",
        )
        db.add(existing)
    db.add(Event(
        organization_id=membership.program.organization_id,
        customer_id=membership.customer_id,
        event_type=EventType.WALLET_ADDED,
        metadata_json=json.dumps({"membership_id": membership.id, "provider": provider, "mode": "mock"}),
    ))
    db.commit()
    return RedirectResponse(f"/wallet/mock/{provider}/{membership.wallet_token}", status_code=303)
'''
new_wallet = '''@app.get("/m/{token}/wallet/{provider}")
def member_wallet(token: str, provider: str, db: Session = Depends(get_db)):
    if provider not in {"apple", "google"}:
        raise HTTPException(404)
    membership = db.scalar(select(LoyaltyMembership).where(LoyaltyMembership.wallet_token == token, LoyaltyMembership.active.is_(True)))
    if not membership:
        raise HTTPException(404)
    program = membership.program
    organization = db.get(Organization, program.organization_id)
    customer = db.get(Customer, membership.customer_id)
    existing = db.scalar(select(WalletPass).where(WalletPass.membership_id == membership.id, WalletPass.provider == provider))
    if not existing:
        existing = WalletPass(
            membership_id=membership.id,
            provider=provider,
            status="mock",
            serial_number=f"{provider}-{membership.id}-{membership.wallet_token[:12]}",
        )
        db.add(existing)

    mode = "mock"
    redirect_url = f"/wallet/mock/{provider}/{membership.wallet_token}"
    if provider == "google" and settings.google_wallet_ready:
        try:
            redirect_url, external_id = google_wallet_save_url(
                membership=membership,
                customer=customer,
                program=program,
                organization=organization,
            )
            existing.status = "ready"
            existing.external_id = external_id
            existing.last_synced_at = datetime.now(timezone.utc)
            mode = "google_wallet"
        except ValueError:
            existing.status = "configuration_error"
            mode = "mock"

    db.add(Event(
        organization_id=program.organization_id,
        customer_id=membership.customer_id,
        event_type=EventType.WALLET_ADDED,
        metadata_json=json.dumps({"membership_id": membership.id, "provider": provider, "mode": mode}),
    ))
    db.commit()
    return RedirectResponse(redirect_url, status_code=303)
'''
replace_once(main, old_wallet, new_wallet, "google wallet route")

status_anchor = '''@app.get("/api/club-qr/{slug}.png")
def club_qr_png(slug: str, db: Session = Depends(get_db)):
'''
status_route = '''@app.get("/api/wallet/google/status")
def google_wallet_status():
    return {
        "provider": "google",
        "configured": settings.google_wallet_ready,
        "mode": "real" if settings.google_wallet_ready else "mock",
    }


@app.get("/api/club-qr/{slug}.png")
def club_qr_png(slug: str, db: Session = Depends(get_db)):
'''
replace_once(main, status_anchor, status_route, "wallet status endpoint")

print("Google Wallet preparation patch applied")
