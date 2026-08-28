FROM mysql:8.4

COPY docker/mysql/entrypoint.sh /usr/local/bin/fasa-social-mysql-entrypoint.sh
COPY docker/mysql/healthcheck.sh /usr/local/bin/fasa-social-mysql-healthcheck.sh
RUN chmod 0755 /usr/local/bin/fasa-social-mysql-entrypoint.sh /usr/local/bin/fasa-social-mysql-healthcheck.sh

ENTRYPOINT ["/usr/local/bin/fasa-social-mysql-entrypoint.sh"]
