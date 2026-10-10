from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY MEXICO TIME V12"
if marker not in s:
    local="((created_at AT TIME ZONE 'UTC') AT TIME ZONE 'America/Mexico_City')"
    a=s.index("def xp_survey_details(");b=s.index("\n@app.",a)
    t=s[a:b]
    t=t.replace("SELECT * FROM xp_survey_responses WHERE slug=:slug ORDER BY created_at DESC LIMIT 100","SELECT *, to_char("+local+",'DD/MM/YYYY HH24:MI') AS created_local FROM xp_survey_responses WHERE slug=:slug ORDER BY created_at DESC LIMIT 100")
    t=t.replace("r['created_at'],r['overall']", "r['created_local'],r['overall']")
    s=s[:a]+t+s[b:]
    a=s.index("def xp_survey_csv_export(");b=s.index("\n",s.index("    return Response(",a))
    t=s[a:b]
    t=t.replace("SELECT created_at,overall,cleanliness,clarity,attendant,comment", "SELECT to_char("+local+",'DD/MM/YYYY HH24:MI:SS') AS created_at,overall,cleanliness,clarity,attendant,comment")
    t=t.replace("['Fecha','Atención'", "['Fecha (Guadalajara / Ciudad de México)','Atención'")
    s=s[:a]+t+s[b:]
    a=s.index("def xp_survey_analytics(");b=s.index("\n@app.",a)
    t=s[a:b]
    t=t.replace("to_char(created_at,'YYYY-MM')", "to_char("+local+",'YYYY-MM')")
    t=t.replace("SELECT attendant,comment,overall,created_at FROM xp_survey_responses", "SELECT attendant,comment,overall,to_char("+local+",'DD/MM/YYYY HH24:MI') AS created_at FROM xp_survey_responses")
    s=s[:a]+t+s[b:]
    s=marker+"\n"+s
    p.write_text(s,encoding="utf-8")
print("Survey reports, analytics filters and CSV display Mexico local time")

