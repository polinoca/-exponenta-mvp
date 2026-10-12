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
p.write_text(s+'\n# XP IMAGE RESIZE V1\n')
