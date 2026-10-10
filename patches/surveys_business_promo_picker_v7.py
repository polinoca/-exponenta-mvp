from pathlib import Path
p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")
marker="# XP SURVEY BUSINESS PROMO PICKER V7"
if marker not in s:
    start=s.find('def xp_business_survey_promotion(')
    end=s.find('\n@app.',start)
    if start<0 or end<0:raise SystemExit('Business promotion form missing')
    part=s[start:end]
    old="""body+='<label>Imagen del producto o promoción</label><input type="file" name="promotion_file" accept="image/png,image/jpeg,image/webp">'"""
    new="""body+='<div class="xp-promo-upload"><label for="promotion_file">Imagen del producto o promoción</label><input id="promotion_file" type="file" name="promotion_file" accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp" style="display:block!important;position:relative!important;opacity:1!important;visibility:visible!important;pointer-events:auto!important;width:100%!important;min-height:55px;border:2px dashed #8db9be;border-radius:12px;background:#f6fbfb;padding:12px;cursor:pointer"><p id="promo_file_status" class="muted" role="status">Selecciona una imagen de hasta 8 MB o arrástrala aquí. Se optimizará al guardar.</p></div>'"""
    if old not in part:raise SystemExit('Promotion input changed')
    part=part.replace(old,new)
    oldreturn="    return xp_survey_page('Promoción',body)"
    js="""    body+='''<script>document.addEventListener("DOMContentLoaded",()=>{const box=document.querySelector(".xp-promo-upload"),input=document.getElementById("promotion_file"),status=document.getElementById("promo_file_status");if(!box||!input)return;const show=()=>{const file=input.files&&input.files[0];status.textContent=file?(file.name+" · "+Math.round(file.size/1024)+" KB · "+(file.size>8388608?"Supera 8 MB":"Listo para guardar; optimización automática")):"Selecciona una imagen o arrástrala aquí";};input.addEventListener("change",show);box.addEventListener("dragover",e=>{e.preventDefault();box.style.background="#dff5f2"});box.addEventListener("dragleave",()=>box.style.background="");box.addEventListener("drop",e=>{e.preventDefault();box.style.background="";if(e.dataTransfer.files.length){input.files=e.dataTransfer.files;show();}});});</script>'''
    return xp_survey_page('Promoción',body)"""
    if oldreturn not in part:raise SystemExit('Promotion return missing')
    part=part.replace(oldreturn,js)
    s=s[:start]+part+s[end:]
    p.write_text(marker+"\n"+s,encoding="utf-8")
print("Promotion image file picker enabled for business account")
