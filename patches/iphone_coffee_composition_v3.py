from pathlib import Path
p=Path("/app/app/static/app.css")
s=p.read_text(encoding="utf-8")
if "/* XP IPHONE COFFEE COMPOSITION V3 */" not in s:
    s+=r'''
/* XP IPHONE COFFEE COMPOSITION V3 */
@media (max-device-width:760px), (max-width:760px){
  .xp-launch-float{width:180px!important;min-height:68px!important;gap:7px!important;padding:9px 10px!important;border-radius:14px!important}
  .xp-launch-float b{width:26px!important;height:26px!important;flex:0 0 26px!important}
  .xp-launch-float strong,.xp-launch-float small{font-size:.58rem!important;line-height:1.18!important}
  .xp-launch-float.one{left:18px!important;right:auto!important;top:auto!important;bottom:28px!important}
  .xp-launch-float.two{left:auto!important;right:18px!important;top:auto!important;bottom:28px!important}
}
'''
p.write_text(s,encoding="utf-8")
print("iPhone coffee composition adjusted")
