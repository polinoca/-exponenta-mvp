from pathlib import Path

base = Path("/app/app/templates/base.html")
text = base.read_text(encoding="utf-8")
marker = "<!-- EXPONENTA UNIVERSAL PASSWORD TOGGLE V1 -->"
if marker not in text:
    if "</body>" not in text:
        raise SystemExit("base closing body anchor not found")
    script = r'''
<script>
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('input[type="password"]').forEach(function (input) {
    if (input.closest(".xp-password-wrap")) return;
    const wrap = document.createElement("div");
    wrap.className = "xp-password-wrap xp-password-wrap-universal";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "xp-password-toggle";
    button.setAttribute("aria-label", "Mostrar contraseña");
    button.setAttribute("aria-pressed", "false");
    button.textContent = "Mostrar";
    button.addEventListener("click", function () {
      const visible = input.type === "text";
      input.type = visible ? "password" : "text";
      button.textContent = visible ? "Mostrar" : "Ocultar";
      button.setAttribute("aria-label", visible ? "Mostrar contraseña" : "Ocultar contraseña");
      button.setAttribute("aria-pressed", String(!visible));
    });
    wrap.appendChild(button);
  });
});
</script>
<!-- EXPONENTA UNIVERSAL PASSWORD TOGGLE V1 -->'''
    text = text.replace("</body>", script + "\n</body>", 1)
    base.write_text(text, encoding="utf-8")

css = Path("/app/app/static/app.css")
styles = css.read_text(encoding="utf-8")
if "EXPONENTA UNIVERSAL PASSWORD TOGGLE V1" not in styles:
    styles += r'''
/* EXPONENTA UNIVERSAL PASSWORD TOGGLE V1 */
.xp-password-wrap-universal{position:relative;width:100%}
.xp-password-wrap-universal input[type=password],
.xp-password-wrap-universal input[type=text]{padding-right:84px!important}
.xp-password-wrap-universal .xp-password-toggle{z-index:2}
'''
    css.write_text(styles, encoding="utf-8")
print("Universal password visibility toggle installed")
