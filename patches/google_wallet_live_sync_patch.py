from pathlib import Path

path = Path("/app/app/main.py")
text = path.read_text(encoding="utf-8")

imports = '''\nfrom sqlalchemy import event, inspect\nfrom urllib.parse import quote, urlencode\nfrom urllib.request import Request as UrlRequest, urlopen\n'''
if "from sqlalchemy import event, inspect" not in text:
    anchor = "from __future__ import annotations\n"
    if anchor not in text:
        raise SystemExit("main imports anchor not found")
    text = text.replace(anchor, anchor + imports, 1)

anchor = '@app.get("/api/wallet/google/status")\n'
if anchor not in text:
    raise SystemExit("Google Wallet status anchor not found")

block = r'''
# GOOGLE WALLET LIVE SYNC + OPERATOR SCAN V1
# The same immutable membership token is carried by the customer's QR and NFC.
# Only an authenticated business account may add a stamp.

GOOGLE_WALLET_SCOPE = "https://www.googleapis.com/auth/wallet_object.issuer"
GOOGLE_WALLET_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_WALLET_OBJECT_URL = "https://walletobjects.googleapis.com/walletobjects/v1/genericObject/"


def _google_wallet_credentials() -> tuple[str, str]:
    try:
        credentials = json.loads(settings.google_wallet_service_account_json)
        return credentials["client_email"], credentials["private_key"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError("Credenciales de Google Wallet inválidas") from exc


def _google_wallet_access_token() -> str:
    client_email, private_key = _google_wallet_credentials()
    now = int(time.time())
    assertion = jwt.encode(
        {
            "iss": client_email,
            "scope": GOOGLE_WALLET_SCOPE,
            "aud": GOOGLE_WALLET_TOKEN_URL,
            "iat": now,
            "exp": now + 3600,
        },
        private_key,
        algorithm="RS256",
    )
    request = UrlRequest(
        GOOGLE_WALLET_TOKEN_URL,
        data=urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=12) as response:
        payload = json.loads(response.read().decode("utf-8"))
    token = payload.get("access_token")
    if not token:
        raise ValueError("Google no devolvió un token de acceso")
    return token


def _google_wallet_live_payload(membership, customer, program, organization, wallet_branding) -> dict:
    app_url = settings.app_base_url.rstrip("/")
    scan_url = f"{app_url}/s/{membership.wallet_token}"
    member_url = f"{app_url}/m/{membership.wallet_token}"
    payload = {
        "state": "ACTIVE",
        "barcode": {"type": "QR_CODE", "value": scan_url},
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
                {"uri": member_url, "description": "Abrir mi tarjeta Exponenta", "id": "member_card"},
                {"uri": f"{app_url}/api/member-qr/{membership.wallet_token}.png", "description": "Mi QR de cliente", "id": "member_qr"},
            ]
        },
    }
    color = (getattr(wallet_branding, "background_color", None) if wallet_branding else None) or organization.brand_color
    if color:
        payload["hexBackgroundColor"] = color
    return payload


def sync_google_wallet_membership(membership_id: int) -> bool:
    """Push a committed loyalty change to the existing Google Wallet pass."""
    if not settings.google_wallet_ready:
        return False
    db = next(get_db())
    try:
        membership = db.get(LoyaltyMembership, membership_id)
        if not membership or not membership.active:
            return False
        wallet_pass = db.scalar(
            select(WalletPass).where(
                WalletPass.membership_id == membership.id,
                WalletPass.provider == "google",
                WalletPass.status == "ready",
            )
        )
        if not wallet_pass or not wallet_pass.external_id:
            return False
        program = membership.program
        organization = db.get(Organization, program.organization_id)
        customer = db.get(Customer, membership.customer_id)
        if not organization or not customer:
            return False
        wallet_branding = db.scalar(select(WalletBranding).where(WalletBranding.organization_id == organization.id))
        payload = json.dumps(
            _google_wallet_live_payload(membership, customer, program, organization, wallet_branding)
        ).encode("utf-8")
        request = UrlRequest(
            GOOGLE_WALLET_OBJECT_URL + quote(wallet_pass.external_id, safe="."),
            data=payload,
            headers={
                "Authorization": f"Bearer {_google_wallet_access_token()}",
                "Content-Type": "application/json",
            },
            method="PATCH",
        )
        with urlopen(request, timeout=12):
            pass
        wallet_pass.last_synced_at = datetime.now(timezone.utc)
        db.add(wallet_pass)
        db.commit()
        return True
    except Exception:
        # The loyalty event remains valid even if Google is temporarily unreachable.
        # It will be retried the next time the member is updated.
        db.rollback()
        return False
    finally:
        db.close()


@event.listens_for(Session, "after_flush")
def _queue_google_wallet_sync(session, flush_context):
    queued = session.info.setdefault("google_wallet_sync_memberships", set())
    for instance in session.dirty:
        if isinstance(instance, LoyaltyMembership):
            history = inspect(instance).attrs.stamps.history
            if history.has_changes():
                queued.add(instance.id)


@event.listens_for(Session, "after_commit")
def _flush_google_wallet_sync(session):
    membership_ids = session.info.pop("google_wallet_sync_memberships", set())
    for membership_id in membership_ids:
        sync_google_wallet_membership(membership_id)


@event.listens_for(Session, "after_rollback")
def _clear_google_wallet_sync(session):
    session.info.pop("google_wallet_sync_memberships", None)


@app.get("/s/{token}", response_class=HTMLResponse)
def operator_scan_landing(token: str, request: Request, db: Session = Depends(get_db)):
    membership = db.scalar(
        select(LoyaltyMembership).where(
            LoyaltyMembership.wallet_token == token,
            LoyaltyMembership.active.is_(True),
        )
    )
    if not membership:
        raise HTTPException(404)
    # NFC tags carry this URL. QR scanners can read the same immutable token.
    user, organization = business_admin_context(request, db)
    if membership.program.organization_id != organization.id:
        raise HTTPException(403, "Esta membresía pertenece a otro negocio.")
    customer = db.get(Customer, membership.customer_id)
    program = membership.program
    return HTMLResponse(
        f"""<!doctype html><html lang="es"><meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Registrar visita · Exponenta</title>
        <style>body{{font-family:system-ui;background:#f7f4f1;color:#1f1713;margin:0;padding:24px}}main{{max-width:420px;margin:auto;background:#fff;border-radius:22px;padding:24px;box-shadow:0 10px 35px #29180d14}}small{{letter-spacing:.12em;font-weight:800;color:#786c64}}h1{{font-size:2rem;margin:.35rem 0}}p{{color:#665d58}}button{{width:100%;padding:17px;border:0;border-radius:15px;background:#6b3b22;color:white;font-size:1.05rem;font-weight:800}}#result{{margin-top:14px;font-weight:800}}</style>
        <main><small>REGISTRAR VISITA</small><h1>{customer.name}</h1><p>{program.name} · <b>{membership.stamps} / {program.stamps_required} sellos</b></p>
        <button id="stamp">Agregar sello</button><div id="result"></div></main>
        <script>
        document.getElementById("stamp").onclick=async()=>{{const b=document.getElementById("stamp"),r=document.getElementById("result");b.disabled=true;b.textContent="Registrando…";const x=await fetch("/api/operator/membership/{token}/stamp",{{method:"POST",credentials:"same-origin"}});const d=await x.json();if(x.ok){{navigator.vibrate&&navigator.vibrate(80);b.textContent="¡Sello agregado!";r.textContent=d.message}}else{{b.disabled=false;b.textContent="Agregar sello";r.textContent=d.detail||"No se pudo registrar."}}}};
        </script></html>"""
    )


@app.post("/api/operator/membership/{token}/stamp")
def operator_add_stamp(token: str, request: Request, db: Session = Depends(get_db)):
    user, organization = business_admin_context(request, db)
    membership = db.scalar(
        select(LoyaltyMembership).where(
            LoyaltyMembership.wallet_token == token,
            LoyaltyMembership.active.is_(True),
        )
    )
    if not membership:
        raise HTTPException(404)
    program = membership.program
    if program.organization_id != organization.id:
        raise HTTPException(403, "Esta membresía pertenece a otro negocio.")
    if membership.stamps >= program.stamps_required:
        raise HTTPException(409, "Esta membresía ya alcanzó su recompensa.")
    membership.stamps += 1
    stamp_event_type = getattr(EventType, "STAMP_ADDED", None)
    if stamp_event_type:
        db.add(Event(
            organization_id=organization.id,
            customer_id=membership.customer_id,
            event_type=stamp_event_type,
            metadata_json=json.dumps({
                "membership_id": membership.id,
                "program_id": program.id,
                "operator_id": getattr(user, "id", None),
                "source": "qr_or_nfc",
                "stamps_after": membership.stamps,
            }),
        ))
    db.add(membership)
    db.commit()
    db.refresh(membership)
    reached_reward = membership.stamps >= program.stamps_required
    return {
        "ok": True,
        "stamps": membership.stamps,
        "required": program.stamps_required,
        "reward_reached": reached_reward,
        "message": (
            f"¡Sello agregado! Recompensa disponible: {program.reward_name}"
            if reached_reward
            else f"¡Sello agregado! {membership.stamps} de {program.stamps_required}."
        ),
    }


'''
text = text.replace(anchor, block + anchor, 1)
path.write_text(text, encoding="utf-8")
print("Google Wallet live sync and operator scan patch applied")
