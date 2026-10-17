from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK QR DOWNLOAD V1'

if marker not in s:
    block=r'''
# XP PET CLINIK QR DOWNLOAD V1
@app.get("/negocio/encuestas/{slug}/qr.png")
def xp_survey_business_qr(slug: str, request: Request, db: Session = Depends(get_db)):
    import io
    import qrcode
    xp_survey_extended(db)
    _, _, survey = xp_survey_business(request, db, slug)
    public_url = str(request.base_url).rstrip("/") + "/encuesta/" + slug
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=24,
        border=4,
    )
    qr.add_data(public_url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#111111", back_color="#FFFFFF").convert("RGB")
    image = image.resize((1200, 1200))
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    filename=(str(survey.get("name") or "encuesta").lower().replace(" ", "-") + "-qr-para-imprimir.png")
    return Response(
        content=output.getvalue(),
        media_type="image/png",
        headers={
            "Content-Disposition": 'attachment; filename="'+filename+'"',
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )

def xp_survey_business_theme(title, body, survey):
    name=str(survey.get("name") or "Tu negocio")
    logo=str(survey.get("logo_data") or survey.get("logo_url") or "")
    slug=str(survey.get("slug") or "")
    esc=lambda v: xp_html.escape(str(v),quote=True)
    brand=survey.get("brand_color") if xp_survey_re.fullmatch(r"#[0-9A-Fa-f]{6}",str(survey.get("brand_color") or "")) else "#2D71B1"
    logo_html=('<span class="xp-client-logo"><img src="'+esc(logo)+'" alt="Logotipo de '+esc(name)+'"></span>' if logo else '<span class="xp-client-name">'+esc(name)+'</span>')
    style="""<style>
    header,footer,.footer{display:none!important}body{background:#f4fafd!important}main{max-width:1080px!important;margin:0 auto!important;padding:16px 14px 56px!important}
    .xp-client-brandbar{display:flex!important;align-items:center!important;gap:12px!important;background:#fff!important;border:1px solid #d7e8f2!important;border-radius:18px!important;padding:11px 14px!important;margin:0 0 18px!important;box-shadow:0 8px 24px rgba(23,76,112,.07)!important}
    .xp-client-logo{display:flex;width:52px;height:52px;align-items:center;justify-content:center;border-radius:50%;background:#fff;border:1px solid #e0edf4;padding:6px;overflow:hidden;flex:0 0 auto}.xp-client-logo img{display:block;max-width:100%;max-height:100%;object-fit:contain}.xp-client-name{color:var(--client-brand);font-size:20px;font-weight:850;letter-spacing:-.03em}.xp-client-brandcopy{min-width:0;display:grid;gap:3px}.xp-client-brandcopy b{font-size:15px;line-height:1.1;color:#17324d}.xp-client-brandcopy small{font-size:11px;color:#6f879a;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
    .xp-print-qr{display:inline-flex;align-items:center;justify-content:center;gap:8px;margin:-7px 0 18px;padding:12px 16px;border-radius:13px;background:var(--client-brand);color:#fff!important;font-size:14px;font-weight:800;text-decoration:none!important;box-shadow:0 8px 18px rgba(28,91,162,.18)}
    @media(max-width:540px){main{padding:12px 11px 45px!important}.xp-client-brandbar{border-radius:15px;padding:9px 11px;margin-bottom:13px!important}.xp-client-logo{width:45px;height:45px}.xp-client-brandcopy b{font-size:14px}.xp-print-qr{display:flex;width:100%;min-height:48px;margin:0 0 14px}}
    </style>"""
    qr_action=('<a class="xp-print-qr" href="/negocio/encuestas/'+esc(slug)+'/qr.png" download>↓ Descargar QR para imprimir</a>' if slug and str(title).startswith("Resultados") else "")
    shell=style.replace("--client-brand",brand)+'<div class="xp-client-brandbar">'+logo_html+'<div class="xp-client-brandcopy"><b>'+esc(name)+'</b><small>Panel de experiencia</small></div></div>'+qr_action+body
    return xp_survey_page(title,shell)
'''
    p.write_text(s+'\n'+block+'\n'+marker+'\n',encoding='utf-8')

print('PET Clinik client panel QR download is available')
