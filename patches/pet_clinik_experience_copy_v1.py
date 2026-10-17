from pathlib import Path

p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
marker='# XP PET CLINIK EXPERIENCE COPY V1'

if marker not in s:
    # Header on the public PET Clinik questionnaire.
    s=s.replace('¿Cómo fue tu visita?', 'Queremos conocer tu experiencia en Pet Clinik')

    # Preserve the requested optional nature of the final free-text question,
    # even when its wording was previously customized in the database.
    old_xp_pet_questions=xp_pet_questions
    def xp_pet_questions(db,slug):
        questions=old_xp_pet_questions(db,slug)
        if slug=='pet-clinick':
            questions['comment']='¿Hay algo que podamos mejorar o que quieras reconocer de nuestro servicio?'
        return questions

    p.write_text(s+'\\n'+marker+'\\n',encoding='utf-8')

print('PET Clinik questionnaire heading and optional final question updated')
