from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text()
assert '# XP IMAGE RESIZE V1' not in s
a=s.index('def xp_survey_data_image(')
b=s.index('\n@app.',a)
s=s[:a]+'''def xp_survey_data_image(filedata,filename,maximum=12*1024*1024):
    from PIL import ImageOps, UnidentifiedImageError
    if not filedata or len(filedata)>maximum:
        raise HTTPException(422,'Imagen demasiado grande: máximo 12 MB')
    try:
        with xp_survey_Image.open(xp_survey_io.BytesIO(filedata)) as source:
            if source.format not in ('PNG','JPEG','WEBP'):
                raise HTTPException(422,'Solo PNG, JPG o WebP')
            if source.width*source.height>20000000:
                raise HTTPException(422,'Máximo 20 megapíxeles')
            source.load()
            im=ImageOps.exif_transpose(source)
            im.thumbnail((1200,1200))
            if im.mode in ('RGBA','LA') or 'transparency' in im.info:
                rgba=im.convert('RGBA')
                rgb=xp_survey_Image.new('RGB',rgba.size,'white')
                rgb.paste(rgba,mask=rgba.getchannel('A'))
            else:
                rgb=im.convert('RGB')
            dst=xp_survey_io.BytesIO()
            rgb.save(dst,format='JPEG',quality=80,optimize=True)
            return 'data:image/jpeg;base64,'+xp_survey_b64.b64encode(dst.getvalue()).decode('ascii')
    except HTTPException:
        raise
    except (OSError,ValueError,UnidentifiedImageError,xp_survey_Image.DecompressionBombError):
        raise HTTPException(422,'No se pudo procesar la imagen')
'''+s[b:]
a=s.index('def xp_business_survey_promotion(')
b=s.index('\n@app.',a)
part=s[a:b]
part=part.replace("    body+='<label>Imagen del producto o promoción</label>", """    if p['promotion_image']:
        body+='<label><input type="checkbox" name="remove_promotion_image" value="1"> Eliminar imagen actual al guardar</label>'
    body+='<p class="muted">JPG, PNG o WebP hasta 12 MB. Se ajusta automáticamente.</p>'
    body+='<label>Imagen del producto o promoción</label>""",1)
s=s[:a]+part+s[b:]
a=s.index('async def xp_business_survey_promotion_update(')
b=s.index('\n@app.',a)
part=s[a:b]
part=part.replace("    file=form.get('promotion_file')", """    if str(form.get('remove_promotion_image') or '')=='1':
        updates['image']=None
    file=form.get('promotion_file')""",1)
part=part.replace("    if file is not None and getattr(file,'filename',None):","    if file is not None and getattr(file,'filename',None) and str(form.get('remove_promotion_image') or '')!='1':",1)
s=s[:a]+part+s[b:]
a=s.index('def xp_survey_customize(')
b=s.index('\n@app.',a)
part=s[a:b]
part=part.replace("    if p['logo_data']:body+=", """    if p['logo_data']:
        body+='<label><input type="checkbox" name="remove_logo" value="1"> Eliminar logotipo actual al guardar</label>'
    if p['promotion_image']:
        body+='<label><input type="checkbox" name="remove_promotion_image" value="1"> Eliminar imagen de promoción al guardar</label>'
    if p['logo_data']:body+=""",1)
s=s[:a]+part+s[b:]
a=s.index("updates={'slug':slug,'color':")
b=s.index('\n@app.',a)
part=s[a:b]
part=part.replace("    for key in ['color','secondary']:", """    if str(form.get('remove_logo') or '')=='1':
        updates['logo']=None
    if str(form.get('remove_promotion_image') or '')=='1':
        updates['image']=None
    for key in ['color','secondary']:""",1)
part=part.replace("        if obj is not None and getattr(obj,'filename',None):","        if obj is not None and getattr(obj,'filename',None) and not (str(form.get('remove_logo') or '')=='1' if dest=='logo' else str(form.get('remove_promotion_image') or '')=='1'):",1)
s=s[:a]+part+s[b:]
p.write_text(s+'\n# XP IMAGE RESIZE V1\n')
