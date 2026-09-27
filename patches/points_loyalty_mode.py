from pathlib import Path
import re

main_path = Path("/app/app/main.py")
service_path = Path("/app/app/services/loyalty.py")
loyalty_tpl = Path("/app/app/templates/business/loyalty.html")
quick_tpl = Path("/app/app/templates/business/member_quick.html")
member_tpl = Path("/app/app/templates/public/member.html")
join_tpl = Path("/app/app/templates/public/join.html")
wallet_tpl = Path("/app/app/templates/wallet_mock.html")
settings_tpl = Path("/app/app/templates/business/settings.html")
operator_tpl = Path("/app/app/templates/business/operator.html")

# Point movements reuse the audited membership balance column. Existing visit clubs remain unchanged.
service = service_path.read_text()
if "def adjust_points(" not in service:
    service += r'''

@dataclass
class PointsResult:
    balance: int
    rewards_available: int
    reward_earned: bool


def adjust_points(
    db: Session,
    *,
    membership: LoyaltyMembership,
    actor_user_id: Optional[int],
    amount: int,
    idempotency_key: str,
    note: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> PointsResult:
    if getattr(membership.program.mechanic, "value", membership.program.mechanic) != "points":
        raise ValueError("Este club funciona por visitas, no por puntos.")
    if not membership.active or not membership.program.active:
        raise ValueError("La membresía o el programa están pausados.")
    if not amount or abs(int(amount)) > 100000:
        raise ValueError("Ingresa un ajuste entre -100000 y 100000 puntos.")

    locked = db.scalar(select(LoyaltyMembership).where(LoyaltyMembership.id == membership.id).with_for_update())
    if not locked:
        raise ValueError("Membresía no encontrada.")
    membership = locked
    actor, _ = _ensure_operator(
        db, membership=membership, actor_user_id=actor_user_id, permission="grant"
    )
    _check_idempotency(db, idempotency_key)

    before_balance = membership.stamps
    before_rewards = membership.rewards_available
    next_balance = before_balance + int(amount)
    if next_balance < 0:
        raise ValueError("El cliente no tiene suficientes puntos para ese ajuste.")

    membership.stamps = next_balance
    earned = False
    required = max(1, membership.program.stamps_required)
    if amount > 0:
        while membership.stamps >= required:
            membership.stamps -= required
            membership.rewards_available += 1
            earned = True

    db.add(LoyaltyTransaction(
        membership_id=membership.id,
        kind="points",
        amount=int(amount),
        note=(note or ("Puntos agregados" if amount > 0 else "Ajuste de puntos"))[:300],
        created_by_user_id=actor.id,
    ))
    _audit(
        db,
        membership=membership,
        actor_user_id=actor.id,
        action="points_adjust",
        decision="allowed",
        reason="puntos_agregados" if amount > 0 else "puntos_ajustados",
        idempotency_key=idempotency_key,
        stamps_before=before_balance,
        stamps_after=membership.stamps,
        rewards_before=before_rewards,
        rewards_after=membership.rewards_available,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.flush()
    return PointsResult(membership.stamps, membership.rewards_available, earned)
'''
    service_path.write_text(service)

s = main_path.read_text()
if "adjust_points," not in s:
    marker = "    add_stamp,\n"
    if marker not in s:
        raise SystemExit("loyalty service import anchor missing")
    s = s.replace(marker, marker + "    adjust_points,\n", 1)

# Add the modality field to the existing program configuration endpoint.
sig = '    name: str = Form(...),\n    stamps_required: int = Form(...),'
if sig not in s:
    raise SystemExit("loyalty config signature anchor missing")
s = s.replace(sig, '    name: str = Form(...),\n    mechanic: str = Form("visits"),\n    stamps_required: int = Form(...),', 1)

