from pathlib import Path
p=Path("/app/app/templates/connect/profile.html")
s=p.read_text(encoding="utf-8")
s=s.replace('<span class="xp-eyebrow">EXPONENTA CONNECT</span>','')
s=s.replace('<small>Conoce más del negocio</small>','<small>Síguenos y conoce más</small>')
s=s.replace('<footer class="xp-foot">Conectado por <b>Exponenta</b></footer>','<footer class="xp-foot">Powered by <b>Exponenta</b></footer>')
p.write_text(s,encoding="utf-8")
print("Public Connect labels updated")
