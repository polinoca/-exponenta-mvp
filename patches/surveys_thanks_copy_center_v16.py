from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY THANK YOU COPY AND PROMO CENTER V16"
if marker not in s:
 a=s.index("def xp_survey_thanks(")
 b=s.index("\n@app.",a)
 t=s[a:b]
 t=t.replace('xp_html.escape(p["thanks_text"] or "Tu experiencia nos ayuda a seguir mejorando.")','xp_html.escape("Tu experiencia nos ayuda a seguir mejorando.")')
 t=t.replace('Muestra este beneficio al personal. Aplican las condiciones indicadas.','Menciona el beneficio al personal. Aplican condiciones.')
 t=t.replace('.xp-promo-copy{padding:15px 9px 8px}', '.xp-promo-copy{padding:15px 9px 8px;text-align:center}')
 t=t.replace('.xp-promo{margin-top:28px;', '.xp-promo{margin-top:28px;')
 t=t.replace('if p["promo_code"]:', 'if (p["promo_code"] or "").strip():')
 t=t.replace("body+='<div class=\"xp-promo-copy\"><h2>'", "body+='<div class=\"xp-promo-copy\"><h2>'")
 # Keeps promo photo and information centered when no code or date was configured.
 s=s[:a]+t+s[b:]
 p.write_text(marker+"\n"+s,encoding="utf-8")
print("Thank-you text corrected, promotion details centered and optional code hidden when empty")