validation = '''    if stamps_required < 2 or stamps_required > 30:
        raise HTTPException(422, "La meta debe estar entre 2 y 30 sellos.")
'''
replacement = '''    mechanic = (mechanic or "visits").strip().lower()
    if mechanic not in {"visits", "points"}:
        raise HTTPException(422, "Selecciona visitas o puntos.")
    if mechanic == "visits" and (stamps_required < 2 or stamps_required > 30):
        raise HTTPException(422, "La meta debe estar entre 2 y 30 sellos.")
    if mechanic == "points" and (stamps_required < 10 or stamps_required > 100000):
        raise HTTPException(422, "La meta debe estar entre 10 y 100000 puntos.")
'''
if validation not in s:
    raise SystemExit("loyalty config validation anchor missing")
s = s.replace(validation, replacement, 1)

assignment = '    program.name = name.strip() or f"Club {org.name}"\n    program.stamps_required = stamps_required'
if assignment not in s:
    raise SystemExit("program assignment anchor missing")
s = s.replace(assignment, '    program.name = name.strip() or f"Club {org.name}"\n    program.mechanic = mechanic\n    program.stamps_required = stamps_required', 1)

# Provide an audited signed adjustment endpoint for point programs.
route_anchor = '@app.get("/negocio/cliente/{token}", response_class=HTMLResponse)'
if "def business_adjust_points(" not in s:
    point_route = r'''
@app.post("/negocio/lealtad/{membership_id}/puntos")
def business_adjust_points(
    membership_id: int,
    request: Request,
    amount: int = Form(...),
    note: str = Form(""),
    csrf_token: str = Form(""),
    idempotency_key: str = Form(...),
    db: Session = Depends(get_db),
):
    user, org = business_context(request, db)
    verify_csrf(request, csrf_token)
    membership = db.get(LoyaltyMembership, membership_id)
    if not membership or membership.program.organization_id != org.id:
        raise HTTPException(404)
    try:
        result = adjust_points(
            db,
            membership=membership,
            actor_user_id=user.id,
            amount=amount,
            note=note,
            idempotency_key=idempotency_key,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", ""),
        )
    except ValueError as exc:
        db.commit()
        return RedirectResponse(
            f"/negocio/cliente/{membership.wallet_token}?points_error={str(exc)}",
            status_code=303,
        )
    db.commit()
    label = "Recompensa desbloqueada" if result.reward_earned else "Puntos actualizados"
    return RedirectResponse(
        f"/negocio/cliente/{membership.wallet_token}?message={label.replace(' ', '+')}",
        status_code=303,
    )


'''
    if route_anchor not in s:
        raise SystemExit("member quick route anchor missing")
    s = s.replace(route_anchor, point_route + route_anchor, 1)

# Existing QR/NFC operator endpoint grants one point when the club is points based.
scan_anchor = '''    if program.organization_id != organization.id:
        raise HTTPException(403, "Esta membresía pertenece a otro negocio.")
    if membership.stamps >= program.stamps_required:
'''
if scan_anchor in s and 'source=\"qr_or_nfc_points\"' not in s:
    scan_insert = '''    if program.organization_id != organization.id:
        raise HTTPException(403, "Esta membresía pertenece a otro negocio.")
    if getattr(program.mechanic, "value", program.mechanic) == "points":
        try:
            result = adjust_points(
                db, membership=membership, actor_user_id=user.id, amount=1,
                note="QR/NFC", idempotency_key=secrets.token_urlsafe(24),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent", ""),
            )
            db.commit()
            return {
                "ok": True, "points": result.balance, "required": program.stamps_required,
                "reward_reached": result.reward_earned,
                "message": "¡Punto agregado!" if not result.reward_earned else f"¡Recompensa disponible: {program.reward_name}!",
            }
        except ValueError as exc:
            db.rollback()
            raise HTTPException(409, str(exc)) from exc
    if membership.stamps >= program.stamps_required:
'''
    s = s.replace(scan_anchor, scan_insert, 1)

