from pathlib import Path

path = Path("/app/app/main.py")
text = path.read_text(encoding="utf-8")

old = '''    if settings.force_https and forwarded_proto != "https" and request.url.hostname not in {"127.0.0.1", "localhost", "testserver"}:
        target = request.url.replace(scheme="https")
        return RedirectResponse(str(target), status_code=308)
'''

new = '''    health_path = request.url.path in {"/health", "/ready"}
    if (
        settings.force_https
        and not health_path
        and forwarded_proto != "https"
        and request.url.hostname not in {"127.0.0.1", "localhost", "testserver"}
    ):
        target = request.url.replace(scheme="https")
        return RedirectResponse(str(target), status_code=308)
'''

if old not in text:
    raise SystemExit("Expected HTTPS middleware block not found; refusing unsafe patch")

path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Patched HTTPS middleware: /health and /ready bypass redirects")
