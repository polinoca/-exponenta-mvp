from pathlib import Path

# Wallet fallbacks must be human-readable, never a JSON 404/download.
path = Path("/app/app/main.py")
text = path.read_text(encoding="utf-8")
if '@app.get("/wallet/mock/{provider}/{token}", response_class=HTMLResponse)' not in text:
    anchor='@app.get("/api/wallet/apple/status")\n'
    if anchor not in text:
        raise SystemExit("Wallet status route anchor missing")
    block=r'''
@app.get("/wallet/mock/{provider}/{token}", response_class=HTMLResponse)
def wallet_pending_page(provider: str, token: str, db: Session = Depends(get_db)):
    if provider not in {"apple", "google"}:
        raise HTTPException(404)
    membership = db.scalar(
        select(LoyaltyMembership).where(
            LoyaltyMembership.wallet_token == token,
            LoyaltyMembership.active.is_(True),
        )
    )
    if not membership:
        raise HTTPException(404)
    back = f"/m/{membership.wallet_token}"
    if provider == "apple":
        title = "Apple Wallet estará disponible pronto"
        detail = "La tarjeta ya funciona en este enlace. La instalación en Apple Wallet se activará cuando terminemos la autorización y certificados de Apple."
        action = "Volver a mi tarjeta"
    else:
        title = "Google Wallet está en prueba"
        detail = "Este pase requiere una cuenta autorizada por Google para pruebas. Si ya tienes acceso, vuelve a intentarlo desde esa misma cuenta de Google."
        action = "Volver a mi tarjeta"
    return HTMLResponse(f"""<!doctype html><html lang="es"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{title} · Exponenta</title><style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#f6f2ed;color:#201711;font-family:system-ui;padding:24px;box-sizing:border-box}}main{{max-width:430px;background:#fff;border:1px solid #e3d9cf;border-radius:26px;padding:30px;box-shadow:0 15px 45px #2d160f16}}small{{letter-spacing:.13em;font-weight:800;color:#8a5a3e}}h1{{font-size:2rem;letter-spacing:-.05em;margin:.45rem 0 1rem;line-height:1}}p{{line-height:1.55;color:#665b53}}a{{display:block;margin-top:24px;text-align:center;padding:16px;background:#211712;color:#fff;border-radius:15px;text-decoration:none;font-weight:800}}</style>
    <main><small>TU TARJETA EXPONENTA</small><h1>{title}</h1><p>{detail}</p><a href="{back}">{action}</a></main></html>""")

'''
    text=text.replace(anchor, block+anchor,1)
path.write_text(text,encoding="utf-8")
print("Wallet fallback experience installed")
