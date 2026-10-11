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
echo "RESTORE_AUDIT_START"
psql -h /tmp -p 55432 -U postgres -d restorecheck -At -v ON_ERROR_STOP=1 <<'SQL'
SELECT 'AUDIT_TABLE|'||table_name||'|'||
       (xpath('/row/c/text()',query_to_xml(format('SELECT COUNT(*) AS c FROM %I.%I','public',table_name),false,true,'')))[1]::text
FROM information_schema.tables
WHERE table_schema='public' AND table_type='BASE TABLE'
ORDER BY table_name;
SELECT 'AUDIT_IMAGE_COLUMN|'||table_name||'|'||column_name||'|'||data_type
FROM information_schema.columns
WHERE table_schema='public' AND (column_name ILIKE '%logo%' OR column_name ILIKE '%image%' OR column_name ILIKE '%photo%' OR column_name ILIKE '%blob%')
ORDER BY table_name,column_name;
SQL
echo "RESTORE_AUDIT_OK"
psql -h /tmp -p 55432 -U postgres -d restorecheck -At -v ON_ERROR_STOP=1 <<'SQL'
SELECT 'PET_SURVEY|'||slug||'|org_id='||coalesce(organization_id::text,'NULL') FROM xp_surveys WHERE slug='pet-clinick';
SELECT 'PET_ORG_MATCHES|'||count(*) FROM organizations WHERE lower(name) LIKE '%pet%clin%';
SELECT 'PET_USER_MATCHES|'||count(*) FROM users WHERE lower(email)='hv.petclinik@gmail.com';
SELECT 'ORG_COLUMNS|'||string_agg(column_name,',') FROM information_schema.columns WHERE table_name='organizations';
SELECT 'USER_COLUMNS|'||string_agg(column_name,',') FROM information_schema.columns WHERE table_name='users';
SQL
echo "OBJECT_COPY_START"
key="verified/$(basename "$backup")"
aws --endpoint-url "$BACKUP_S3_ENDPOINT" s3 cp "$backup" "s3://$BACKUP_S3_BUCKET/$key" --no-progress --only-show-errors
remote_bytes=$(aws --endpoint-url "$BACKUP_S3_ENDPOINT" s3api head-object --bucket "$BACKUP_S3_BUCKET" --key "$key" --query ContentLength --output text)
local_bytes=$(wc -c < "$backup" | tr -d ' ')
test "$remote_bytes" = "$local_bytes"
aws --endpoint-url "$BACKUP_S3_ENDPOINT" s3 cp "$backup.sha256" "s3://$BACKUP_S3_BUCKET/$key.sha256" --no-progress --only-show-errors
echo "OBJECT_COPY_OK bytes=$remote_bytes key=$key"
su-exec postgres pg_ctl -D /tmp/exponenta-restore-data -m fast -w stop >/dev/null
trap - EXIT
sleep infinity
