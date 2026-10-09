from pathlib import Path

main = Path('/app/app/main.py')
s = main.read_text(encoding='utf-8')
marker = '# XP SEED ARMONIA PARA TUS PIES'
if marker in s:
    raise SystemExit(0)

needle = 'def xp_connect_profile(db, slug: str):\n    xp_connect_ensure(db)\n    return db.execute('
if needle not in s:
    raise SystemExit('xp_connect_profile anchor not found')

replacement = '''# XP SEED ARMONIA PARA TUS PIES\ndef xp_seed_armonia(db):\n    row = db.execute(\n        xp_sql_text("SELECT slug FROM exponenta_connect_profiles WHERE slug=:slug"),\n        {"slug": "armonia-para-tus-pies"},\n    ).first()\n    if row:\n        return\n    db.execute(xp_sql_text("""\n        INSERT INTO exponenta_connect_profiles\n        (slug,name,subtitle,brand_color,google_url,whatsapp,maps_url,phone,address,active)\n        VALUES\n        (:slug,:name,:subtitle,:brand_color,:google_url,:whatsapp,:maps_url,:phone,:address,1)\n    """), {\n        "slug": "armonia-para-tus-pies",\n        "name": "Armonía para tus pies",\n        "subtitle": "Podología",\n        "brand_color": "#6b3b22",\n        "google_url": "https://search.google.com/local/writereview?placeid=ChIJL8lHc92vKIQRREL7VGePJdA",\n        "whatsapp": "https://wa.me/523316563386",\n        "maps_url": "https://www.google.com/maps/search/?api=1&query=Cuitl%C3%A1huac%2075%2C%20Centro%2C%2045100%20Zapopan%2C%20Jalisco",\n        "phone": "3316563386",\n        "address": "Cuitláhuac #75, Col. Centro, 45100 Zapopan, Jalisco, México",\n    })\n    db.commit()\n\ndef xp_connect_profile(db, slug: str):\n    xp_connect_ensure(db)\n    xp_seed_armonia(db)\n    return db.execute('''

s = s.replace(needle, replacement, 1)
main.write_text(s, encoding='utf-8')