# Google Wallet sync and save payload display the proper balance type.
old_wallet_progress = '''"header": "PROGRESO",
                "body": f"{membership.stamps} / {program.stamps_required} sellos",'''
new_wallet_progress = '''"header": "PUNTOS" if getattr(program.mechanic, "value", program.mechanic) == "points" else "PROGRESO",
                "body": (
                    f"{membership.stamps} puntos"
                    if getattr(program.mechanic, "value", program.mechanic) == "points"
                    else f"{membership.stamps} / {program.stamps_required} sellos"
                ),'''
s = s.replace(old_wallet_progress, new_wallet_progress)

main_path.write_text(s)

# Business configuration and operational surfaces.
t = loyalty_tpl.read_text()
if 'name="mechanic"' not in t:
    t = t.replace(
        '<label>Nombre <input name="name" value="{{ program.name if program else \'Club \' ~ organization.name }}" required></label>',
        '''<label>Nombre <input name="name" value="{{ program.name if program else 'Club ' ~ organization.name }}" required></label>
<label>Tipo de programa <select name="mechanic" id="xp-mechanic"><option value="visits" {% if not program or program.mechanic.value == 'visits' %}selected{% endif %}>Visitas y sellos</option><option value="points" {% if program and program.mechanic.value == 'points' %}selected{% endif %}>Puntos</option></select></label>
<p class="xp-points-help">Visitas: una compra = un sello. Puntos: el equipo suma o ajusta puntos desde el QR/NFC o la ficha del cliente.</p>''',
        1,
    )
t = t.replace(
    '<label>Sellos para recompensa <input name="stamps_required" type="number" min="2" max="30" value="{{ program.stamps_required if program else 9 }}" required></label>',
    '<label id="xp-goal-label">{{ "Puntos para recompensa" if program and program.mechanic.value == "points" else "Sellos para recompensa" }} <input name="stamps_required" type="number" min="2" max="100000" value="{{ program.stamps_required if program else 9 }}" required></label>',
    1,
)
t = t.replace('<th>Sellos</th><th>Visitas</th><th>Premios</th><th>Última visita</th>', '<th>{{ "Puntos" if program and program.mechanic.value == "points" else "Sellos" }}</th>{% if not program or program.mechanic.value != "points" %}<th>Visitas</th>{% endif %}<th>Premios</th><th>Último movimiento</th>', 1)
t = t.replace('<td>{{ m.stamps }}/{{ item.program.stamps_required }}</td><td>{{ item.lifetime_visits }}</td><td>{{ m.rewards_available }}</td>', '<td>{% if item.program.mechanic.value == "points" %}{{ m.stamps }} puntos{% else %}{{ m.stamps }}/{{ item.program.stamps_required }}{% endif %}</td>{% if item.program.mechanic.value != "points" %}<td>{{ item.lifetime_visits }}</td>{% endif %}<td>{{ m.rewards_available }}</td>', 1)
t = t.replace('<tr><td colspan="6">Aún no hay clientes.</td></tr>', '<tr><td colspan="6">Aún no hay clientes.</td></tr>', 1)
if "xp-mechanic-script" not in t:
    t = t.replace('{% endblock %}', '''<script id="xp-mechanic-script">(() => {const s=document.getElementById('xp-mechanic'),l=document.getElementById('xp-goal-label');if(!s||!l)return;const u=()=>{l.firstChild.textContent=s.value==='points'?'Puntos para recompensa ':'Sellos para recompensa ';};s.addEventListener('change',u);u();})();</script>
{% endblock %}''', 1)
loyalty_tpl.write_text(t)

