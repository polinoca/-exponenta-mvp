from pathlib import Path
p=Path('/app/app/main.py')
s=p.read_text(encoding='utf-8')
tag='# SURVEY TENANT MOBILE THEME'
if tag not in s:
    helper='''# SURVEY TENANT MOBILE THEME
def xp_survey_business_theme(title, body, brand):
    primary=brand.get('brand_color') or '#2D71B1'
    secondary=brand.get('secondary_color') or '#4BB8DE'
    if not xp_survey_re.fullmatch(r'#[0-9A-Fa-f]{6}', primary):primary='#2D71B1'
    if not xp_survey_re.fullmatch(r'#[0-9A-Fa-f]{6}', secondary):secondary='#4BB8DE'
    css="<style>:root{--primary:"+primary+";--secondary:"+secondary+"}body{background:#f6f8fb}header{background:var(--primary);color:white}header a{color:white}.btn{background:var(--primary);min-height:48px}.btn.secondary{background:#eaf2f8;color:var(--primary)}.metric strong{color:var(--primary)}input,select,textarea{font-size:16px} @media(max-width:640px){main{padding:18px 13px 70px}.card{padding:16px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.btn{width:100%;margin:7px 0}.scroll table{min-width:0}.scroll thead{display:none}.scroll tr{display:block;padding:10px;border:1px solid #dce4ee;border-radius:12px;margin:10px 0}.scroll td{display:block;border:0;overflow-wrap:anywhere}.scroll td:before{content:attr(data-label);display:block;font-size:12px;font-weight:700;color:var(--primary)}}</style>"
    css+='<style>.xp-business-logo-badge{width:132px;height:132px;display:flex;align-items:center;justify-content:center;box-sizing:border-box;padding:19px;margin:10px auto 22px;background:#fff;border:1px solid #dcecf5;border-radius:50%;box-shadow:0 8px 24px rgba(29,94,148,.10);overflow:hidden}.xp-business-logo-badge img{width:100%;height:100%;min-width:0;min-height:0;max-width:100%;max-height:100%;object-fit:contain}@media(max-width:600px){.xp-business-logo-badge{width:116px;height:116px;padding:16px;margin:5px auto 17px}}.xp-db-actions a,.xp-db-tabs a{touch-action:manipulation;min-height:44px}.xp-db-panel,.xp-db-stat{min-width:0}.xp-db-grid,.xp-db-stats{width:100%;max-width:100%}@media(max-width:380px){.xp-db-stats{gap:9px}.xp-db-stat{padding:12px 10px}.xp-db-tabs{gap:5px}.xp-db-tabs a{padding:7px 10px}}</style>'
    if brand.get('logo_data'):
        body='<div class="xp-business-logo-badge"><img alt="Logotipo del negocio" src="'+xp_html.escape(brand['logo_data'],quote=True)+'"></div>'+body
    return xp_survey_page(title,body).replace('</head>',css+'</head>',1)

'''
    key='@app.get("/negocio/encuestas",response_class=HTMLResponse)'
    assert key in s
    s=s.replace(key,helper+key,1)
    s=s.replace('SELECT slug,name FROM xp_surveys WHERE organization_id=', 'SELECT slug,name,brand_color,secondary_color,logo_data FROM xp_surveys WHERE organization_id=',1)
    s=s.replace('return xp_survey_page("Encuestas",body+\'</div>\')','return xp_survey_business_theme("Encuestas",body+\'</div>\',dict(rows[0]) if rows else {})',1)
    s=s.replace('return xp_survey_page("Resultados",body+\'</tbody></table></div></div>\')','return xp_survey_business_theme("Resultados",body+\'</tbody></table></div></div>\',p)',1)
    s=s.replace("'<td>'+xp_html.escape(str(r[k] or \"\"))+'</td>'", "'<td data-label=\"'+k+'\">'+xp_html.escape(str(r[k] or \"\"))+'</td>'")
    p.write_text(s,encoding='utf-8')
print('Business survey theme and mobile card layout installed')
