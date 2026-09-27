from pathlib import Path

main = Path("/app/app/main.py")
s = main.read_text()

marker = "@app."
helper = """# XP_DESTINATION_NORMALIZER
def xp_safe_destination(value):
    value = (value or "").strip()
    if value and not value.startswith(("http://", "https://")):
        value = "https://" + value
    return safe_destination(value)


"""

if "XP_DESTINATION_NORMALIZER" not in s:
    pos = s.find(marker)
    if pos < 0:
        raise SystemExit("FastAPI route marker not found")
    s = s[:pos] + helper + s[pos:]

# Route every existing destination validation through the normalizing wrapper.
# Keep the wrapper itself calling the original safe_destination.
before, sep, after = s.partition("# XP_DESTINATION_NORMALIZER")
if not sep:
    raise SystemExit("normalizer insertion failed")
after = after.replace("safe_destination(", "xp_safe_destination(")
after = after.replace("return xp_safe_destination(value)", "return safe_destination(value)", 1)
s = before + sep + after
main.write_text(s)

print("shared destination URL wrapper applied")
