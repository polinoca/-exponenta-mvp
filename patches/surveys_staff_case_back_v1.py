from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text()
marker='# XP SURVEY BACK AND STAFF CASE V1'
assert marker not in s
a=s.index('def xp_survey_business_results(')
b=s.index('\n@app.',a)
part=s[a:b]
old='SELECT TRIM(attendant) AS person,COUNT(*) AS n,'
new='SELECT INITCAP(LOWER(TRIM(attendant))) AS person,COUNT(*) AS n,'
assert old in part
part=part.replace(old,new,1)
old='GROUP BY TRIM(attendant) ORDER BY n DESC,score DESC LIMIT 8'
new='GROUP BY LOWER(TRIM(attendant)) ORDER BY n DESC,score DESC LIMIT 8'
assert old in part
part=part.replace(old,new,1)
s=s[:a]+part+s[b:]
# Prevent accidental repeat in same browser tab after successful submission.
a=s.index('def xp_survey_public(')
b=s.index('\n@app.',a)
part=s[a:b]
old="    return xp_survey_page('Tu opinión',content)"
assert old in part
part=part.replace(old,'''    content+='<script>(function(){var key="xp_survey_completed_"+'+xp_survey_json.dumps(slug)+';if(sessionStorage.getItem(key)==="1"){location.replace("/encuesta/"+'+xp_survey_json.dumps(slug)+'+"/gracias");}window.addEventListener("pageshow",function(){if(sessionStorage.getItem(key)==="1"){location.replace("/encuesta/"+'+xp_survey_json.dumps(slug)+'+"/gracias");}});})();</script>'
'''+old,1)
s=s[:a]+part+s[b:]
a=s.index('def xp_survey_thanks(')
b=s.index('\n@app.',a)
part=s[a:b]
old="    return xp_survey_page('Gracias',body)"
assert old in part
part=part.replace(old,'''    body+='<script>try{sessionStorage.setItem("xp_survey_completed_"+'+xp_survey_json.dumps(slug)+',"1");}catch(e){}</script>'
'''+old,1)
s=s[:a]+part+s[b:]
p.write_text(s+'\n'+marker+'\n')
