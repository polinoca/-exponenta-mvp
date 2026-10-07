from pathlib import Path

p=Path("/app/app/main.py")
s=p.read_text(encoding="utf-8")

# Ensure persistent field exists.
needle='db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS button_border_color VARCHAR(16)"))'
if needle in s and 'hub_background_color VARCHAR(16)' not in s:
    s=s.replace(
        needle,
        needle+'\n    db.execute(xp_sql_text("ALTER TABLE exponenta_connect_profiles ADD COLUMN IF NOT EXISTS hub_background_color VARCHAR(16)"))',
        1
    )

# Add field to both Connect save endpoints.
for func_name in ("exponenta_connect_save","business_connect_save"):
    start=s.find("def "+func_name+"(")
    if start<0:
        start=s.find("async def "+func_name+"(")
    end=s.find("\n):", start)
    if start>=0 and end>start:
        sig=s[start:end]
        if "hub_background_color: str = Form(" not in sig and 'brand_color: str = Form("#6b3b22"),' in sig:
            sig=sig.replace(
                'brand_color: str = Form("#6b3b22"),',
                'brand_color: str = Form("#6b3b22"),\n    hub_background_color: str = Form("#f7f4f0"),',
                1
            )
            s=s[:start]+sig+s[end:]

# Validate background in both save bodies wherever brand color validation appears.
# Keep it intentionally simple: hex only.
for func_name in ("exponenta_connect_save","business_connect_save"):
    start=s.find("def "+func_name+"(")
    if start<0:
        start=s.find("async def "+func_name+"(")
    end=s.find("\n@app.", start)
    if start>=0:
        if end<0: end=len(s)
        block=s[start:end]
        if "hub_background_color = " not in block:
            marker='''if len(brand_color) != 7 or not brand_color.startswith("#"):
        brand_color = "#6b3b22"'''
            marker2='''if len(brand_color)!=7 or not brand_color.startswith("#"):
        brand_color = getattr(org,"brand_color",None) or "#6b3b22"'''
            add='''\n    if len(hub_background_color)!=7 or not hub_background_color.startswith("#"):
        hub_background_color = "#f7f4f0"'''
            if marker in block:
                block=block.replace(marker,marker+add,1)
            elif marker2 in block:
                block=block.replace(marker2,marker2+add,1)
        # Values dict.
        if '"hub_background_color": hub_background_color' not in block and '"hub_background_color":hub_background_color' not in block:
            block=block.replace(
                '"brand_color": brand_color, "button_border_color": button_border_color,',
                '"brand_color": brand_color, "hub_background_color": hub_background_color, "button_border_color": button_border_color,',
                1
            )
            block=block.replace(
                '"brand_color":brand_color,"button_border_color":button_border_color,',
                '"brand_color":brand_color,"hub_background_color":hub_background_color,"button_border_color":button_border_color,',
                1
            )
        # INSERT columns/values.
        block=block.replace(
            '(slug,name,subtitle,brand_color,button_border_color,',
            '(slug,name,subtitle,brand_color,hub_background_color,button_border_color,'
        )
        block=block.replace(
            '(:slug,:name,:subtitle,:brand_color,:button_border_color,',
            '(:slug,:name,:subtitle,:brand_color,:hub_background_color,:button_border_color,'
        )
        block=block.replace(
            '(organization_id,slug,name,subtitle,brand_color,button_border_color,',
            '(organization_id,slug,name,subtitle,brand_color,hub_background_color,button_border_color,'
        )
        block=block.replace(
            '(:organization_id,:slug,:name,:subtitle,:brand_color,:button_border_color,',
            '(:organization_id,:slug,:name,:subtitle,:brand_color,:hub_background_color,:button_border_color,'
        )
        # UPSERT update.
        block=block.replace(
            'brand_color=EXCLUDED.brand_color, button_border_color=EXCLUDED.button_border_color,',
            'brand_color=EXCLUDED.brand_color, hub_background_color=EXCLUDED.hub_background_color, button_border_color=EXCLUDED.button_border_color,'
        )
        block=block.replace(
            'brand_color=EXCLUDED.brand_color,button_border_color=EXCLUDED.button_border_color,',
            'brand_color=EXCLUDED.brand_color,hub_background_color=EXCLUDED.hub_background_color,button_border_color=EXCLUDED.button_border_color,'
        )
        s=s[:start]+block+s[end:]

p.write_text(s,encoding="utf-8")

# Public mini hub: use the chosen background.
pub=Path("/app/app/templates/connect/profile.html")
t=pub.read_text(encoding="utf-8")
t=t.replace(
    '--bg:#f7f4f0;--card:#ffffff;',
    "--bg:{{ profile.hub_background_color or '#f7f4f0' }};--card:#ffffff;",
    1
)
pub.write_text(t,encoding="utf-8")

# Business editor: remove literal \\n artifact and add one simple background picker.
biz=Path("/app/app/templates/business/connect.html")
b=biz.read_text(encoding="utf-8")
b=b.replace('</label>\\n      <label>Color del marco de botones','</label>\n      <label>Color del marco de botones')
if 'name="hub_background_color"' not in b:
    marker='<label>Color de marca<input type="color" name="brand_color" value="{{ profile.brand_color if profile and profile.brand_color else organization.brand_color or \'#6b3b22\' }}"></label>'
    add=marker+'\n      <label>Fondo del Hub<input type="color" name="hub_background_color" value="{{ profile.hub_background_color if profile and profile.hub_background_color else \'#f7f4f0\' }}"></label>'
    if marker in b:
        b=b.replace(marker,add,1)
biz.write_text(b,encoding="utf-8")

# Superadmin editor: same single setting.
adm=Path("/app/app/templates/admin/connect_edit.html")
a=adm.read_text(encoding="utf-8")
a=a.replace('</label>\\n      <label>Color del marco de botones','</label>\n      <label>Color del marco de botones')
if 'name="hub_background_color"' not in a:
    candidates=[
      '<label>Color de marca<input type="color" name="brand_color" value="{{ profile.brand_color if profile and profile.brand_color else \'#6b3b22\' }}"></label>',
      '<label>Color de marca<input type="color" name="brand_color" value="{{ profile.brand_color if profile else \'#6b3b22\' }}"></label>'
    ]
    for marker in candidates:
        if marker in a:
            a=a.replace(marker,marker+'\n      <label>Fondo del Hub<input type="color" name="hub_background_color" value="{{ profile.hub_background_color if profile and profile.hub_background_color else \'#f7f4f0\' }}"></label>',1)
            break
adm.write_text(a,encoding="utf-8")

print("Connect hub background color and literal newline fix installed")
