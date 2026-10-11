from pathlib import Path
p=Path("/app/app/main.py");s=p.read_text(encoding="utf-8")
marker="# XP SURVEY CHECK CONFETTI V17"
if marker not in s:
 a=s.index("def xp_survey_thanks(");b=s.index("\n@app.",a);t=s[a:b]
 t=t.replace("Menciona el beneficio al personal. Aplican condiciones.","Menciona el beneficio al personal.<br>Aplican condiciones.")
 t=t.replace('body+=\'<section class="xp-thanks-card"><div class="xp-thanks-check" aria-hidden="true">✓</div>\'','body+=\'<section class="xp-thanks-card"><div class="xp-confetti-wrap"><button class="xp-thanks-check" type="button" aria-label="Celebrar respuesta registrada">✓</button><span class="xp-confetti-burst" aria-hidden="true"></span></div>\'')
 target="    body+='</section>'"
 inject="""    body+='''<style>
    .xp-confetti-wrap{position:relative;width:180px;height:105px;margin:0 auto 12px;display:grid;place-items:center}
    .xp-confetti-wrap .xp-thanks-check{background:#4BB8DE!important;color:#fff!important;position:relative;z-index:2;margin:0;border:0;cursor:pointer;touch-action:manipulation}
    .xp-confetti-wrap .xp-thanks-check:focus-visible{outline:3px solid var(--pet-accent);outline-offset:5px}
    .xp-confetti-burst{position:absolute;inset:0;pointer-events:none}
    .xp-confetti-piece{position:absolute;left:50%;top:50%;width:7px;height:11px;border-radius:2px;background:var(--pet-accent);opacity:0}
    .xp-confetti-wrap.xp-celebrate .xp-confetti-piece{animation:xp-confetti-fly 980ms cubic-bezier(.17,.7,.35,1) both;animation-delay:var(--delay)}
    @keyframes xp-confetti-fly{0%{opacity:0;transform:translate(-50%,-50%) scale(.2) rotate(0)}12%{opacity:1}78%{opacity:1}100%{opacity:0;transform:translate(calc(-50% + var(--x)),calc(-50% + var(--y))) rotate(var(--spin)) scale(.8)}}
    @media(prefers-reduced-motion:reduce){.xp-confetti-piece{animation:none!important}.xp-thanks-check{animation:none!important}}
    </style><script>(function(){
    var wrap=document.querySelector(".xp-confetti-wrap"),burst=document.querySelector(".xp-confetti-burst"),check=document.querySelector(".xp-thanks-check");
    if(!wrap||!burst||!check)return;
    var colors=["#2D71B1","#4BB8DE","#B1E1F7","#F5C66F","#fff"];
    for(var i=0;i<20;i++){var bit=document.createElement("i");bit.className="xp-confetti-piece";var angle=(i/20)*Math.PI*2;var distance=58+(i%4)*12;bit.style.setProperty("--x",Math.round(Math.cos(angle)*distance)+"px");bit.style.setProperty("--y",Math.round(Math.sin(angle)*distance)+"px");bit.style.setProperty("--spin",(180+i*37)+"deg");bit.style.setProperty("--delay",(i%5)*18+"ms");bit.style.background=colors[i%colors.length];burst.appendChild(bit)}
    function celebrate(){if(window.matchMedia("(prefers-reduced-motion: reduce)").matches)return;wrap.classList.remove("xp-celebrate");void wrap.offsetWidth;wrap.classList.add("xp-celebrate")}
    check.addEventListener("click",celebrate);setTimeout(celebrate,300);
    })();</script>'''
"""
 if target not in t:raise SystemExit("Missing thanks close")
 t=t.replace(target,inject+target,1)
 if "xp-confetti-wrap" not in t:raise SystemExit("Check element missing")
 s=s[:a]+t+s[b:];p.write_text(marker+"\n"+s,encoding="utf-8")
print("Lightweight confetti added around confirmation check, replays on tap")
