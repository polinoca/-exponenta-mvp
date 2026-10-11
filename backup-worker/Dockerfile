FROM postgres:18-alpine
RUN apk add --no-cache su-exec aws-cli
COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh
ENTRYPOINT ["/bin/sh", "/usr/local/bin/backup.sh"]
