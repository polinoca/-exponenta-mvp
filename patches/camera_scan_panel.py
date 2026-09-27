from pathlib import Path

main=Path("/app/app/main.py")
s=main.read_text(encoding="utf-8")
if "# XP CAMERA SCAN PANEL V1" not in s:
    anchor='@app.get("/negocio/lealtad", response_class=HTMLResponse)'
    if anchor not in s: raise SystemExit("camera route anchor missing")
    block=r'''
# XP CAMERA SCAN PANEL V1
@app.get("/negocio/operacion/escanear", response_class=HTMLResponse)
def business_camera_scan_panel(request: Request, db: Session = Depends(get_db)):
    user, org = business_admin_context(request, db)
    require_org_feature(db, org, "loyalty")
    return render(request, "business/camera_scan.html", {"user":user, "organization":org})

'''
    s=s.replace(anchor,block+anchor,1)
    main.write_text(s,encoding="utf-8")

tpl=Path("/app/app/templates/business/camera_scan.html")
tpl.write_text(r'''{% extends "base.html" %}
{% block title %}Escanear tarjeta · {{ organization.name }}{% endblock %}
{% block body %}
<main class="business-shell xp-scan-page">
  <nav class="xp-business-nav"><a href="/negocio">Inicio</a><a class="active" href="/negocio/operacion">Operación</a><a href="/negocio/lealtad">Clientes</a><a href="/negocio/seguridad">Equipo</a><a href="/negocio/marca">Marca</a></nav>
  <header class="xp-scan-head"><a href="/negocio/operacion">← Operación</a><span class="eyebrow">MODO CAJA</span><h1>Escanear tarjeta</h1><p>Apunta la cámara al QR del cliente. Al reconocerlo, se abrirá su registro para sumar una visita o punto.</p></header>
  <section class="xp-camera-card">
    <div class="xp-camera-stage" id="camera-stage">
      <video id="scan-video" playsinline muted></video>
      <canvas id="scan-canvas" hidden></canvas>
      <div class="xp-scan-frame"><i></i><i></i><i></i><i></i><b></b></div>
      <div class="xp-camera-empty" id="camera-empty"><span>⌁</span><strong>La cámara está apagada</strong><small>Presiona el botón para escanear.</small></div>
      <div class="xp-camera-status" id="scan-status" role="status">Listo para escanear.</div>
    </div>
    <button class="btn btn-primary xp-start-camera" id="start-camera" type="button">▣ Activar cámara y escanear</button>
    <p class="xp-camera-tip">Si el cliente usa <b>NFC</b>, no necesitas abrir la cámara: acerca su tarjeta al celular y se abrirá su registro automáticamente.</p>
  </section>
  <section class="xp-scan-alternatives"><div><span>¿NO TIENE SU TARJETA?</span><strong>Búscalo manualmente desde Clientes.</strong><small>Útil si el cliente cambió de celular o no puede abrir su QR.</small></div><a class="btn btn-secondary" href="/negocio/lealtad">Buscar cliente</a></section>
</main>
<script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js" defer></script>
<script>
(()=>{const v=document.getElementById("scan-video"),c=document.getElementById("scan-canvas"),ctx=c.getContext("2d",{willReadFrequently:true}),start=document.getElementById("start-camera"),empty=document.getElementById("camera-empty"),status=document.getElementById("scan-status");let stream=null,active=false,detector=null;
const say=(text,kind="")=>{status.textContent=text;status.className="xp-camera-status "+kind};
const tokenFrom=text=>{try{const u=new URL(text,location.origin),m=u.pathname.match(/^\/(?:s|m)\/([^/?#]+)/);return m&&m[1]}catch(e){const m=String(text).match(/\/(?:s|m)\/([^/?#]+)/);return m&&m[1]}};
const found=text=>{if(!active)return;const token=tokenFrom(text);if(!token){say("Este código no es una tarjeta de este negocio.","error");return}active=false;say("Tarjeta encontrada. Abriendo registro…","success");if(stream)stream.getTracks().forEach(t=>t.stop());setTimeout(()=>location.assign("/s/"+encodeURIComponent(token)),350)};
const fallback=()=>{if(!active||v.readyState<2){requestAnimationFrame(fallback);return}c.width=v.videoWidth;c.height=v.videoHeight;ctx.drawImage(v,0,0,c.width,c.height);const img=ctx.getImageData(0,0,c.width,c.height),code=window.jsQR&&window.jsQR(img.data,img.width,img.height,{inversionAttempts:"dontInvert"});if(code)found(code.data);else requestAnimationFrame(fallback)};
const nativeLoop=async()=>{if(!active)return;try{const codes=await detector.detect(v);if(codes[0])return found(codes[0].rawValue)}catch(e){}setTimeout(nativeLoop,220)};
start.addEventListener("click",async()=>{try{say("Solicitando cámara…");stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:"environment"},width:{ideal:1280},height:{ideal:720}},audio:false});v.srcObject=stream;await v.play();active=true;empty.hidden=true;start.disabled=true;start.textContent="Cámara activa";say("Busca el QR dentro del recuadro.");if("BarcodeDetector" in window){detector=new BarcodeDetector({formats:["qr_code"]});nativeLoop()}else fallback()}catch(e){say("No pudimos abrir la cámara. Revisa el permiso del navegador e inténtalo de nuevo.","error")}});window.addEventListener("pagehide",()=>stream&&stream.getTracks().forEach(t=>t.stop()))})()
</script>
{% endblock %}''',encoding="utf-8")

