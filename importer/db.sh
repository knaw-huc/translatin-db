set -x

grep -C4 db config.ini \
	| tail -5 \
	| sed -e 's/: /=/' \
	      -e 's/database/dbname/' \
> pgserv.conf

PGSERVICEFILE=pgserv.conf psql service=db
