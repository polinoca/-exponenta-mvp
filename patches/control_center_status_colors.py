from pathlib import Path

p=Path("/app/app/static/app.css")
s=p.read_text(encoding="utf-8")
marker="/* CONTROL CENTER STATUS COLORS */"
if marker not in s:
    s += r'''
/* CONTROL CENTER STATUS COLORS */
.xp-feature-grid .xp-toggle.on{background:#159447;color:#fff;box-shadow:0 2px 7px rgba(21,148,71,.24)}
.xp-feature-grid .xp-toggle.off{background:#c9372c;color:#fff;box-shadow:0 2px 7px rgba(201,55,44,.20)}
.xp-feature-grid .xp-toggle.on b::before{content:"● ";color:#c8f7d6}
.xp-feature-grid .xp-toggle.off b::before{content:"● ";color:#ffe0dc}
'''
p.write_text(s,encoding="utf-8")
print("Control Center status colors installed")
