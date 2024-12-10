#!/usr/bin/env bash
#SBATCH --partition=skx-dev
#SBATCH --time=00:15:00
#SBATCH --nodes=1

w=$DEEP_PROJECT_DIR

function cleanup() {
    $w/bin/db_ctl.sh $w/repo stop
}

trap cleanup SIGINT
trap cleanup SIGTERM

./bin/db_ctl.sh ./repo start
$@
./bin/db_ctl.sh ./repo stop

