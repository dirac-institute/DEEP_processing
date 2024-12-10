#!/bin/bash 

set -u

REPO=$(realpath $1)
PG_PORT=$2
DB_NAME=$3
PG_DATA_PATH=$REPO/_registry
unset PGUSER
unset PGPASSWORD
unset PGHOST
unset PGPORT

mkdir -p $PG_DATA_PATH
pushd $PG_DATA_PATH

initdb -D ${PG_DATA_PATH}
escaped_path=$(printf "'%s'\n" "$PG_DATA_PATH" | sed -e 's/[\/&]/\\&/g')
sed --in-place "s/#unix_socket_directories.*/unix_socket_directories = ${escaped_path}/g" ${PG_DATA_PATH}/postgresql.conf
sed --in-place "s/#port.*/port = ${PG_PORT}/g" ${PG_DATA_PATH}/postgresql.conf
sed --in-place "s/max_connections.*/max_connections = 8192/g" ${PG_DATA_PATH}/postgresql.conf
sed --in-place "s/#listen_addresses.*/listen_addresses = '*'/g" ${PG_DATA_PATH}/postgresql.conf

# allow all connections as anyone to any database on any interface
echo "host    all             all             0.0.0.0/0               trust" >> ${PG_DATA_PATH}/pg_hba.conf
# cat db/postgresql.conf | grep unix_

pg_ctl -D ${PG_DATA_PATH} -w start

createdb -p ${PG_PORT} -h ${PG_DATA_PATH} ${DB_NAME}

psql -h localhost -p ${PG_PORT} ${DB_NAME} -c "CREATE USER butler;"
psql -h localhost -p ${PG_PORT} ${DB_NAME} -c "ALTER USER butler WITH PASSWORD 'lsst';"
psql -h localhost -p ${PG_PORT} ${DB_NAME} -c "ALTER ROLE butler WITH CREATEDB;"
psql -h localhost -p ${PG_PORT} ${DB_NAME} -c "ALTER DATABASE ${DB_NAME} OWNER TO butler;"
psql -h localhost -p ${PG_PORT} ${DB_NAME} -c "CREATE EXTENSION btree_gist;"

printf "registry:\n  db: postgresql://butler:lsst@localhost:${PG_PORT}/${DB_NAME}\n" > ${REPO}/butler_seed.yaml

butler create ${REPO} --seed-config ${REPO}/butler_seed.yaml

pg_ctl -D ${PG_DATA_PATH} -w stop

mv $REPO/butler.yaml $REPO/butler.yaml.bak
sed --in-place "s/localhost/PGHOST/g" $REPO/butler.yaml.bak
mv ${PG_DATA_PATH}/postgresql.conf ${PG_DATA_PATH}/postgresql.conf.bak
sed --in-place "s/unix_socket_directories.*/unix_socket_directories = PGDATADIR/g" ${PG_DATA_PATH}/postgresql.conf.bak
