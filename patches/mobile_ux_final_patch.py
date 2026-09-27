from pathlib import Path

css_path = Path("/app/app/static/app.css")
css = css_path.read_text(encoding="utf-8")
marker = "/* MOBILE UX FINAL V1 */"
if marker not in css:
    css += r"""

/* MOBILE UX FINAL V1 */
@media (max-width: 760px) {
  html, body { max-width: 100%; overflow-x: hidden; }
  img, svg, video, canvas { max-width: 100%; height: auto; }
  button, a, input, select, textarea { touch-action: manipulation; }
  .xp4 { overflow: hidden; }
  .xp4-wrap { width: min(100% - 32px, 680px); }
  .xp4-top { padding: 9px 18px; font-size: .67rem; text-align: center; }
  .xp4-nav { position: relative; }
  .xp4-navin { min-height: 68px; gap: 10px; }
  .xp4-logo { flex: 1 1 auto; min-width: 0; }
  .xp4-logo img { width: 122px; max-height: 48px; object-fit: contain; }
  .xp4-nav nav, .xp5-lang { display: none; }
  .xp4-navin > .xp4-btn { min-height: 40px; padding: 0 14px; white-space: nowrap; }
  .xp4-hero { padding-top: 54px; padding-bottom: 46px; }
  .xp4-hero h1 { font-size: clamp(2.55rem, 13vw, 4rem); line-height: .94; letter-spacing: -.065em; }
  .xp4-hero > p { max-width: 34rem; font-size: 1rem; line-height: 1.55; }
  .xp4-actions { display: grid; grid-template-columns: 1fr; gap: 10px; width: 100%; }
  .xp4-actions .xp4-btn { justify-content: center; min-height: 50px; }
  .xp5-hero-media { min-height: 430px; height: min(118vw, 500px); margin-top: 30px; overflow: hidden; border-radius: 25px; }
  .xp5-hero-media > img { width: 100%; height: 100%; object-fit: cover; object-position: 56% center; }
  .xp5-phone { width: min(57vw, 245px); right: 4.5%; bottom: 14px; transform: none; }
  .xp5-phone-top { font-size: .48rem; }
  .xp5-card { padding: 17px 14px; }
  .xp5-card h3 { font-size: 1.17rem; line-height: 1.02; }
  .xp5-card strong { font-size: 2.4rem; }
  .xp5-toast { max-width: 164px; padding: 9px 10px; gap: 7px; border-radius: 13px; }
  .xp5-toast span { width: 26px; height: 26px; flex: 0 0 26px; }
  .xp5-toast b, .xp5-toast small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .xp5-toast-a { left: 10px; top: 34px; }
  .xp5-toast-b { left: 10px; bottom: 22px; }
  .xp4-intro, .xp4-program, .xp4-how, .xp5-cases, .xp5-connected, .xp4-tools, .xp4-compare, .xp4-faq { padding-top: 58px; padding-bottom: 58px; }
  .xp4-intro h2, .xp4-program h2, .xp4-how h2, .xp5-cases h2, .xp5-connected h2, .xp4-tools h2, .xp4-compare h2, .xp4-faq h2 { font-size: clamp(2rem, 10vw, 2.8rem); line-height: .98; letter-spacing: -.045em; }
  .xp4-benefits { gap: 42px; }
  .xp4-benefits article, .xp4-benefits article.reverse { display: flex; flex-direction: column; gap: 22px; }
  .xp4-benefits article.reverse .xp4-copy { order: 0; }
  .xp4-benefits article.reverse .xp4-visual { order: 1; }
  .xp4-visual, .xp5-photo-visual { width: 100%; min-height: 330px; overflow: hidden; border-radius: 22px; }
  .xp4-visual > img { width: 100%; height: 100%; object-fit: cover; }
  .xp4-loyalty, .xp5-overlay-card, .xp4-metrics, .xp5-overlay-metrics, .xp4-review, .xp5-overlay-review { max-width: calc(100% - 28px); left: 14px; right: 14px; bottom: 14px; }
  .xp4-metrics { grid-template-columns: 1fr 1fr; gap: 8px; }
  .xp4-metrics .wide { grid-column: 1 / -1; }
  .xp4-review { padding: 16px; }
  .xp4-review button { width: 100%; min-height: 44px; }
  .xp4-programgrid, .xp4-steps, .xp5-casegrid, .xp4-toolgrid, .xp4-comparegrid, .xp5-connected-grid { grid-template-columns: 1fr; }
  .xp4-programgrid article, .xp4-steps article { min-height: 0; }
  .xp4-stepmock { min-height: 135px; }
  .xp5-casegrid { gap: 14px; }
  .xp5-casegrid article { min-height: 260px; overflow: hidden; border-radius: 20px; }
  .xp5-casegrid article > img { width: 100%; height: 100%; object-fit: cover; }
  .xp5-casegrid article > div { position: relative; inset: auto; margin-top: -1px; }
  .xp5-connected { overflow: hidden; }
  .xp5-connected-grid { gap: 30px; }
  .xp5-connected-visual { min-height: 385px; overflow: hidden; }
  .xp5-card-large { width: min(82vw, 330px); left: 50%; transform: translateX(-50%); }
  .xp5-notification { max-width: 170px; font-size: .65rem; }
  .xp5-notification.n1 { left: 4px; top: 26px; }
  .xp5-notification.n2 { right: 4px; bottom: 72px; }
  .xp5-notification.n3 { left: 4px; bottom: 18px; }
  .xp5-wallet-row { display: grid; grid-template-columns: 1fr; gap: 8px; }
  .xp4-final { padding: 65px 0; }
  .xp4-final h2 { font-size: clamp(2.15rem, 11vw, 3rem); }
  .xp4-footer { display: grid; gap: 13px; text-align: center; justify-items: center; padding-top: 28px; padding-bottom: 28px; }
  .app-shell, .dashboard-shell, .business-shell, .panel-shell, .admin-shell { max-width: 100%; overflow-x: hidden; }
  .app-shell .topbar, .dashboard-shell .topbar, .business-shell .topbar, .panel-topbar { flex-wrap: wrap; gap: 10px; }
  .app-shell .topbar nav, .dashboard-shell .topbar nav, .business-shell .topbar nav, .panel-topbar nav { width: 100%; overflow-x: auto; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
  .app-shell .topbar nav::-webkit-scrollbar, .dashboard-shell .topbar nav::-webkit-scrollbar, .business-shell .topbar nav::-webkit-scrollbar, .panel-topbar nav::-webkit-scrollbar { display: none; }
  .app-shell .topbar nav a, .dashboard-shell .topbar nav a, .business-shell .topbar nav a, .panel-topbar nav a { flex: 0 0 auto; min-height: 42px; display: inline-flex; align-items: center; }
  .panel-grid, .dashboard-grid, .business-grid, .stats-grid, .metrics-grid, .xp-ss-steps, .xp-onboarding-v2 .xp-ss-steps { grid-template-columns: 1fr !important; }
  .stat-grid, .stats-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .panel-card, .card, .stat-card { min-width: 0; overflow-wrap: anywhere; }
  .panel-card table, .card table, .business-shell table, .admin-shell table { display: block; width: 100%; max-width: 100%; overflow-x: auto; white-space: nowrap; -webkit-overflow-scrolling: touch; }
  .form-grid, .form-row, .settings-grid, .xp-wallet-branding { grid-template-columns: 1fr !important; }
  .form-stack input, .form-stack select, .form-stack textarea, .panel-card input, .panel-card select, .panel-card textarea { max-width: 100%; }
  .btn, .button, button[type="submit"] { min-height: 44px; }
  .xp-onboarding-steps > a { min-width: 0; }
}
@media (max-width: 390px) {
  .xp4-wrap { width: min(100% - 24px, 680px); }
  .xp4-hero h1 { font-size: 2.42rem; }
  .xp5-hero-media { min-height: 400px; }
  .xp5-phone { width: 58vw; }
  .xp5-toast { max-width: 145px; }
  .stat-grid, .stats-row { grid-template-columns: 1fr; }
}
"""
    css_path.write_text(css, encoding="utf-8")
print("Mobile UX final styles installed")
