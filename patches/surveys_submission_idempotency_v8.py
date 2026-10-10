from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
marker="# XP SURVEY SUBMISSION IDEMPOTENCY V8"
if marker not in s:
    if "async def xp_survey_submit(" not in s:raise SystemExit("Survey submit handler not found")
    s=marker+"\n"+s
    s=s.replace("import csv as xp_survey_csv","import csv as xp_survey_csv\nimport uuid as xp_survey_uuid",1)
    start=s.index("def xp_survey_public(");end=s.index("\n@app.",start)
    part=s[start:end]
    target="content+='<button class=\"btn\" type=\"submit\">Enviar mi opinión</button></form></div>'"
    if target not in part: raise SystemExit("Survey submit form location unavailable")
    part=part.replace(target,'''content+='<input type="hidden" name="submission_token" value="'+xp_survey_uuid.uuid4().hex+'">'
    content+='<button class="btn" type="submit">Enviar mi opinión</button></form></div>' ''')
    s=s[:start]+part+s[end:]
    start=s.index("async def xp_survey_submit(");end=s.index("\n@app.",start);part=s[start:end]
    part=part.replace("request:Request,overall:int=Form(...)", "request:Request,submission_token:str=Form(...),overall:int=Form(...)")
    if "submission_token:str=Form(...)" not in part:raise SystemExit("Could not add token form param")
    target="    submission=None"
    if target not in part:raise SystemExit("Insert location unavailable")
    part=part.replace(target,'''    xp_survey_token_valid=bool(xp_survey_re.fullmatch(r"[a-f0-9]{32}",submission_token))
    if not xp_survey_token_valid:raise HTTPException(422,"Identificador de encuesta inválido")
    db.execute(xp_survey_sql("ALTER TABLE xp_survey_responses ADD COLUMN IF NOT EXISTS submission_token VARCHAR(32)"))
    db.execute(xp_survey_sql("CREATE UNIQUE INDEX IF NOT EXISTS xp_survey_response_token_unique ON xp_survey_responses(slug,submission_token) WHERE submission_token IS NOT NULL"))
    db.commit()
    submission=None''')
    part=part.replace("attendant,comment)\n      VALUES (:slug,:overall,:cleanliness,:clarity,:attendant,:comment) RETURNING id", "attendant,comment,submission_token)\n      VALUES (:slug,:overall,:cleanliness,:clarity,:attendant,:comment,:submission_token) ON CONFLICT DO NOTHING RETURNING id")
    part=part.replace('"comment":comment.strip()[:1000]}','"comment":comment.strip()[:1000],"submission_token":submission_token}')
    part=part.replace("    submission_id=submission.scalar_one()",'''    submission_id=submission.scalar_one_or_none()
    if submission_id is None:
        db.rollback()
        return RedirectResponse("/encuesta/"+slug+"/gracias",status_code=303)''')
    if "ON CONFLICT DO NOTHING RETURNING id" not in part:raise SystemExit("Idempotent insert failed to install")
    s=s[:start]+part+s[end:]
    p.write_text(s,encoding="utf-8")
print("Survey form uses a one-time token and database-backed replay protection")
