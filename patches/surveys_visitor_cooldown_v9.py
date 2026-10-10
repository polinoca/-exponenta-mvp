from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
marker="# XP SURVEY VISITOR COOLDOWN V9"
if marker not in s:
 s=marker+"\n"+s
 s=s.replace("import uuid as xp_survey_uuid","import uuid as xp_survey_uuid\nimport secrets as xp_survey_secrets",1)
 anchor="def xp_survey_lookup(db,slug):"
 helper='''def xp_survey_cooldown_schema(db):
    db.execute(xp_survey_sql("ALTER TABLE xp_survey_responses ADD COLUMN IF NOT EXISTS visitor_id VARCHAR(64)"))
    db.execute(xp_survey_sql("CREATE INDEX IF NOT EXISTS xp_survey_visitor_recent ON xp_survey_responses(slug,visitor_id,created_at) WHERE visitor_id IS NOT NULL"))
    db.commit()

def xp_survey_recent(db,slug,visitor_id):
    return db.execute(xp_survey_sql("""
      SELECT EXISTS(SELECT 1 FROM xp_survey_responses
      WHERE slug=:slug AND visitor_id=:visitor
      AND created_at > CURRENT_TIMESTAMP - INTERVAL '60 minutes')"""),
      {"slug":slug,"visitor":visitor_id}).scalar()

'''
 if anchor not in s:raise SystemExit("lookup missing")
 s=s.replace(anchor,helper+anchor,1)
 a=s.index("def xp_survey_public(");b=s.index("\n@app.",a);t=s[a:b]
 t=t.replace("def xp_survey_public(slug: str, db: Session = Depends(get_db)):","def xp_survey_public(slug: str, request: Request, db: Session = Depends(get_db)):")
 t=t.replace("    p=xp_survey_lookup(db,slug)","    xp_survey_cooldown_schema(db)\n    p=xp_survey_lookup(db,slug)",1)
 t=t.replace("    def scale(field,labels):",'''    visitor=request.cookies.get("xp_survey_visitor","")
    if not xp_survey_re.fullmatch(r"[a-f0-9]{48}",visitor):
        visitor=xp_survey_secrets.token_hex(24)
    if xp_survey_recent(db,slug,visitor):
        page=xp_survey_page("Opinión registrada",'<div class="card" style="text-align:center"><h1>Ya recibimos tu opinión</h1><p>Gracias por ayudarnos a mejorar.</p><p class="muted">Podrás responder una nueva encuesta después de 60 minutos.</p></div>')
        response=HTMLResponse(page)
        response.set_cookie("xp_survey_visitor",visitor,max_age=31536000,secure=True,httponly=True,samesite="lax")
        return response
    def scale(field,labels):''',1)
 t=t.replace("    return xp_survey_page('Tu opinión',content)",'''    response=HTMLResponse(xp_survey_page('Tu opinión',content))
    response.set_cookie("xp_survey_visitor",visitor,max_age=31536000,secure=True,httponly=True,samesite="lax")
    response.headers["Cache-Control"]="no-store"
    return response''',1)
 s=s[:a]+t+s[b:]
 a=s.index("async def xp_survey_submit(");b=s.index("\n@app.",a);t=s[a:b]
 t=t.replace("    p=xp_survey_lookup(db,slug)","    xp_survey_cooldown_schema(db)\n    p=xp_survey_lookup(db,slug)",1)
 find='    submission=None'
 if find not in t:raise SystemExit("submission anchor absent")
 t=t.replace(find,'''    visitor=request.cookies.get("xp_survey_visitor","")
    if not xp_survey_re.fullmatch(r"[a-f0-9]{48}",visitor):
        raise HTTPException(403,"Abre la encuesta nuevamente antes de enviarla")
    # Serializes submissions from this browser for this business to prevent simultaneous duplicates.
    db.execute(xp_survey_sql("SELECT pg_advisory_xact_lock(hashtext(:key))"),{"key":slug+":"+visitor})
    if xp_survey_recent(db,slug,visitor):
        db.rollback()
        return RedirectResponse("/encuesta/"+slug+"/gracias",status_code=303)
    submission=None''',1)
 t=t.replace("attendant,comment,submission_token)","attendant,comment,submission_token,visitor_id)")
 t=t.replace(":comment,:submission_token) ON CONFLICT",":comment,:submission_token,:visitor_id) ON CONFLICT")
 t=t.replace('"submission_token":submission_token}', '"submission_token":submission_token,"visitor_id":visitor}')
 if ':visitor_id' not in t:raise SystemExit("visitor insert not applied")
 s=s[:a]+t+s[b:]
 p.write_text(s,encoding="utf-8")
 print("60-minute per-browser survey cooldown enforced server-side")
