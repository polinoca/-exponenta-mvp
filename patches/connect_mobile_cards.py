from pathlib import Path
p=Path("/app/app/templates/admin/connect.html")
s=p.read_text(encoding="utf-8")
if 'xp-connect-mobile-v2' not in s:
 s=s.replace('{% endblock %}', '''<style id="xp-connect-mobile-v2">
.xp-connect-admin,.xp-connect-admin *{box-sizing:border-box}
.xp-connect-admin{width:100%;max-width:1120px;margin-inline:auto;min-width:0}
.xp-connect-admin-head{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap}
.xp-connect-table article{min-width:0}
@media(max-width:640px){
 .xp-connect-admin{padding:28px 16px 64px!important;margin:0 auto!important;overflow-x:hidden}
 .xp-connect-admin-head{display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:22px!important;margin-bottom:24px!important}
 .xp-connect-admin-head h1{font-size:clamp(34px,10vw,44px)!important;line-height:1.05!important;letter-spacing:-.045em!important;margin:12px 0!important}
 .xp-connect-admin-head p{font-size:15px!important;line-height:1.5!important;margin:0!important}
 .xp-connect-admin-head .btn{width:100%!important;min-height:50px!important;display:flex!important;align-items:center;justify-content:center;text-align:center}
 .xp-connect-table{display:grid!important;grid-template-columns:minmax(0,1fr)!important;gap:14px!important;width:100%!important}
 .xp-connect-table article{display:grid!important;grid-template-columns:60px minmax(0,1fr)!important;gap:12px!important;align-items:center!important;padding:18px!important;border-radius:22px!important;min-width:0!important;overflow:hidden!important}
 .xp-connect-table article>div:first-child{grid-column:1!important;grid-row:1!important;width:60px!important;height:60px!important;margin:0!important}
 .xp-connect-table article>div:first-child img{max-width:100%;max-height:100%;object-fit:contain}
 .xp-connect-table article>section{grid-column:2!important;grid-row:1!important;min-width:0!important;overflow-wrap:anywhere}
 .xp-connect-table article>section strong{display:block!important;font-size:22px!important;line-height:1.2!important}
 .xp-connect-table article>section small{display:block!important;font-size:13px!important;line-height:1.5!important}
 .xp-connect-table article>a{display:flex!important;align-items:center!important;justify-content:center!important;min-height:43px!important;padding:9px 6px!important;margin:0!important;border:1px solid #e4ddd7!important;border-radius:12px!important;font-size:13px!important;font-weight:700!important;text-align:center!important;line-height:1.25!important;white-space:normal!important;text-decoration:none!important;min-width:0!important}
 .xp-connect-table article>a:nth-of-type(1){grid-column:1!important;grid-row:2!important}
 .xp-connect-table article>a:nth-of-type(2){grid-column:2!important;grid-row:2!important}
 .xp-connect-table article>a:nth-of-type(3){grid-column:1!important;grid-row:3!important}
 .xp-connect-table article>a:nth-of-type(4){grid-column:2!important;grid-row:3!important}
}
</style>
{% endblock %}''',1)
 p.write_text(s,encoding="utf-8")
print("Connect responsive cards installed")
