#!/bin/sh
set -eu
mkdir -p /backups
echo "BACKUP_START $(date -u +%Y-%m-%dT%H:%M:%SZ)"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
tmp="/backups/exponenta-$stamp.dump.tmp"
out="/backups/exponenta-$stamp.dump"
if pg_dump --format=custom --no-owner --no-acl --file="$tmp" "$DATABASE_URL"; then
  pg_restore --list "$tmp" > /dev/null
  mv "$tmp" "$out"
  sha256sum "$out" > "$out.sha256"
  echo "BACKUP_OK file=$(basename "$out") bytes=$(wc -c < "$out")"
else
  echo "BACKUP_FAILED"
  rm -f "$tmp"
  exit 1
fi
sleep infinity
