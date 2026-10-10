from pathlib import Path
p=Path('/app/app/main.py');s=p.read_text(encoding='utf-8')
if '# XP SURVEY UPLOAD UX FIX V4' not in s:
    s='# XP SURVEY UPLOAD UX FIX V4\n'+s
    # Fix QR API
    s=s.replace('qr.add(str(request.base_url).rstrip("/")+"/encuesta/"+slug)','qr.add_data(str(request.base_url).rstrip("/")+"/encuesta/"+slug)')
    # Improve chooser and feedback without replacing native input capability.
    a=s.find('def xp_survey_customize(');b=s.find('\n@app.',a)
    if a<0 or b<0:raise SystemExit("Personalization endpoint missing")
    sec=s[a:b]
    sec=sec.replace("""body+='<label>'+label+'</label><input type="file" accept="image/png,image/jpeg,image/webp" name="'+key+'">'""",
"""body+='<label>'+label+'</label><input type="file" accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp" name="'+key+'" id="'+key+'" style="display:block;cursor:pointer;background:#fff;min-height:54px"><div id="'+key+'_status" class="muted" role="status" style="font-size:13px;margin:6px 0 14px">Ningún archivo elegido · máximo 2 MB</div>'""")
    sec=sec.replace("    body+='<div class=\"card\"><h2>Preguntas adicionales</h2>", """    body+='<script>document.addEventListener("DOMContentLoaded",()=>{for(const id of ["logo_file","promotion_file"]){const el=document.getElementById(id),status=document.getElementById(id+"_status");if(!el)continue;el.addEventListener("change",()=>{let f=el.files&&el.files[0];status.textContent=f?(f.name+" · "+Math.round(f.size/1024)+" KB · seleccionado, pulsa Guardar cambios"):"Ningún archivo seleccionado";status.style.color=f?"#05716b":"#65757d";if(f&&f.size>2097152){status.textContent="El archivo supera 2 MB. Selecciona otro.";el.value="";}})}})</script>'
    body+='<div class="card"><h2>Preguntas adicionales</h2>""")
    s=s[:a]+sec+s[b:]
    p.write_text(s,encoding='utf-8')
print('Survey logo upload selector feedback and QR route repaired')
