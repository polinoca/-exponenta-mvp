from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK EXPERIENCE COPY V1'

if marker not in s:
    # The public survey uses this phrase only as its visible headline.
    s=s.replace('¿Cómo fue tu visita?', 'Queremos conocer tu experiencia en Pet Clinik')
    s=s.replace('''<p class="muted" style="margin:0 0 19px">Queremos conocer tu experiencia en '+xp_html.escape(p["name"])+'</p>''', '')
    s=s.replace('¿Quieres compartir algún comentario?', '¿Hay algo que podamos mejorar o que quieras reconocer de nuestro servicio?')
    runtime=r'''
# XP PET CLINIK EXPERIENCE COPY V1
_xp_pet_questions_before_experience_copy = xp_pet_questions
def xp_pet_questions(db,slug):
    questions=_xp_pet_questions_before_experience_copy(db,slug)
    if slug=='pet-clinick':
        questions['comment']='¿Hay algo que podamos mejorar o que quieras reconocer de nuestro servicio?'
    return questions
'''
    p.write_text(s+'\n'+runtime+'\n',encoding='utf-8')

print('PET Clinik questionnaire heading and optional final question updated')
