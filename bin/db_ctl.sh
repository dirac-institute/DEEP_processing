#!/bin/bash

set -u
REPO=$(realpath "$1")
DB=${REPO}/_registry
start_file="${DB}/repo.started"

if [[ "${2}" == "start" ]]; then
    if test -f "${start_file}"; then
        echo "database already started! check contents of ${start_file} for host" 1>&2
        exit 1
    fi
    hostname > "${start_file}"
    escaped_path=$(printf "'%s'\n" "${REPO}/_registry" | sed -e 's/[\/&]/\\&/g')
    sed "s/PGDATADIR/${escaped_path}/g" "${DB}/postgresql.conf.bak" > "${DB}/postgresql.conf"
fi

pg_ctl -D "${DB}" -w "$2"

if [[ "${2}" == "start" ]]; then
    sed "s/PGHOST/$(hostname)/g" "$REPO/butler.yaml.bak" > "$REPO/butler.yaml"
fi
if [[ "${2}" == "stop" ]]; then
    rm -f "$REPO/butler.yaml"
    rm -f "${DB}/postgresql.conf"
    rm -f "${start_file}"
fi
