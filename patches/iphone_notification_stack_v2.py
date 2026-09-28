from pathlib import Path
p=Path("/app/app/static/app.css")
s=p.read_text(encoding="utf-8")
if "/* XP IPHONE FLOAT STACK V2 */" not in s:
    s+=r'''
/* XP IPHONE FLOAT STACK V2 */
@media (max-device-width:760px), (max-width:760px){
  .xp-launch-device{min-height:650px!important;overflow:hidden!important}
  .xp-launch-float{z-index:5!important;left:20px!important;right:20px!important;max-width:none!important}
  .xp-launch-float.one{top:auto!important;bottom:150px!important}
  .xp-launch-float.two{top:auto!important;bottom:35px!important}
}
'''
p.write_text(s,encoding="utf-8")
print("iPhone notification stack adjusted")