# Make the operation CTA lead directly into scanning; no intermediate operational screen.
guide=Path("/app/app/templates/business/operation_guide.html")
if guide.exists():
    t=guide.read_text(encoding="utf-8").replace('href="/operar">Abrir modo escáner','href="/negocio/operacion/escanear">Abrir modo escáner')
    guide.write_text(t,encoding="utf-8")

css=Path("/app/app/static/app.css")
c=css.read_text(encoding="utf-8")
if "/* XP CAMERA SCAN PANEL V1 */" not in c:
    c+=r'''
/* XP CAMERA SCAN PANEL V1 */
.xp-scan-page{max-width:800px!important}.xp-scan-head{margin:22px 0 16px}.xp-scan-head>a{display:inline-block;margin-bottom:15px;font-size:.75rem;font-weight:850;text-decoration:none}.xp-scan-head h1{margin:5px 0;font-size:clamp(2.2rem,6vw,3.4rem)!important}.xp-scan-head p{max-width:600px;color:#6d635c}.xp-camera-card{border:1px solid #e4d9d0;border-radius:25px;background:#fff;padding:15px;box-shadow:0 14px 30px rgba(56,34,20,.08)}.xp-camera-stage{position:relative;overflow:hidden;min-height:345px;border-radius:18px;background:#151515;display:grid;place-items:center}.xp-camera-stage video{position:absolute;width:100%;height:100%;inset:0;object-fit:cover}.xp-camera-empty{z-index:2;display:grid;gap:7px;text-align:center;color:#fff}.xp-camera-empty span{font-size:2rem;color:#d2b09a}.xp-camera-empty strong{font-size:1.05rem}.xp-camera-empty small{font-size:.76rem;color:#c7c0b9}.xp-scan-frame{position:relative;z-index:3;width:min(58vw,240px);height:min(58vw,240px);pointer-events:none}.xp-scan-frame i{position:absolute;width:32px;height:32px;border-color:#fff;border-style:solid}.xp-scan-frame i:nth-child(1){top:0;left:0;border-width:4px 0 0 4px;border-radius:8px 0 0 0}.xp-scan-frame i:nth-child(2){top:0;right:0;border-width:4px 4px 0 0;border-radius:0 8px 0 0}.xp-scan-frame i:nth-child(3){bottom:0;left:0;border-width:0 0 4px 4px;border-radius:0 0 0 8px}.xp-scan-frame i:nth-child(4){bottom:0;right:0;border-width:0 4px 4px 0;border-radius:0 0 8px 0}.xp-scan-frame b{display:block;position:absolute;left:12px;right:12px;top:50%;height:2px;background:#f5b883;box-shadow:0 0 13px #f5b883;animation:xp-scan-line 2s ease-in-out infinite}@keyframes xp-scan-line{0%,100%{transform:translateY(-85px)}50%{transform:translateY(85px)}}.xp-camera-status{position:absolute;z-index:4;bottom:13px;left:13px;right:13px;border-radius:11px;padding:10px 12px;background:rgba(0,0,0,.64);backdrop-filter:blur(8px);color:#fff;text-align:center;font-size:.75rem;font-weight:760}.xp-camera-status.error{background:rgba(149,40,32,.89)}.xp-camera-status.success{background:rgba(27,115,55,.88)}.xp-start-camera{width:100%;justify-content:center;margin-top:13px;font-size:.9rem}.xp-start-camera:disabled{opacity:.7;cursor:default}.xp-camera-tip{margin:13px 4px 2px;text-align:center;font-size:.72rem;color:#71675f}.xp-scan-alternatives{display:flex;align-items:center;justify-content:space-between;gap:15px;margin-top:17px;padding:19px 4px}.xp-scan-alternatives div{display:grid;gap:4px}.xp-scan-alternatives span{font-size:.58rem;letter-spacing:.12em;font-weight:900;color:#9a694b}.xp-scan-alternatives strong{font-size:.88rem;color:#3f362f}.xp-scan-alternatives small{font-size:.72rem;color:#776c64}@media(max-width:600px){.xp-camera-stage{min-height:430px}.xp-scan-alternatives{align-items:flex-start;flex-direction:column}.xp-scan-alternatives .btn{width:100%}}
'''
    css.write_text(c,encoding="utf-8")
print("Camera scan panel installed")
