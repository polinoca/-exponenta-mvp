from pathlib import Path

# OPERATOR SUCCESS FEEDBACK + CONTROLLED OPEN WALLET TESTING
main_path = Path("/app/app/main.py")
main = main_path.read_text(encoding="utf-8")

css_old = '#result{{margin-top:14px;font-weight:800}}</style>'
css_new = '#result{{margin-top:14px;font-weight:800}}.xp-stamp-success{{position:fixed;inset:0;z-index:99;display:grid;place-items:center;background:#142318b8;color:#fff;text-align:center;padding:28px}}.xp-stamp-success .mark{{width:88px;height:88px;border-radius:50%;background:#8bdb79;color:#173d1e;display:grid;place-items:center;margin:auto;font-size:3rem;font-weight:900;box-shadow:0 8px 28px #0008}}.xp-stamp-success h2{{font-size:2.2rem;margin:14px 0 5px}}.xp-stamp-success p{{color:#edf9ed;font-size:1rem}}.xp-burst{{position:absolute;width:9px;height:16px;border-radius:3px;animation:xp-burst .9s ease-out forwards}}@keyframes xp-burst{{to{{transform:translate(var(--x),var(--y)) rotate(520deg);opacity:0}}}}</style>'
if css_old in main and ".xp-stamp-success" not in main:
    main = main.replace(css_old, css_new, 1)

js_old = 'if(x.ok){{navigator.vibrate&&navigator.vibrate(80);b.textContent="¡Sello agregado!";r.textContent=d.message}}else{{b.disabled=false;b.textContent="Agregar sello";r.textContent=d.detail||"No se pudo registrar."}}'
js_new = '''if(x.ok){{
  navigator.vibrate&&navigator.vibrate([55,35,100]);
  try{{const C=window.AudioContext||window.webkitAudioContext,a=new C(),o=a.createOscillator(),g=a.createGain();o.frequency.setValueAtTime(880,a.currentTime);o.frequency.exponentialRampToValueAtTime(1320,a.currentTime+.12);g.gain.setValueAtTime(.0001,a.currentTime);g.gain.exponentialRampToValueAtTime(.12,a.currentTime+.02);g.gain.exponentialRampToValueAtTime(.0001,a.currentTime+.22);o.connect(g);g.connect(a.destination);o.start();o.stop(a.currentTime+.23)}}catch(e){{}}
  b.textContent="¡Sello agregado!";r.textContent=d.message;
  const e=document.createElement("div");e.className="xp-stamp-success";e.innerHTML='<div><div class="mark">✓</div><h2>¡Visita registrada!</h2><p>'+d.message+'</p></div>';
  ["#f7b24a","#f06f63","#83d274","#76b8e4","#f3e6a1"].forEach((c,i)=>{{for(let n=0;n<7;n++){{const q=document.createElement("i");q.className="xp-burst";q.style.background=c;q.style.left=(42+(i*4))+"%";q.style.top="45%";q.style.setProperty("--x",((Math.random()-.5)*620)+"px");q.style.setProperty("--y",((Math.random()-.5)*520)+"px");e.append(q)}}}});document.body.append(e);setTimeout(()=>e.remove(),2100)
}}else{{b.disabled=false;b.textContent="Agregar sello";r.textContent=d.detail||"No se pudo registrar.";}}'''
if js_old in main and "xp-stamp-success" not in main:
    main = main.replace(js_old, js_new, 1)
main_path.write_text(main, encoding="utf-8")

config_path = Path("/app/app/config.py")
config = config_path.read_text(encoding="utf-8")
field = '    google_wallet_test_enabled: bool = os.getenv("GOOGLE_WALLET_TEST_ENABLED", "false").strip().lower() in {"1", "true", "yes"}\n'
open_field = field + '    google_wallet_test_open: bool = os.getenv("GOOGLE_WALLET_TEST_OPEN", "false").strip().lower() in {"1", "true", "yes"}\n'
if "google_wallet_test_open:" not in config:
    if field not in config:
        raise SystemExit("Google Wallet test setting anchor missing")
    config = config.replace(field, open_field, 1)
config_path.write_text(config, encoding="utf-8")

main = main_path.read_text(encoding="utf-8")
old_gate = '''    google_wallet_test_allowed = (
        settings.google_wallet_test_enabled
        and bool(customer.email)
        and customer.email.strip().lower() in {item.strip() for item in (settings.google_wallet_test_emails + "," + settings.google_wallet_test_emails_extra).split(",") if item.strip()}
    )
'''
new_gate = '''    google_wallet_test_allowed = (
        settings.google_wallet_test_enabled
        and (
            settings.google_wallet_test_open
            or (
                bool(customer.email)
                and customer.email.strip().lower() in {item.strip() for item in (settings.google_wallet_test_emails + "," + settings.google_wallet_test_emails_extra).split(",") if item.strip()}
            )
        )
    )
'''
if old_gate in main:
    main = main.replace(old_gate, new_gate, 1)
elif "settings.google_wallet_test_open" not in main:
    raise SystemExit("Google Wallet test gate anchor missing")
main_path.write_text(main, encoding="utf-8")
print("Operator success feedback and open Wallet test mode installed")
