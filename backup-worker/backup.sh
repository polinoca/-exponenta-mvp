#!/bin/sh
set -eu
backup="/backups/exponenta-20261011T222032Z.dump"
test -s "$backup"
cd /backups
sha256sum -c "$(basename "$backup").sha256"
pg_restore --list "$backup" >/dev/null
echo "RESTORE_TEST_START $(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p /tmp/exponenta-restore-data
chown postgres:postgres /tmp/exponenta-restore-data
su-exec postgres initdb -D /tmp/exponenta-restore-data -A trust --no-instructions >/dev/null
su-exec postgres pg_ctl -D /tmp/exponenta-restore-data -o "-k /tmp -p 55432 -c listen_addresses=''" -w start >/dev/null
trap 'su-exec postgres pg_ctl -D /tmp/exponenta-restore-data -m immediate stop >/dev/null 2>&1 || true' EXIT
createdb -h /tmp -p 55432 -U postgres restorecheck
pg_restore --exit-on-error --no-owner --no-acl -h /tmp -p 55432 -U postgres -d restorecheck "$backup"
tables=$(psql -h /tmp -p 55432 -U postgres -d restorecheck -Atc "select count(*) from information_schema.tables where table_schema='public' and table_type='BASE TABLE'")
test "$tables" -gt 0
echo "RESTORE_TEST_OK tables=$tables file=$(basename "$backup")"
su-exec postgres pg_ctl -D /tmp/exponenta-restore-data -m fast -w stop >/dev/null
trap - EXIT
sleep infinity
