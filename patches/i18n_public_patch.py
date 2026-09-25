from pathlib import Path

base = Path("/app/app/templates/base.html")
html = base.read_text(encoding="utf-8")
script_tag = '  <script src="/static/i18n.js?v=20260925-1" defer></script>\n'
if "/static/i18n.js" not in html:
    html = html.replace('  <script src="/static/app.js?v=20260925-3" defer></script>\n', '  <script src="/static/app.js?v=20260925-3" defer></script>\n' + script_tag)
base.write_text(html, encoding="utf-8")

js = r'''(() => {
  const path = location.pathname;
  const supported = path === "/login" || path.startsWith("/club/") || path.startsWith("/m/") || path.startsWith("/wallet/mock/");
  if (!supported) return;

  const pairs = [
    ["Panel SaaS","SaaS Dashboard"],["Bienvenido.","Welcome."],
    ["Administra negocios, códigos y recurrencia desde un solo lugar.","Manage businesses, codes and repeat customers from one place."],
    ["Correo","Email"],["Contraseña","Password"],["Ingresar","Log in"],
    ["Nombre","Name"],["WhatsApp","WhatsApp"],["Email opcional","Optional email"],["Unirme al club","Join the club"],
    ["Sin instalar apps. Podrás guardar tu tarjeta en Wallet y decidir si activas ofertas por ubicación y push.","No app to install. You can save your card to Wallet and choose whether to enable location-based offers and notifications."],
    ["Acumula ","Collect "],[" visitas y recibe: "," visits and receive: "],
    ["PRÓXIMA RECOMPENSA","NEXT REWARD"],["MARKETING OPCIONAL","OPTIONAL MARKETING"],
    ["Activa beneficios cercanos","Enable nearby benefits"],
    ["Tú decides. Puedes permitir notificaciones y ubicación para recibir promociones relevantes cuando estés cerca.","You're in control. You can allow notifications and location to receive relevant offers when you're nearby."],
    ["Activar notificaciones","Enable notifications"],["Activar ubicación","Enable location"],
    ["⭐ Dejar reseña en Google","⭐ Leave a Google review"],["PROGRESO","PROGRESS"],
    [" recompensa disponible"," reward available"],[" recompensas disponibles"," rewards available"],
    ["Ver tarjeta completa","View full card"],["Miembro","Member"]
  ];
  const esToEn = new Map(pairs), enToEs = new Map(pairs.map(([es,en]) => [en,es]));

  function replaceText(lang) {
    const map = lang === "en" ? esToEn : enToEs;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(n => {
      if (n.parentElement && ["SCRIPT","STYLE"].includes(n.parentElement.tagName)) return;
      let value = n.nodeValue;
      for (const [from,to] of map) {
        if (value.includes(from)) value = value.split(from).join(to);
      }
      n.nodeValue = value;
    });
    document.documentElement.lang = lang;
    localStorage.setItem("exponenta_lang", lang);
    const btn = document.querySelector("[data-public-lang]");
    if (btn) btn.textContent = lang === "es" ? "ES / EN" : "EN / ES";
  }

  let lang = localStorage.getItem("exponenta_lang") || ((navigator.language || "").toLowerCase().startsWith("en") ? "en" : "es");
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "xp-public-lang";
  btn.setAttribute("data-public-lang","");
  btn.setAttribute("aria-label","Cambiar idioma / Change language");
  document.body.appendChild(btn);
  replaceText(lang);
  btn.addEventListener("click", () => {
    lang = lang === "es" ? "en" : "es";
    replaceText(lang);
  });
})();'''
Path("/app/app/static/i18n.js").write_text(js, encoding="utf-8")

css_path = Path("/app/app/static/app.css")
css = css_path.read_text(encoding="utf-8")
if "PUBLIC I18N V1" not in css:
    css += r"""
/* PUBLIC I18N V1 */
.xp-public-lang{position:fixed;right:14px;top:max(14px,env(safe-area-inset-top));z-index:120;border:1px solid #ddd4ca;background:rgba(255,253,249,.94);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);color:#5c5149;border-radius:999px;padding:9px 12px;font:inherit;font-size:.66rem;font-weight:900;letter-spacing:.04em;box-shadow:0 8px 24px rgba(42,30,22,.08);cursor:pointer}
.xp-public-lang:hover{border-color:#aa6338;color:#7b4326}
"""
css_path.write_text(css, encoding="utf-8")
print("Public ES/EN i18n installed")