t = quick_tpl.read_text()
if "xp-points-adjust" not in t:
    stats_old = '<div class="stat-card"><span>Sellos</span><strong>{{ item.membership.stamps }}</strong></div>'
    stats_new = '<div class="stat-card"><span>{{ "Puntos" if item.program.mechanic.value == "points" else "Sellos" }}</span><strong>{{ item.membership.stamps }}</strong></div>'
    t = t.replace(stats_old, stats_new, 1)
    insert = '''{% if item.program.mechanic.value == "points" and can_grant %}
<section class="panel-card xp-points-adjust"><div class="kicker">PUNTOS</div><h2>Ajustar saldo</h2><p class="muted">Usa un número positivo para sumar o negativo para descontar. Cada movimiento queda registrado.</p>{% if request.query_params.get("points_error") %}<div class="alert error">{{ request.query_params.get("points_error") }}</div>{% endif %}<form class="form-stack" method="post" action="/negocio/lealtad/{{ item.membership.id }}/puntos"><input type="hidden" name="csrf_token" value="{{ csrf }}"><input type="hidden" name="idempotency_key" value="{{ item.stamp_token }}"><label>Puntos <input name="amount" type="number" step="1" required placeholder="Ej. 10 o -10"></label><label>Nota <input name="note" maxlength="300" placeholder="Ej. compra $250"></label><button class="btn btn-primary">Guardar puntos</button></form></section>{% endif %}
'''
    t = t.replace('</div>\n{% endblock %}', insert + '</div>\n{% endblock %}', 1)
quick_tpl.write_text(t)

# Customer and Wallet views show a balance rather than stamp dots for points.
for path in (member_tpl, wallet_tpl, settings_tpl):
    t = path.read_text()
    t = t.replace(
        '<h2>{{ membership.stamps }} / {{ program.stamps_required }} sellos</h2>',
        '<h2>{% if program.mechanic.value == "points" %}{{ membership.stamps }} puntos{% else %}{{ membership.stamps }} / {{ program.stamps_required }} sellos{% endif %}</h2>',
    )
    t = t.replace(
        '<div class="stamp-row">{% for i in range(program.stamps_required if program.stamps_required <= 10 else 10) %}<i class="{% if i < membership.stamps %}filled{% endif %}"></i>{% endfor %}</div>',
        '{% if program.mechanic.value != "points" %}<div class="stamp-row">{% for i in range(program.stamps_required if program.stamps_required <= 10 else 10) %}<i class="{% if i < membership.stamps %}filled{% endif %}"></i>{% endfor %}</div>{% endif %}',
    )
    t = t.replace(
        '{{ lifetime_visits }} visitas acumuladas',
        '{% if program.mechanic.value == "points" %}Saldo actual de puntos{% else %}{{ lifetime_visits }} visitas acumuladas{% endif %}',
    )
    t = t.replace(
        '0 / {{ program.stamps_required }} sellos',
        '{% if program.mechanic.value == "points" %}0 puntos{% else %}0 / {{ program.stamps_required }} sellos{% endif %}',
    )
    path.write_text(t)

t = join_tpl.read_text()
t = t.replace(
    'Acumula {{ program.stamps_required }} visitas y recibe:',
    '{% if program.mechanic.value == "points" %}Acumula puntos y canjéalos por:{% else %}Acumula {{ program.stamps_required }} visitas y recibe:{% endif %}',
)
join_tpl.write_text(t)

t = operator_tpl.read_text()
t = t.replace(
    '<small>sellos por premio</small>',
    '<small>{{ "puntos por premio" if program.mechanic.value == "points" else "sellos por premio" }}</small>',
)
t = t.replace(
    '<small>sellos otorgados</small>',
    '<small>{{ "puntos registrados" if program.mechanic.value == "points" else "sellos otorgados" }}</small>',
)
operator_tpl.write_text(t)

css = Path("/app/app/static/app.css")
c = css.read_text()
if ".xp-points-help" not in c:
    c += "\n.xp-points-help{font-size:.72rem;line-height:1.45;margin:-4px 0 4px;color:#6d6259}.xp-points-adjust{margin-top:16px}.xp-points-adjust h2{margin:.3rem 0}.xp-points-adjust .muted{font-size:.78rem}\n"
    css.write_text(c)

print("points loyalty mode installed")
