from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
marker="# XP SURVEY CHECK SKY BLUE V18"
if marker not in s:
 a=s.index("def xp_survey_thanks(");b=s.index("\n@app.",a);t=s[a:b]
 t=t.replace("    body+='</section>'","    body+='<style>.xp-thanks-check,.xp-confetti-wrap .xp-thanks-check{background:#4BB8DE!important;color:#fff!important}</style>'\n    body+='</section>'",1)
 if ".xp-thanks-check,.xp-confetti-wrap" not in t:raise SystemExit("Checkmark color patch failed")
 s=s[:a]+t+s[b:];p.write_text(marker+"\n"+s,encoding="utf-8")
print("Confirmation check button is now #4BB8DE")
