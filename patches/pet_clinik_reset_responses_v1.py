from pathlib import Path

p = Path('/app/app/main.py')
s = p.read_text(encoding='utf-8')
marker = '# XP PET CLINIK RESET RESPONSES V1'

if marker not in s:
    anchor = '''        bootstrap_superadmin(db)
    yield
'''
    replacement = '''        bootstrap_superadmin(db)
        # XP PET CLINIK RESET RESPONSES V1
        # One-time cleanup of test submissions; the database marker prevents future data from being touched.
        db.execute(text("""CREATE TABLE IF NOT EXISTS xp_maintenance_flags (
          flag VARCHAR(120) PRIMARY KEY, executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""))
        reset_flag = db.execute(text("""INSERT INTO xp_maintenance_flags(flag) VALUES ('pet_clinik_reset_20261025')
          ON CONFLICT (flag) DO NOTHING RETURNING flag""")).scalar()
        if reset_flag:
            db.execute(text("""DELETE FROM xp_pet_clinik_extras WHERE response_id IN
              (SELECT id FROM xp_survey_responses WHERE slug='pet-clinick')"""))
            db.execute(text("""DELETE FROM xp_survey_answers WHERE response_id IN
              (SELECT id FROM xp_survey_responses WHERE slug='pet-clinick')"""))
            db.execute(text("DELETE FROM xp_survey_responses WHERE slug='pet-clinick'"))
            db.commit()
    yield
'''
    if anchor not in s:
        raise RuntimeError('Lifespan anchor not found; reset was not installed')
    p.write_text(s.replace(anchor, replacement, 1), encoding='utf-8')

print('PET Clinik test responses will reset once at next application startup')
