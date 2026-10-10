from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
marker="# XP SURVEY AUTO IMAGE OPTIMIZATION V5"
if marker not in s:
    s=marker+"\n"+s
    start=s.index("def xp_survey_data_image(")
    end=s.index("\n@app.",start)
    new=r'''def xp_survey_data_image(filedata,filename,maximum=None):
    from PIL import ImageOps,UnidentifiedImageError
    is_logo=bool(filename.startswith("__logo__:"))
    limit=5*1024*1024 if is_logo else 8*1024*1024
    if len(filedata)>limit:
        raise HTTPException(422,'Imagen supera el límite de '+('5' if is_logo else '8')+' MB')
    try:
        image=xp_survey_Image.open(xp_survey_io.BytesIO(filedata))
        if image.format not in ('PNG','JPEG','WEBP'):
            raise HTTPException(422,'Usa PNG, JPG o WebP')
        image=ImageOps.exif_transpose(image)
        image.thumbnail((1400,1400),xp_survey_Image.Resampling.LANCZOS)
        transparent=is_logo and ('A' in image.getbands() or 'transparency' in image.info)
        if transparent:
            image=image.convert('RGBA')
            mode='WEBP';mime='image/webp'
        else:
            if image.mode!='RGB':image=image.convert('RGB')
            mode='JPEG';mime='image/jpeg'
        target=2*1024*1024
        for maxdimension in (1400,1100,850,650,450):
            if max(image.size)>maxdimension:
                image.thumbnail((maxdimension,maxdimension),xp_survey_Image.Resampling.LANCZOS)
            for quality in (90,82,72,60,48):
                output=xp_survey_io.BytesIO()
                image.save(output,format=mode,quality=quality,optimize=True)
                payload=output.getvalue()
                if len(payload)<=target:
                    return 'data:'+mime+';base64,'+xp_survey_b64.b64encode(payload).decode('ascii')
        raise HTTPException(422,'No fue posible optimizar esta imagen')
    except (UnidentifiedImageError,OSError,ValueError) as err:
        raise HTTPException(422,'El archivo no es una imagen válida') from err

'''
    s=s[:start]+new+s[end:]
    s=s.replace("updates[dest]=xp_survey_data_image(data,obj.filename)","updates[dest]=xp_survey_data_image(data,('__logo__:' if dest=='logo' else '')+obj.filename)")
    # Keep color detection on original image; it is processed just once.
    s=s.replace('Ningún archivo elegido · máximo 2 MB','Ningún archivo elegido · logos hasta 5 MB / promociones hasta 8 MB')
    s=s.replace('if(f&&f.size>2097152){status.textContent="El archivo supera 2 MB. Selecciona otro.";el.value="";}', 'if(f&&f.size>(id==="logo_file"?5242880:8388608)){status.textContent="El archivo supera el límite permitido.";el.value="";}else if(f){status.textContent+=" · se optimizará automáticamente al guardar";}')
    # Business promotions have same upgraded conversion function; user-facing text for business page
    p.write_text(s,encoding='utf-8')
print('Auto compression of survey logos and promotion images enabled')
