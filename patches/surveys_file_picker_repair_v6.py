from pathlib import Path
p=Path('/app/app/main.py');s=p.read_text(encoding='utf-8')
marker='# XP SURVEY FILE PICKER REPAIR V6'
if marker not in s:
    start=s.find('def xp_survey_customize(');end=s.find('\n@app.',start)
    if start<0 or end<0:raise SystemExit('Customize view missing')
    sec=s[start:end]
    old='''body+='<label>'+label+'</label><input type="file" accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp" name="'+key+'" id="'+key+'" style="display:block;cursor:pointer;background:#fff;min-height:54px"><div id="'+key+'_status" class="muted" role="status" style="font-size:13px;margin:6px 0 14px">Ningún archivo elegido · logos hasta 5 MB / promociones hasta 8 MB</div>' '''
    # Instead match exact line by location
    lines=sec.splitlines()
    replaced=False
    for i,line in enumerate(lines):
        if "type=\"file\"" in line and "name=\"'+key+'\"" in line:
            lines[i]='''        body+='<div class="xp-image-upload"><label for="'+key+'" style="font-size:15px">'+label+'</label><input type="file" accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp" name="'+key+'" id="'+key+'" style="display:block!important;position:relative!important;opacity:1!important;visibility:visible!important;pointer-events:auto!important;width:100%!important;min-height:55px;border:2px dashed #8db9be;border-radius:12px;background:#f6fbfb;padding:12px;cursor:pointer"><div id="'+key+'_status" class="muted" role="status" style="font-size:13px;margin:6px 0 14px">Haz clic en Elegir archivo o arrastra tu imagen aquí</div></div>' '''
            replaced=True
    if not replaced:raise SystemExit('Expected upload input not located')
    sec='\n'.join(lines)+'\n'
    # make sure layout has no overlays that can eat clicks; add drag drop support and diagnostic
    sec=sec.replace("    return xp_survey_page('Personalizar',body,True)",'''    body+='''+'''"""<script>
document.querySelectorAll('.xp-image-upload input[type=file]').forEach(input=>{
const box=input.closest('.xp-image-upload');
box.addEventListener('dragover',e=>{e.preventDefault();box.style.background='#dff5f2'});
box.addEventListener('dragleave',()=>box.style.background='');
box.addEventListener('drop',e=>{
 e.preventDefault();box.style.background='';
 if(e.dataTransfer.files.length){try{input.files=e.dataTransfer.files;input.dispatchEvent(new Event('change',{bubbles:true}))}catch(err){document.getElementById(input.id+'_status').textContent='Selecciona el archivo con el botón';}}
});
});
</script>"""'''+'''
    return xp_survey_page('Personalizar',body,True)''')
    s=s[:start]+sec+s[end:]
    s=marker+'\n'+s
    p.write_text(s,encoding='utf-8')
print('Native file selector visibility and drag/drop restored')
